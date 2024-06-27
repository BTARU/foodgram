"""Models for recipes app."""
from django.contrib.auth import get_user_model
from django.db import models

from foodgram_backend.constants import (
    TRUNCATE_AMOUNT, TAG_FIELD_MAX_LENGTH, INGREDIENT_NAME_LENGTH,
    INGREDIENT_M_UNIT_LENGTH, RECIPE_NAME_LENGTH
)
User = get_user_model()


class Tag(models.Model):
    """Tag for recipe."""
    name = models.CharField(
        verbose_name='Name',
        max_length=TAG_FIELD_MAX_LENGTH
    )
    slug = models.SlugField(
        verbose_name='Short url name',
        max_length=TAG_FIELD_MAX_LENGTH,
        unique=True,
        null=True,
        help_text=(
            'Page ID for URL; '
            'Only latin characters, numbers, hyphens and underscores.'
        )
    )

    class Meta:
        verbose_name = 'Tag'
        verbose_name_plural = 'Tags'

    def __str__(self) -> str:
        return self.name[:TRUNCATE_AMOUNT]


class Ingredient(models.Model):
    """Ingredient for recipe."""
    name = models.CharField(
        verbose_name='Name',
        max_length=INGREDIENT_NAME_LENGTH,
        unique=True
    )
    measurement_unit = models.CharField(
        verbose_name='Measurement unit',
        max_length=INGREDIENT_M_UNIT_LENGTH
    )

    class Meta:
        verbose_name = 'Ingredient'
        verbose_name_plural = 'Ingredients'

    def __str__(self) -> str:
        return self.name[:TRUNCATE_AMOUNT]


class Recipe(models.Model):
    """Main project model - cooking recipe."""
    name = models.CharField(
        verbose_name='Name',
        max_length=RECIPE_NAME_LENGTH
    )
    text = models.TextField(
        verbose_name='Text'
    )
    cooking_time = models.PositiveSmallIntegerField(
        verbose_name='Cooking time'
    )
    image = models.ImageField(
        verbose_name='Image',
        upload_to='recipe_images',
        default=None
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Created at'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes_author',
        verbose_name='Recipe author',
    )
    tags = models.ManyToManyField(
        Tag,
        through='TagRecipe',
        verbose_name='Tags'
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through='IngredientRecipe',
        verbose_name='Ingredients'
    )

    class Meta:
        ordering = ('-created_at',)
        verbose_name = 'Recipe'
        verbose_name_plural = 'Recipes'

    def __str__(self) -> str:
        return self.name[:TRUNCATE_AMOUNT]


class TagRecipe(models.Model):
    """Recipe and Tag relational model."""
    tag = models.ForeignKey(
        Tag,
        on_delete=models.CASCADE
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE
    )

    class Meta:
        verbose_name = 'TagRecipe'
        verbose_name_plural = 'TagRecipe'

    def __str__(self) -> str:
        return self.tag.name + ' ' + self.recipe.name


class IngredientRecipe(models.Model):
    """Recipe and Ingredient relational model."""
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        verbose_name='Ingredient'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Recipe'
    )
    amount = models.PositiveSmallIntegerField(
        verbose_name='Ingredient amount for recipe'
    )

    class Meta:
        verbose_name = 'IngredientRecipe'
        verbose_name_plural = 'IngredientRecipe'

    def __str__(self) -> str:
        return (
            self.recipe.name[:TRUNCATE_AMOUNT] + ' ' +
            self.ingredient.name[:TRUNCATE_AMOUNT]
        )


class UserFavoriteRecipes(models.Model):
    """User favorite recipes relational model."""
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='User',
        related_name='user_favorite_recipes'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Recipe',
        related_name='recipe_favorite'
    )

    class Meta:
        verbose_name = 'UserFavoriteRecipes'
        verbose_name_plural = 'UserFavoriteRecipes'

    def __str__(self) -> str:
        return (
            self.user.email[:TRUNCATE_AMOUNT] + ' ' +
            self.recipe.name[:TRUNCATE_AMOUNT]
        )


class UserRecipeShoppingCart(models.Model):
    """User recipes in shopping cart relational model."""
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='User',
        related_name='user_shopping_cart_recipes'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Recipe'
    )

    class Meta:
        verbose_name = 'UserRecipeShoppingCart'
        verbose_name_plural = 'UserRecipeShoppingCart'

    def __str__(self) -> str:
        return (
            self.user.email[:TRUNCATE_AMOUNT] + ' ' +
            self.recipe.name[:TRUNCATE_AMOUNT]
        )
