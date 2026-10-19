"""Offline Mock LLM Provider for local development and test automation."""

import json
import logging
from typing import Any, Callable, Dict, List, Optional

from backend.agent.providers.base import (
    BaseChatSession,
    BaseLLMProvider,
    ToolCall,
    TurnResult,
)

logger = logging.getLogger(__name__)


class MockChatSession(BaseChatSession):
    """Simulates multi-turn tool-calling loop deterministically without external API keys."""

    def __init__(self, system_instruction: str, tools: Optional[List[Callable]] = None) -> None:
        self.system_instruction = system_instruction
        self.tools = tools or []
        self.turn_count = 0
        self.gathered_tool_results: Dict[str, Any] = {}
        self.profile_data: Dict[str, Any] = {}

    async def send_message(self, message: str) -> TurnResult:
        """First turn: analyze profile from message and issue initial Qloo tool calls."""
        self.turn_count += 1
        logger.info("MockChatSession turn %d: processing user prompt", self.turn_count)

        # Extract profile hints from message
        era = "1960s"
        region = "Maharashtra"
        seeds = ["seed_bhimsen_joshi", "seed_pune_1960s"]

        if "chicago" in message.lower():
            region = "Chicago"
            seeds = ["seed_miles_davis", "seed_chicago_1960s"]

        # Issue initial tool calls to query music, film, dining
        tool_calls = [
            ToolCall(
                name="get_recommendations",
                args={
                    "seed_entity_ids": seeds,
                    "target_domain": "music",
                    "era": era,
                    "region": region,
                    "limit": 3,
                },
                id="call_mock_music_01",
            ),
            ToolCall(
                name="get_recommendations",
                args={
                    "seed_entity_ids": seeds,
                    "target_domain": "film",
                    "era": era,
                    "region": region,
                    "limit": 3,
                },
                id="call_mock_film_01",
            ),
            ToolCall(
                name="get_recommendations",
                args={
                    "seed_entity_ids": seeds,
                    "target_domain": "dining",
                    "era": era,
                    "region": region,
                    "limit": 3,
                },
                id="call_mock_dining_01",
            ),
        ]
        return TurnResult(tool_calls=tool_calls)

    async def send_tool_results(self, results: List[Dict[str, Any]]) -> TurnResult:
        """Subsequent turns: process tool results, request health adaptation, or finish."""
        self.turn_count += 1
        logger.info("MockChatSession turn %d: received %d tool results", self.turn_count, len(results))

        # Store results for final plan assembly
        for item in results:
            t_name = item.get("name")
            t_res = item.get("result")
            self.gathered_tool_results[t_name] = t_res

        # If we just received recommendations and haven't adapted dining yet:
        if self.turn_count == 2:
            dining_items = []
            for item in results:
                if item.get("name") == "get_recommendations":
                    res = item.get("result", [])
                    if isinstance(res, list) and len(res) > 0 and res[0].get("domain") == "dining":
                        dining_items = res

            if dining_items:
                tool_calls = []
                for idx, dish in enumerate(dining_items):
                    tool_calls.append(
                        ToolCall(
                            name="adapt_for_health",
                            args={
                                "dish_title": dish.get("title", ""),
                                "dish_description": dish.get("description", ""),
                                "texture_requirement": "soft_food",
                                "dietary_restrictions": ["diabetic_friendly", "low_sodium"],
                                "allergies": ["peanuts"],
                            },
                            id=f"call_mock_adapt_{idx}",
                        )
                    )
                return TurnResult(tool_calls=tool_calls)

        # Final turn: synthesize grounded JSON output
        final_payload = {
            "summary": "Care plan synthesized from verified Qloo taste graph nodes.",
            "caregiver_guidance": [
                "Play music during morning or late afternoon transition hours.",
                "Verify temperature and texture before serving softened meals.",
            ],
        }
        return TurnResult(text=json.dumps(final_payload, indent=2))


class MockLLMProvider(BaseLLMProvider):
    """Mock LLM provider for zero-key local execution and unit tests."""

    def create_chat_session(
        self,
        system_instruction: str,
        tools: Optional[List[Callable]] = None,
    ) -> BaseChatSession:
        return MockChatSession(system_instruction=system_instruction, tools=tools)

    async def generate_text(
        self,
        prompt: str,
        system_instruction: Optional[str] = None,
    ) -> str:
        return (
            "Generic LLM response: Suggesting generic 1960s pop hits (e.g. The Beatles, Elvis Presley) "
            "and generic classic Hollywood cinema (e.g. Casablanca) with unadapted standard foods."
        )
