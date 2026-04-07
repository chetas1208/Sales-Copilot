"""
OpenAI API Client Wrapper
Handles all interactions with OpenAI's GPT API
"""

import os
import logging
from typing import List, Dict, Any, Optional
from openai import AsyncOpenAI

logger = logging.getLogger(__name__)


class OpenAIClient:
    """Wrapper for OpenAI API with async support"""

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize OpenAI client

        Args:
            api_key: OpenAI API key (defaults to OPENAI_API_KEY env var)
        """
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY not found in environment variables")

        self.client = AsyncOpenAI(api_key=self.api_key)
        self.default_model = "gpt-4o"  # GPT-4o (optimized)
        self.default_max_tokens = 4096

        logger.info(f"OpenAI client initialized with model: {self.default_model}")

    async def create_message(
        self,
        system: str,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        max_tokens: Optional[int] = None,
        temperature: float = 1.0,
        response_format: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Create a message with OpenAI

        Args:
            system: System prompt
            messages: List of message dicts with 'role' and 'content'
            model: OpenAI model to use (defaults to gpt-4o)
            max_tokens: Maximum tokens in response
            temperature: Sampling temperature (0-2)
            response_format: Optional response format (e.g., {"type": "json_object"})

        Returns:
            Response dict with content and metadata
        """
        try:
            # Build messages array with system message first
            full_messages = [{"role": "system", "content": system}]
            full_messages.extend(messages)

            request_params = {
                "model": model or self.default_model,
                "messages": full_messages,
                "max_tokens": max_tokens or self.default_max_tokens,
                "temperature": temperature
            }

            # Add response format if specified (for JSON mode)
            if response_format:
                request_params["response_format"] = response_format

            logger.debug(f"Sending message to OpenAI: {len(messages)} messages, model={request_params['model']}")

            response = await self.client.chat.completions.create(**request_params)

            logger.debug(f"Received response from OpenAI: {response.choices[0].finish_reason}")

            # Extract content
            content = response.choices[0].message.content

            return {
                "content": content,
                "model": response.model,
                "finish_reason": response.choices[0].finish_reason,
                "usage": {
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens,
                    "total_tokens": response.usage.total_tokens
                }
            }

        except Exception as e:
            logger.error(f"Error calling OpenAI API: {str(e)}")
            raise

    async def create_message_stream(
        self,
        system: str,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        max_tokens: Optional[int] = None,
        temperature: float = 1.0
    ):
        """
        Create a streaming message with OpenAI

        Args:
            system: System prompt
            messages: List of message dicts with 'role' and 'content'
            model: OpenAI model to use
            max_tokens: Maximum tokens in response
            temperature: Sampling temperature

        Yields:
            Stream chunks from OpenAI
        """
        try:
            # Build messages array
            full_messages = [{"role": "system", "content": system}]
            full_messages.extend(messages)

            request_params = {
                "model": model or self.default_model,
                "messages": full_messages,
                "max_tokens": max_tokens or self.default_max_tokens,
                "temperature": temperature,
                "stream": True
            }

            logger.debug(f"Starting streaming message to OpenAI: model={request_params['model']}")

            stream = await self.client.chat.completions.create(**request_params)

            async for chunk in stream:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content

        except Exception as e:
            logger.error(f"Error in OpenAI streaming API: {str(e)}")
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
            model: OpenAI model to use
            max_tokens: Maximum tokens in response

        Returns:
            Text response from OpenAI
        """
        messages = [{"role": "user", "content": prompt}]

        response = await self.create_message(
            system=system or "You are a helpful AI assistant.",
            messages=messages,
            model=model,
            max_tokens=max_tokens
        )

        return response["content"]

    async def agent_prompt(
        self,
        agent_name: str,
        agent_system: str,
        user_prompt: str,
        context: Optional[Dict[str, Any]] = None,
        max_iterations: int = 1
    ) -> Dict[str, Any]:
        """
        Execute an agent with OpenAI

        Args:
            agent_name: Name of the agent (for logging)
            agent_system: System prompt defining agent's role
            user_prompt: Initial user prompt
            context: Optional context dict to inject into prompt
            max_iterations: Maximum iterations (OpenAI doesn't have native tool use like Claude)

        Returns:
            Dict with 'result' (final text)
        """
        messages = []

        # Add context to prompt if provided
        if context:
            context_str = "\n\nContext:\n" + "\n".join([f"- {k}: {v}" for k, v in context.items()])
            user_prompt += context_str

        messages.append({"role": "user", "content": user_prompt})

        logger.info(f"Starting agent: {agent_name}")

        response = await self.create_message(
            system=agent_system,
            messages=messages
        )

        return {
            "result": response["content"],
            "usage": response["usage"],
            "model": response["model"]
        }

    def get_available_models(self) -> List[str]:
        """Get list of available OpenAI models"""
        return [
            "gpt-4o",              # GPT-4 Optimized (recommended)
            "gpt-4o-mini",         # Cheaper, faster variant
            "gpt-4-turbo",         # GPT-4 Turbo
            "gpt-4",               # GPT-4 (original)
            "gpt-3.5-turbo",       # GPT-3.5 (cheapest)
        ]


# Singleton instance
_openai_client: Optional[OpenAIClient] = None


def get_openai_client() -> OpenAIClient:
    """Get or create singleton OpenAI client"""
    global _openai_client
    if _openai_client is None:
        _openai_client = OpenAIClient()
    return _openai_client
