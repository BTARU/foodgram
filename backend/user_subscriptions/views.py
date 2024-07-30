from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from users.views import UserViewSet
from .models import Subscription
from .serializers import (UserSubscriptionCreationSerializer,
                          UserSubscriptionDeleteSerializer,
                          UserSubscriptionSerializer)


class UserSubscriptionViewSet(UserViewSet):
    """Добавляет вьюсету Юзеров функционал подписок."""

    def get_serializer_class(self):
        if self.action == 'subscriptions':
            return UserSubscriptionSerializer
        elif self.action == 'subscribe':
            return UserSubscriptionCreationSerializer
        elif self.action == 'delete_subscribe':
            return UserSubscriptionDeleteSerializer
        return super().get_serializer_class()

    def get_queryset(self):
        if self.action == 'subscriptions':
            queryset = self.request.user.subscriptions.all()
            return [sub.subscribe_target for sub in queryset]
        return super().get_queryset()

    @action(
        ['get'],
        detail=False,
        permission_classes=[IsAuthenticated],
    )
    def subscriptions(self, request):
        """Вывести список подписок пользователя."""
        return super().list(request)

    @action(
        ['post'],
        detail=False,
        permission_classes=[IsAuthenticated],
        url_path=r'(?P<pk>\d+)/subscribe'
    )
    def subscribe(self, request, pk):
        """Подписаться на пользователя."""
        sub_user = self.get_object()

        serializer = self.get_serializer(
            instance=sub_user,
            data={'id': pk},
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        Subscription.objects.create(
            subscriber=request.user,
            subscribe_target=sub_user
        )
        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED
        )

    @subscribe.mapping.delete
    def delete_subscribe(self, request, pk):
        """Отписаться от пользователя."""
        sub_user = self.get_object()

        serializer = self.get_serializer(
            instance=sub_user,
            data={'id': pk},
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        Subscription.objects.filter(
            subscriber=request.user,
            subscribe_target=sub_user
        ).delete()
        return Response(
            status=status.HTTP_204_NO_CONTENT
        )
