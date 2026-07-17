from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from django.views.generic import RedirectView
from django.conf import settings
from django.conf.urls.static import static
from myweb import views as garden_views 

urlpatterns = [
    # 1. PORTAL
    path('', include('portal_main.urls')),

    # 2. AI VISION
    path('esp-ai/', include('myweb.esp_ai.urls')),

    # 3. GARDEN
    path('garden/', include([
        path('', garden_views.home_view, name='home'),
        path('dashboard/<str:node_id>/', garden_views.node_dashboard, name='node_dashboard'),
        path('delete_node/<str:node_id>/', garden_views.delete_node, name='delete_node'),
    ])),
    
    # 4. CNC PCB (MỚI)
    path('cnc/', garden_views.cnc_view, name='cnc_app'),
    
    # 5. ADMIN & AUTH
    path('admin/', admin.site.urls),
    path('logout/', auth_views.LogoutView.as_view(next_page='/esp-ai/login/'), name='logout'),
    path('login-redirect/', garden_views.login_success, name='login_redirect'),
    path('accounts/login/', RedirectView.as_view(url='/esp-ai/login/', query_string=True)),
    
    # 6. API (DÒNG 41 - Đã sửa lỗi get_node_data)
    path('api/data/<str:node_id>/', garden_views.get_node_data, name='get_node_data'),
    path('api/control/<str:node_id>/<str:device_id>/<str:state>/', garden_views.control_node_pump, name='control_node'),
    path('ota/', garden_views.ota_view, name='ota'),
    path('api/check_update/', garden_views.check_firmware, name='check_fw'),
    
    # API Gửi dữ liệu CNC thực tế (Bổ sung để nút Gửi trên Web hoạt động)
    path('api/cnc/send/', garden_views.send_cnc_data, name='send_cnc_data'),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)