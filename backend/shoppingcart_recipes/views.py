import csv

from django.http import HttpResponse
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from favorite_recipes.views import FavoriteRecipeViewSet
from .models import UserRecipeShoppingCart
from .serializers import RecipeShoppingCartSerializer


class RecipeShoppingCartViewSet(FavoriteRecipeViewSet):
    """Расширяет вьюсет рецептов, позволяя добавлять их в корзину покупок."""

    def get_serializer_class(self):
        if self.action in ('shopping_cart', 'delete_shopping_cart'):
            return RecipeShoppingCartSerializer
        return super().get_serializer_class()

    @action(
        ['post'],
        detail=False,
        url_path=r'(?P<pk>\d+)/shopping_cart',
        permission_classes=[IsAuthenticated]
    )
    def shopping_cart(self, request, pk):
        recipe = self.get_object()

        serializer = self.get_serializer(
            instance=recipe,
            data={'id': pk},
            context={'request': request}
        )
        if serializer.is_valid():
            UserRecipeShoppingCart.objects.create(
                user=request.user,
                recipe=recipe
            )
            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )

    @shopping_cart.mapping.delete
    def delete_shopping_cart(self, request, pk):
        recipe = self.get_object()

        serializer = self.get_serializer(
            instance=recipe,
            data={'id': pk},
            context={'request': request}
        )
        if serializer.is_valid():
            UserRecipeShoppingCart.objects.filter(
                user=request.user,
                recipe=recipe
            ).delete()
            return Response(
                status=status.HTTP_204_NO_CONTENT
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )

    @action(
        ['get'],
        detail=False,
        permission_classes=[IsAuthenticated],
    )
    def download_shopping_cart(self, request):
        queryset = request.user.user_shopping_cart_recipes.all()
        queryset = [user_shop_cart.recipe for user_shop_cart in queryset]
        ingredient_list = {}
        serializer = self.get_serializer(queryset, many=True)
        response = HttpResponse(
            content_type='text/csv',
            headers={
                'Content-Disposition':
                'attachment; filename="shopping_list.csv"'
            },
        )

        for recipe in serializer.data:
            for ingredient in recipe.get('ingredients'):
                ingredient_name = ingredient.get('name')
                if ingredient_name not in ingredient_list:
                    ingredient_list[ingredient_name] = [
                        ingredient.get('measurement_unit'),
                        ingredient.get('amount')
                    ]
                else:
                    ingredient_list[ingredient_name][1] += ingredient.get(
                        'amount'
                    )

        writer = csv.writer(response)
        for name, values in ingredient_list.items():
            writer.writerow((name, values[0], values[1]))
        return response
