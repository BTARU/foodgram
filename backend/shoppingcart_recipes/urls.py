"""Добавляет маршруты для рецептов и добавление в корзину покупок."""

from django.urls import include, path
from rest_framework.routers import DefaultRouter as Router

from .views import RecipeShoppingCartViewSet


app_name = 'shoppingcart_recipes'

router = Router()
router.register(r'recipes', RecipeShoppingCartViewSet, basename='recipes')

urlpatterns = [
    path('', include(router.urls)),
]
