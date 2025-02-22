from rest_framework import viewsets
from rest_framework.permissions import AllowAny

from .models import Tag
from .serializers import TagSerializer


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (AllowAny,)
    pagination_class = None
