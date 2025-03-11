from rest_framework.routers import DefaultRouter
from .views import ClientModelViewSet

app_name = 'client'

router = DefaultRouter()
router.register('client', ClientModelViewSet, basename='client')

urlpatterns = [] + router.urls 