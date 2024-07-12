from django.contrib.auth import get_user_model
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from .models import Subscription
from .serializers import (UserSubscriptionSerializer,
                          UserSubscriptionActionSerializer)
from users.views import UserViewSet

User = get_user_model()


class UserSubscriptionViewSet(UserViewSet):
    """Добавляет вьюсету Юзеров функционал подписок."""

    def get_serializer_class(self):
        if self.action == 'subscriptions':
            return UserSubscriptionSerializer
        elif self.action in ('subscribe', 'delete_subscribe'):
            return UserSubscriptionActionSerializer
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
        return super().list(request)

    @action(
        ['post'],
        detail=False,
        permission_classes=[IsAuthenticated],
        url_path=r'(?P<pk>\d+)/subscribe'
    )
    def subscribe(self, request, pk):
        sub_user = self.get_object()

        serializer = self.get_serializer(
            instance=sub_user,
            data={'id': pk},
            context={'request': request}
        )
        if serializer.is_valid():
            Subscription.objects.create(
                subscriber=request.user,
                subscribe_target=sub_user
            )
            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )

    @subscribe.mapping.delete
    def delete_subscribe(self, request, pk):
        sub_user = self.get_object()

        serializer = self.get_serializer(
            instance=sub_user,
            data={'id': pk},
            context={'request': request}
        )
        if serializer.is_valid():
            Subscription.objects.filter(
                subscriber=request.user,
                subscribe_target=sub_user
            ).delete()
            return Response(
                status=status.HTTP_204_NO_CONTENT
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )
