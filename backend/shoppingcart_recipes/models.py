from django.contrib.auth import get_user_model
from django.db import models

from recipes.models import Recipe
from foodgram_backend.constants import TRUNCATE_AMOUNT

User = get_user_model()


class UserRecipeShoppingCart(models.Model):
    """Связующая модель рецептов пользователя в корзине покупок."""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Пользователь',
        related_name='user_shopping_cart_recipes'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепт',
        related_name='shopping_cart_recipes'
    )

    class Meta:
        verbose_name = 'Рецепт пользователя в корзине'
        verbose_name_plural = 'Рецепты пользователя в корзине'
        constraints = [
            models.UniqueConstraint(
                fields=('user', 'recipe'),
                name='unique_user_recipe_in_shopping_cart',
            ),
        ]

    def __str__(self) -> str:
        return (
            self.user.email[:TRUNCATE_AMOUNT] + ' '
            + self.recipe.name[:TRUNCATE_AMOUNT]
        )
