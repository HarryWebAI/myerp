from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from .models import Brand
from .serializers import BrandSerializer
from apps.staff.permissions import IsBoss

class BrandModelViewSet(viewsets.mixins.CreateModelMixin,
                        viewsets.mixins.UpdateModelMixin,
                        viewsets.mixins.ListModelMixin,
                        viewsets.GenericViewSet):
    """
    品牌模型视图集
    """
    queryset = Brand.objects.all()
    serializer_class = BrandSerializer
    permission_classes = [IsAuthenticated, IsBoss]
