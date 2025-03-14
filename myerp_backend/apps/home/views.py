from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Sum, Count, F, DecimalField, ExpressionWrapper
from django.db.models.functions import TruncMonth
from django.utils import timezone
import datetime
from apps.inventory.models import Inventory
from apps.order.models import Order
from rest_framework.permissions import IsAuthenticated
from django.views.decorators.cache import cache_page
from django.utils.decorators import method_decorator

class InventoryByBrandView(APIView):
    """
    获取所有品牌下的所有库存信息的累加总价值
    """
    permission_classes = [IsAuthenticated]
    
    @method_decorator(cache_page(60 * 5))  # 缓存5分钟
    def get(self, request):
        try:
            # 获取所有品牌及其库存总价值
            inventory_by_brand = Inventory.objects.values(
                'brand__id', 
                'brand__name'
            ).annotate(
                total_value=Sum(
                    ExpressionWrapper(
                        (F('on_road') + F('in_stock')) * F('cost'),
                        output_field=DecimalField()
                    )
                )  # 每个品牌的库存总价值
            ).order_by('-total_value')  # 按库存总价值降序排序
            
            return Response({
                'inventory_by_brand': inventory_by_brand
            })
            
        except Exception as e:
            return Response({
                'detail': f'获取库存信息失败: {str(e)}'
            }, status=status.HTTP_400_BAD_REQUEST)


class MonthlyOrdersByStaffView(APIView):
    """
    获取每个员工本月的销售业绩总金额
    """
    permission_classes = [IsAuthenticated]

    @method_decorator(cache_page(60 * 5))
    def get(self, request):
        try:
            # 获取当前月的第一天和最后一天
            today = timezone.now().date()
            first_day = datetime.date(today.year, today.month, 1)
            if today.month == 12:
                last_day = datetime.date(today.year + 1, 1, 1) - datetime.timedelta(days=1)
            else:
                last_day = datetime.date(today.year, today.month + 1, 1) - datetime.timedelta(days=1)
            
            # 查询本月的订单并按员工分组，只统计销售总金额
            staff_performance = Order.objects.filter(
                sign_time__date__gte=first_day,
                sign_time__date__lte=last_day
            ).exclude(
                delivery_status=3  # 排除已作废订单
            ).values(
                'staff__uid', 
                'staff__name'
            ).annotate(
                total_amount=Sum('total_amount')  # 订单总额
            ).order_by('-total_amount')  # 按订单总额降序排序
            
            # 计算员工业绩占比
            total_amount_sum = sum([staff['total_amount'] for staff in staff_performance]) or 1
            for staff in staff_performance:
                staff['amount_percentage'] = round(float(staff['total_amount']) / float(total_amount_sum) * 100, 2)
            
            return Response({
                'current_month': {
                    'year': today.year,
                    'month': today.month,
                    'first_day': first_day.strftime('%Y-%m-%d'),
                    'last_day': last_day.strftime('%Y-%m-%d')
                },
                'staff_performance': staff_performance
            })
            
        except Exception as e:
            return Response({
                'detail': f'获取订单信息失败: {str(e)}'
            }, status=status.HTTP_400_BAD_REQUEST)



class CurrentYearMonthlySalesView(APIView):
    """
    获取当前年份1~12月的销售数据(每个月的订单总额)
    """
    permission_classes = [IsAuthenticated]
    
    @method_decorator(cache_page(60 * 5))
    def get(self, request):
        try:
            # 锚定当前年份
            current_year = timezone.now().year
            
            # 查询当前年份的订单数据并按月分组
            monthly_sales = Order.objects.filter(
                sign_time__year=current_year
            ).exclude(
                delivery_status=3  # 排除已作废订单
            ).annotate(
                month=TruncMonth('sign_time')
            ).values('month').annotate(
                total_amount=Sum('total_amount')  # 每月的订单总额
            ).order_by('month')
            
            # 创建初始化的月份数据字典(1-12月)，默认销售额为0
            sales_by_month = {month: 0 for month in range(1, 13)}
            
            # 使用查询结果更新字典
            for item in monthly_sales:
                if item['month']:
                    month_number = item['month'].month
                    sales_by_month[month_number] = float(item['total_amount']) if item['total_amount'] else 0
            
            # 直接返回月份->销售额的字典
            return Response(sales_by_month)
            
        except Exception as e:
            return Response({
                'detail': f'获取月度销售数据失败: {str(e)}'
            }, status=status.HTTP_400_BAD_REQUEST)