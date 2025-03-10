from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import InventoryViewSet, AllInventoryViewSet, PurchaseView, PurchaseList, PurchaseDetailView, ReceiveView, \
    ReceiveList, ReceiveDetailView

app_name = 'inventory'

router = DefaultRouter()
router.register('inventory', InventoryViewSet, basename='inventory')  # 库存列表
router.register('allinventory', AllInventoryViewSet, basename='allinventory')  # 收发货接口(获取不分页的库存信息)

urlpatterns = [
                  # 收货
                  path('purchase/', PurchaseView.as_view(), name='purchase'),
                  path('purchase/list/', PurchaseList.as_view(), name='purchase_list'),
                  path('purchase/detail/<int:id>/', PurchaseDetailView.as_view(), name='purchase-detail'),
                  # 发货
                  path('receive/', ReceiveView.as_view(), name='receive'),
                  path('receive/list/', ReceiveList.as_view()),
                  path('receive/detail/<int:id>', ReceiveDetailView.as_view()),
              ] + router.urls
