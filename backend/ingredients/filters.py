from django_filters.rest_framework import Filter, FilterSet

from .models import Ingredient


class IngredientFilter(FilterSet):
    """Фильтрация по вхождению в название ингредиента."""

    name = Filter(method='filter_name')

    class Meta:
        model = Ingredient
        fields = ['name']

    def filter_name(self, queryset, name, value):
        return queryset.filter(name__contains=value)
