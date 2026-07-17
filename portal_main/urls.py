from django.urls import path
from . import views

urlpatterns = [
    # Route này xử lý trang chủ (/) của cả hệ thống
    path('', views.portal_home, name='portal_home'),
]
