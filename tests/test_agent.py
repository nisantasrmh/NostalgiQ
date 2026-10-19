"""Tests for Reminiscence Care Plan Agent and Health Rules."""

import pytest
from backend.agent.agent import ReminiscenceAgent
from backend.agent.health_rules import adapt_dish_for_health
from backend.models.schemas import (
    CulturalFavorites,
    DietaryConstraint,
    ElderProfile,
    HealthConstraints,
    TextureRequirement,
)


@pytest.fixture
def sample_profile() -> ElderProfile:
    """Fixture returning a sample elder profile."""
    return ElderProfile(
        id="test_sharada",
        name="Sharada Kulkarni",
        age=79,
        birth_year=1947,
        current_residence="Pune, India",
        formative_years_decade="1960s",
        formative_region="Pune, Maharashtra",
        favorites=CulturalFavorites(
            music_artists=["Pandit Bhimsen Joshi"],
            films_and_shows=["Pinjra (1972)"],
            favorite_dishes=["Puran Poli"],
        ),
        health_constraints=HealthConstraints(
            texture_requirement=TextureRequirement.SOFT_FOOD,
            dietary_restrictions=[DietaryConstraint.DIABETIC_FRIENDLY, DietaryConstraint.LOW_SODIUM],
            allergies=["peanuts"],
        ),
    )


def test_health_rules_adaptation():
    """Verify that culinary health adaptation applies dysphagia and diabetic rules."""
    constraints = HealthConstraints(
        texture_requirement=TextureRequirement.SOFT_FOOD,
        dietary_restrictions=[DietaryConstraint.DIABETIC_FRIENDLY, DietaryConstraint.LOW_SODIUM],
        allergies=["peanuts"],
    )

    adaptation = adapt_dish_for_health(
        dish_title="Puran Poli with Ghee",
        dish_description="Traditional festive flatbread with sweet filling",
        constraints=constraints,
    )

    assert adaptation.is_adapted is True
    assert "texture:soft_food" in adaptation.addressed_constraints
    assert "diabetic_friendly" in adaptation.addressed_constraints
    assert "allergy_free:peanuts" in adaptation.addressed_constraints
    assert len(adaptation.substitutions) > 0


@pytest.mark.asyncio
async def test_agent_generates_grounded_plan(sample_profile: ElderProfile):
    """Verify agent generates plan with music, film, meals, and reasoning trail."""
    agent = ReminiscenceAgent()
    plan = await agent.generate_plan(sample_profile)

    assert plan.persona_id == sample_profile.id
    assert len(plan.music_recommendations) > 0
    assert len(plan.film_recommendations) > 0
    assert len(plan.meal_recommendations) > 0
    assert len(plan.reasoning_trail) > 0

    # Ensure every recommendation traces to MOCK source in mock mode
    for item in plan.music_recommendations + plan.film_recommendations + plan.meal_recommendations:
        assert item.source == "MOCK"

    # Ensure meals have health adaptations attached
    for meal in plan.meal_recommendations:
        assert meal.health_adaptation is not None
