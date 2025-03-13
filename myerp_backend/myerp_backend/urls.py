from django.urls import path, include

urlpatterns = [
    path('api/staff/', include('apps.staff.urls')),  # 登录 & 重置密码
    path('api/', include('apps.brand.urls')),  # 品牌(视图集)
    path('api/', include('apps.category.urls')),  # 种类(视图集)
    path('api/', include('apps.inventory.urls')),  # 库存管理
    path('api/', include('apps.client.urls')),  # 客户管理
    path('api/', include('apps.order.urls')),  # 订单管理
    path('api/', include('apps.home.urls')),  # 首页管理
]
