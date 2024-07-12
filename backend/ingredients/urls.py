from django.urls import include, path
from rest_framework.routers import DefaultRouter as Router

from .views import IngredientViewSet


app_name = 'ingredients'

router = Router()
router.register(r'ingredients', IngredientViewSet, basename='ingredients')

urlpatterns = [
    path('', include(router.urls)),
]
