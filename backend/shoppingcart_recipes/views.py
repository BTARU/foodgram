import csv

from django.http import HttpResponse
from django.db.models import Sum
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from recipes.models import IngredientRecipe
from favorite_recipes.views import FavoriteRecipeViewSet
from .models import UserRecipeShoppingCart
from .serializers import (RecipeShoppingCartCreateSerializer,
                          RecipeShoppingCartDeleteSerializer)


class RecipeShoppingCartViewSet(FavoriteRecipeViewSet):
    """Расширяет вьюсет рецептов, позволяя добавлять их в корзину покупок."""

    def get_serializer_class(self):
        if self.action == 'shopping_cart':
            return RecipeShoppingCartCreateSerializer
        elif self.action == 'delete_shopping_cart':
            return RecipeShoppingCartDeleteSerializer
        return super().get_serializer_class()

    @action(
        ['post'],
        detail=False,
        url_path=r'(?P<pk>\d+)/shopping_cart',
        permission_classes=[IsAuthenticated]
    )
    def shopping_cart(self, request, pk):
        """Добавить рецепт в корзину покупок."""
        recipe = self.get_object()

        serializer = self.get_serializer(
            instance=recipe,
            data={'id': pk},
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        UserRecipeShoppingCart.objects.create(
            user=request.user,
            recipe=recipe
        )
        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED
        )

    @shopping_cart.mapping.delete
    def delete_shopping_cart(self, request, pk):
        """Удалить рецепт из корзины покупок."""
        recipe = self.get_object()

        serializer = self.get_serializer(
            instance=recipe,
            data={'id': pk},
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        UserRecipeShoppingCart.objects.filter(
            user=request.user,
            recipe=recipe
        ).delete()
        return Response(
            status=status.HTTP_204_NO_CONTENT
        )

    @action(
        ['get'],
        detail=False,
        permission_classes=[IsAuthenticated],
    )
    def download_shopping_cart(self, request):
        """Скачать список ингредиентов из корзины покупок."""
        ingredient_list = IngredientRecipe.objects.filter(
            recipe__shopping_cart_recipes__user=request.user
        ).values_list(
            'ingredient__name',
            'ingredient__measurement_unit',
        ).annotate(Sum('amount'))

        response = HttpResponse(
            content_type='text/csv',
            headers={
                'Content-Disposition':
                'attachment; filename="shopping_list.csv"'
            },
        )

        writer = csv.writer(response)
        for name, measurement_unit, sum in ingredient_list:
            writer.writerow((name, measurement_unit, sum))
        return response
