"""
Slack Integration Service
Handles Slack communication for PM alerts and responses
"""

import logging
import os
import asyncio
from typing import Dict, Any, Optional, Callable
from datetime import datetime

logger = logging.getLogger(__name__)


class SlackService:
    """Service for Slack integration with PM group"""

    def __init__(self, websocket_manager=None):
        """
        Initialize Slack service

        Args:
            websocket_manager: WebSocket manager for broadcasting PM responses
        """
        self.websocket_manager = websocket_manager
        self.slack_client = None
        self.pm_channel_id = os.getenv('SLACK_PM_CHANNEL_ID')
        self.bot_token = os.getenv('SLACK_BOT_TOKEN')
        self.signing_secret = os.getenv('SLACK_SIGNING_SECRET')

        # Thread tracking: maps message timestamps to meeting context
        self.active_threads = {}

        # Response callback handlers
        self.response_handlers = []

        # Initialize Slack client if credentials available
        if self.bot_token and self.pm_channel_id:
            self._initialize_slack_client()
        else:
            logger.warning(
                "Slack credentials not configured. "
                "Set SLACK_BOT_TOKEN and SLACK_PM_CHANNEL_ID in .env"
            )

    def _initialize_slack_client(self):
        """Initialize Slack SDK client"""
        try:
            from slack_sdk import WebClient
            from slack_sdk.errors import SlackApiError

            self.slack_client = WebClient(token=self.bot_token)

            # Test connection
            response = self.slack_client.auth_test()
            logger.info(f"Slack client initialized successfully. Bot: {response['user']}")

        except ImportError:
            logger.error(
                "Slack SDK not installed. Install with: pip install slack-sdk"
            )
            self.slack_client = None
        except Exception as e:
            logger.error(f"Failed to initialize Slack client: {str(e)}")
            self.slack_client = None

    async def send_pm_alert(
        self,
        message_content: Dict[str, Any],
        meeting_context: Optional[Dict[str, Any]] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Send knowledge gap alert to PM Slack channel

        Args:
            message_content: Formatted Slack message (from KnowledgeGapAgent.format_slack_message)
            meeting_context: Meeting metadata for tracking

        Returns:
            Dict with message timestamp and channel ID, or None if failed
        """
        if not self.slack_client:
            logger.warning("Slack client not initialized. Returning mock response.")
            return self._mock_send_message(message_content, meeting_context)

        try:
            from slack_sdk.errors import SlackApiError

            # Send message to PM channel
            response = self.slack_client.chat_postMessage(
                channel=self.pm_channel_id,
                text=message_content.get('text', 'Knowledge Gap Alert'),
                blocks=message_content.get('blocks', []),
                unfurl_links=False,
                unfurl_media=False
            )

            # Track this thread
            thread_ts = response['ts']
            self.active_threads[thread_ts] = {
                'meeting_context': meeting_context,
                'question': message_content.get('text'),
                'timestamp': datetime.utcnow().isoformat(),
                'status': 'waiting_for_pm'
            }

            logger.info(
                f"Slack message sent successfully. Thread: {thread_ts}, "
                f"Channel: {self.pm_channel_id}"
            )

            # Start listening for replies in this thread
            asyncio.create_task(self._monitor_thread(thread_ts))

            return {
                'thread_ts': thread_ts,
                'channel': self.pm_channel_id,
                'success': True,
                'message': 'PM notified via Slack'
            }

        except SlackApiError as e:
            logger.error(f"Slack API error: {e.response['error']}")
            return {
                'success': False,
                'error': e.response['error']
            }
        except Exception as e:
            logger.error(f"Error sending Slack message: {str(e)}", exc_info=True)
            return {
                'success': False,
                'error': str(e)
            }

    async def _monitor_thread(self, thread_ts: str, max_duration: int = 1800):
        """
        Monitor a Slack thread for PM responses

        Args:
            thread_ts: Thread timestamp to monitor
            max_duration: Maximum monitoring duration in seconds (default 30 minutes)
        """
        start_time = datetime.utcnow()
        check_interval = 5  # Check every 5 seconds

        logger.info(f"Started monitoring Slack thread: {thread_ts}")

        try:
            while (datetime.utcnow() - start_time).seconds < max_duration:
                # Check for new replies
                pm_response = await self._check_thread_replies(thread_ts)

                if pm_response:
                    # PM responded! Broadcast to WebSocket
                    await self._handle_pm_response(thread_ts, pm_response)
                    break

                # Wait before next check
                await asyncio.sleep(check_interval)

            # Cleanup if monitoring expired
            if thread_ts in self.active_threads:
                self.active_threads[thread_ts]['status'] = 'expired'
                logger.warning(f"Thread monitoring expired: {thread_ts}")

        except Exception as e:
            logger.error(f"Error monitoring thread {thread_ts}: {str(e)}")

    async def _check_thread_replies(self, thread_ts: str) -> Optional[Dict[str, Any]]:
        """
        Check if PM has replied to thread

        Args:
            thread_ts: Thread timestamp

        Returns:
            PM response dict if found, None otherwise
        """
        if not self.slack_client:
            return None

        try:
            from slack_sdk.errors import SlackApiError

            # Get thread replies
            response = self.slack_client.conversations_replies(
                channel=self.pm_channel_id,
                ts=thread_ts,
                limit=10
            )

            messages = response.get('messages', [])

            # Check if there are replies (more than just the original message)
            if len(messages) > 1:
                # Get latest reply (skip the first message which is the alert)
                for msg in messages[1:]:
                    # Skip bot's own messages
                    if msg.get('bot_id'):
                        continue

                    # This is a human reply from PM
                    thread_info = self.active_threads.get(thread_ts, {})

                    # Check if we've already processed this reply
                    if thread_info.get('status') == 'answered':
                        continue

                    return {
                        'text': msg.get('text', ''),
                        'user': msg.get('user'),
                        'timestamp': msg.get('ts'),
                        'thread_ts': thread_ts
                    }

            return None

        except SlackApiError as e:
            logger.error(f"Error fetching thread replies: {e.response['error']}")
            return None
        except Exception as e:
            logger.error(f"Error checking thread replies: {str(e)}")
            return None

    async def _handle_pm_response(self, thread_ts: str, pm_response: Dict[str, Any]):
        """
        Handle PM response from Slack thread

        Args:
            thread_ts: Thread timestamp
            pm_response: PM's response message
        """
        thread_info = self.active_threads.get(thread_ts)

        if not thread_info:
            logger.warning(f"No thread info found for {thread_ts}")
            return

        # Update thread status
        thread_info['status'] = 'answered'
        thread_info['pm_response'] = pm_response
        thread_info['answered_at'] = datetime.utcnow().isoformat()

        # Get meeting context
        meeting_context = thread_info.get('meeting_context', {})

        # Build WebSocket message
        ws_message = {
            'type': 'pm_response_received',
            'data': {
                'response_text': pm_response.get('text'),
                'pm_user_id': pm_response.get('user'),
                'original_question': thread_info.get('question'),
                'meeting_context': meeting_context,
                'timestamp': pm_response.get('timestamp')
            },
            'metadata': {
                'thread_ts': thread_ts,
                'answered_at': thread_info['answered_at']
            }
        }

        # Broadcast to WebSocket (sales rep extension)
        if self.websocket_manager:
            await self.websocket_manager.broadcast(ws_message)
            logger.info(f"PM response broadcasted to sales rep: {pm_response.get('text')[:100]}")

        # Call registered response handlers
        for handler in self.response_handlers:
            try:
                await handler(thread_info, pm_response)
            except Exception as e:
                logger.error(f"Error in response handler: {str(e)}")

        # TODO: Store PM response in knowledge base for future meetings
        await self._store_in_knowledge_base(thread_info, pm_response)

    async def _store_in_knowledge_base(
        self,
        thread_info: Dict[str, Any],
        pm_response: Dict[str, Any]
    ):
        """
        Store PM response in knowledge base for future reference

        Args:
            thread_info: Thread metadata
            pm_response: PM's response
        """
        # TODO: Integrate with ChromaDB to store Q&A pairs
        logger.info(
            f"TODO: Store knowledge - Q: {thread_info.get('question')[:50]}, "
            f"A: {pm_response.get('text')[:50]}"
        )

    def register_response_handler(self, handler: Callable):
        """
        Register callback for PM responses

        Args:
            handler: Async function to call when PM responds
        """
        self.response_handlers.append(handler)
        logger.info(f"Registered response handler: {handler.__name__}")

    def get_thread_status(self, thread_ts: str) -> Optional[Dict[str, Any]]:
        """
        Get status of a Slack thread

        Args:
            thread_ts: Thread timestamp

        Returns:
            Thread info dict or None
        """
        return self.active_threads.get(thread_ts)

    def get_active_threads(self) -> Dict[str, Dict[str, Any]]:
        """
        Get all active threads

        Returns:
            Dict of active threads
        """
        return {
            ts: info for ts, info in self.active_threads.items()
            if info.get('status') != 'expired'
        }

    def _mock_send_message(
        self,
        message_content: Dict[str, Any],
        meeting_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Mock Slack message send for testing without credentials

        Args:
            message_content: Message to send
            meeting_context: Meeting metadata

        Returns:
            Mock response
        """
        mock_thread_ts = f"mock_{datetime.utcnow().timestamp()}"

        logger.info("=" * 80)
        logger.info("MOCK SLACK MESSAGE (Slack not configured)")
        logger.info("=" * 80)
        logger.info(f"Text: {message_content.get('text')}")
        logger.info(f"Blocks: {len(message_content.get('blocks', []))} blocks")
        if meeting_context:
            logger.info(f"Meeting: {meeting_context.get('company_name', 'Unknown')}")
        logger.info("=" * 80)

        # Track mock thread
        self.active_threads[mock_thread_ts] = {
            'meeting_context': meeting_context,
            'question': message_content.get('text'),
            'timestamp': datetime.utcnow().isoformat(),
            'status': 'mock'
        }

        return {
            'thread_ts': mock_thread_ts,
            'channel': 'MOCK_CHANNEL',
            'success': True,
            'message': 'Mock Slack message (Slack not configured)',
            'mock': True
        }

    async def send_test_message(self, text: str = "Test message from Meetstream AI"):
        """
        Send a test message to verify Slack integration

        Args:
            text: Test message text

        Returns:
            Response from Slack API
        """
        if not self.slack_client:
            logger.error("Cannot send test message - Slack client not initialized")
            return None

        try:
            response = self.slack_client.chat_postMessage(
                channel=self.pm_channel_id,
                text=text
            )
            logger.info(f"Test message sent successfully: {response['ts']}")
            return response
        except Exception as e:
            logger.error(f"Error sending test message: {str(e)}")
            return None

    def is_configured(self) -> bool:
        """Check if Slack is properly configured"""
        return self.slack_client is not None and self.pm_channel_id is not None
