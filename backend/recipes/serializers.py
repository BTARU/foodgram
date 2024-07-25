from rest_framework import serializers
# from rest_framework.validators import UniqueTogetherValidator

from favorite_recipes.models import UserFavoriteRecipes
from foodgram_backend.constants import RECIPE_NAME_LENGTH
from ingredients.models import Ingredient
from ingredients.serializers import IngredientSerializer
from shoppingcart_recipes.models import UserRecipeShoppingCart
from tags.models import Tag
from tags.serializers import TagSerializer
from users.serializers import UserSerializer
from utils.serializer_fields import Base64ImageField
from .models import IngredientRecipe, Recipe
from .utils import add_tags_to_recipe, create_recipe_ingredient


class IngredientRecipeSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField()

    class Meta:
        model = IngredientRecipe
        fields = ('id', 'amount')


class RecipeShortInfoSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = (
            'id',
            'name',
            'image',
            'cooking_time'
        )

    def get_image(self, obj):
        return self.context.get('request').build_absolute_uri(obj.image.url)


class RecipeCreateSerializer(serializers.ModelSerializer):
    image = Base64ImageField()
    ingredients = IngredientRecipeSerializer(many=True)
    tags = serializers.ListField(child=serializers.IntegerField())
    cooking_time = serializers.IntegerField()
    name = serializers.CharField(max_length=RECIPE_NAME_LENGTH)

    class Meta:
        model = Recipe
        fields = (
            'ingredients',
            'tags',
            'image',
            'name',
            'text',
            'cooking_time',
        )
        # validators = [
        #     UniqueTogetherValidator(
        #         queryset=Recipe.objects.all(),
        #         fields=['name', 'author'],
        #         message='У вас уже есть рецепт с таким названием.'
        #     )
        # ]

    def validate_name(self, value):
        if Recipe.objects.filter(
            name=value,
            author=self.context['request'].user
        ).exists() and self.context['request'].method == 'POST':
            raise serializers.ValidationError(
                'У вас уже есть рецепт с таким названием.'
            )
        return value

    def validate_ingredients(self, value):
        if not value:
            raise serializers.ValidationError(
                'Поле ингредиентов не должно быть пустым.'
            )
        ingredient_ids = []
        for ingredient in value:
            if ingredient['amount'] < 1:
                raise serializers.ValidationError(
                    'Количество ингредиентов не должно быть меньше 1.'
                )

            ingredient_id = ingredient['id']
            if ingredient_id in ingredient_ids:
                raise serializers.ValidationError(
                    'Не должно быть повторяющихся ингредиентов.'
                )
            ingredient_ids.append(ingredient_id)

            if not Ingredient.objects.filter(pk=ingredient_id).exists():
                raise serializers.ValidationError(
                    f'Ингредиента с id {ingredient_id} не существует.'
                )
        return value

    def validate_tags(self, value):
        if not value:
            raise serializers.ValidationError(
                'Поле тэгов не должно быть пустым.'
            )

        if len(value) != len(set(value)):
            raise serializers.ValidationError(
                'Не должно быть повторяющихся тэгов.'
            )

        for tag in value:
            if not Tag.objects.filter(pk=tag).exists():
                raise serializers.ValidationError(
                    f'Тэга с id {tag} не существует.'
                )
        return value

    def validate_cooking_time(self, value):
        if value < 1:
            raise serializers.ValidationError(
                'Время готовки должно быть не меньше 1.'
            )
        return value

    def create(self, validated_data):
        ingredients_data = validated_data.pop('ingredients')
        tags_data = validated_data.pop('tags')
        recipe = Recipe.objects.create(**validated_data)
        create_recipe_ingredient(recipe, ingredients_data)
        add_tags_to_recipe(recipe, tags_data)
        return recipe

    def update(self, instance, validated_data):
        ingredients_data = validated_data.pop('ingredients')
        instance.ingredients.clear()
        create_recipe_ingredient(instance, ingredients_data)

        tags_data = validated_data.pop('tags')
        instance.tags.clear()
        add_tags_to_recipe(instance, tags_data)
        return super().update(instance, validated_data)

    def to_representation(self, instance):
        serializer = RecipeReadSerializer(
            instance,
            context={'request': self.context['request']}
        )
        return serializer.data


class RecipeReadSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    ingredients = serializers.SerializerMethodField()
    tags = TagSerializer(many=True)
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'is_favorited',
            'is_in_shopping_cart',
            'name',
            'image',
            'text',
            'cooking_time'
        )

    def get_ingredients(self, obj):
        recipe_ingredients = IngredientRecipe.objects.filter(recipe=obj)
        result = []
        for recipe_ingredient in recipe_ingredients:
            ingredient_data = IngredientSerializer(
                recipe_ingredient.ingredient
            ).data
            ingredient_data['amount'] = recipe_ingredient.amount
            result.append(ingredient_data)
        return result

    def get_is_favorited(self, obj):
        return (
            self.context['request'].user.is_authenticated
            and UserFavoriteRecipes.objects.filter(
                user=self.context['request'].user,
                recipe=obj
            ).exists()
        )

    def get_is_in_shopping_cart(self, obj):
        return (
            self.context['request'].user.is_authenticated
            and UserRecipeShoppingCart.objects.filter(
                user=self.context['request'].user,
                recipe=obj
            ).exists()
        )
