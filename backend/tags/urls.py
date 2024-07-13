"""Добавляет маршруты для тэгов."""

from django.urls import include, path
from rest_framework.routers import DefaultRouter as Router

from .views import TagViewSet


app_name = 'tags'

router = Router()
router.register(r'tags', TagViewSet, basename='tags')

urlpatterns = [
    path('', include(router.urls)),
]
