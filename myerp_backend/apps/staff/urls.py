from django.urls import path
from . import views

app_name = 'staff'

urlpatterns = [
    path('login/', views.LoginView.as_view(), name='login')
]