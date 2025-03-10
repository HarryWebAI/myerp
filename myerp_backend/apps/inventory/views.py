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


class PurchaseDetailUpdateView(APIView):
    """
    采购明细修正接口
    """
    permission_classes = [IsAuthenticated]

    @transaction.atomic
    def put(self, request, id):
        try:
            # 1. 获取并验证输入数据
            new_quantity = request.data.get('quantity')
            if new_quantity is None:
                return Response({'detail': '必须提供新数量'}, status=status.HTTP_400_BAD_REQUEST)
            
            try:
                new_quantity = int(new_quantity)
                if new_quantity < 0:
                    raise ValueError
            except (ValueError, TypeError):
                return Response({'detail': '数量必须为正整数'}, status=status.HTTP_400_BAD_REQUEST)
            
            # 2. 锁定并获取采购明细
            detail = models.PurchaseDetail.objects.select_for_update().get(id=id)
            old_quantity = detail.quantity
            diff = new_quantity - old_quantity
            
            if diff == 0:
                return Response({'detail': '数量未变更'}, status=status.HTTP_400_BAD_REQUEST)
            
            # 3. 获取关联的库存和采购单
            inventory = models.Inventory.objects.select_for_update().get(id=detail.inventory.id)
            purchase = models.Purchase.objects.select_for_update().get(id=detail.purchase.id)
            
            # 4. 检查是否已有收货记录
            # 获取该库存项关联的收货记录
            related_receives = models.ReceiveDetail.objects.filter(
                inventory=inventory,
                receive__create_time__gt=purchase.create_time
            ).aggregate(Sum('quantity'))['quantity__sum'] or 0
            
            # 如果减少数量，确保不会小于已收货数量
            if diff < 0 and (inventory.on_road + diff) < 0:
                return Response({
                    'detail': f'修改失败！该库存项在途数量不足以减少{-diff}个单位'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # 5. 更新库存
            inventory.on_road = F('on_road') + diff
            inventory.save(update_fields=['on_road'])
            inventory.refresh_from_db()  # 刷新获取最新值
            
            # 6. 更新采购明细
            detail.quantity = new_quantity
            detail.save(update_fields=['quantity'])
            
            # 7. 更新采购单总成本
            cost_diff = diff * inventory.cost
            purchase.total_cost = F('total_cost') + cost_diff
            purchase.save(update_fields=['total_cost'])
            
            # 8. 可选：记录修改历史
            # 如果有PurchaseModificationLog模型，可以在这里创建记录
            
            return Response({
                'detail': '采购明细更新成功',
                'old_quantity': old_quantity,
                'new_quantity': new_quantity,
                'diff': diff,
                'cost_diff': str(cost_diff)
            })
            
        except models.PurchaseDetail.DoesNotExist:
            return Response({'detail': '找不到指定的采购明细'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'detail': f'更新失败：{str(e)}'}, status=status.HTTP_400_BAD_REQUEST)


class ReceiveDetailUpdateView(APIView):
    """
    收货明细修正接口
    """
    permission_classes = [IsAuthenticated]

    @transaction.atomic
    def put(self, request, id):
        try:
            # 1. 获取并验证输入数据
            new_quantity = request.data.get('quantity')
            if new_quantity is None:
                return Response({'detail': '必须提供新数量'}, status=status.HTTP_400_BAD_REQUEST)
            
            try:
                new_quantity = int(new_quantity)
                if new_quantity < 0:
                    raise ValueError
            except (ValueError, TypeError):
                return Response({'detail': '数量必须为正整数'}, status=status.HTTP_400_BAD_REQUEST)
            
            # 2. 锁定并获取收货明细
            detail = models.ReceiveDetail.objects.select_for_update().get(id=id)
            old_quantity = detail.quantity
            diff = new_quantity - old_quantity
            
            if diff == 0:
                return Response({'detail': '数量未变更'}, status=status.HTTP_400_BAD_REQUEST)
            
            # 3. 获取关联的库存
            inventory = models.Inventory.objects.select_for_update().get(id=detail.inventory.id)

            
            # 4. 更新库存
            inventory.in_stock = F('in_stock') + diff
            # 同时需要更新on_road（在途数量会相应减少）
            if inventory.on_road >= diff:
                inventory.on_road = F('on_road') - diff
            inventory.save(update_fields=['in_stock', 'on_road'])
            inventory.refresh_from_db()  # 刷新获取最新值
            
            # 5. 更新收货明细
            detail.quantity = new_quantity
            detail.save(update_fields=['quantity'])
            
            # 6. 可选：记录修改历史
            # 如果有ReceiveModificationLog模型，可以在这里创建记录
            
            return Response({
                'detail': '收货明细更新成功',
                'old_quantity': old_quantity,
                'new_quantity': new_quantity,
                'diff': diff,
                'current_in_stock': inventory.in_stock,
                'current_on_road': inventory.on_road
            })
            
        except models.ReceiveDetail.DoesNotExist:
            return Response({'detail': '找不到指定的收货明细'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'detail': f'更新失败：{str(e)}'}, status=status.HTTP_400_BAD_REQUEST)


class PurchaseDetailDeleteView(APIView):
    """
    删除采购明细接口
    """
    permission_classes = [IsAuthenticated]

    @transaction.atomic
    def delete(self, request, id):
        try:
            # 1. 锁定并获取采购明细
            detail = models.PurchaseDetail.objects.select_for_update().get(id=id)
            
            # 2. 锁定并获取相关的库存和采购单
            inventory = models.Inventory.objects.select_for_update().get(id=detail.inventory.id)
            purchase = models.Purchase.objects.select_for_update().get(id=detail.purchase.id)
            
            # 3. 检查是否已有收货记录
            related_receives = models.ReceiveDetail.objects.filter(
                inventory=inventory,
                receive__create_time__gt=purchase.create_time
            ).aggregate(Sum('quantity'))['quantity__sum'] or 0
            
            # 如果已有收货记录，不允许删除
            if related_receives > 0:
                return Response({
                    'detail': '该采购明细已有收货记录，无法删除'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # 4. 更新库存（减少在途数量）
            if inventory.on_road < detail.quantity:
                return Response({
                    'detail': f'库存在途数量异常，当前在途数量{inventory.on_road}小于待删除数量{detail.quantity}'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            inventory.on_road = F('on_road') - detail.quantity
            inventory.save(update_fields=['on_road'])
            
            # 5. 更新采购单总成本
            cost_reduction = detail.quantity * inventory.cost
            purchase.total_cost = F('total_cost') - cost_reduction
            purchase.save(update_fields=['total_cost'])
            
            # 6. 删除采购明细
            detail.delete()
            
            # 7. 如果这是采购单的最后一个明细，删除采购单
            order_deleted = False  # 初始化变量
            if not models.PurchaseDetail.objects.filter(purchase=purchase).exists():
                purchase.delete()
                order_deleted = True
            
            return Response({
                'detail': '采购明细删除成功',
                'deleted_quantity': detail.quantity,
                'cost_reduction': str(cost_reduction),
                'order_deleted': order_deleted
            })
            
        except models.PurchaseDetail.DoesNotExist:
            return Response({'detail': '找不到指定的采购明细'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'detail': f'删除失败：{str(e)}'}, status=status.HTTP_400_BAD_REQUEST)


class ReceiveDetailDeleteView(APIView):
    """
    删除收货明细接口
    """
    permission_classes = [IsAuthenticated]

    @transaction.atomic
    def delete(self, request, id):
        try:
            # 1. 锁定并获取收货明细
            detail = models.ReceiveDetail.objects.select_for_update().get(id=id)
            
            # 2. 锁定并获取相关的库存和收货单
            inventory = models.Inventory.objects.select_for_update().get(id=detail.inventory.id)
            receive = models.Receive.objects.select_for_update().get(id=detail.receive.id)
            
            # 3. 检查库存是否足够（已入库数量必须大于等于已售出数量）
            if (inventory.in_stock - detail.quantity) < inventory.sold:
                return Response({
                    'detail': f'库存不足，当前库存{inventory.in_stock}，已售出{inventory.sold}，无法删除{detail.quantity}个单位'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # 4. 更新库存（减少实际库存，增加在途数量）
            inventory.in_stock = F('in_stock') - detail.quantity
            inventory.on_road = F('on_road') + detail.quantity
            inventory.save(update_fields=['in_stock', 'on_road'])
            
            # 5. 删除收货明细
            detail.delete()
            
            # 6. 如果这是收货单的最后一个明细，删除收货单
            order_deleted = False  # 初始化变量
            if not models.ReceiveDetail.objects.filter(receive=receive).exists():
                receive.delete()
                order_deleted = True
            
            return Response({
                'detail': '收货明细删除成功',
                'deleted_quantity': detail.quantity,
                'order_deleted': order_deleted
            })
            
        except models.ReceiveDetail.DoesNotExist:
            return Response({'detail': '找不到指定的收货明细'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'detail': f'删除失败：{str(e)}'}, status=status.HTTP_400_BAD_REQUEST)
