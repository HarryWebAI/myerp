from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from .models import Category
from .serializers import CategorySerializer


class CategoryModelViewSet(viewsets.mixins.CreateModelMixin,
                           viewsets.mixins.UpdateModelMixin,
                           viewsets.mixins.ListModelMixin,
                           viewsets.GenericViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticated]
