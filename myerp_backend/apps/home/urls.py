app_name = 'home'

from django.urls import path
from . import views

urlpatterns = [
    # 获取所有品牌的库存总价值
    path('inventory-by-brand/', views.InventoryByBrandView.as_view(), name='inventory_by_brand'),
    
    # 获取每个员工本月的销售业绩
    path('staff-performance/', views.MonthlyOrdersByStaffView.as_view(), name='staff_performance'),
    
    # 获取当前年份1~12月的销售数据
    path('current-year-sales/', views.CurrentYearMonthlySalesView.as_view(), name='current_year_sales'),
]
