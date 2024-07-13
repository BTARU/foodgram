from rest_framework import serializers

from recipes.models import Recipe
from recipes.serializers import RecipeShortInfoSerializer
from .models import UserFavoriteRecipes


class FavoriteRecipeSerializer(serializers.ModelSerializer):
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
