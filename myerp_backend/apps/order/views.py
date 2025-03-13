from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, viewsets, filters
from rest_framework.permissions import IsAuthenticated
from django.db import transaction
from django.db.models import F, Q, Sum, Count
from django.db.models.functions import TruncMonth
from decimal import Decimal
import datetime
from apps.staff.permissions import IsBoss,IsManager
from . import serializers
from . import paginations
from .models import Order, OrderDetail, OperationLog, BalancePayment, Installer
from apps.inventory.models import Inventory

class CreateOrderView(APIView):
    """
    新增订单接口
    """
    permission_classes = [IsAuthenticated,IsBoss|IsManager]

    def post(self, request):
        # 获取序列化器实例
        serializer = serializers.OrderCreateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({'detail': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)    

        # 开始修改数据
        try:
            # 开启数据库原子事务
            with transaction.atomic():
                validated_data = serializer.validated_data
                details_data = validated_data['details']  # 不需要pop，直接获取即可
                
                # 计算待收尾款
                pending_balance = validated_data['total_amount'] - validated_data['down_payment']
                
                # 创建订单
                order = Order.objects.create(
                    order_number=validated_data['order_number'],
                    brand_id=validated_data['brand_id'],
                    client_id=validated_data['client_id'],
                    staff_id=validated_data['staff_id'],
                    total_amount=validated_data['total_amount'],
                    down_payment=validated_data['down_payment'],
                    pending_balance=pending_balance,
                    total_cost=validated_data['total_cost'],
                    gross_profit=validated_data['gross_profit'],
                    address=validated_data['address'],
                    remark=validated_data['remark'],
                    # 默认值处理
                    received_balance=0,
                    delivery_status=1,  # 新订单
                    payment_status=2 if pending_balance == 0 else 1,  # 如果待收尾款为0，则设置为已结清
                    installation_fee=0,
                    transportation_fee=0
                )
                
                # 验证成本总价并处理订单明细
                calculated_cost = Decimal('0.00')
                order_details = []
                
                # 批量处理订单详情
                for item in details_data:
                    # 使用select_for_update锁定库存记录，防止并发问题
                    inventory = Inventory.objects.select_for_update().get(id=item['inventory_id'])
                    quantity = item['quantity']
                    
                    # 计算成本 - 确保使用Decimal类型计算
                    item_cost = inventory.cost * Decimal(str(quantity))
                    calculated_cost += item_cost
                    
                    # 原子更新已订购数量
                    inventory.been_order = F('been_order') + quantity
                    inventory.save(update_fields=['been_order'])
                    
                    # 构建订单明细对象
                    order_details.append(OrderDetail(
                        order=order,
                        inventory=inventory,
                        quantity=quantity
                    ))
                
                # 批量创建订单明细
                OrderDetail.objects.bulk_create(order_details)
                
                # 操作日志
                now = datetime.datetime.now()
                timestamp = now.strftime('%Y-%m-%d %H:%M:%S')
                
                # 创建基本操作日志
                log_description = f"于 {timestamp} 创建订单, 订单总额: {order.total_amount}, 成本总价: {order.total_cost}, 初算毛利(未扣安装费和运输费): {order.gross_profit}"
                
                OperationLog.objects.create(
                    order=order,
                    description=log_description,
                    operator=request.user
                )

                # 校对成本总价，如有任何差异则添加警告日志
                user_provided_cost = validated_data['total_cost']
                if calculated_cost != user_provided_cost:
                    cost_difference = abs(calculated_cost - user_provided_cost)
                    warning_log = f"警告! 创建订单时, 您填写的成本总价({user_provided_cost})与系统自动计算的成本总价({calculated_cost})不一致! 差额: {cost_difference}"
                    
                    # 创建额外的警告日志
                    OperationLog.objects.create(
                        order=order,
                        description=warning_log,
                        operator=request.user
                    )
                
                # 校对毛利润, 当提交数据的毛利润为负数时, 写入警告日志
                if order.gross_profit < 0:
                    profit_warning_log = f"警告! 创建订单时, 订单的毛利润为负数({order.gross_profit})! 请确认该订单是否为亏本处理?"
                    
                    # 创建毛利润警告日志
                    OperationLog.objects.create(
                        order=order,
                        description=profit_warning_log,
                        operator=request.user
                    )
                
                # 返回订单ID
            return Response({'order_id': order.id, 'message': "订单创建成功!"}, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({'detail': f'订单创建失败! {str(e)}'}, status=status.HTTP_400_BAD_REQUEST)
        
class OrderViewSet(viewsets.ReadOnlyModelViewSet):
    """
    订单视图集
    """
    queryset = Order.objects.all()
    serializer_class = serializers.OrderSerializer
    permission_classes = [IsAuthenticated,IsBoss|IsManager]
    pagination_class = paginations.OrderPagination
    filter_backends = [filters.SearchFilter]
    search_fields = ['order_number', 'client__name', 'brand__name']
    
    def get_serializer_class(self):
        """根据动作选择序列化器"""
        if self.action == 'list':
            return serializers.OrderListSerializer
        return serializers.OrderSerializer
    
    def get_queryset(self):
        """根据查询参数过滤订单"""
        queryset = super().get_queryset()
        
        # 获取查询参数
        order_number = self.request.query_params.get('order_number')
        brand_id = self.request.query_params.get('brand_id')
        client_uid = self.request.query_params.get('client_uid')
        staff_uid = self.request.query_params.get('staff_uid')
        delivery_status = self.request.query_params.get('delivery_status')
        payment_status = self.request.query_params.get('payment_status')
        date_start = self.request.query_params.get('date_start')
        date_end = self.request.query_params.get('date_end')
        
        # 应用过滤条件（只有当值不是默认值时）
        if order_number and order_number != '':
            queryset = queryset.filter(order_number__icontains=order_number)
        if brand_id and brand_id != '0':
            queryset = queryset.filter(brand_id=brand_id)
        if client_uid and client_uid != '':
            queryset = queryset.filter(client__uid=client_uid)
        if staff_uid and staff_uid != '':
            queryset = queryset.filter(staff__uid=staff_uid)
        if delivery_status and delivery_status != '':
            queryset = queryset.filter(delivery_status=delivery_status)
        if payment_status and payment_status != '':
            queryset = queryset.filter(payment_status=payment_status)
        if date_start and date_start != '':
            queryset = queryset.filter(sign_time__gte=date_start)
        if date_end and date_end != '':
            queryset = queryset.filter(sign_time__lte=date_end)
            
        return queryset
    
    def list(self, request, *args, **kwargs):
        """重写list方法，增加当月总销量、当月总利润和全部待收尾款的统计"""
        # 获取过滤后的查询集
        queryset = self.filter_queryset(self.get_queryset())
        
        # 获取当前年月
        now = datetime.datetime.now()
        current_year = now.year
        current_month = now.month
        
        # 计算当月订单的总销量和总利润
        current_month_orders = Order.objects.filter(
            sign_time__year=current_year,
            sign_time__month=current_month
        )
        
        monthly_total_amount = current_month_orders.aggregate(
            total=Sum('total_amount')
        )['total'] or 0
        
        monthly_total_profit = current_month_orders.aggregate(
            total=Sum('gross_profit')
        )['total'] or 0
        
        # 计算全部待收尾款
        total_pending_balance = Order.objects.filter(
            payment_status=1  # 未结清
        ).aggregate(
            total=Sum('pending_balance')
        )['total'] or 0
        
        # 分页
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            response_data = self.get_paginated_response(serializer.data)
            
            # 添加统计数据到响应中
            response_data.data['monthly_total_amount'] = monthly_total_amount
            response_data.data['monthly_total_profit'] = monthly_total_profit
            response_data.data['total_pending_balance'] = total_pending_balance
            
            return response_data
        
        serializer = self.get_serializer(queryset, many=True)
        response_data = {
            'results': serializer.data,
            'monthly_total_amount': monthly_total_amount,
            'monthly_total_profit': monthly_total_profit,
            'total_pending_balance': total_pending_balance
        }
        
        return Response(response_data)

class OrderDetailViewSet(viewsets.ReadOnlyModelViewSet):
    """
    订单详情视图集
    """
    queryset = OrderDetail.objects.all()
    serializer_class = serializers.OrderDetailSerializer
    permission_classes = [IsAuthenticated,IsBoss|IsManager]
    pagination_class = paginations.OrderDetailPagination
    
    def get_queryset(self):
        """根据订单ID过滤详情"""
        queryset = super().get_queryset()
        order_id = self.request.query_params.get('order_id')
        if order_id:
            queryset = queryset.filter(order_id=order_id)
        return queryset

class OperationLogViewSet(viewsets.ReadOnlyModelViewSet):
    """
    操作日志视图集
    """
    queryset = OperationLog.objects.all().order_by('-created_at')
    serializer_class = serializers.OperationLogSerializer
    permission_classes = [IsAuthenticated,IsBoss|IsManager]
    pagination_class = paginations.OperationLogPagination
    
    def get_queryset(self):
        """根据订单ID过滤日志"""
        queryset = super().get_queryset()
        order_id = self.request.query_params.get('order_id')
        if order_id:
            queryset = queryset.filter(order_id=order_id)
        return queryset

class BalancePaymentViewSet(viewsets.mixins.CreateModelMixin, viewsets.GenericViewSet):
    """
    尾款支付视图集
    """
    queryset = BalancePayment.objects.all().order_by('-payment_time')
    serializer_class = serializers.BalancePaymentSerializer
    permission_classes = [IsAuthenticated,IsBoss]
    
    def get_queryset(self):
        """根据订单ID过滤支付记录"""
        queryset = super().get_queryset()
        order_id = self.request.query_params.get('order_id')
        if order_id:
            queryset = queryset.filter(order_id=order_id)
        return queryset
    
    def create(self, request, *args, **kwargs):
        """重写创建方法，添加验证逻辑"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # 获取订单和支付金额
        order_id = serializer.validated_data.get('order').id
        payment_amount = serializer.validated_data.get('amount')
        
        # 验证支付金额不能为0
        if payment_amount <= 0:
            return Response(
                {'detail': '支付金额必须大于0'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # 获取订单信息，验证支付金额不能超过待收尾款
        try:
            order = Order.objects.get(id=order_id)
            pending_balance = order.pending_balance
            
            if payment_amount > pending_balance:
                return Response(
                    {'detail': f'支付金额(¥{payment_amount})不能超过待收尾款(¥{pending_balance})'},
                    status=status.HTTP_400_BAD_REQUEST
                )
                
        except Order.DoesNotExist:
            return Response(
                {'detail': '订单不存在'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # 执行原有的创建逻辑
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
    
    def perform_create(self, serializer):
        """创建尾款支付记录"""
        with transaction.atomic():
            # 保存支付记录
            payment = serializer.save(operator=self.request.user)
            
            # 创建操作日志
            order = payment.order
            now = datetime.datetime.now()
            timestamp = now.strftime('%Y-%m-%d %H:%M:%S')
            
            OperationLog.objects.create(
                order=order,
                description=f"于 {timestamp} 收到尾款 ¥{payment.amount}",
                operator=self.request.user
            )
            
            # 更新订单状态 (Order模型的save方法会自动更新payment_status)

class OrderInstallViewSet(viewsets.mixins.UpdateModelMixin, viewsets.GenericViewSet):
    """
    订单安装(一键出库)视图集
    """
    queryset = Order.objects.all()
    serializer_class = serializers.OrderInstallSerializer
    permission_classes = [IsAuthenticated,IsBoss|IsManager]
    
    def update(self, request, *args, **kwargs):
        """重写update方法实现一键出库功能"""
        # 1. 获取订单并验证数据
        order_id = kwargs.get('pk')
        try:
            order = Order.objects.get(id=order_id)
        except Order.DoesNotExist:
            return Response({'detail': '订单不存在'}, status=status.HTTP_404_NOT_FOUND)
        
        # 检查订单是否已经出库
        if order.delivery_status == 2:  # 已送货
            return Response({'detail': '订单已出库，不能重复操作'}, status=status.HTTP_400_BAD_REQUEST)
        
        # 验证序列化器数据
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            return Response({'detail': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        
        validated_data = serializer.validated_data
        installer = validated_data.get('installer_id')  # 现在这是一个Installer实例
        installation_fee = validated_data.get('installation_fee')
        transportation_fee = validated_data.get('transportation_fee')
        
        # 2. 开启数据库事务
        try:
            with transaction.atomic():
                # 2.1 遍历订单详情
                order_details = OrderDetail.objects.filter(order=order).select_related('inventory')
                
                # 先验证所有商品库存是否足够
                insufficient_items = []
                for detail in order_details:
                    inventory = detail.inventory
                    quantity = detail.quantity
                    
                    # 检查库存是否足够
                    if inventory.in_stock < quantity:
                        insufficient_items.append({
                            'name': inventory.full_name() if hasattr(inventory, 'full_name') else inventory.name,
                            'required': quantity,
                            'available': inventory.in_stock
                        })
                
                # 如果有库存不足的商品，返回错误
                if insufficient_items:
                    error_message = "以下商品库存不足：\n"
                    for item in insufficient_items:
                        error_message += f"- {item['name']}：需要 {item['required']} 件，库存仅 {item['available']} 件\n"
                    return Response({'detail': error_message}, status=status.HTTP_400_BAD_REQUEST)
                
                # 库存充足，执行出库操作
                for detail in order_details:
                    inventory = detail.inventory
                    quantity = detail.quantity
                    
                    # 2.1.2 同步减少been_order和in_stock数量
                    inventory.been_order = F('been_order') - quantity
                    inventory.in_stock = F('in_stock') - quantity
                    inventory.sold = F('sold') + quantity
                    inventory.save(update_fields=['been_order', 'in_stock', 'sold'])
                
                # 2.2 更新订单状态和相关信息
                now = datetime.datetime.now()
                order.delivery_status = 2  # 已送货
                order.installer = installer  # 直接使用installer实例
                order.installation_fee = installation_fee
                order.transportation_fee = transportation_fee
                order.installation_time = now
                
                # 重新计算毛利润 = 订单总额 - 成本总价 - 安装费用 - 运输费用
                order.gross_profit = order.total_amount - order.total_cost - installation_fee - transportation_fee
                order.save()
                
                # 2.3 记录操作日志
                timestamp = now.strftime('%Y-%m-%d %H:%M:%S')
                log_description = (
                    f"于 {timestamp} 进行一键出库操作。"
                    f"安装人员: {installer.name}, "
                    f"安装费用: ¥{installation_fee}, "
                    f"运输费用: ¥{transportation_fee}, "
                    f"最终毛利(扣除安装费和运输费): ¥{order.gross_profit}"
                )
                
                OperationLog.objects.create(
                    order=order,
                    description=log_description,
                    operator=request.user
                )
                
                # 3. 返回响应
                return Response({
                    'detail': '订单出库成功',
                    'order_id': order.id,
                    'delivery_status': order.delivery_status,
                    'gross_profit': float(order.gross_profit),
                    'installation_time': order.installation_time
                }, status=status.HTTP_200_OK)
                
        except Exception as e:
            return Response({'detail': f'订单出库失败: {str(e)}'}, status=status.HTTP_400_BAD_REQUEST)

class InstallerViewSet(viewsets.mixins.CreateModelMixin,viewsets.mixins.UpdateModelMixin, viewsets.mixins.ListModelMixin, viewsets.mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    """
    安装师傅视图集
    """
    queryset = Installer.objects.all()
    serializer_class = serializers.InstallerSerializer
    permission_classes = [IsAuthenticated,IsBoss|IsManager]

    # 重写详情函数, 该接口不只返回安装工人的姓名和电话,还有其本月安装费
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        
        # 获取基础数据
        data = serializer.data
        
        # 获取当前年月
        import datetime
        now = datetime.datetime.now()
        current_year = now.year
        current_month = now.month
        
        # 处理月份边界情况：如果是1月，则查询上一年的12月
        query_year = current_year
        query_month = current_month - 1
        if query_month == 0:
            query_month = 12
            query_year = current_year - 1
        
        # 计算当月安装费总和
        from django.db.models import Sum
        current_month_installation_fee = Order.objects.filter(
            installer=instance,
            installation_time__year=query_year,
            installation_time__month=query_month
        ).aggregate(total=Sum('installation_fee'))['total'] or 0
        
        data['current_month_installation_fee'] = current_month_installation_fee
        
        return Response(data)

class AbandonOrderViewSet(APIView):
    """
    订单作废接口
    """
    permission_classes = [IsAuthenticated,IsBoss]

    def post(self, request):
        # 获取订单ID
        order_id = request.data.get('order_id')
        if not order_id:
            return Response({'detail': '请提供订单ID'}, status=status.HTTP_400_BAD_REQUEST)
        
        # 1, 根据编号获取订单
        try:
            order = Order.objects.get(id=order_id)
        except Order.DoesNotExist:
            return Response({'detail': '订单不存在'}, status=status.HTTP_404_NOT_FOUND)
        
        # 2, 判断订单状态是否为"新订单", 如果不是"新订单", 则不能作废
        if order.delivery_status != 1:  # 1表示新订单
            return Response({'detail': '只有新订单状态的订单才能作废'}, status=status.HTTP_400_BAD_REQUEST)
        
        # 3, 找到订单详情
        order_details = OrderDetail.objects.filter(order=order).select_related('inventory')
        
        # 4, 开启数据库原子事务
        try:
            with transaction.atomic():
                # 提前收集所有需要更新的库存ID，减少锁定次数
                inventory_ids = [detail.inventory_id for detail in order_details]
                
                # 一次性锁定所有相关的库存记录
                inventories = {
                    inv.id: inv for inv in Inventory.objects.select_for_update().filter(id__in=inventory_ids)
                }
                
                # 批量更新库存的been_order字段
                for detail in order_details:
                    inventory = inventories.get(detail.inventory_id)
                    if inventory:
                        inventory.been_order -= detail.quantity
                
                # 批量保存更新后的库存
                if inventories:
                    Inventory.objects.bulk_update(inventories.values(), ['been_order'])
                
                # 记录操作日志
                now = datetime.datetime.now()
                timestamp = now.strftime('%Y-%m-%d %H:%M:%S')
                
                OperationLog.objects.create(
                    order=order,
                    description=f"于 {timestamp} 作废订单: {order.order_number}",
                    operator=request.user
                )
                
                # 4.2, 直接删除订单
                order.delete()  # 删除订单会级联删除订单详情
                
        except Exception as e:
            return Response({'detail': f'订单作废失败: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        # 5, 返回成功信息
        return Response({'detail': '订单作废成功'}, status=status.HTTP_200_OK)
