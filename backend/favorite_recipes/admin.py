from django.contrib import admin

from .models import UserFavoriteRecipes

admin.site.empty_value_display = 'Не задано'


@admin.register(UserFavoriteRecipes)
class UserFavoriteRecipesAdmin(admin.ModelAdmin):
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
