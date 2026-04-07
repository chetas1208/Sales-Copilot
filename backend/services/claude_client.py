"""
Claude API Client Wrapper
Handles all interactions with Anthropic's Claude API
"""

import os
import logging
from typing import List, Dict, Any, Optional, AsyncIterator
from anthropic import AsyncAnthropic
from anthropic.types import Message, MessageStreamEvent

logger = logging.getLogger(__name__)


class ClaudeClient:
    """Wrapper for Anthropic Claude API with async support"""

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize Claude client

        Args:
            api_key: Anthropic API key (defaults to ANTHROPIC_API_KEY env var)
        """
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        if not self.api_key:
            raise ValueError("ANTHROPIC_API_KEY not found in environment variables")

        self.client = AsyncAnthropic(api_key=self.api_key)
        self.default_model = "claude-sonnet-4-5-20250929"
        self.default_max_tokens = 4096

        logger.info(f"Claude client initialized with model: {self.default_model}")

    async def create_message(
        self,
        system: str,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        max_tokens: Optional[int] = None,
        temperature: float = 1.0,
        tools: Optional[List[Dict[str, Any]]] = None,
        tool_choice: Optional[Dict[str, Any]] = None
    ) -> Message:
        """
        Create a message with Claude

        Args:
            system: System prompt
            messages: List of message dicts with 'role' and 'content'
            model: Claude model to use (defaults to claude-sonnet-4-5)
            max_tokens: Maximum tokens in response
            temperature: Sampling temperature (0-1)
            tools: Optional list of tool definitions for function calling
            tool_choice: Optional tool choice configuration

        Returns:
            Message object from Claude
        """
        try:
            request_params = {
                "model": model or self.default_model,
                "system": system,
                "messages": messages,
                "max_tokens": max_tokens or self.default_max_tokens,
                "temperature": temperature
            }

            # Add tools if provided
            if tools:
                request_params["tools"] = tools
            if tool_choice:
                request_params["tool_choice"] = tool_choice

            logger.debug(f"Sending message to Claude: {len(messages)} messages, model={request_params['model']}")

            response = await self.client.messages.create(**request_params)

            logger.debug(f"Received response from Claude: {response.stop_reason}")

            return response

        except Exception as e:
            logger.error(f"Error calling Claude API: {str(e)}")
            raise

    async def create_message_stream(
        self,
        system: str,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        max_tokens: Optional[int] = None,
        temperature: float = 1.0
    ) -> AsyncIterator[MessageStreamEvent]:
        """
        Create a streaming message with Claude

        Args:
            system: System prompt
            messages: List of message dicts with 'role' and 'content'
            model: Claude model to use
            max_tokens: Maximum tokens in response
            temperature: Sampling temperature

        Yields:
            Stream events from Claude
        """
        try:
            request_params = {
                "model": model or self.default_model,
                "system": system,
                "messages": messages,
                "max_tokens": max_tokens or self.default_max_tokens,
                "temperature": temperature
            }

            logger.debug(f"Starting streaming message to Claude: model={request_params['model']}")

            async with self.client.messages.stream(**request_params) as stream:
                async for event in stream:
                    yield event

        except Exception as e:
            logger.error(f"Error in Claude streaming API: {str(e)}")
            raise

    async def simple_prompt(
        self,
        prompt: str,
        system: Optional[str] = None,
        model: Optional[str] = None,
        max_tokens: Optional[int] = None
    ) -> str:
        """
        Simple wrapper for single-turn prompts

        Args:
            prompt: User prompt
            system: Optional system prompt
            model: Claude model to use
            max_tokens: Maximum tokens in response

        Returns:
            Text response from Claude
        """
        messages = [{"role": "user", "content": prompt}]

        response = await self.create_message(
            system=system or "You are a helpful AI assistant.",
            messages=messages,
            model=model,
            max_tokens=max_tokens
        )

        # Extract text from response
        text_content = ""
        for block in response.content:
            if hasattr(block, "text"):
                text_content += block.text

        return text_content

    async def agent_prompt(
        self,
        agent_name: str,
        agent_system: str,
        user_prompt: str,
        context: Optional[Dict[str, Any]] = None,
        tools: Optional[List[Dict[str, Any]]] = None,
        max_iterations: int = 5
    ) -> Dict[str, Any]:
        """
        Execute an agent with Claude, handling tool use and multi-turn interactions

        Args:
            agent_name: Name of the agent (for logging)
            agent_system: System prompt defining agent's role
            user_prompt: Initial user prompt
            context: Optional context dict to inject into prompt
            tools: Optional MCP tools the agent can use
            max_iterations: Maximum tool use iterations

        Returns:
            Dict with 'result' (final text) and 'tool_calls' (list of tool calls made)
        """
        messages = []
        tool_calls = []

        # Add context to prompt if provided
        if context:
            context_str = "\n\nContext:\n" + "\n".join([f"- {k}: {v}" for k, v in context.items()])
            user_prompt += context_str

        messages.append({"role": "user", "content": user_prompt})

        logger.info(f"Starting agent: {agent_name}")

        for iteration in range(max_iterations):
            response = await self.create_message(
                system=agent_system,
                messages=messages,
                tools=tools
            )

            # Check if Claude wants to use tools
            if response.stop_reason == "tool_use":
                logger.debug(f"{agent_name} iteration {iteration + 1}: tool_use")

                # Extract tool calls
                for block in response.content:
                    if hasattr(block, "type") and block.type == "tool_use":
                        tool_calls.append({
                            "tool_name": block.name,
                            "tool_input": block.input,
                            "tool_use_id": block.id
                        })

                        logger.info(f"{agent_name} calling tool: {block.name}")

                        # Here you would execute the actual tool
                        # For now, we'll return the tool calls for the orchestrator to handle
                        # In a full implementation, you'd call MCP tools here

                # Add assistant response to messages
                messages.append({"role": "assistant", "content": response.content})

                # TODO: Execute tools via MCP and add tool results to messages
                # For now, break to avoid infinite loop
                break

            elif response.stop_reason == "end_turn":
                logger.debug(f"{agent_name} completed: end_turn")

                # Extract final text
                result_text = ""
                for block in response.content:
                    if hasattr(block, "text"):
                        result_text += block.text

                return {
                    "result": result_text,
                    "tool_calls": tool_calls,
                    "iterations": iteration + 1
                }

            else:
                logger.warning(f"{agent_name} unexpected stop_reason: {response.stop_reason}")
                break

        # If we exhausted iterations
        logger.warning(f"{agent_name} reached max iterations ({max_iterations})")

        # Extract whatever text we have
        result_text = ""
        for block in response.content:
            if hasattr(block, "text"):
                result_text += block.text

        return {
            "result": result_text,
            "tool_calls": tool_calls,
            "iterations": max_iterations,
            "truncated": True
        }

    def get_available_models(self) -> List[str]:
        """Get list of available Claude models"""
        return [
            "claude-sonnet-4-5-20250929",  # Latest Sonnet
            "claude-opus-4-20250514",       # Opus 4
            "claude-3-5-sonnet-20241022",   # Claude 3.5 Sonnet
            "claude-3-opus-20240229",       # Claude 3 Opus
            "claude-3-sonnet-20240229",     # Claude 3 Sonnet
            "claude-3-haiku-20240307"       # Claude 3 Haiku (fast & cheap)
        ]


# Singleton instance
_claude_client: Optional[ClaudeClient] = None


def get_claude_client() -> ClaudeClient:
    """Get or create singleton Claude client"""
    global _claude_client
    if _claude_client is None:
        _claude_client = ClaudeClient()
    return _claude_client
