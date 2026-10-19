"""Data models and schemas for Memory Lane.

Defines Pydantic models for elder profiles, Qloo recommendations,
reasoning steps, memory plans, and baseline comparisons.
"""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class RecommendationDomain(str, Enum):
    """Domains supported by Qloo taste graph for reminiscence."""
    MUSIC = "music"
    FILM = "film"
    DINING = "dining"


class TextureRequirement(str, Enum):
    """Swallowing/texture capabilities for dietary adaptation."""
    NORMAL = "normal"
    SOFT_FOOD = "soft_food"
    MINCED_MOIST = "minced_moist"
    PUREE = "puree"
    LIQUID = "liquid"


class DietaryConstraint(str, Enum):
    """Common chronic condition dietary guidelines."""
    DIABETIC_FRIENDLY = "diabetic_friendly"
    LOW_SODIUM = "low_sodium"
    CARDIAC_FRIENDLY = "cardiac_friendly"
    LOW_CHOLESTEROL = "low_cholesterol"
    RENAL_FRIENDLY = "renal_friendly"
    VEGETARIAN = "vegetarian"
    VEGAN = "vegan"


class HealthConstraints(BaseModel):
    """Health constraints to adapt cultural food recommendations safely."""
    texture_requirement: TextureRequirement = Field(
        default=TextureRequirement.NORMAL,
        description="Texture modification required (e.g., soft foods for dysphagia).",
    )
    texture_details: Optional[str] = Field(
        default=None,
        description="Specific caregiver notes on food texture preparation.",
    )
    dietary_restrictions: List[DietaryConstraint] = Field(
        default_factory=list,
        description="List of clinical dietary guidelines like diabetic-friendly or low-sodium.",
    )
    allergies: List[str] = Field(
        default_factory=list,
        description="Strict allergen exclusions (e.g., peanuts, shellfish, lactose).",
    )
    spiciness_tolerance: str = Field(
        default="mild",
        description="Caregiver-reported tolerance for spices or acidity ('mild', 'medium', 'spicy').",
    )


class CulturalFavorites(BaseModel):
    """User-reported favorite cultural anchors from earlier life."""
    music_artists: List[str] = Field(
        default_factory=list,
        description="Favorite singers, musicians, or composers.",
    )
    music_genres: List[str] = Field(
        default_factory=list,
        description="Preferred genres (e.g., Natyasangeet, Chicago Blues).",
    )
    films_and_shows: List[str] = Field(
        default_factory=list,
        description="Beloved films, actors, or television broadcasts.",
    )
    favorite_dishes: List[str] = Field(
        default_factory=list,
        description="Comfort foods or festive regional dishes from youth.",
    )


class ElderProfile(BaseModel):
    """Profile of the senior individual receiving reminiscence curation."""
    id: str = Field(description="Unique profile identifier.")
    name: str = Field(description="Full or preferred name of the elder.")
    age: int = Field(ge=50, le=120, description="Age in years.")
    birth_year: int = Field(description="Four-digit birth year.")
    current_residence: str = Field(description="Current city/region.")
    formative_years_decade: str = Field(
        description="The decade of formative youth/early adulthood (e.g. '1960s').",
    )
    formative_region: str = Field(
        description="Geographic region where the person spent their youth.",
    )
    primary_language: str = Field(default="English", description="Primary native language.")
    secondary_language: Optional[str] = Field(default=None, description="Secondary or regional language.")
    biography: Optional[str] = Field(
        default=None,
        description="Brief background or life story notes.",
    )
    favorites: CulturalFavorites = Field(
        default_factory=CulturalFavorites,
        description="Cultural tastes from youth.",
    )
    health_constraints: HealthConstraints = Field(
        default_factory=HealthConstraints,
        description="Dietary adaptations and texture guidelines.",
    )
    reminiscence_notes: Optional[str] = Field(
        default=None,
        description="Caregiver observations on soothing stimuli or sensory cues.",
    )


class HealthAdaptation(BaseModel):
    """Transformation applied to a meal or activity to guarantee safety."""
    is_adapted: bool = Field(default=False, description="Whether modifications were applied.")
    original_dish: str = Field(description="Name of original regional dish.")
    adapted_dish: str = Field(description="Safely modified culinary preparation.")
    texture_instructions: str = Field(
        description="Texture preparation advice (e.g., steamed soft, pureed).",
    )
    substitutions: List[str] = Field(
        default_factory=list,
        description="Specific ingredient replacements (e.g., stevia instead of sugar).",
    )
    addressed_constraints: List[str] = Field(
        default_factory=list,
        description="List of health constraints resolved by this adaptation.",
    )


class Recommendation(BaseModel):
    """A cultural reminiscence item (song, film, or meal)."""
    id: str = Field(description="Unique recommendation ID.")
    domain: RecommendationDomain = Field(description="Media or lifestyle domain.")
    title: str = Field(description="Title of song, film, or traditional dish.")
    creator_or_artist: Optional[str] = Field(
        default=None,
        description="Singer, director, or culinary region.",
    )
    era: Optional[str] = Field(
        default=None,
        description="Year or decade of release/prominence.",
    )
    description: str = Field(description="Summary of the entity.")
    reminiscence_connection: str = Field(
        description="Why this item connects back to the elder's formative years/taste graph seeds.",
    )
    source: str = Field(
        default="MOCK",
        description="Data provenance: 'MOCK' or 'QLOO'.",
    )
    qloo_entity_id: Optional[str] = Field(
        default=None,
        description="Entity ID from Qloo taste graph.",
    )
    confidence_score: float = Field(
        default=0.9,
        ge=0.0,
        le=1.0,
        description="Correlation confidence score from taste graph.",
    )
    health_adaptation: Optional[HealthAdaptation] = Field(
        default=None,
        description="Dietary modifications for dining recommendations.",
    )


class ReasoningStep(BaseModel):
    """Step in the agent's chain-of-thought tool calling trajectory."""
    step_number: int = Field(description="Sequential index of reasoning step.")
    action: str = Field(description="Tool or operation executed (e.g., 'search_qloo_taste_graph').")
    rationale: str = Field(description="Why this action was chosen by the agent.")
    input_data: Dict[str, Any] = Field(default_factory=dict, description="Parameters sent to tool.")
    output_summary: str = Field(description="Brief summary of results obtained.")


class MemoryPlan(BaseModel):
    """Complete personalized reminiscence care plan."""
    plan_id: str = Field(description="Unique plan identifier.")
    persona_id: str = Field(description="Associated elder persona ID.")
    persona_name: str = Field(description="Elder's name.")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    music_recommendations: List[Recommendation] = Field(default_factory=list)
    film_recommendations: List[Recommendation] = Field(default_factory=list)
    meal_recommendations: List[Recommendation] = Field(default_factory=list)
    reasoning_trail: List[ReasoningStep] = Field(
        default_factory=list,
        description="Transparent log of agent decisions and Qloo queries.",
    )
    caregiver_tips: List[str] = Field(
        default_factory=list,
        description="Gentle guidance on presenting music, viewing films, and dining safely.",
    )


class ComparisonResult(BaseModel):
    """Side-by-side evaluation of Qloo-grounded plan vs Generic LLM baseline."""
    persona_id: str
    persona_name: str
    qloo_grounded_plan: MemoryPlan
    generic_llm_plan: MemoryPlan
    comparison_summary: Dict[str, Any] = Field(
        description="Evaluation of grounding authenticity, cultural relevance, and dietary safety.",
    )
