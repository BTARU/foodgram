from django.apps import AppConfig


class ShoppingcartRecipesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'shoppingcart_recipes'
    verbose_name = 'Рецепты пользователя в корзине'
    verbose_name_plural = 'Рецепты пользователя в корзине'
