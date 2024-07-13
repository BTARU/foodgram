from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.db import models

from ingredients.models import Ingredient
from tags.models import Tag
from .constants import RECIPE_NAME_LENGTH, TRUNCATE_AMOUNT

User = get_user_model()


class Recipe(models.Model):
    """Основная модель проекта - кулинарный рецепт."""

    name = models.CharField(
        verbose_name='Название',
        max_length=RECIPE_NAME_LENGTH
    )
    text = models.TextField(
        verbose_name='Текст'
    )
    cooking_time = models.PositiveSmallIntegerField(
        verbose_name='Время приготовления',
        validators=[MinValueValidator(1)]
    )
    image = models.ImageField(
        verbose_name='Изображение',
        upload_to='recipe_images',
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Создано'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name='Автор рецепта',
    )
    tags = models.ManyToManyField(
        Tag,
        verbose_name='Тэги'
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through='IngredientRecipe',
        verbose_name='Ингредиенты'
    )

    class Meta:
        ordering = ('-created_at',)
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        constraints = [
            models.UniqueConstraint(
                fields=('name', 'author'),
                name='unique_author_recipe',
            ),
        ]

    def __str__(self) -> str:
        return self.name[:TRUNCATE_AMOUNT]


class IngredientRecipe(models.Model):
    """Связующая модель рецепта и ингредиентов к нему."""

    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        verbose_name='Ингредиент'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепт'
    )
    amount = models.PositiveSmallIntegerField(
        verbose_name='Количество ингредиентов для рецепта',
        validators=[MinValueValidator(1)]
    )

    class Meta:
        verbose_name = 'Ингредиент к рецепту'
        verbose_name_plural = 'Ингредиенты к рецепту'
        constraints = [
            models.UniqueConstraint(
                fields=('ingredient', 'recipe'),
                name='unique_ingredient_recipe',
            ),
        ]

    def __str__(self) -> str:
        return (
            self.recipe.name[:TRUNCATE_AMOUNT] + ' '
            + self.ingredient.name[:TRUNCATE_AMOUNT]
        )
