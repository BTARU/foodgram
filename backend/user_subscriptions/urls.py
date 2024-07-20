"""Добавляет маршруты для пользователей и подписок."""

from django.urls import include, path
from rest_framework.routers import SimpleRouter as Router

from .views import UserSubscriptionViewSet


app_name = 'user_subscriptions'

router = Router()
router.register(r'users', UserSubscriptionViewSet, basename='users')

urlpatterns = [
    path('', include(router.urls)),
]
