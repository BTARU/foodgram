from rest_framework import serializers

from recipes.models import Recipe
from recipes.serializers import RecipeShortInfoSerializer
from .models import UserRecipeShoppingCart


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
