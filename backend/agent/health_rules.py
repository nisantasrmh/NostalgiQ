"""Deterministic culinary health adaptation rules.

Provides domain-specific adaptation strategies for:
- Soft food & dysphagia texture modifications
- Low sodium seasoning replacements
- Diabetic-friendly sugar and carbohydrate substitutions
- Allergen screening and ingredient substitutions
"""

from typing import Any, Dict, List
from backend.models.schemas import HealthAdaptation, HealthConstraints, TextureRequirement


def adapt_dish_for_health(
    dish_title: str,
    dish_description: str,
    constraints: HealthConstraints,
) -> HealthAdaptation:
    """Transform a traditional cultural recipe into a medically conscious, safe adaptation.

    Args:
        dish_title: Name of the traditional cultural dish.
        dish_description: Standard recipe or dish profile.
        constraints: Patient's clinical and texture constraints.

    Returns:
        HealthAdaptation schema detailing ingredient swaps, texture changes, and rationale.
    """
    substitutions: List[str] = []
    addressed_constraints: List[str] = []
    texture_instructions = "Standard preparation appropriate for normal chewing ability."
    adapted_dish_title = dish_title

    # 1. Texture Requirements (Dysphagia & Soft Food)
    if constraints.texture_requirement in (TextureRequirement.SOFT_FOOD, TextureRequirement.MINCED_MOIST, TextureRequirement.PUREE):
        addressed_constraints.append(f"texture:{constraints.texture_requirement.value}")
        if "poli" in dish_title.lower() or "flatbread" in dish_title.lower() or "pizza" in dish_title.lower():
            adapted_dish_title = f"Steamed Soft {dish_title} (Crustless & Tender)"
            texture_instructions = (
                "Steam lightly or soften with warm broth/milk until fork-tender; remove any dry or crunchy edges. "
                "Ensure no chewing fatigue."
            )
            substitutions.append("Remove crispy crusts; steam flatbread with a drizzle of warm milk or clarified ghee.")
        elif "roast" in dish_title.lower() or "meat" in dish_title.lower():
            adapted_dish_title = f"Slow-Braised Shredded {dish_title}"
            texture_instructions = (
                "Braise until meat fibers gently pull apart with a fork; puree root vegetables with broth for smooth swallowability."
            )
            substitutions.append("Slow-cook to internal temperature > 195°F for effortless fork-shredding.")
        else:
            adapted_dish_title = f"Gentle Soft-Prepared {dish_title}"
            texture_instructions = (
                "Cook to a soft, uniform consistency. Mash gently with a fork before serving."
            )

    # 2. Diabetic-Friendly Modifications
    restriction_values = [r.value if hasattr(r, "value") else str(r) for r in constraints.dietary_restrictions]
    if "diabetic_friendly" in restriction_values:
        addressed_constraints.append("diabetic_friendly")
        if any(w in dish_title.lower() for w in ["puran", "sweet", "tart", "pie", "shrikhand", "apple"]):
            substitutions.append(
                "Replace refined sugar/high-ratio jaggery with a stevia/monkfruit blend and increase cardamom/cinnamon for perceived natural sweetness."
            )
            substitutions.append("Use roasted almond meal or chana dal fiber base to minimize glycemic spikes.")
        else:
            substitutions.append("Pair with extra soluble fiber and avoid high-glycemic sweet glazes.")

    # 3. Low-Sodium & Cardiac Adaptations
    if "low_sodium" in restriction_values or "cardiac_friendly" in restriction_values:
        addressed_constraints.append("low_sodium")
        substitutions.append(
            "Eliminate added salt; boost flavor profile with fresh lemon zest, roasted cumin powder, crushed coriander, and garlic."
        )

    # 4. Strict Allergen Screening
    for allergen in constraints.allergies:
        allergen_clean = allergen.strip().lower()
        addressed_constraints.append(f"allergy_free:{allergen_clean}")
        if allergen_clean in ("peanut", "peanuts"):
            substitutions.append(
                "Strict zero-peanut policy: substitute crushed roasted sesame or sunflower seed butter if nutty aroma is desired."
            )
        elif allergen_clean in ("shellfish", "fish"):
            substitutions.append("Ensure 100% vegetarian vegetable stock bases with no fish or oyster sauces.")
        elif allergen_clean in ("dairy", "lactose"):
            substitutions.append("Replace ghee/dairy milk with fortified oat milk or coconut-based alternatives.")

    return HealthAdaptation(
        is_adapted=len(addressed_constraints) > 0,
        original_dish=dish_title,
        adapted_dish=adapted_dish_title,
        texture_instructions=texture_instructions,
        substitutions=substitutions or ["No ingredient substitutions required."],
        addressed_constraints=addressed_constraints,
    )
