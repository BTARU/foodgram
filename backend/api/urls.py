"""Api app urls."""

from django.urls import include, path
from rest_framework.routers import DefaultRouter
# from rest_framework.authtoken import views

from .views import UserViewSet

app_name = 'api'
router = DefaultRouter()
router.register(r'users', UserViewSet, basename='users')

urlpatterns = [
    # path('', include('djoser.urls')),
    # path('auth/', views.obtain_auth_token),
    path('auth/', include('djoser.urls.authtoken')),
    path('', include(router.urls)),
]
