from django.urls import path, include
from rest_framework.routers import DefaultRouter

from . import views

app_name = 'order'

router = DefaultRouter()
router.register('orders', views.OrderViewSet, basename='orders')  # 订单列表和详情
router.register('order-details', views.OrderDetailViewSet, basename='order_details')  # 订单明细
router.register('operation-logs', views.OperationLogViewSet, basename='operation_logs')  # 操作日志
router.register('balance-payments', views.BalancePaymentViewSet, basename='balance_payments')  # 尾款支付
router.register('order-install', views.OrderInstallViewSet, basename='order_install')  # 订单出库
router.register('installer', views.InstallerViewSet, basename='installer')  # 安装师傅列表

urlpatterns = [
    path('order/create/', views.CreateOrderView.as_view(), name='order_create'),
] + router.urls
