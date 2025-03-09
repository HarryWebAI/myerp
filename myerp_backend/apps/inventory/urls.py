from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import InventoryViewSet, AllInventoryViewSet, PurchaseView

app_name = 'inventory'

router = DefaultRouter()
router.register('inventory', InventoryViewSet, basename='inventory')
router.register('allinventory', AllInventoryViewSet, basename='allinventory')

urlpatterns = [
                  path('purchase/', PurchaseView.as_view(), name='purchase'),
              ] + router.urls
