from django_filters.rest_framework import (AllValuesMultipleFilter, Filter,
                                           FilterSet)

from .models import Recipe


class RecipeFilter(FilterSet):
    """Фильтрует запросы к рецептам по тэгам, корзине покупок, избранному."""

    tags = AllValuesMultipleFilter(field_name='tags__slug', conjoined=True)
    is_in_shopping_cart = Filter(method='filter_shopping_cart')
    is_favorited = Filter(method='filter_is_favorited')

    class Meta:
        model = Recipe
        fields = ['author', 'tags', 'is_in_shopping_cart', 'is_favorited']

    def filter_shopping_cart(self, queryset, name, value):
        user = self.request.user
        if user.is_authenticated:
            recipes_in_shop_cart = user.user_shopping_cart_recipes.all()
            for user_recipe_in_shop_cart in recipes_in_shop_cart:
                queryset = queryset.filter(
                    id=user_recipe_in_shop_cart.recipe.id
                )
        return queryset

    def filter_is_favorited(self, queryset, name, value):
        user = self.request.user
        if user.is_authenticated:
            favorite_recipes = user.user_favorite_recipes.all()
            for user_favorite_recipe in favorite_recipes:
                queryset = queryset.filter(
                    id=user_favorite_recipe.recipe.id
                )
        return queryset
