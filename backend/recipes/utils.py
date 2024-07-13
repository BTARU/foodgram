from ingredients.models import Ingredient
from tags.models import Tag
from .models import IngredientRecipe, Recipe


def create_recipe_ingredient(
        recipe: Recipe, ingredients_data: list[dict[str, int]]
) -> None:
    """Добавляет ингредиенты к полученному рецепту."""
    if not recipe or not ingredients_data:
        return
    for ingredient in ingredients_data:
        IngredientRecipe.objects.create(
            ingredient=Ingredient.objects.get(
                pk=ingredient['id']
            ),
            recipe=recipe,
            amount=ingredient['amount']
        )


def add_tags_to_recipe(recipe: Recipe, tags_data: list[int]) -> None:
    """Добавляет тэги к полученному рецепту."""
    if not recipe or not tags_data:
        return
    for tag_id in tags_data:
        recipe.tags.add(
            Tag.objects.get(pk=tag_id)
        )
