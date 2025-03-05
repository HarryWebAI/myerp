from django.urls import path, include

urlpatterns = [
    path('api/staff/', include('apps.staff.urls'))  # 员工接口
]
