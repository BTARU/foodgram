from django.contrib.auth import get_user_model
from rest_framework import serializers

from .models import Subscription
from recipes.models import Recipe
from recipes.serializers import RecipeShortInfoSerializer

User = get_user_model()


class UserSubscriptionActionSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField()

    class Meta:
        model = User
        fields = (
            'id',
        )

    def validate_id(self, value):
        is_subscribed = Subscription.objects.filter(
            subscriber=self.context['request'].user,
            subscribe_target=value
        ).exists()
        if self.context['request'].method == 'POST':
            if self.context['request'].user.id == value:
                raise serializers.ValidationError(
                    'Нельзя подписаться на себя.'
                )
            if is_subscribed:
                raise serializers.ValidationError(
                    'Вы уже подписаны на этого пользователя.'
                )

        if self.context['request'].method == 'DELETE':
            if not is_subscribed:
                raise serializers.ValidationError(
                    'Нет подписки на этого пользователя.'
                )
        return value

    def to_representation(self, instance):
        serializer = UserSubscriptionSerializer(
            instance,
            context={'request': self.context['request']}
        )
        return serializer.data


class UserSubscriptionSerializer(serializers.ModelSerializer):
    recipes_count = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()
    is_subscribed = serializers.BooleanField(default=True)

    class Meta:
        model = User
        fields = (
            'id',
            'username',
            'first_name',
            'last_name',
            'email',
            'is_subscribed',
            'avatar',
            'recipes',
            'recipes_count'
        )

    def get_recipes_count(self, obj):
        return Recipe.objects.filter(author=obj).count()

    def get_recipes(self, obj):
        recipes_limit = self.context['request'].query_params.get(
            'recipes_limit'
        )
        queryset = Recipe.objects.filter(author=obj)
        if recipes_limit:
            queryset = queryset[:int(recipes_limit)]
        serializer = RecipeShortInfoSerializer(
            queryset,
            context={'request': self.context['request']},
            many=True
        )
        return serializer.data
