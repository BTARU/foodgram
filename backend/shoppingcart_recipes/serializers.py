from rest_framework import serializers

from recipes.models import Recipe
from recipes.serializers import RecipeShortInfoSerializer
from .models import UserRecipeShoppingCart


class RecipeShoppingCartSerializer(serializers.ModelSerializer):
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


class RecipeShoppingCartCreateSerializer(RecipeShoppingCartSerializer):
    def validate_id(self, value):
        if UserRecipeShoppingCart.objects.filter(
            user=self.context['request'].user,
            recipe=value
        ).exists():
            raise serializers.ValidationError(
                'Рецепт уже в корзине покупок.'
            )
        return value


class RecipeShoppingCartDeleteSerializer(RecipeShoppingCartSerializer):
    def validate_id(self, value):
        if not UserRecipeShoppingCart.objects.filter(
            user=self.context['request'].user,
            recipe=value
        ).exists():
            raise serializers.ValidationError(
                'Рецепта нет в корзине покупок.'
            )
        return value
