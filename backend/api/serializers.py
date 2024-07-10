from django.contrib.auth import get_user_model
from rest_framework import serializers

from recipes.models import (Ingredient, IngredientRecipe, Recipe, Tag,
                            UserFavoriteRecipes,
                            UserRecipeShoppingCart)
from users.models import Subscription
from .serializer_fields import Base64ImageField
from foodgram_backend.constants import RECIPE_NAME_LENGTH
from .utils import create_recipe_ingredient, add_tags_to_recipe

User = get_user_model()


class UserAvatarSerializer(serializers.ModelSerializer):
    avatar = Base64ImageField()

    class Meta:
        model = User
        fields = (
            'avatar',
        )


class UserSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'id',
            'username',
            'first_name',
            'last_name',
            'email',
            'is_subscribed',
            'avatar'
        )

    def get_is_subscribed(self, obj):
        return (
            self.context['request'].user.is_authenticated
            and Subscription.objects.filter(
                subscriber=self.context['request'].user,
                subscribe_target=obj
            ).exists()
        )


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = (
            'id',
            'name',
            'slug'
        )


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = (
            'id',
            'name',
            'measurement_unit'
        )


class IngredientRecipeSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField()

    class Meta:
        model = IngredientRecipe
        fields = ('id', 'amount')


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
            'cooking_time'
        )

    def validate_name(self, value):
        if Recipe.objects.filter(
            name=value,
            author=self.context['request'].user
        ).exists():
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


class RecipeFavoriteSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField()

    class Meta:
        model = Recipe
        fields = (
            'id',
        )

    def validate_id(self, value):
        favorite_recipe_check = UserFavoriteRecipes.objects.filter(
            user=self.context['request'].user,
            recipe=value
        ).exists()
        if self.context['request'].method == 'POST':
            if favorite_recipe_check:
                raise serializers.ValidationError(
                    'Рецепт уже в избранном.'
                )

        if self.context['request'].method == 'DELETE':
            if not favorite_recipe_check:
                raise serializers.ValidationError(
                    'Рецепта нет в избранном.'
                )
        return value

    def to_representation(self, instance):
        serializer = RecipeShortInfoSerializer(
            instance,
            context={'request': self.context['request']}
        )
        return serializer.data


class RecipeShoppingCartSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField()

    class Meta:
        model = Recipe
        fields = (
            'id',
        )

    def validate_id(self, value):
        shopping_cart_recipe_check = UserRecipeShoppingCart.objects.filter(
            user=self.context['request'].user,
            recipe=value
        ).exists()
        if self.context['request'].method == 'POST':
            if shopping_cart_recipe_check:
                raise serializers.ValidationError(
                    'Рецепт уже в корзине покупок.'
                )

        if self.context['request'].method == 'DELETE':
            if not shopping_cart_recipe_check:
                raise serializers.ValidationError(
                    'Рецепта нет в корзине покупок.'
                )
        return value

    def to_representation(self, instance):
        serializer = RecipeShortInfoSerializer(
            instance,
            context={'request': self.context['request']}
        )
        return serializer.data


class UserSubscriptionSerializer(serializers.ModelSerializer):
    recipes_count = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()
    is_subscribed = serializers.BooleanField(default=True)

    class Meta:
        model = User
        fields = (
            'id',
            'username',
            'first_name',
            'last_name',
            'email',
            'is_subscribed',
            'avatar',
            'recipes',
            'recipes_count'
        )

    def get_recipes_count(self, obj):
        return Recipe.objects.filter(author=obj).count()

    def get_recipes(self, obj):
        recipes_limit = self.context['request'].query_params.get(
            'recipes_limit'
        )
        queryset = Recipe.objects.filter(author=obj)
        if recipes_limit:
            queryset = queryset[:int(recipes_limit)]
        serializer = RecipeShortInfoSerializer(
            queryset,
            context={'request': self.context['request']},
            many=True
        )
        return serializer.data


class UserSubscriptionActionSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField()

    class Meta:
        model = User
        fields = (
            'id',
        )

    def validate_id(self, value):
        is_subscribed = Subscription.objects.filter(
            subscriber=self.context['request'].user,
            subscribe_target=value
        ).exists()
        if self.context['request'].method == 'POST':
            if self.context['request'].user.id == value:
                raise serializers.ValidationError(
                    'Нельзя подписаться на себя.'
                )
            if is_subscribed:
                raise serializers.ValidationError(
                    'Вы уже подписаны на этого пользователя.'
                )

        if self.context['request'].method == 'DELETE':
            if not is_subscribed:
                raise serializers.ValidationError(
                    'Нет подписки на этого пользователя.'
                )
        return value

    def to_representation(self, instance):
        serializer = UserSubscriptionSerializer(
            instance,
            context={'request': self.context['request']}
        )
        return serializer.data
