from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class Tag(models.Model):
    name = models.CharField(
        verbose_name='Name',
        max_length=128
    )
    slug = models.SlugField(
        verbose_name='Slug',
        max_length=64,
        unique=True,
        help_text=(
            'Page ID for URL; '
            'Only latin characters, numbers, hyphens and underscores.'
        )
    )


class Ingredient(models.Model):
    name = models.CharField(
        verbose_name='Name',
        max_length=128,
        unique=True
    )
    measurement_unit = models.CharField(
        verbose_name='Measurement_unit',
        max_length=64
    )


class Recipe(models.Model):
    name = models.CharField(
        verbose_name='Name',
        max_length=256
    )
    text = models.TextField(
        verbose_name='Text'
    )
    cooking_time = models.PositiveSmallIntegerField(
        verbose_name='cooking_time'
    )
    image = models.ImageField(
        verbose_name='Photo',
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
        through='TagRecipe'
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through='IngredientRecipe'
    )

    class Meta:
        ordering = ('-created_at',)


class TagRecipe(models.Model):
    tag = models.ForeignKey(
        Tag,
        on_delete=models.CASCADE
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE
    )


class IngredientRecipe(models.Model):
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


class UserFavoriteRecipes(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='User',
        related_name='user_favorite_recipes'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Recipe'
    )


class UserRecipeShoppingCart(models.Model):
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
