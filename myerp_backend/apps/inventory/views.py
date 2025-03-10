from django.db import transaction
from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from django.db.models import F, Sum, ExpressionWrapper, DecimalField
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

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        total_cost = queryset.annotate(
            current_inventory=F('on_road') + F('in_stock')
        ).aggregate(
            total=Sum(
                ExpressionWrapper(
                    F('current_inventory') * F('cost'),
                    output_field=DecimalField(max_digits=20, decimal_places=2)
                )
            )
        )['total'] or 0

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            response = self.get_paginated_response(serializer.data)
            # 4. 将总成本添加到响应中
            response.data['total_cost'] = str(total_cost)
            return response

        # 无分页时的响应
        serializer = self.get_serializer(queryset, many=True)

        return Response({'data': serializer.data, 'total_cost': total_cost})


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
    """
    发货接口
    """
    permission_classes = [IsAuthenticated]

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


class PurchaseList(APIView):
    """
    发货列表（支持分页查询）
    """
    permission_classes = [IsAuthenticated]
    pagination_class = paginations.PurchasePagination

    def get_queryset(self):
        return models.Purchase.objects.select_related('brand', 'user').order_by('-create_time', '-id').all()

    def get(self, request):
        # 获取分页器实例
        paginator = self.pagination_class()

        # 获取查询集
        queryset = self.get_queryset()

        # 分页处理
        page = paginator.paginate_queryset(queryset, request, view=self)

        # 序列化数据
        serializer = serializers.PurchaseListSerializer(page, many=True)

        # 返回分页响应
        return paginator.get_paginated_response(serializer.data)


class PurchaseDetailView(APIView):
    """
    发货详情
    """
    def get(self, request, id):
        try:
            # 添加类型校验
            if not str(id).isdigit():
                raise ValueError("ID必须为数字")

            queryset = models.PurchaseDetail.objects.filter(purchase__id=id).select_related('inventory')

            if not queryset.exists():
                return Response(
                    {"detail": "未找到指定的采购详情"},
                    status=status.HTTP_404_NOT_FOUND
                )

            serializer = serializers.PurchaseDetailSerializer(queryset, many=True)
            return Response(serializer.data)

        except ValueError as e:
            return Response({"detail": str(e)},status=status.HTTP_400_BAD_REQUEST)


class ReceiveView(APIView):
    """
    入库接口
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = serializers.ReceiveSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({'detail': '错误, 数据不合规!'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            with transaction.atomic():

                receive = models.Receive.objects.create(
                    brand_id=serializer.validated_data['brand_id'],
                    user=request.user
                )

                # 批量处理入库详情
                details = []
                for detail in serializer.validated_data['details']:
                    inventory = models.Inventory.objects.select_for_update().get(id=detail['inventory_id'])

                    if inventory.brand != receive.brand:
                        raise Exception('错误!单次入库必须同一品牌!')

                    # 原子更新库存：减少on_road，增加in_stock
                    inventory.on_road = F('on_road') - detail['quantity']
                    inventory.in_stock = F('in_stock') + detail['quantity']
                    inventory.save(update_fields=['on_road', 'in_stock'])

                    # 构建入库明细对象
                    details.append(models.ReceiveDetail(
                        receive=receive,
                        inventory=inventory,
                        quantity=detail['quantity']
                    ))

                # 批量创建入库明细
                models.ReceiveDetail.objects.bulk_create(details)

            return Response({'receive_id': receive.id, 'message': "入库成功!"}, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({'detail': f'入库失败! {str(e)}'}, status=status.HTTP_400_BAD_REQUEST)


class ReceiveList(APIView):
    """
    收货列表（支持分页查询）
    """
    permission_classes = [IsAuthenticated]
    pagination_class = paginations.PurchasePagination  # 可以复用或创建专用的分页器

    def get_queryset(self):
        return models.Receive.objects.select_related('brand', 'user').order_by('-create_time', '-id').all()

    def get(self, request):
        # 获取分页器实例
        paginator = self.pagination_class()

        # 获取查询集
        queryset = self.get_queryset()

        # 分页处理
        page = paginator.paginate_queryset(queryset, request, view=self)

        # 序列化数据
        serializer = serializers.ReceiveListSerializer(page, many=True)

        # 返回分页响应
        return paginator.get_paginated_response(serializer.data)


class ReceiveDetailView(APIView):
    """
    收货详情
    """
    def get(self, request, id):
        try:
            # 添加类型校验
            if not str(id).isdigit():
                raise ValueError("ID必须为数字")

            queryset = models.ReceiveDetail.objects.filter(receive__id=id).select_related('inventory')

            if not queryset.exists():
                return Response(
                    {"detail": "未找到指定的收货详情"},
                    status=status.HTTP_404_NOT_FOUND
                )

            serializer = serializers.ReceiveDetailSerializer(queryset, many=True)
            return Response(serializer.data)

        except ValueError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
