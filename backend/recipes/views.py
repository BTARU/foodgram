from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import mixins, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from urlshortner.utils import shorten_url

from .filters import RecipeFilter
from .mixins import PatchModelMixin
from .models import Recipe
from .permissions import IsAuthorOrAdmin
from .serializers import RecipeCreateSerializer, RecipeReadSerializer


class RecipeViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.DestroyModelMixin,
    mixins.RetrieveModelMixin,
    PatchModelMixin,
    viewsets.GenericViewSet
):
    permission_classes = (IsAuthenticatedOrReadOnly, IsAuthorOrAdmin,)
    filter_backends = (DjangoFilterBackend,)
    queryset = Recipe.objects.all()
    filterset_class = RecipeFilter

    def get_serializer_class(self):
        if self.action in ('create', 'partial_update'):
            return RecipeCreateSerializer
        return RecipeReadSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(
        ['get'],
        detail=False,
        url_path=r'(?P<pk>\d+)/get-link'
    )
    def get_link(self, request, pk):
        self.get_object()
        url = f'/recipes/{pk}'
        short_url = shorten_url(url, is_permanent=True)
        host = request.get_host()
        return Response(
            {
                'short-link': f'https://{host}/s/{short_url}'
            }
        )
