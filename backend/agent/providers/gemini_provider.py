"""Google Gemini LLM Provider implementation using google-genai SDK."""

import logging
from typing import Any, Callable, Dict, List, Optional
from google import genai
from google.genai import types
from backend.services.gemini_service import get_gemini_model


from backend.agent.providers.base import (
    BaseChatSession,
    BaseLLMProvider,
    ToolCall,
    TurnResult,
)

logger = logging.getLogger(__name__)


class GeminiChatSession(BaseChatSession):
    """Encapsulates a multi-turn chat session with Gemini function calling."""

    def __init__(
        self,
        client: genai.Client,
        model: str,
        system_instruction: str,
        tools: Optional[List[Callable]] = None,
    ) -> None:
        self.client = client
        self.model = model
        self.config = types.GenerateContentConfig(
            system_instruction=system_instruction,
            tools=tools if tools else None,
            temperature=0.3,
        )
        self.chat = self.client.aio.chats.create(model=self.model, config=self.config)

    def _parse_response(self, response: types.GenerateContentResponse) -> TurnResult:
        """Parse Gemini GenerateContentResponse into a standardized TurnResult."""
        tool_calls: List[ToolCall] = []
        if response.function_calls:
            for fc in response.function_calls:
                call_args = dict(fc.args) if fc.args else {}
                tool_calls.append(
                    ToolCall(
                        name=fc.name,
                        args=call_args,
                        id=getattr(fc, "id", None),
                    )
                )

        text_content = None
        try:
            if response.text:
                text_content = response.text
        except Exception:
            text_content = None

        return TurnResult(text=text_content, tool_calls=tool_calls)

    async def send_message(self, message: str) -> TurnResult:
        """Send a user message to Gemini chat session."""
        logger.info("Sending message to Gemini chat session (%s)", self.model)
        response = await self.chat.send_message(message)
        return self._parse_response(response)

    async def send_tool_results(self, results: List[Dict[str, Any]]) -> TurnResult:
        """Send executed tool results back to Gemini chat session."""
        logger.info("Sending %d tool results back to Gemini", len(results))
        parts = []
        for item in results:
            part = types.Part.from_function_response(
                name=item["name"],
                response={"result": item["result"]},
            )
            parts.append(part)

        response = await self.chat.send_message(parts)
        return self._parse_response(response)


class GeminiLLMProvider(BaseLLMProvider):
    """Gemini provider implementation."""

    def __init__(
        self,
        api_key: str,
        model: str = "gemini-1.5-flash",
    ) -> None:
        if not api_key:
            raise ValueError("Gemini API key is required to instantiate GeminiLLMProvider.")
        self.api_key = api_key
        # Use helper to ensure clean model name (no 'models/' prefix)
        _ = get_gemini_model("gemini-1.5-flash")
        self.model = "gemini-1.5-flash"
        self.client = genai.Client(api_key=self.api_key)
        logger.info("Initialized GeminiLLMProvider with model=%s", self.model)

    def create_chat_session(
        self,
        system_instruction: str,
        tools: Optional[List[Callable]] = None,
    ) -> BaseChatSession:
        return GeminiChatSession(
            client=self.client,
            model=self.model,
            system_instruction=system_instruction,
            tools=tools,
        )

    async def generate_text(
        self,
        prompt: str,
        system_instruction: Optional[str] = None,
    ) -> str:
        """Generate single-turn text completion without tool calling."""
        config = types.GenerateContentConfig(
            system_instruction=system_instruction,
            temperature=0.5,
        )
        try:
            response = await self.client.aio.models.generate_content(
                model=self.model,
                contents=prompt,
                config=config,
            )
        except Exception as e:
            logger.exception("Gemini generate_text failed: %s", e)
            raise RuntimeError(f"Failed to generate text with Gemini model '{self.model}'. Ensure the model name is correct and the API key is valid.")
        return response.text or ""
