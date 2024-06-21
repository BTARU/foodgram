import base64

from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from rest_framework import serializers
from recipes.models import (
    Tag, Ingredient, Recipe, IngredientRecipe, TagRecipe
)
from users.models import Subscription

User = get_user_model()


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]
            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)

        return super().to_internal_value(data)


class AvatarSerializer(serializers.Serializer):
    avatar = Base64ImageField()

    def update(self, instance, validated_data):
        instance.avatar = validated_data.get('avatar', instance.avatar)
        instance.save()
        return instance


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
        if self.context['request'].user.is_authenticated:
            return Subscription.objects.filter(
                subscriber=self.context['request'].user,
                subscribe_target=obj
            ).exists()
        return False


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

    def validate(self, attrs):
        if len(self.fields) != len(attrs):
            raise serializers.ValidationError('Required field missing.')
        errors_dict = {}
        if attrs['cooking_time'] < 1:
            errors_dict['cooking_time'] = 'Cooking_time must be positive.'
        if not attrs['ingredients']:
            errors_dict['ingredients'] = 'Empty ingredients field.'
        else:
            ingredients = attrs.get('ingredients')
            ingredient_pks = [ingredient['id'] for ingredient in ingredients]
            if len(ingredients) != len(set(ingredient_pks)):
                errors_dict['ingredients'] = 'Repeated ingredients.'
            for ingredient in ingredients:
                if ingredient['amount'] < 1:
                    errors_dict['ingredients'] = (
                        'Ingredient amount less than 1.'
                    )
                ingredient_id = ingredient['id']
                if not Ingredient.objects.filter(pk=ingredient_id).exists():
                    errors_dict['ingredients'] = (
                        f'Unexisting ingredient {ingredient_id}.'
                    )
        if not attrs['tags']:
            errors_dict['tags'] = 'Empty tags field.'
        else:
            tags = attrs.get('tags')
            if len(tags) != len(set(tags)):
                errors_dict['tags'] = 'Repeated tags.'
            for tag in tags:
                if not Tag.objects.filter(pk=tag).exists():
                    errors_dict['tags'] = f'Unexisting tag {tag}.'
        if errors_dict:
            raise serializers.ValidationError(errors_dict)
        return attrs

    def create(self, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(**validated_data)

        for ingredient in ingredients:
            current_ingredient = Ingredient.objects.get(pk=ingredient['id'])
            IngredientRecipe.objects.create(
                ingredient=current_ingredient,
                recipe=recipe,
                amount=ingredient['amount']
            )
        for tag in tags:
            current_tag = Tag.objects.get(pk=tag)
            TagRecipe.objects.create(
                recipe=recipe,
                tag=current_tag
            )
        return recipe

    def update(self, instance, validated_data):
        instance.name = validated_data.get('name', instance.name)
        instance.text = validated_data.get('text', instance.text)
        instance.cooking_time = validated_data.get(
            'cooking_time',
            instance.cooking_time
        )
        instance.image = validated_data.get('image', instance.image)

        ingredients_data = validated_data.pop('ingredients')
        lst = []
        for ingredient in ingredients_data:
            current_ingredient = Ingredient.objects.get(
                pk=ingredient['id']
            )
            lst.append(current_ingredient)
        instance.ingredients.set(lst)

        tags_data = validated_data.pop('tags')
        lst = []
        for tag in tags_data:
            current_tag = Tag.objects.get(pk=tag)
            lst.append(current_tag)
        instance.tags.set(lst)

        instance.save()
        return instance

    def to_representation(self, instance):
        serializer = RecipeReadSerializer(instance)
        return serializer.data


class RecipeReadSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    ingredients = serializers.SerializerMethodField()
    tags = TagSerializer(many=True)

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
        return [
            {
                'id': recipe_ingredient.ingredient.id,
                'name': recipe_ingredient.ingredient.name,
                'measurement_unit':
                recipe_ingredient.ingredient.measurement_unit,
                'amount': recipe_ingredient.amount
            }
            for recipe_ingredient in recipe_ingredients
        ]


class RecipeShortInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = (
            'id',
            'name',
            'image',
            'cooking_time'
        )


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
        serializer = RecipeShortInfoSerializer(queryset, many=True)
        return serializer.data
