from django_filters.rest_framework import (
    DjangoFilterBackend, FilterSet, CharFilter
)
from rest_framework import viewsets
from rest_framework.permissions import AllowAny


from .models import Ingredient
from .serializers import IngredientSerializer


class IngredientFilter(FilterSet):
    name = CharFilter(max_length=128)

    class Meta:
        model = Ingredient
        fields = ['name']


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (AllowAny,)
    pagination_class = None
    filter_backends = (DjangoFilterBackend,)
    # filterset_fields = ('name',)
    filterset_class = IngredientFilter
