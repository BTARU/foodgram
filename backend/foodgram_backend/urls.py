"""Основные пути маршрутизации проекта."""

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path


urlpatterns = [
    path('admin/', admin.site.urls),

    path('s/', include('urlshortner.urls')),

    path('api/auth/', include('djoser.urls.authtoken')),

    path('api/', include('tags.urls')),
    path('api/', include('ingredients.urls')),
    path('api/', include('shoppingcart_recipes.urls')),
    path('api/', include('user_subscriptions.urls')),
]

if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL, document_root=settings.MEDIA_ROOT
    )
