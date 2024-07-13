from django.contrib import admin

from .models import UserRecipeShoppingCart

admin.site.empty_value_display = 'Не задано'


@admin.register(UserRecipeShoppingCart)
class UserRecipeShoppingCartAdmin(admin.ModelAdmin):
    list_display = (
        'user',
        'recipe'
    )
    list_display_links = (
        'user',
        'recipe',
    )
    search_fields = (
        'user',
    )
