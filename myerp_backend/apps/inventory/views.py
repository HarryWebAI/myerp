from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from . import models, serializers, paginations


class InventoryViewSet(viewsets.GenericViewSet,
                       viewsets.mixins.CreateModelMixin,
                       viewsets.mixins.UpdateModelMixin,
                       viewsets.mixins.ListModelMixin
                       ):
    queryset = models.Inventory.objects.order_by('-id').all()
    serializer_class = serializers.InventorySerializer
    permission_classes = [IsAuthenticated]
    pagination_class = paginations.InventoryPagination

    def get_queryset(self):
        queryset = self.queryset
        request = self.request
        # 如果请求路由中有参数, 再进行筛选
        if request.query_params:
            brand_id = request.query_params.get('brand_id')
            category_id = request.query_params.get('category_id')
            name = request.query_params.get('name')

            if int(brand_id) > 0:
                queryset = queryset.filter(brand_id=brand_id)
            if int(category_id) > 0:
                queryset = queryset.filter(category_id=category_id)
            if str(name) != '':
                queryset = queryset.filter(name__contains=name)

        return queryset.order_by('-id').all()
