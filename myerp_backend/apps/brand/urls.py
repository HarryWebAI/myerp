from rest_framework.routers import DefaultRouter
from .views import BrandModelViewSet

app_name = 'brand'

router = DefaultRouter()
router.register('brand',BrandModelViewSet,basename='brand')

urlpatterns = [] + router.urls