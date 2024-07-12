from django.urls import include, path
from rest_framework.routers import DefaultRouter as Router

from .views import UserViewSet


app_name = 'users'

router = Router()
router.register(r'users', UserViewSet, basename='users')

urlpatterns = [
    path('', include(router.urls)),
]
