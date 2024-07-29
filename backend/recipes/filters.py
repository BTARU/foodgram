from django_filters.rest_framework import (AllValuesMultipleFilter, Filter,
                                           FilterSet)

from .models import Recipe


class RecipeFilter(FilterSet):
    """Фильтрует запросы к рецептам по тэгам, корзине покупок, избранному."""

    tags = AllValuesMultipleFilter(field_name='tags__slug', conjoined=False)
    is_in_shopping_cart = Filter(method='filter_shopping_cart')
    is_favorited = Filter(method='filter_is_favorited')

    class Meta:
        model = Recipe
        fields = ['author', 'tags', 'is_in_shopping_cart', 'is_favorited']

    def filter_shopping_cart(self, queryset, name, value):
        user = self.request.user
        if user.is_authenticated and value == '1':
            recipes_in_shop_cart = user.user_shopping_cart_recipes.values_list(
                'recipe__id',
                flat=True
            )
            return queryset.filter(id__in=recipes_in_shop_cart)
        return queryset

    def filter_is_favorited(self, queryset, name, value):
        user = self.request.user
        if user.is_authenticated and value == '1':
            favorite_recipes = user.user_favorite_recipes.values_list(
                'recipe__id',
                flat=True
            )
            return queryset.filter(id__in=favorite_recipes)
        return queryset
