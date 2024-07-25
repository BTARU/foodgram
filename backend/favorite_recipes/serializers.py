from rest_framework import serializers

from recipes.models import Recipe
from recipes.serializers import RecipeShortInfoSerializer
from .models import UserFavoriteRecipes


class FavoriteRecipeSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField()

    class Meta:
        model = Recipe
        fields = ('id',)

    def to_representation(self, instance):
        serializer = RecipeShortInfoSerializer(
            instance,
            context={'request': self.context['request']}
        )
        return serializer.data


class FavoriteRecipeCreateSerializer(FavoriteRecipeSerializer):
    def validate_id(self, value):
        if UserFavoriteRecipes.objects.filter(
            user=self.context['request'].user,
            recipe=value
        ).exists():
            raise serializers.ValidationError(
                'Рецепт уже в избранном.'
            )
        return value


class FavoriteRecipeDeleteSerializer(FavoriteRecipeSerializer):
    def validate_id(self, value):
        if not UserFavoriteRecipes.objects.filter(
            user=self.context['request'].user,
            recipe=value
        ).exists():
            raise serializers.ValidationError(
                'Рецепта нет в избранном.'
            )
        return value
