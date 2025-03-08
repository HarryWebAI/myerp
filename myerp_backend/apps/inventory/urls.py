from rest_framework.routers import DefaultRouter
from .views import InventoryViewSet,AllInventoryViewSet

app_name = 'inventory'

router = DefaultRouter()
router.register('inventory',InventoryViewSet,basename='inventory')
router.register('allinventory',AllInventoryViewSet,basename='allinventory')

urlpatterns = [] + router.urls