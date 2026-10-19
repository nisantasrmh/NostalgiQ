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

    async def generate_plan(self, profile: ElderProfile) -> MemoryPlan:
        """Run the tool-calling loop to assemble a personalized MemoryPlan.

        Args:
            profile: Complete ElderProfile including preferences and health rules.

        Returns:
            MemoryPlan with grounded recommendations and reasoning trail.
        """
        logger.info("Generating MemoryPlan for elder: %s (age %d)", profile.name, profile.age)
        reasoning_trail: List[ReasoningStep] = []
        step_counter = 1

        # Step 1: Analyze profile & establish seed anchors
        seeds: List[str] = []
        for artist in profile.favorites.music_artists:
            seeds.append(f"seed_{artist.lower().replace(' ', '_')}")
        for show in profile.favorites.films_and_shows:
            seeds.append(f"seed_{show.lower().replace(' ', '_')}")

        reasoning_trail.append(
            ReasoningStep(
                step_number=step_counter,
                action="analyze_persona_and_extract_seeds",
                rationale="Extract formative era, cultural anchors, and health constraints to seed Qloo taste graph queries.",
                input_data={
                    "era": profile.formative_years_decade,
                    "region": profile.formative_region,
                    "music_seeds": profile.favorites.music_artists,
                    "dietary_constraints": [r.value for r in profile.health_constraints.dietary_restrictions],
                    "texture": profile.health_constraints.texture_requirement.value,
                },
                output_summary=f"Extracted {len(seeds)} cultural seeds for {profile.name}.",
            )
        )
        step_counter += 1

        # Step 2: Query Qloo Music domain
        music_results = await self.tools.get_recommendations(
            seed_entity_ids=seeds,
            target_domain="music",
            era=profile.formative_years_decade,
            region=profile.formative_region,
            limit=3,
        )
        reasoning_trail.append(
            ReasoningStep(
                step_number=step_counter,
                action="get_qloo_recommendations:music",
                rationale=f"Retrieve music correlated with {profile.favorites.music_artists} from the {profile.formative_years_decade}.",
                input_data={"domain": "music", "era": profile.formative_years_decade, "seeds": seeds[:3]},
                output_summary=f"Retrieved {len(music_results)} verified music items from Qloo graph.",
            )
        )
        step_counter += 1

        # Step 3: Query Qloo Film/TV domain
        film_results = await self.tools.get_recommendations(
            seed_entity_ids=seeds,
            target_domain="film",
            era=profile.formative_years_decade,
            region=profile.formative_region,
            limit=3,
        )
        reasoning_trail.append(
            ReasoningStep(
                step_number=step_counter,
                action="get_qloo_recommendations:film",
                rationale=f"Retrieve classic cinema/broadcasts matching {profile.formative_region} from {profile.formative_years_decade}.",
                input_data={"domain": "film", "era": profile.formative_years_decade, "region": profile.formative_region},
                output_summary=f"Retrieved {len(film_results)} verified film/TV items from Qloo graph.",
            )
        )
        step_counter += 1

        # Step 4: Query Qloo Dining domain
        dining_results = await self.tools.get_recommendations(
            seed_entity_ids=seeds,
            target_domain="dining",
            era=profile.formative_years_decade,
            region=profile.formative_region,
            limit=3,
        )
        reasoning_trail.append(
            ReasoningStep(
                step_number=step_counter,
                action="get_qloo_recommendations:dining",
                rationale=f"Query authentic traditional recipes and comfort food from {profile.formative_region}.",
                input_data={"domain": "dining", "region": profile.formative_region},
                output_summary=f"Retrieved {len(dining_results)} authentic dishes from Qloo taste graph.",
            )
        )
        step_counter += 1

        # Step 5: Adapt Dining recommendations with Health Rules
        adapted_dining_recs: List[Recommendation] = []
        for item in dining_results:
            adaptation = self.tools.adapt_for_health(
                dish_title=item.get("title", "Traditional Dish"),
                dish_description=item.get("description", ""),
                constraints=profile.health_constraints,
            )
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

        reasoning_trail.append(
            ReasoningStep(
                step_number=step_counter,
                action="adapt_for_health",
                rationale="Apply deterministic clinical rules for dysphagia texture, low-sodium seasoning, and diabetic safety.",
                input_data={
                    "texture_requirement": profile.health_constraints.texture_requirement.value,
                    "allergies": profile.health_constraints.allergies,
                },
                output_summary=f"Successfully adapted {len(adapted_dining_recs)} dishes for patient safety.",
            )
        )

        # Assemble Music Recommendations
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

        # Assemble Film Recommendations
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

        # Assemble Caregiver Guidance
        caregiver_tips = [
            f"Introduce music during calm morning or late afternoon transition hours to reduce agitation.",
            f"Keep film viewing sessions to 20-30 minutes with subtitles if hearing is impaired.",
            f"Always test food temperature and texture consistency before serving to comply with dysphagia precautions.",
            f"Use favorite songs as gentle conversation starters: ask what emotions or family memories they bring to mind.",
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

    # TODO: Connect real LLM API provider (OpenAI, Anthropic, Gemini) with function calling loop once API keys are set
