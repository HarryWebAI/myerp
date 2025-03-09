from rest_framework.routers import DefaultRouter
from .views import CategoryModelViewSet

app_name = 'category'

router = DefaultRouter()
router.register('category',CategoryModelViewSet,basename='category')

urlpatterns = [] + router.urls