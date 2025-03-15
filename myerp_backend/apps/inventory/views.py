from django.db import transaction
from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from django.db.models import F, Sum, ExpressionWrapper, DecimalField
from . import models, serializers, paginations
import pandas as pd
from django.http import HttpResponse
from datetime import datetime
import os  # 添加os模块用于文件扩展名验证
from rest_framework.parsers import MultiPartParser  # 添加文件上传解析器
from apps.order.models import OperationLog
from django.db.models import Prefetch
from apps.staff.permissions import IsStorekeeper,IsBoss

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
    permission_classes = [IsAuthenticated,IsBoss]
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
    permission_classes = [IsAuthenticated,IsBoss|IsStorekeeper]

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
    permission_classes = [IsAuthenticated,IsBoss]

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

                # 创建采购日志，记录详细的采购信息
                log_content = f"用户{request.user.name}于{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}进行了采购操作\n"
                log_content += "采购明细：\n"
                for detail in details:
                    log_content += f"- {detail.inventory.full_name()}：{detail.quantity}个，单价：{detail.inventory.cost}元\n"
                log_content += f"总成本：{serializer.validated_data['total_cost']}元"

                models.PurchaseLog.objects.create(
                    purchase=purchase,
                    content=log_content,
                    operator=request.user
                )

            return Response({'purchase_id': purchase.id, 'message': "发货成功!"}, status=status.HTTP_201_CREATED)
        except:
            return Response({'detail': '发货失败!'}, status=status.HTTP_400_BAD_REQUEST)

class PurchaseList(APIView):
    """
    发货列表（支持分页查询）
    """
    permission_classes = [IsAuthenticated,IsBoss]
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
    permission_classes = [IsAuthenticated,IsBoss]
    def get(self, request, id):
        try:
            # 添加类型校验
            if not str(id).isdigit():
                raise ValueError("ID必须为数字")

            # 获取采购单及其关联数据
            purchase = models.Purchase.objects.select_related(
                'brand', 
                'user'
            ).prefetch_related(
                'details__inventory',
                Prefetch('logs', queryset=models.PurchaseLog.objects.order_by('-create_time'), to_attr='ordered_logs')
            ).get(id=id)

            serializer = serializers.PurchaseDetailFullSerializer(purchase)
            return Response(serializer.data)

        except models.Purchase.DoesNotExist:
            return Response(
                {"detail": "未找到指定的采购单"},
                status=status.HTTP_404_NOT_FOUND
            )
        except ValueError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"detail": f"获取详情失败：{str(e)}"}, status=status.HTTP_400_BAD_REQUEST)

class ReceiveView(APIView):
    """
    入库接口
    """
    permission_classes = [IsAuthenticated,IsBoss|IsStorekeeper]

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

                # 创建入库日志，记录详细的入库信息
                log_content = f"用户{request.user.name}于{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}进行了入库操作\n"
                log_content += "入库明细：\n"
                for detail in details:
                    log_content += f"- {detail.inventory.full_name()}：{detail.quantity}个\n"

                models.ReceiveLog.objects.create(
                    receive=receive,
                    content=log_content,
                    operator=request.user
                )

            return Response({'receive_id': receive.id, 'message': "入库成功!"}, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({'detail': f'入库失败! {str(e)}'}, status=status.HTTP_400_BAD_REQUEST)

class ReceiveList(APIView):
    """
    收货列表（支持分页查询）
    """
    permission_classes = [IsAuthenticated,IsBoss|IsStorekeeper]
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
    permission_classes = [IsAuthenticated,IsBoss|IsStorekeeper]
    def get(self, request, id):
        try:
            # 添加类型校验
            if not str(id).isdigit():
                raise ValueError("ID必须为数字")

            # 获取收货单及其关联数据
            receive = models.Receive.objects.select_related(
                'brand', 
                'user'
            ).prefetch_related(
                'details__inventory',
                Prefetch('logs', queryset=models.ReceiveLog.objects.order_by('-create_time'), to_attr='ordered_logs')
            ).get(id=id)

            serializer = serializers.ReceiveDetailFullSerializer(receive)
            return Response(serializer.data)

        except models.Receive.DoesNotExist:
            return Response(
                {"detail": "未找到指定的收货单"},
                status=status.HTTP_404_NOT_FOUND
            )
        except ValueError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"detail": f"获取详情失败：{str(e)}"}, status=status.HTTP_400_BAD_REQUEST)

class PurchaseDetailUpdateView(APIView):
    """
    采购明细修正接口
    """
    permission_classes = [IsAuthenticated,IsBoss]

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
            
            # 8. 创建采购修正日志
            log_content = f"用户{request.user.name}于{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}进行了采购明细修正操作\n"
            log_content += f"商品：{inventory.full_name()}\n"
            log_content += f"原数量：{old_quantity}个\n"
            log_content += f"新数量：{new_quantity}个\n"
            log_content += f"变化：{diff}个\n"
            log_content += f"成本变化：{cost_diff}元"

            models.PurchaseLog.objects.create(
                purchase=purchase,
                content=log_content,
                operator=request.user
            )
            
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
    permission_classes = [IsAuthenticated,IsBoss|IsStorekeeper]

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
            
            # 6. 创建收货修正日志
            log_content = f"用户{request.user.name}于{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}进行了收货明细修正操作\n"
            log_content += f"商品：{inventory.full_name()}\n"
            log_content += f"原数量：{old_quantity}个\n"
            log_content += f"新数量：{new_quantity}个\n"
            log_content += f"变化：{diff}个\n"
            log_content += f"当前在库：{inventory.in_stock}个\n"
            log_content += f"当前在途：{inventory.on_road}个"

            models.ReceiveLog.objects.create(
                receive=detail.receive,
                content=log_content,
                operator=request.user
            )
            
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
    permission_classes = [IsAuthenticated,IsBoss]

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
            
            # 7. 采购日志记录采购单作废
            log_content = f"用户{request.user.name}于{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}删除了采购明细\n"
            log_content += f"商品：{inventory.full_name()}\n"
            log_content += f"删除数量：{detail.quantity}个\n"
            log_content += f"成本减少：{cost_reduction}元"
            order_deleted = False  # 初始化变量
            if not models.PurchaseDetail.objects.filter(purchase=purchase).exists():
                order_deleted = True
            models.PurchaseLog.objects.create(
                purchase=purchase,
                content=log_content,
                operator=request.user
            )
            
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
    permission_classes = [IsAuthenticated,IsBoss]

    @transaction.atomic
    def delete(self, request, id):
        try:
            # 1. 锁定并获取收货明细
            detail = models.ReceiveDetail.objects.select_for_update().get(id=id)
            
            # 2. 锁定并获取相关的库存和收货单
            inventory = models.Inventory.objects.select_for_update().get(id=detail.inventory.id)
            receive = models.Receive.objects.select_for_update().get(id=detail.receive.id)
            
            
            # 3. 更新库存（减少实际库存，增加在途数量）
            inventory.in_stock = F('in_stock') - detail.quantity
            inventory.on_road = F('on_road') + detail.quantity
            inventory.save(update_fields=['in_stock', 'on_road'])
            
            # 4. 删除收货明细
            detail.delete()
            
            # 5. 如果这是收货单的最后一个明细，告诉前端
            order_deleted = False  # 初始化变量
            if not models.ReceiveDetail.objects.filter(receive=receive).exists():
                order_deleted = True
            
            # 6. 创建收货作废日志
            log_content = f"用户{request.user.name}于{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}删除了收货明细\n"
            log_content += f"商品：{inventory.full_name()}\n"
            log_content += f"当前在途：{inventory.on_road}个"
            if order_deleted:
                log_content += "\n该收货单所有明细已删除，收货单作废"

            models.ReceiveLog.objects.create(
                receive=receive,
                content=log_content,
                operator=request.user
            )
            
            return Response({
                'detail': '收货明细删除成功',
                'deleted_quantity': detail.quantity,
                'order_deleted': order_deleted
            })
            
        except models.ReceiveDetail.DoesNotExist:
            return Response({'detail': '找不到指定的收货明细'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'detail': f'删除失败：{str(e)}'}, status=status.HTTP_400_BAD_REQUEST)

class InventoryDownloadView(APIView):
    """
    库存数据下载接口
    """
    permission_classes = [IsAuthenticated,IsBoss]
    def get(self, request):
        # 获取所有库存数据
        queryset = models.Inventory.objects.order_by('-brand__id', '-category__id', '-id').all()
        results = queryset.values('id', 'name', 'brand__name', 'category__name', 'size', 'color', 'cost', 'on_road', 'in_stock', 'been_order', 'sold')

        try: 
            # 如果没有数据，创建一个空的DataFrame但包含所有列
            if not results:
                inventory_df = pd.DataFrame(columns=[
                    'id', 'name', 'brand__name', 'category__name', 'size', 
                    'color', 'cost', 'on_road', 'in_stock', 'been_order', 'sold'
                ])
            else:
                inventory_df = pd.DataFrame(results)

            inventory_df = inventory_df.rename(columns={
                'name': '名称',
                'brand__name': '品牌',
                'category__name': '分类',
                'size': '规格',
                'color': '颜色',
                'cost': '成本',
                'on_road': '物流在途',
                'in_stock': '当前在库',
                'been_order': '已被订购',
                'sold': '已售出'
            })
            
            # 获取日期 yyyy-mm-dd
            date = datetime.now().strftime('%Y-%m-%d')
            response = HttpResponse(content_type='application/xlsx')
            response['Content-Disposition'] = f"attachment; filename=库存列表_{date}.xlsx"
            with pd.ExcelWriter(response) as writer:
                inventory_df.to_excel(writer, sheet_name='库存信息', index=False)
            
            return response
        except Exception as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)

class InventoryUploadView(APIView):
    """
    库存数据上传接口
    """
    permission_classes = [IsAuthenticated,IsBoss]
    parser_classes = [MultiPartParser]  # 添加文件上传解析器
    
    def post(self, request):
        try:
            # 验证当前系统中是否存在未出库的订单
            from apps.order.models import Order
            undelivered_orders = Order.objects.filter(delivery_status=1)  # 1表示新订单
            if undelivered_orders.exists():
                return Response({
                    'detail': '系统中存在未出库的订单，请先完成所有订单出库操作再进行库存盘点',
                    'order_count': undelivered_orders.count(),
                    'order_numbers': list(undelivered_orders.values_list('order_number', flat=True))
                }, status=status.HTTP_400_BAD_REQUEST)

            # 1. 验证文件是否存在
            if 'file' not in request.FILES:
                return Response({'detail': '请上传文件'}, status=status.HTTP_400_BAD_REQUEST)
            
            file = request.FILES['file']
            
            # 2. 验证文件格式
            file_extension = os.path.splitext(file.name)[1].lower()
            if file_extension not in ['.xlsx', '.xls']:
                return Response({'detail': '只支持.xlsx或.xls格式的文件'}, status=status.HTTP_400_BAD_REQUEST)
            
            # 3. 读取Excel文件
            df = pd.read_excel(file)
            
            # 4. 验证必要的列是否存在
            required_columns = ['名称', '品牌', '分类', '规格', '颜色', '成本']
            missing_columns = [col for col in required_columns if col not in df.columns]
            if missing_columns:
                return Response(
                    {'detail': f'缺少必要的列: {", ".join(missing_columns)}'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # 5. 创建空列表用于存储要创建的库存对象
            inventory_objects = []
            
            # 获取所有品牌和分类的集合，用于验证
            existing_brands = set(models.Brand.objects.values_list('name', flat=True))
            existing_categories = set(models.Category.objects.values_list('name', flat=True))
            
            # 获取Excel中的所有品牌和分类
            excel_brands = set(df['品牌'].astype(str).unique())
            excel_categories = set(df['分类'].astype(str).unique())
            
            # 检查是否有不存在的品牌
            invalid_brands = excel_brands - existing_brands
            if invalid_brands:
                return Response({
                    'detail': f'发现未经授权的品牌: {", ".join(invalid_brands)}，请先在系统中创建这些品牌。'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # 检查是否有不存在的分类
            invalid_categories = excel_categories - existing_categories
            if invalid_categories:
                return Response({
                    'detail': f'发现未经授权的分类: {", ".join(invalid_categories)}，请先在系统中创建这些分类。'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # 预先获取所有需要用到的品牌和分类对象
            brands_dict = {brand.name: brand for brand in models.Brand.objects.filter(name__in=excel_brands)}
            categories_dict = {category.name: category for category in models.Category.objects.filter(name__in=excel_categories)}
            
            # 6. 开启事务处理
            with transaction.atomic():
                # 首先清空所有库存记录
                models.Inventory.objects.all().delete()
                
                # 遍历Excel的每一行
                for index, row in df.iterrows():
                    # 从预加载的字典中获取品牌和分类对象
                    brand = brands_dict[str(row['品牌'])]
                    category = categories_dict[str(row['分类'])]
                    
                    # 确保数值字段为正确的类型，处理空值和NaN
                    try:
                        # 处理成本字段
                        cost = row['成本']
                        if pd.isna(cost) or cost == '':
                            return Response({
                                'detail': f'第{index + 1}行成本不能为空'
                            }, status=status.HTTP_400_BAD_REQUEST)
                        cost = float(cost)
                        
                        # 处理其他数值字段，空值或NaN都转为0
                        def safe_convert_to_int(value):
                            if pd.isna(value) or value == '':
                                return 0
                            return int(float(value))
                        
                        # 只统计in_stock库存数量，其他数量都设为0
                        in_stock = safe_convert_to_int(row.get('当前在库', 0))
                        
                        # 验证数值是否为负数
                        if cost < 0 or in_stock < 0:
                            return Response({
                                'detail': f'第{index + 1}行存在负数，所有数值必须大于等于0'
                            }, status=status.HTTP_400_BAD_REQUEST)
                            
                    except (ValueError, TypeError) as e:
                        return Response({
                            'detail': f'第{index + 1}行数据格式错误：{str(e)}，请确保数值字段格式正确'
                        }, status=status.HTTP_400_BAD_REQUEST)
                    
                    # 创建库存对象（但不保存到数据库）
                    inventory = models.Inventory(
                        name=str(row['名称']).upper(),  # 将名称中的英文字母转为大写
                        brand=brand,
                        category=category,
                        size=str(row['规格']),
                        color=str(row['颜色']),
                        cost=cost,
                        on_road=0,  # 物流在途设为0
                        in_stock=in_stock,  # 只保留当前在库数量
                        been_order=0,  # 已被订购设为0
                        sold=0  # 已售出设为0
                    )
                    inventory_objects.append(inventory)
                
                # 7. 批量创建库存记录
                models.Inventory.objects.bulk_create(inventory_objects)

                # 8. 创建库存日志
                log_content = f"{request.user.name}于{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}进行了库存盘点\n"
                log_content += f"成功导入{len(inventory_objects)}条库存记录"
                models.InventoryLog.objects.create(
                    content=log_content,
                    operator=request.user
                )

                # 获取当前时间作为盘点时间点
                current_time = datetime.now()
                inventory_check_message = f"{current_time.strftime('%Y-%m-%d %H:%M:%S')}进行了库存盘点，此次盘点之前的所有数据已失效!"
                
                # 为所有采购记录添加盘点日志
                purchases = models.Purchase.objects.filter(create_time__lt=current_time)
                for purchase in purchases:
                    models.PurchaseLog.objects.create(
                        purchase=purchase,
                        content=inventory_check_message,
                        operator=request.user
                    )
                
                # 为所有收货记录添加盘点日志
                receives = models.Receive.objects.filter(create_time__lt=current_time)
                for receive in receives:
                    models.ReceiveLog.objects.create(
                        receive=receive,
                        content=inventory_check_message,
                        operator=request.user
                    )
                
                # 为订单添加操作日志
                from apps.order.models import Order
                orders = Order.objects.filter(sign_time__lt=current_time)
                for order in orders:
                    OperationLog.objects.create(
                        order=order,
                        description=inventory_check_message,
                        operator=request.user
                    )
                
            return Response({
                'detail': f'成功导入{len(inventory_objects)}条库存记录，所有库存仅保留当前在库数量，其他数量已重置为0',
                'count': len(inventory_objects)
            }, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            return Response({'detail': f'导入失败: {str(e)}'}, status=status.HTTP_400_BAD_REQUEST)

class InventoryLogView(APIView):
    """
    库存日志接口
    """
    permission_classes = [IsAuthenticated,IsBoss]
    
    def get(self, request):
        # 获取所有库存日志
        queryset = models.InventoryLog.objects.order_by('-create_time').all()
        serializer = serializers.InventoryLogSerializer(queryset, many=True)
        return Response(serializer.data)

class PurchaseCostUpdateView(APIView):
    """
    采购成本修正接口
    """
    permission_classes = [IsAuthenticated,IsBoss]
    
    @transaction.atomic
    def put(self, request, id):
        try:
            # 1. 获取并验证输入数据
            new_total_cost = request.data.get('total_cost')
            if new_total_cost is None:
                return Response({'detail': '必须提供新的总成本'}, status=status.HTTP_400_BAD_REQUEST)
            
            try:
                new_total_cost = float(new_total_cost)
                if new_total_cost < 0:
                    raise ValueError
            except (ValueError, TypeError):
                return Response({'detail': '总成本必须为非负数'}, status=status.HTTP_400_BAD_REQUEST)
            
            # 2. 锁定并获取采购单
            purchase = models.Purchase.objects.select_for_update().get(id=id)
            old_total_cost = purchase.total_cost
            
            # 如果成本没有变化，直接返回
            if float(old_total_cost) == new_total_cost:
                return Response({'detail': '总成本未变更'}, status=status.HTTP_400_BAD_REQUEST)
            
            # 3. 检查是否已有收货记录
            has_received = models.ReceiveDetail.objects.filter(
                inventory__in=models.PurchaseDetail.objects.filter(purchase=purchase).values('inventory'),
                receive__create_time__gt=purchase.create_time
            ).exists()
            
            # 如果已有收货记录，提示用户但仍允许修改
            warning_message = ""
            if has_received:
                warning_message = "警告：该采购单已有收货记录，修改成本可能导致数据不一致"
            
            # 4. 更新采购单总成本
            purchase.total_cost = new_total_cost
            purchase.save(update_fields=['total_cost'])
            
            # 5. 创建采购修正日志
            log_content = f"用户{request.user.name}于{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}修改了采购单总成本\n"
            log_content += f"原总成本：{old_total_cost}元\n"
            log_content += f"新总成本：{new_total_cost}元\n"
            log_content += f"变化：{new_total_cost - float(old_total_cost)}元"
            
            models.PurchaseLog.objects.create(
                purchase=purchase,
                content=log_content,
                operator=request.user
            )
            
            response_data = {
                'detail': '采购总成本更新成功',
                'old_total_cost': str(old_total_cost),
                'new_total_cost': str(new_total_cost),
                'diff': str(new_total_cost - float(old_total_cost))
            }
            
            if warning_message:
                response_data['warning'] = warning_message
                
            return Response(response_data)
            
        except models.Purchase.DoesNotExist:
            return Response({'detail': '找不到指定的采购单'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'detail': f'修改失败：{str(e)}'}, status=status.HTTP_400_BAD_REQUEST)


