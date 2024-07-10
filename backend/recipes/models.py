from django.contrib.auth import get_user_model
from django.db import models
from django.core.validators import MinValueValidator

from foodgram_backend.constants import (INGREDIENT_M_UNIT_LENGTH,
                                        INGREDIENT_NAME_LENGTH,
                                        RECIPE_NAME_LENGTH,
                                        TAG_FIELD_MAX_LENGTH, TRUNCATE_AMOUNT)

User = get_user_model()


class Tag(models.Model):
    """Тэг для рецептов."""

    name = models.CharField(
        verbose_name='Название',
        max_length=TAG_FIELD_MAX_LENGTH
    )
    slug = models.SlugField(
        verbose_name='Идентификатор',
        max_length=TAG_FIELD_MAX_LENGTH,
        unique=True,
        help_text=(
            'Идентификатор страницы для URL; '
            'разрешены символы латиницы, цифры, дефис и подчёркивание.'
        )
    )

    class Meta:
        verbose_name = 'Тэг'
        verbose_name_plural = 'Тэги'

    def __str__(self) -> str:
        return self.name[:TRUNCATE_AMOUNT]


class Ingredient(models.Model):
    """Ингредиент для рецептов."""

    name = models.CharField(
        verbose_name='Название',
        max_length=INGREDIENT_NAME_LENGTH,
        unique=True
    )
    measurement_unit = models.CharField(
        verbose_name='Единица измерения',
        max_length=INGREDIENT_M_UNIT_LENGTH
    )

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'

    def __str__(self) -> str:
        return self.name[:TRUNCATE_AMOUNT]


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
        verbose_name='Рецепт'
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
