"""Reminiscence Care Plan Agent.

Orchestrates tool-calling workflows:
1. Gathers elder personal history & cultural seeds.
2. Traverses Qloo Taste Graph for correlated music, films, and regional foods.
3. Adapts culinary items using deterministic clinical rules.
4. Synthesizes a structured MemoryPlan with a verifiable reasoning trail.

LLM Provider abstraction allows swapping OpenAI, Anthropic, Gemini, or offline rule-based agent.
"""

import uuid
from typing import Any, Dict, List, Optional
import logging

from backend.agent.prompts import MEMORY_LANE_SYSTEM_PROMPT
from backend.agent.tools import AgentTools
from backend.models.schemas import (
    ElderProfile,
    HealthAdaptation,
    MemoryPlan,
    ReasoningStep,
    Recommendation,
    RecommendationDomain,
)
from backend.qloo.factory import get_qloo_client

logger = logging.getLogger(__name__)


class ReminiscenceAgent:
    """Agent orchestrator for memory care planning."""

    def __init__(self, tools: Optional[AgentTools] = None, llm_provider: str = "mock") -> None:
        """Initialize the agent with tools and LLM backend.

        Args:
            tools: AgentTools instance. If None, default tools with configured Qloo client are used.
            llm_provider: Name of LLM provider ('mock', 'openai', 'anthropic', 'gemini').
        """
        self.qloo_client = get_qloo_client()
        self.tools = tools or AgentTools(self.qloo_client)
        self.llm_provider = llm_provider
        self.system_prompt = MEMORY_LANE_SYSTEM_PROMPT



    # TODO: Connect real LLM API provider (OpenAI, Anthropic, Gemini) with function calling loop once API keys are set
    async def generate_plan(self, profile: ElderProfile) -> MemoryPlan:
        """Run the tool-calling loop to assemble a personalized MemoryPlan.

        Args:
            profile: Complete ElderProfile including preferences and health rules.

        Returns:
            MemoryPlan with grounded recommendations and reasoning trail.
        """
        logger.info("Generating MemoryPlan for elder: %s (age %d)", profile.name, profile.age)
        # Initialise LLM provider and chat session
        from backend.agent.providers.factory import get_llm_provider
        llm = get_llm_provider(provider_name=self.llm_provider)
        chat = llm.create_chat_session(system_instruction=self.system_prompt, tools=None)
        # Send profile as JSON
        turn = await chat.send_message(profile.json())
        reasoning_trail: List[ReasoningStep] = []
        step_counter = 1
        music_results: List[Dict[str, Any]] = []
        film_results: List[Dict[str, Any]] = []
        dining_results: List[Dict[str, Any]] = []
        adapted_dining_recs: List[Recommendation] = []
        for _ in range(8):
            if turn.text:
                break
            if not getattr(turn, "tool_calls", None):
                break
            tool_results: List[Dict[str, Any]] = []
            for call in turn.tool_calls:
                name = call.name
                args = call.args or {}
                if name == "search_entity":
                    result = await self.tools.search_entity(**args)
                elif name == "get_recommendations":
                    result = await self.tools.get_recommendations(**args)
                elif name == "adapt_for_health":
                    result = self.tools.adapt_for_health(**args)
                else:
                    logger.warning("Unknown tool: %s", name)
                    result = None
                reasoning_trail.append(
                    ReasoningStep(
                        step_number=step_counter,
                        action=f"tool:{name}",
                        rationale=f"Executed tool {name}.",
                        input_data=args,
                        output_summary=f"Tool returned {len(result) if isinstance(result, list) else 1} items.",
                    )
                )
                step_counter += 1
                tool_results.append({"name": name, "result": result})
                if name == "get_recommendations":
                    domain = args.get("target_domain")
                    if domain == "music":
                        music_results.extend(result)
                    elif domain == "film":
                        film_results.extend(result)
                    elif domain == "dining":
                        dining_results.extend(result)
            turn = await chat.send_tool_results(tool_results)
        # Adapt dining recommendations using health constraints
        for item in dining_results:
            adaptation = self.tools.adapt_for_health(
                dish_title=item.get("title", "Traditional Dish"),
                dish_description=item.get("description", ""),
                constraints=profile.health_constraints,
            )
            if isinstance(adaptation, dict):
                adaptation = HealthAdaptation(**adaptation)
            rec = Recommendation(
                id=str(uuid.uuid4())[:8],
                domain=RecommendationDomain.DINING,
                title=adaptation.adapted_dish if adaptation.is_adapted else item.get("title", ""),
                creator_or_artist=item.get("region"),
                era=item.get("era"),
                description=item.get("description", ""),
                reminiscence_connection=item.get("emotional_resonance_reason", "Traditional comfort favorite."),
                source=item.get("source", "MOCK"),
                qloo_entity_id=item.get("id"),
                confidence_score=item.get("confidence_score", 0.92),
                health_adaptation=adaptation,
            )
            adapted_dining_recs.append(rec)
        # Build music recommendations
        music_recs: List[Recommendation] = [
            Recommendation(
                id=str(uuid.uuid4())[:8],
                domain=RecommendationDomain.MUSIC,
                title=item.get("title", ""),
                creator_or_artist=item.get("artist"),
                era=item.get("era"),
                description=item.get("description", ""),
                reminiscence_connection=item.get("emotional_resonance_reason", "Formative musical anchor."),
                source=item.get("source", "MOCK"),
                qloo_entity_id=item.get("id"),
                confidence_score=item.get("confidence_score", 0.95),
            )
            for item in music_results
        ]
        # Build film recommendations
        film_recs: List[Recommendation] = [
            Recommendation(
                id=str(uuid.uuid4())[:8],
                domain=RecommendationDomain.FILM,
                title=item.get("title", ""),
                creator_or_artist=item.get("creator_or_artist"),
                era=item.get("era"),
                description=item.get("description", ""),
                reminiscence_connection=item.get("emotional_resonance_reason", "Culturally resonant classic."),
                source=item.get("source", "MOCK"),
                qloo_entity_id=item.get("id"),
                confidence_score=item.get("confidence_score", 0.90),
            )
            for item in film_results
        ]
        caregiver_tips = [
            "Introduce music during calm morning or late afternoon transition hours to reduce agitation.",
            "Keep film viewing sessions to 20-30 minutes with subtitles if hearing is impaired.",
            "Always test food temperature and texture consistency before serving to comply with dysphagia precautions.",
            "Use favorite songs as gentle conversation starters: ask what emotions or family memories they bring to mind.",
        ]
        return MemoryPlan(
            plan_id=f"plan_{uuid.uuid4().hex[:10]}",
            persona_id=profile.id,
            persona_name=profile.name,
            music_recommendations=music_recs,
            film_recommendations=film_recs,
            meal_recommendations=adapted_dining_recs,
            reasoning_trail=reasoning_trail,
            caregiver_tips=caregiver_tips,
        )
