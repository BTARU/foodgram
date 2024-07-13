"""Добавляет маршруты для рецептов."""

from django.urls import include, path
from rest_framework.routers import DefaultRouter as Router

from .views import RecipeViewSet


app_name = 'recipes'

router = Router()
router.register(r'recipes', RecipeViewSet, basename='recipes')

urlpatterns = [
    path('', include(router.urls)),
]
