from rest_framework.routers import DefaultRouter
from .views import CategoryModelViewSet

app_name = 'brand'

router = DefaultRouter()
router.register('category',CategoryModelViewSet,basename='category')

urlpatterns = [] + router.urls