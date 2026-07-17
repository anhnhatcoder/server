from django.urls import path
from django.contrib.auth import views as auth_views
from . import views 

urlpatterns = [
    # Giao diện chính: https://anhnhatiot.cloud/esp-ai/
    path('', views.ai_dashboard, name='ai_dashboard'),
    
    # TRANG LOGIN RIÊNG CHO AI
    path('login/', auth_views.LoginView.as_view(
        template_name='esp_ai/login.html'
    ), name='ai_login'),

    # FIX LỖI: Khi thoát, quay lại trang login AI kèm tham số ?next=/esp-ai/
    # Việc này giúp khi bạn đăng nhập lại, hệ thống biết để đưa bạn về đúng trang AI.
    path('logout/', auth_views.LogoutView.as_view(
        next_page='/esp-ai/login/?next=/esp-ai/' 
    ), name='ai_logout'),
    
    # API
    path('upload/', views.upload_capture, name='ai_upload'),
    path('api/status/', views.get_ai_status, name='ai_status'),
]