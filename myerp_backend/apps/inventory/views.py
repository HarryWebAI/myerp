from django.db import transaction
from django.db.models import F
from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from . import models, serializers, paginations


class InventoryViewSet(viewsets.GenericViewSet,
                       viewsets.mixins.CreateModelMixin,
                       viewsets.mixins.UpdateModelMixin,
                       viewsets.mixins.ListModelMixin
                       ):
    """
    库存接口(带分页)
    """

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


class AllInventoryViewSet(viewsets.GenericViewSet,
                          viewsets.mixins.ListModelMixin):
    """
    所有库存接口: 用于收发货, 不带分页
    """

    queryset = models.Inventory.objects.order_by('-id').all()
    serializer_class = serializers.InventorySerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = self.queryset
        request = self.request
        brand_id = request.query_params.get('brand_id')

        if int(brand_id) > 0:
            queryset = queryset.filter(brand_id=brand_id)
        else:
            return None

        return queryset.order_by('-id').all()


class PurchaseView(APIView):
    def post(self, request):
        serializer = serializers.PurchaseSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({'detail': '错误, 数据不合规!'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            with transaction.atomic():

                purchase = models.Purchase.objects.create(
                    brand_id=serializer.validated_data['brand_id'],
                    total_cost=serializer.validated_data['total_cost'],
                    user=request.user
                )

                # 批量处理采购详情
                details = []
                for detail in serializer.validated_data['details']:
                    inventory = models.Inventory.objects.select_for_update().get(id=detail['inventory_id'])

                    if inventory.brand != purchase.brand:
                        raise Exception('错误!单次发货必须同一品牌!')

                    # 原子更新在途库存
                    inventory.on_road = F('on_road') + detail['quantity']
                    inventory.save(update_fields=['on_road'])

                    # 构建采购明细对象
                    details.append(models.PurchaseDetail(
                        purchase=purchase,
                        inventory=inventory,
                        quantity=detail['quantity']
                    ))

                # 批量创建采购明细
                models.PurchaseDetail.objects.bulk_create(details)

            return Response({'purchase_id': purchase.id, 'message': "发货成功!"}, status=status.HTTP_201_CREATED)
        except:
            return Response({'detail': '发货失败!'}, status=status.HTTP_400_BAD_REQUEST)
