from rest_framework.routers import DefaultRouter
from .views import InventoryViewSet

app_name = 'inventory'

router = DefaultRouter()
router.register('inventory',InventoryViewSet,basename='inventory')

urlpatterns = [] + router.urls