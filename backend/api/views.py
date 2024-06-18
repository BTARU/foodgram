from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from djoser.serializers import UserCreateSerializer, SetPasswordSerializer
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, status, mixins
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import (
    AllowAny, IsAuthenticated, IsAuthenticatedOrReadOnly
)
from urlshortner.utils import shorten_url
from .serializers import (
    UserSerializer, TagSerializer, IngredientSerializer, AvatarSerializer,
    RecipeCreateSerializer, RecipeReadSerializer
)
from recipes.models import Tag, Ingredient, Recipe, UserFavoriteRecipes
from .permissions import IsAuthorOrAdmin

User = get_user_model()


class UserViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet
):
    queryset = User.objects.all()
    permission_classes = (AllowAny,)

    def get_serializer_class(self):
        if self.action == 'create':
            return UserCreateSerializer
        elif self.action == "set_password":
            return SetPasswordSerializer
        elif self.action == 'avatar':
            return AvatarSerializer
        return UserSerializer

    @action(detail=False, permission_classes=[IsAuthenticated])
    def me(self, request):
        user = request.user
        serializer = self.get_serializer(user)
        return Response(serializer.data)

    @action(['post'], detail=False, permission_classes=[IsAuthenticated])
    def set_password(self, request):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            request.user.set_password(serializer.data["new_password"])
            request.user.save()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(
        ['put', 'delete'],
        detail=False,
        permission_classes=[IsAuthenticated],
        url_path='me/avatar'
    )
    def avatar(self, request):
        if request.method == 'PUT':
            serializer = self.get_serializer(
                request.user, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )
        # if request.method == 'DELETE':
        request.user.avatar = None
        request.user.save()
        return Response(status=status.HTTP_204_NO_CONTENT)


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (AllowAny,)
    pagination_class = None


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.annotate().all()
    serializer_class = IngredientSerializer
    permission_classes = (AllowAny,)
    pagination_class = None


class RecipeViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticatedOrReadOnly, IsAuthorOrAdmin,)
    http_method_names = [
        'get', 'post', 'patch', 'delete', 'head', 'options', 'trace'
    ]
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ('author',)

    def get_serializer_class(self):
        if self.action in ('create', 'partial_update'):
            return RecipeCreateSerializer
        return RecipeReadSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def get_queryset(self):
        queryset = Recipe.objects.all()
        params = self.request.query_params
        if 'tags' in params:
            tags = params.getlist('tags')
            for tag in tags:
                queryset = queryset.filter(tags__slug=tag)
        return queryset

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
            },
            status=status.HTTP_200_OK
        )

    @action(
        ['post', 'delete'],
        detail=False,
        url_path=r'(?P<recipe_id>\d+)/favorite'
    )
    def favorite(self, request, recipe_id):
        recipe = get_object_or_404(Recipe, pk=recipe_id)
        favorite_recipe_check = UserFavoriteRecipes.objects.filter(
            user=request.user,
            recipe=recipe
        ).exists()
        if request.method == 'POST':
            if favorite_recipe_check:
                return Response(
                    {
                        'detail': 'Recipe already in favorites.'
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )

            UserFavoriteRecipes.objects.create(
                user=request.user,
                recipe=recipe
            )
            host = request.get_host()
            return Response(
                {
                    'id': recipe.id,
                    'name': recipe.name,
                    'image': f'https://{host}{recipe.image.url}',
                    'cooking_time': recipe.cooking_time
                },
                status=status.HTTP_201_CREATED
            )
        # if request.method == 'DELETE':
        if not favorite_recipe_check:
            return Response(
                {
                    'detail': 'Recipe not in favorites.'
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        UserFavoriteRecipes.objects.filter(
            user=request.user,
            recipe=recipe
        ).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
