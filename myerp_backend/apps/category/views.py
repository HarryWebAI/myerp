from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from apps.staff.permissions import IsBoss

from .models import Category
from .serializers import CategorySerializer


class CategoryModelViewSet(viewsets.mixins.CreateModelMixin,
                           viewsets.mixins.UpdateModelMixin,
                           viewsets.mixins.ListModelMixin,
                           viewsets.GenericViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

    def get_permissions(self):
        if self.action == 'list':
            permission_classes = [IsAuthenticated]
        else:
            permission_classes = [IsAuthenticated, IsBoss]
        return [permission() for permission in permission_classes]
