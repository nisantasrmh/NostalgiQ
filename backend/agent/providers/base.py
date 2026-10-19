"""Abstract base classes and schemas for LLM provider abstraction."""

from abc import ABC, abstractmethod
from typing import Any, Callable, Dict, List, Optional
from pydantic import BaseModel, Field


class ToolCall(BaseModel):
    """Normalized tool call request emitted by an LLM."""
    name: str = Field(description="Name of the tool requested by the model.")
    args: Dict[str, Any] = Field(default_factory=dict, description="Parsed arguments for the tool.")
    id: Optional[str] = Field(default=None, description="Optional call ID if supported by provider.")


class TurnResult(BaseModel):
    """Result of a single model conversational turn."""
    text: Optional[str] = Field(default=None, description="Textual response from model if not calling a tool.")
    tool_calls: List[ToolCall] = Field(default_factory=list, description="Tool calls requested in this turn.")

    @property
    def has_tool_calls(self) -> bool:
        """Whether the model requested one or more tool calls in this turn."""
        return len(self.tool_calls) > 0


class BaseChatSession(ABC):
    """Interface for an ongoing multi-turn chat session with function calling."""

    @abstractmethod
    async def send_message(self, message: str) -> TurnResult:
        """Send a user message into the conversation and get the next turn result."""
        pass

    @abstractmethod
    async def send_tool_results(self, results: List[Dict[str, Any]]) -> TurnResult:
        """Send results of executed tool calls back into the session."""
        pass


class BaseLLMProvider(ABC):
    """Abstract interface for LLM providers (Gemini, Mock, OpenAI, Anthropic)."""

    @abstractmethod
    def create_chat_session(
        self,
        system_instruction: str,
        tools: Optional[List[Callable]] = None,
    ) -> BaseChatSession:
        """Initialize a new multi-turn conversational session with registered tools."""
        pass

    @abstractmethod
    async def generate_text(
        self,
        prompt: str,
        system_instruction: Optional[str] = None,
    ) -> str:
        """Single-turn text completion without tool calling (used by baselines)."""
        pass
