from django.contrib.auth import get_user_model
from djoser.serializers import UserCreateSerializer, SetPasswordSerializer
from rest_framework import viewsets, status, mixins
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from .serializers import (
    UserSerializer, TagSerializer, IngredientSerializer, RecipeSerializer,
    AvatarSerializer
)
from recipes.models import Tag, Ingredient, Recipe

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
        elif self.action == 'add_avatar':
            return AvatarSerializer
        return UserSerializer

    @action(detail=False, permission_classes=[IsAuthenticated])
    def me(self, request):
        user = self.request.user
        serializer = self.get_serializer(user)
        return Response(serializer.data)

    @action(['post'], detail=False, permission_classes=[IsAuthenticated])
    def set_password(self, request):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            self.request.user.set_password(serializer.data["new_password"])
            self.request.user.save()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(['put', 'delete'],
            detail=False,
            permission_classes=[IsAuthenticated],
            url_path='me/avatar'
            )
    def add_avatar(self, request):
        if request.method == 'PUT':
            serializer = self.get_serializer(
                self.request.user, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )
        if request.method == 'DELETE':
            self.request.user.avatar = None
            self.request.user.save()
            return Response(status=status.HTTP_204_NO_CONTENT)


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (AllowAny,)
    pagination_class = None


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (AllowAny,)
    pagination_class = None


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
