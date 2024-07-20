"""Добавляет маршруты для рецептов и избранных рецептов."""

from django.urls import include, path
from rest_framework.routers import SimpleRouter as Router

from .views import FavoriteRecipeViewSet


app_name = 'favorite_recipes'

router = Router()
router.register(r'recipes', FavoriteRecipeViewSet, basename='recipes')

urlpatterns = [
    path('', include(router.urls)),
]
