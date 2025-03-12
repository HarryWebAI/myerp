from django.urls import path
from rest_framework.routers import DefaultRouter

from . import views

app_name = 'inventory'

router = DefaultRouter()
router.register('inventory', views.InventoryViewSet, basename='inventory')  # 库存列表
router.register('allinventory', views.AllInventoryViewSet, basename='allinventory')  # 收发货接口(获取不分页的库存信息)

urlpatterns = [
                  path('purchase/', views.PurchaseView.as_view(), name='purchase'),
                  path('purchase/list/', views.PurchaseList.as_view(), name='purchase_list'),
                  path('purchase/detail/<int:id>/', views.PurchaseDetailView.as_view(), name='purchase-detail'),
                  path('purchase/detail/update/<int:id>/', views.PurchaseDetailUpdateView.as_view(), name='purchase-detail-update'),
                  path('purchase/detail/delete/<int:id>/', views.PurchaseDetailDeleteView.as_view(), name='purchase-detail-delete'),
                  path('receive/', views.ReceiveView.as_view(), name='receive'),
                  path('receive/list/', views.ReceiveList.as_view()),
                  path('receive/detail/<int:id>', views.ReceiveDetailView.as_view()),
                  path('receive/detail/update/<int:id>/', views.ReceiveDetailUpdateView.as_view(), name='receive-detail-update'),
                  path('receive/detail/delete/<int:id>/', views.ReceiveDetailDeleteView.as_view(), name='receive-detail-delete'),
                  path('download/', views.InventoryDownloadView.as_view(), name='inventory-download')
              ] + router.urls
