from rest_framework.viewsets import ModelViewSet
from .models import Brand
from .serializers import BrandSerializer
from rest_framework.permissions import IsAuthenticated

class BrandModelViewSet(ModelViewSet):
    """
    品牌模型视图集
    """
    queryset = Brand.objects.all()
    serializer_class = BrandSerializer
    permission_classes = [IsAuthenticated]

