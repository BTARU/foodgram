from django.urls import include, path
from rest_framework.routers import DefaultRouter as Router

from .views import UserSubscriptionViewSet


app_name = 'subscriptions'

router = Router()
router.register(r'users', UserSubscriptionViewSet, basename='users')

urlpatterns = [
    path('', include(router.urls)),
]
