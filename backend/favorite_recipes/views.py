from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from recipes.views import RecipeViewSet
from .models import UserFavoriteRecipes
from .serializers import (FavoriteRecipeCreateSerializer,
                          FavoriteRecipeDeleteSerializer)


class FavoriteRecipeViewSet(RecipeViewSet):
    """Расширяет вьюсет рецептов, позволяя добавлять рецепты в избранное."""

    def get_serializer_class(self):
        if self.action == 'favorite':
            return FavoriteRecipeCreateSerializer
        elif self.action == 'delete_favorite':
            return FavoriteRecipeDeleteSerializer
        return super().get_serializer_class()

    @action(
        ['post'],
        detail=False,
        url_path=r'(?P<pk>\d+)/favorite',
        permission_classes=[IsAuthenticated],
    )
    def favorite(self, request, pk):
        """Добавить рецепт в избранное."""
        recipe = self.get_object()

        serializer = self.get_serializer(
            instance=recipe,
            data={'id': pk},
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        UserFavoriteRecipes.objects.create(
            user=request.user,
            recipe=recipe
        )
        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED
        )

    @favorite.mapping.delete
    def delete_favorite(self, request, pk):
        """Удалить рецепт из избранного."""
        recipe = self.get_object()

        serializer = self.get_serializer(
            instance=recipe,
            data={'id': pk},
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        UserFavoriteRecipes.objects.filter(
            user=request.user,
            recipe=recipe
        ).delete()
        return Response(
            status=status.HTTP_204_NO_CONTENT
        )
