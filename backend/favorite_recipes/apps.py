from django.apps import AppConfig


class FavoriteRecipesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'favorite_recipes'
    verbose_name = 'Избранные рецепты пользователя'
    verbose_name_plural = 'Избранные рецепты пользователя'
