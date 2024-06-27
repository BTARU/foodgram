"""Admin panel settings for users app."""
from django.contrib import admin

from .models import CustomUser, Subscription

admin.site.empty_value_display = 'Not set'


@admin.register(CustomUser)
class UserAdmin(admin.ModelAdmin):
    list_display = (
        'email',
        'first_name',
        'last_name'
    )
    search_fields = (
        'email',
        'first_name'
    )


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = (
        'subscriber',
        'subscribe_target'
    )
    list_display_links = (
        'subscriber',
        'subscribe_target'
    )
    search_fields = (
        'subscriber',
    )
