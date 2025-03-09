from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import InventoryViewSet, AllInventoryViewSet, PurchaseView, PurchaseList, PurchaseDetailView

app_name = 'inventory'

router = DefaultRouter()
router.register('inventory', InventoryViewSet, basename='inventory')
router.register('allinventory', AllInventoryViewSet, basename='allinventory')

urlpatterns = [
                  path('purchase/', PurchaseView.as_view(), name='purchase'),
                  path('purchase/list/', PurchaseList.as_view(), name='purchase_list'),
                  path('purchase/detail/<int:id>/', PurchaseDetailView.as_view(), name='purchase-detail'),
              ] + router.urls
