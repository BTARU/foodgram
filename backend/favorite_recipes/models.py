from django.contrib.auth import get_user_model
from django.db import models

from recipes.models import Recipe
from .constants import TRUNCATE_AMOUNT

User = get_user_model()


class UserFavoriteRecipes(models.Model):
    """Связующая модель избранных рецептов пользователя."""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Пользователь',
        related_name='user_favorite_recipes'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепт',
        related_name='recipe_favorite'
    )

    class Meta:
        verbose_name = 'Избранный рецепт пользователя'
        verbose_name_plural = 'Избранные рецепты пользователя'
        constraints = [
            models.UniqueConstraint(
                fields=('user', 'recipe'),
                name='unique_user_favorite_recipe',
            ),
        ]

    def __str__(self) -> str:
        return (
            self.user.email[:TRUNCATE_AMOUNT] + ' '
            + self.recipe.name[:TRUNCATE_AMOUNT]
        )
