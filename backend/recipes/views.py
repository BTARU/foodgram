import csv

from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import (IsAuthenticated,
                                        IsAuthenticatedOrReadOnly)
from rest_framework.response import Response
from urlshortner.utils import shorten_url

from .filters import RecipeFilter
from .mixins import PatchModelMixin
from .models import Recipe, UserFavoriteRecipes, UserRecipeShoppingCart
from .permissions import IsAuthorOrAdmin
from .serializers import (RecipeCreateSerializer,
                          RecipeFavoriteSerializer, RecipeReadSerializer,
                          RecipeShoppingCartSerializer)


class RecipeViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.DestroyModelMixin,
    mixins.RetrieveModelMixin,
    PatchModelMixin,
    viewsets.GenericViewSet
):
    permission_classes = (IsAuthenticatedOrReadOnly, IsAuthorOrAdmin,)
    filter_backends = (DjangoFilterBackend,)
    queryset = Recipe.objects.all()
    filterset_class = RecipeFilter

    def get_serializer_class(self):
        if self.action in ('create', 'partial_update'):
            return RecipeCreateSerializer
        elif self.action in ('favorite', 'delete_favorite'):
            return RecipeFavoriteSerializer
        elif self.action in ('shopping_cart', 'delete_shopping_cart'):
            return RecipeShoppingCartSerializer
        return RecipeReadSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(
        ['get'],
        detail=False,
        url_path=r'(?P<recipe_id>\d+)/get-link'
    )
    def get_link(self, request, recipe_id):
        get_object_or_404(Recipe, pk=recipe_id)
        url = request.build_absolute_uri().rstrip('get-link/')
        short_url = shorten_url(url, is_permanent=True)
        host = request.get_host()
        return Response(
            {
                'short-link': f'https://{host}/s/{short_url}'
            }
        )

    @action(
        ['post'],
        detail=False,
        url_path=r'(?P<recipe_id>\d+)/favorite'
    )
    def favorite(self, request, recipe_id):
        recipe = get_object_or_404(Recipe, pk=recipe_id)

        serializer = self.get_serializer(
            instance=recipe,
            data={'id': recipe_id},
            context={'request': request}
        )
        if serializer.is_valid():
            UserFavoriteRecipes.objects.create(
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

    @favorite.mapping.delete
    def delete_favorite(self, request, recipe_id):
        recipe = get_object_or_404(Recipe, pk=recipe_id)

        serializer = self.get_serializer(
            instance=recipe,
            data={'id': recipe_id},
            context={'request': request}
        )
        if serializer.is_valid():
            UserFavoriteRecipes.objects.filter(
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
        ['post'],
        detail=False,
        url_path=r'(?P<recipe_id>\d+)/shopping_cart'
    )
    def shopping_cart(self, request, recipe_id):
        recipe = get_object_or_404(Recipe, pk=recipe_id)

        serializer = self.get_serializer(
            instance=recipe,
            data={'id': recipe_id},
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
    def delete_shopping_cart(self, request, recipe_id):
        recipe = get_object_or_404(Recipe, pk=recipe_id)

        serializer = self.get_serializer(
            instance=recipe,
            data={'id': recipe_id},
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
