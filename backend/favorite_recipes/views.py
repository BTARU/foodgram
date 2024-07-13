from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from recipes.views import RecipeViewSet
from .models import UserFavoriteRecipes
from .serializers import FavoriteRecipeSerializer


class FavoriteRecipeViewSet(RecipeViewSet):
    """Расширяет вьюсет рецептов, позволяя добавлять рецепты в избранное."""

    def get_serializer_class(self):
        if self.action in ('favorite', 'delete_favorite'):
            return FavoriteRecipeSerializer
        return super().get_serializer_class()

    @action(
        ['post'],
        detail=False,
        url_path=r'(?P<pk>\d+)/favorite',
        permission_classes=[IsAuthenticated],
    )
    def favorite(self, request, pk):
        recipe = self.get_object()

        serializer = self.get_serializer(
            instance=recipe,
            data={'id': pk},
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
    def delete_favorite(self, request, pk):
        recipe = self.get_object()

        serializer = self.get_serializer(
            instance=recipe,
            data={'id': pk},
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
