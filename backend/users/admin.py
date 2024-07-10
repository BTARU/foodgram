from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import CustomUser, Subscription

admin.site.empty_value_display = 'Не задано'


@admin.register(CustomUser)
class UserAdmin(BaseUserAdmin):
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
