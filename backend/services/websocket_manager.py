"""
WebSocket Manager
Manages WebSocket connections from Chrome extensions
"""

import logging
import uuid
import json
from typing import Dict, Set, Any, Optional, List
from fastapi import WebSocket
from datetime import datetime

logger = logging.getLogger(__name__)


class WebSocketManager:
    """Manages multiple WebSocket connections"""

    def __init__(self):
        # Active connections: {websocket: connection_id}
        self.active_connections: Dict[WebSocket, str] = {}

        # Reverse mapping: {connection_id: websocket}
        self.connections_by_id: Dict[str, WebSocket] = {}

        # Store connection metadata
        self.connection_metadata: Dict[str, Dict[str, Any]] = {}

        logger.info("WebSocket manager initialized")

    async def connect(self, websocket: WebSocket) -> str:
        """
        Accept a new WebSocket connection

        Args:
            websocket: FastAPI WebSocket object

        Returns:
            connection_id: Unique ID for this connection
        """
        await websocket.accept()

        connection_id = str(uuid.uuid4())
        self.active_connections[websocket] = connection_id
        self.connections_by_id[connection_id] = websocket

        # Store metadata
        self.connection_metadata[connection_id] = {
            "connected_at": datetime.utcnow().isoformat(),
            "message_count": 0,
            "last_activity": datetime.utcnow().isoformat()
        }

        logger.info(f"WebSocket connected: {connection_id} (total: {len(self.active_connections)})")

        return connection_id

    def disconnect(self, websocket: WebSocket):
        """
        Remove a WebSocket connection

        Args:
            websocket: FastAPI WebSocket object
        """
        if websocket in self.active_connections:
            connection_id = self.active_connections[websocket]

            # Remove from all mappings
            del self.active_connections[websocket]
            del self.connections_by_id[connection_id]
            del self.connection_metadata[connection_id]

            logger.info(f"WebSocket disconnected: {connection_id} (remaining: {len(self.active_connections)})")

    def get_connection_id(self, websocket: WebSocket) -> Optional[str]:
        """Get connection ID for a websocket"""
        return self.active_connections.get(websocket)

    def get_websocket(self, connection_id: str) -> Optional[WebSocket]:
        """Get websocket for a connection ID"""
        return self.connections_by_id.get(connection_id)

    async def send_to_connection(self, websocket: WebSocket, message: Dict[str, Any]):
        """
        Send a message to a specific WebSocket connection

        Args:
            websocket: Target WebSocket
            message: Message dict to send (will be JSON serialized)
        """
        try:
            connection_id = self.get_connection_id(websocket)
            if not connection_id:
                logger.warning("Attempted to send to unknown websocket")
                return

            # Update metadata
            if connection_id in self.connection_metadata:
                self.connection_metadata[connection_id]["message_count"] += 1
                self.connection_metadata[connection_id]["last_activity"] = datetime.utcnow().isoformat()

            # Send message
            await websocket.send_text(json.dumps(message))

            logger.debug(f"Sent message to {connection_id}: {message.get('type')}")

        except Exception as e:
            logger.error(f"Error sending message to {connection_id}: {str(e)}")
            self.disconnect(websocket)

    async def send_to_connection_by_id(self, connection_id: str, message: Dict[str, Any]):
        """
        Send a message to a connection by ID

        Args:
            connection_id: Target connection ID
            message: Message dict to send
        """
        websocket = self.get_websocket(connection_id)
        if websocket:
            await self.send_to_connection(websocket, message)
        else:
            logger.warning(f"Connection not found: {connection_id}")

    async def broadcast(self, message: Dict[str, Any], exclude: Optional[Set[str]] = None):
        """
        Broadcast a message to all connected clients

        Args:
            message: Message dict to broadcast
            exclude: Optional set of connection IDs to exclude
        """
        exclude = exclude or set()

        logger.debug(f"Broadcasting message type '{message.get('type')}' to {len(self.active_connections) - len(exclude)} clients")

        disconnected = []

        for websocket, connection_id in list(self.active_connections.items()):
            if connection_id not in exclude:
                try:
                    await self.send_to_connection(websocket, message)
                except Exception as e:
                    logger.error(f"Error broadcasting to {connection_id}: {str(e)}")
                    disconnected.append(websocket)

        # Clean up disconnected websockets
        for websocket in disconnected:
            self.disconnect(websocket)

    async def broadcast_to_meeting(self, meeting_id: str, message: Dict[str, Any]):
        """
        Broadcast to all connections watching a specific meeting

        Args:
            meeting_id: Meeting ID to broadcast to
            message: Message dict to broadcast

        Note: This requires tracking which connections are in which meetings
        """
        # TODO: Implement meeting room tracking
        # For now, just broadcast to all
        await self.broadcast(message)

    def get_active_connections_count(self) -> int:
        """Get number of active connections"""
        return len(self.active_connections)

    def get_active_connections(self) -> List[WebSocket]:
        """Get list of all active WebSocket connections"""
        return list(self.active_connections)

    def get_connection_stats(self) -> Dict[str, Any]:
        """Get statistics about connections"""
        return {
            "total_connections": len(self.active_connections),
            "connections": [
                {
                    "connection_id": conn_id,
                    "metadata": self.connection_metadata.get(conn_id, {})
                }
                for conn_id in self.connections_by_id.keys()
            ]
        }

    async def send_agent_update(
        self,
        websocket: WebSocket,
        agent_name: str,
        status: str,
        message: Optional[str] = None,
        data: Optional[Dict[str, Any]] = None
    ):
        """
        Send an agent status update to a connection

        Args:
            websocket: Target websocket
            agent_name: Name of the agent
            status: Status (e.g., "started", "processing", "completed", "error")
            message: Optional status message
            data: Optional data payload
        """
        payload = {
            "type": "agent_update",
            "agent_name": agent_name,
            "status": status,
            "timestamp": datetime.utcnow().isoformat()
        }

        if message:
            payload["message"] = message

        if data:
            payload["data"] = data

        await self.send_to_connection(websocket, payload)

    async def send_insight(
        self,
        websocket: WebSocket,
        insight_type: str,
        title: str,
        content: str,
        source: Optional[str] = None,
        priority: str = "normal",
        metadata: Optional[Dict[str, Any]] = None
    ):
        """
        Send a sales insight to the Chrome extension

        Args:
            websocket: Target websocket
            insight_type: Type of insight ("company_research", "objection_handling", "next_steps", etc.)
            title: Title of the insight
            content: Main insight content
            source: Source of the insight (e.g., "Research Agent", "LinkedIn")
            priority: Priority level ("low", "normal", "high", "critical")
            metadata: Optional additional metadata
        """
        payload = {
            "type": "insight",
            "insight_type": insight_type,
            "title": title,
            "content": content,
            "source": source,
            "priority": priority,
            "timestamp": datetime.utcnow().isoformat(),
            "metadata": metadata or {}
        }

        await self.send_to_connection(websocket, payload)

    async def send_error(
        self,
        websocket: WebSocket,
        error_message: str,
        error_code: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        """
        Send an error message to a connection

        Args:
            websocket: Target websocket
            error_message: Error message
            error_code: Optional error code
            details: Optional error details
        """
        payload = {
            "type": "error",
            "message": error_message,
            "timestamp": datetime.utcnow().isoformat()
        }

        if error_code:
            payload["error_code"] = error_code

        if details:
            payload["details"] = details

        await self.send_to_connection(websocket, payload)

    async def send_pm_response(
        self,
        websocket: WebSocket,
        question: str,
        response: str,
        pm_user: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """
        Send PM response from Slack to the sales rep

        Args:
            websocket: Target websocket
            question: Original question that was asked
            response: PM's response from Slack
            pm_user: PM user identifier
            metadata: Optional additional metadata
        """
        payload = {
            "type": "pm_response_received",
            "data": {
                "original_question": question,
                "response_text": response,
                "pm_user": pm_user,
                "timestamp": datetime.utcnow().isoformat()
            },
            "metadata": metadata or {}
        }

        await self.send_to_connection(websocket, payload)

        logger.info(f"PM response sent to sales rep: {response[:100]}...")

    async def send_knowledge_gap_alert(
        self,
        websocket: WebSocket,
        question: str,
        status: str = "notified",
        slack_thread: Optional[str] = None
    ):
        """
        Send knowledge gap detection alert to sales rep

        Args:
            websocket: Target websocket
            question: Question that triggered the gap
            status: Status of the alert ("notified", "answered", "pending")
            slack_thread: Optional Slack thread ID
        """
        payload = {
            "type": "knowledge_gap_detected",
            "data": {
                "question": question,
                "status": status,
                "slack_thread": slack_thread,
                "timestamp": datetime.utcnow().isoformat()
            }
        }

        await self.send_to_connection(websocket, payload)
