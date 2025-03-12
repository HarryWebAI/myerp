from rest_framework.routers import DefaultRouter
from .views import ClientModelViewSet, AllClientViewSet

app_name = 'client'

router = DefaultRouter()
router.register('client', ClientModelViewSet, basename='client')
router.register('allclient', AllClientViewSet, basename='allclient')

urlpatterns = [] + router.urls 