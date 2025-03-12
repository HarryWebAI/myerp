from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, viewsets, filters
from rest_framework.permissions import IsAuthenticated
from django.db import transaction
from django.db.models import F, Q, Sum
from decimal import Decimal
import datetime

from . import serializers
from . import paginations
from .models import Order, OrderDetail, OperationLog, BalancePayment
from apps.inventory.models import Inventory

class CreateOrderView(APIView):
    """
    新增订单接口
    """
    permission_classes = [IsAuthenticated]

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
                
                # 创建订单
                order = Order.objects.create(
                    order_number=validated_data['order_number'],
                    brand_id=validated_data['brand_id'],
                    client_id=validated_data['client_id'],
                    staff_id=validated_data['staff_id'],
                    total_amount=validated_data['total_amount'],
                    down_payment=validated_data['down_payment'],
                    pending_balance=validated_data['total_amount'] - validated_data['down_payment'],
                    total_cost=validated_data['total_cost'],
                    gross_profit=validated_data['gross_profit'],
                    address=validated_data['address'],
                    # 默认值处理
                    received_balance=0,
                    delivery_status=1,  # 新订单
                    payment_status=1,   # 未结清
                    installation_fee=0,
                    transportation_fee=0
                )
                
                # 验证成本总价并处理订单明细
                calculated_cost = 0
                order_details = []
                
                # 批量处理订单详情
                for item in details_data:
                    # 使用select_for_update锁定库存记录，防止并发问题
                    inventory = Inventory.objects.select_for_update().get(id=item['inventory_id'])
                    quantity = item['quantity']
                    
                    # 计算成本
                    item_cost = inventory.cost * quantity
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
                
                # 创建尾款记录（如果有尾款）
                pending_balance = order.pending_balance
                if pending_balance > 0:
                    BalancePayment.objects.create(
                        order=order,
                        amount=0,  # 初始收款为0
                        payment_time=datetime.datetime.now(),
                        operator=request.user
                    )
                # 如果没有尾款, 订单结清状态应该是已结清payment_status=2
                else:
                    order.payment_status = 2  # 已结清
                    order.save(update_fields=['payment_status'])
                
                # 操作日志
                now = datetime.datetime.now()
                timestamp = now.strftime('%Y-%m-%d %H:%M:%S')
                
                # 创建基本操作日志
                log_description = f"于 {timestamp} 创建订单, 订单总额: {order.total_amount}, 成本总价: {order.total_cost}, 初步毛利: {order.gross_profit}"
                
                OperationLog.objects.create(
                    order=order,
                    description=log_description,
                    operator=request.user
                )

                # 校对成本总价，如有较大差异则添加警告日志
                user_provided_cost = validated_data['total_cost']
                if abs(calculated_cost - user_provided_cost) > Decimal('1.00'):
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
        

class OrderViewSet(viewsets.GenericViewSet,
                   viewsets.mixins.ListModelMixin,
                   viewsets.mixins.RetrieveModelMixin):
    """
    订单视图集
    """
    queryset = Order.objects.all()
    serializer_class = serializers.OrderSerializer
    permission_classes = [IsAuthenticated]
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
        brand_id = self.request.query_params.get('brand_id')
        client_uid = self.request.query_params.get('client_uid')
        staff_uid = self.request.query_params.get('staff_uid')
        delivery_status = self.request.query_params.get('delivery_status')
        payment_status = self.request.query_params.get('payment_status')
        date_start = self.request.query_params.get('date_start')
        date_end = self.request.query_params.get('date_end')
        
        # 应用过滤条件（只有当值不是默认值时）
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
    permission_classes = [IsAuthenticated]
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
    permission_classes = [IsAuthenticated]
    pagination_class = paginations.OperationLogPagination
    
    def get_queryset(self):
        """根据订单ID过滤日志"""
        queryset = super().get_queryset()
        order_id = self.request.query_params.get('order_id')
        if order_id:
            queryset = queryset.filter(order_id=order_id)
        return queryset


class BalancePaymentViewSet(viewsets.ModelViewSet):
    """
    尾款支付视图集
    """
    queryset = BalancePayment.objects.all().order_by('-payment_time')
    serializer_class = serializers.BalancePaymentSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = paginations.BalancePaymentPagination
    
    def get_queryset(self):
        """根据订单ID过滤支付记录"""
        queryset = super().get_queryset()
        order_id = self.request.query_params.get('order_id')
        if order_id:
            queryset = queryset.filter(order_id=order_id)
        return queryset
    
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
