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
    RecipeCreateSerializer, RecipeReadSerializer, RecipeShortInfoSerializer,
    UserSubscriptionSerializer
)
from recipes.models import Tag, Ingredient, Recipe, UserFavoriteRecipes
from users.models import Subscription
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
        elif self.action in ('subscribe', 'subscriptions'):
            return UserSubscriptionSerializer
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

    @action(
        ['get'],
        detail=False,
        permission_classes=[IsAuthenticated],
    )
    def subscriptions(self, request):
        queryset = request.user.subscriptions.all()
        queryset = [sub.subscribe_target for sub in queryset]
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )

    @action(
        ['post', 'delete'],
        detail=False,
        permission_classes=[IsAuthenticated],
        url_path=r'(?P<user_id>\d+)/subscribe'
    )
    def subscribe(self, request, user_id):
        sub_user = get_object_or_404(User, pk=user_id)
        errors_dict = {}
        is_subscribed = Subscription.objects.filter(
            subscriber=request.user,
            subscribe_target=sub_user
        ).exists()
        if request.method == 'POST':
            if request.user == sub_user:
                errors_dict['detail'] = 'Cant subscribe on yourself.'
            elif is_subscribed:
                errors_dict['detail'] = 'Already subscribed on that user.'
            if errors_dict:
                return Response(
                    errors_dict,
                    status=status.HTTP_400_BAD_REQUEST
                )

            serializer = self.get_serializer(instance=sub_user)
            Subscription.objects.create(
                subscriber=request.user,
                subscribe_target=sub_user
            )
            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED
            )
        # if request.method == 'DELETE'
        if not is_subscribed:
            return Response(
                {
                    'detail': 'Not subscribed on that user.'
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        Subscription.objects.filter(
            subscriber=request.user,
            subscribe_target=sub_user
        ).delete()
        return Response(
            status=status.HTTP_204_NO_CONTENT
        )


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
            serializer = RecipeShortInfoSerializer(instance=recipe)
            m_data = serializer.data
            m_data['image'] = request.build_absolute_uri(recipe.image.url)
            return Response(
                m_data,
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
