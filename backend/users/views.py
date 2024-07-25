from django.contrib.auth import get_user_model, update_session_auth_hash
from djoser import utils
from djoser.compat import get_user_email
from djoser.conf import settings
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
        serializer = self.get_serializer(request.user)
        return Response(
            serializer.data
        )

    @action(
        ['post'],
        detail=False,
        permission_classes=[IsAuthenticated]
    )
    def set_password(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        self.request.user.set_password(serializer.data['new_password'])
        self.request.user.save()

        if settings.PASSWORD_CHANGED_EMAIL_CONFIRMATION:
            context = {'user': self.request.user}
            to = [get_user_email(self.request.user)]
            settings.EMAIL.password_changed_confirmation(
                self.request, context).send(to)

        if settings.LOGOUT_ON_PASSWORD_CHANGE:
            utils.logout_user(self.request)
        elif settings.CREATE_SESSION_ON_LOGIN:
            update_session_auth_hash(self.request, self.request.user)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        ['put'],
        detail=False,
        permission_classes=[IsAuthenticated],
        url_path='me/avatar'
    )
    def avatar(self, request):
        serializer = self.get_serializer(
            instance=request.user,
            data=request.data
        )
        if serializer.is_valid():
            serializer.save()
            return Response(
                serializer.data
            )
        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )

    @avatar.mapping.delete
    def delete_avatar(self, request):
        request.user.avatar = None
        request.user.save()
        return Response(
            status=status.HTTP_204_NO_CONTENT
        )
