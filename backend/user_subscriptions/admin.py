from django.contrib import admin

from .models import Subscription

admin.site.empty_value_display = 'Не задано'


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
