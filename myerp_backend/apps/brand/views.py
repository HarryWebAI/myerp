from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated, AllowAny

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
    
    def get_permissions(self):
        """
        根据不同的操作返回不同的权限
        - list: 允许所有人访问
        - create/update: 需要认证且是Boss权限
        """
        if self.action == 'list':
            permission_classes = [IsAuthenticated]
        else:
            permission_classes = [IsAuthenticated, IsBoss]
        return [permission() for permission in permission_classes]
