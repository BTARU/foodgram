from django.contrib.auth import get_user_model
from rest_framework import serializers

from user_subscriptions.models import Subscription
from .serializer_fields import Base64ImageField

User = get_user_model()


class UserAvatarSerializer(serializers.ModelSerializer):
    avatar = Base64ImageField()

    class Meta:
        model = User
        fields = (
            'avatar',
        )


class UserSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'id',
            'username',
            'first_name',
            'last_name',
            'email',
            'is_subscribed',
            'avatar'
        )

    def get_is_subscribed(self, obj):
        return (
            self.context['request'].user.is_authenticated
            and Subscription.objects.filter(
                subscriber=self.context['request'].user,
                subscribe_target=obj
            ).exists()
        )
