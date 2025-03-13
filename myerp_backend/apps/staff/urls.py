from django.urls import path
from . import views

app_name = 'staff'

urlpatterns = [
    # 登录
    path('login/', views.LoginView.as_view(), name='login'),
    # 修改密码
    path('reset/', views.ResetPasswordView.as_view(), name='reset'),
    # 获取所有员工
    path('allstaff/', views.StaffListView.as_view(), name='staff_list'),
    # 创建员工
    path('create/', views.CreateStaffView.as_view(), name='create'),
    # 修改员工信息
    path('update/<str:uid>/', views.UpdateStaffView.as_view(), name='update_staff'),
]