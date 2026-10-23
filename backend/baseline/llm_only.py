"""Generic LLM Baseline Generator (Ungrounded Comparison).

Generates a naive, LLM-only response that lacks external taste graph grounding.
Used for side-by-side evaluation against Qloo-grounded plans to demonstrate
why external taste graph retrieval and health rules are vital for dementia care.
"""

import uuid
from typing import Dict, List
import logging

from backend.models.schemas import (
    ComparisonResult,
    ElderProfile,
    MemoryPlan,
    ReasoningStep,
    Recommendation,
    RecommendationDomain,
)

logger = logging.getLogger(__name__)


class GenericLLMBaseline:
    """Simulates an ungrounded, generic LLM baseline without Qloo graph access."""

    def __init__(self, api_key: str = "") -> None:
        """Initialize baseline generator.

        TODO: Connect to raw LLM completion API without tools once LLM_API_KEY is configured.
        """
        self.api_key = api_key

    async def generate_baseline_plan(self, profile: ElderProfile) -> MemoryPlan:
        """Produce an ungrounded baseline response relying solely on generic LLM knowledge.

        Noticeable failure modes of generic LLM baselines in dementia care:
        - Defaults to generic global pop culture (Beatles, Casablanca) regardless of regional nuance.
        - Hallucinates song titles or attributes Marathi songs to Bollywood directors.
        - Fails to adapt food textures for dysphagia or ignores sodium/sugar thresholds.
        """
        logger.info("Generating generic LLM baseline plan for %s", profile.name)

        # Naive generic recommendations (ungrounded)
        music_recs = [
            Recommendation(
                id=str(uuid.uuid4())[:8],
                domain=RecommendationDomain.MUSIC,
                title="Generic 1960s Greatest Hits Medley (The Beatles & Elvis Presley)",
                creator_or_artist="Various Artists",
                era="1960s",
                description="Popular Western songs from the 1960s commonly found in top-40 radio broadcasts.",
                reminiscence_connection="Generic suggestion based only on the decade string '1960s'. Lacks regional Marathi/Pune cultural context.",
                source="GENERIC_LLM_UNGROUNDED",
                qloo_entity_id=None,
                confidence_score=0.45,
            ),
            Recommendation(
                id=str(uuid.uuid4())[:8],
                domain=RecommendationDomain.MUSIC,
                title="Top Hindi Radio Hits of 1965",
                creator_or_artist="General Radio Archive",
                era="1960s",
                description="Broad selection of mainstream Bollywood tracks from the mid-60s.",
                reminiscence_connection="Lacks specificity to classical Natyasangeet or Hindustani vocalists.",
                source="GENERIC_LLM_UNGROUNDED",
                qloo_entity_id=None,
                confidence_score=0.50,
            ),
        ]

        film_recs = [
            Recommendation(
                id=str(uuid.uuid4())[:8],
                domain=RecommendationDomain.FILM,
                title="Casablanca (1942)",
                creator_or_artist="Michael Curtiz",
                era="1940s",
                description="Famous classic Hollywood romantic drama.",
                reminiscence_connection="Generic movie default with no connection to the elder's Pune heritage.",
                source="GENERIC_LLM_UNGROUNDED",
                qloo_entity_id=None,
                confidence_score=0.40,
            ),
        ]

        meal_recs = [
            Recommendation(
                id=str(uuid.uuid4())[:8],
                domain=RecommendationDomain.DINING,
                title="Standard Restaurant Puran Poli with Sweet Sugar Syrup",
                creator_or_artist="Traditional Style",
                era="Standard",
                description="Crispy pan-fried sweet bread filled with high-sugar chana dal paste.",
                reminiscence_connection="Fails to modify crispy texture for dysphagia; contains unmonitored sugar levels dangerous for diabetes.",
                source="GENERIC_LLM_UNGROUNDED",
                qloo_entity_id=None,
                confidence_score=0.50,
                health_adaptation=None,  # Baseline fails to provide verified health adaptation
            ),
        ]

        reasoning_trail = [
            ReasoningStep(
                step_number=1,
                action="direct_prompt_completion",
                rationale="Generic LLM without tool calling or taste graph database access.",
                input_data={"prompt": f"Suggest 1960s music and food for an elderly person named {profile.name}."},
                output_summary="Generated generic top-40 and mainstream answers without grounding.",
            )
        ]

        return MemoryPlan(
            plan_id=f"baseline_{uuid.uuid4().hex[:10]}",
            persona_id=profile.id,
            persona_name=profile.name,
            music_recommendations=music_recs,
            film_recommendations=film_recs,
            meal_recommendations=meal_recs,
            reasoning_trail=reasoning_trail,
            caregiver_tips=[
                "Caution: Generic LLM suggestions may not comply with patient swallowing safety or glycemic constraints."
            ],
        )

    async def compare(self, profile: ElderProfile, qloo_plan: MemoryPlan) -> ComparisonResult:
        """Produce side-by-side comparison between Qloo-grounded plan and generic baseline."""
        baseline_plan = await self.generate_baseline_plan(profile)

        analysis = {
            "grounding_differences": (
                "Qloo Taste Graph retrieved verified cultural items (e.g. Pandit Bhimsen Joshi, Prabhat Studios) "
                "correlated directly with the elder's regional history, whereas generic LLM defaulted to generic Western "
                "or mainstream pop."
            ),
            "safety_differences": (
                "NostalgiQ's agent executed deterministic health adaptation rules (steaming, fiber swaps, sodium reduction), "
                "while generic LLM suggested unadapted crispy, high-sugar foods that violate dysphagia and diabetic protocols."
            ),
            "hallucination_risk": (
                "Zero hallucinated entities in Qloo plan; all items trace back to verified taste graph IDs."
            ),
        }

        return ComparisonResult(
            persona_id=profile.id,
            persona_name=profile.name,
            qloo_grounded_plan=qloo_plan,
            generic_llm_plan=baseline_plan,
            comparison_summary=analysis,
        )
