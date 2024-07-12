from django.contrib import admin

from .models import (IngredientRecipe, Recipe,
                     UserFavoriteRecipes, UserRecipeShoppingCart)

admin.site.empty_value_display = 'Не задано'


class IngredientInline(admin.StackedInline):
    model = IngredientRecipe
    extra = 0
    min_num = 1


# @admin.register(Ingredient)
# class IngredientAdmin(admin.ModelAdmin):
#     list_display = (
#         'name',
#         'measurement_unit'
#     )
#     search_fields = (
#         'name',
#     )


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    inlines = (
        IngredientInline,
    )
    filter_horizontal = ('tags',)
    list_display = (
        'name',
        'author',
        'cooking_time',
        'post_in_favorites_count'
    )
    list_display_links = (
        'name',
        'author',
    )
    list_filter = (
        'tags',
    )
    search_fields = (
        'name',
        'author',
    )

    @admin.display(description='Добавлено в избранное')
    def post_in_favorites_count(self, obj):
        return obj.recipe_favorite.count()


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
