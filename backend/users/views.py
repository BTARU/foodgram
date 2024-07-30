from django.contrib.auth import get_user_model
from djoser.serializers import SetPasswordSerializer, UserCreateSerializer
from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from .serializers import UserAvatarSerializer, UserSerializer

User = get_user_model()


class UserViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet
):
    queryset = User.objects.all()
    permission_classes = (AllowAny,)
    pagination_class = LimitOffsetPagination

    def get_serializer_class(self):
        if self.action == 'create':
            return UserCreateSerializer
        elif self.action == "set_password":
            return SetPasswordSerializer
        elif self.action == 'avatar':
            return UserAvatarSerializer
        return UserSerializer

    @action(
        ['get'],
        detail=False,
        permission_classes=[IsAuthenticated]
    )
    def me(self, request):
        """Выводит пользователю его профиль."""
        serializer = self.get_serializer(request.user)
        return Response(
            serializer.data
        )

    @action(
        ['post'],
        detail=False,
        permission_classes=[IsAuthenticated]
    )
    def set_password(self, request):
        """Изменить пароль пользователя."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        request.user.set_password(serializer.validated_data['new_password'])
        request.user.save()
        return Response(
            status=status.HTTP_204_NO_CONTENT
        )

    @action(
        ['put'],
        detail=False,
        permission_classes=[IsAuthenticated],
        url_path='me/avatar'
    )
    def avatar(self, request):
        """Установить фото аватара профилю пользователя."""
        serializer = self.get_serializer(
            instance=request.user,
            data=request.data
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            serializer.validated_data
        )

    @avatar.mapping.delete
    def delete_avatar(self, request):
        """Удалить фото аватара профиля пользователя."""
        request.user.avatar = None
        request.user.save()
        return Response(
            status=status.HTTP_204_NO_CONTENT
        )
