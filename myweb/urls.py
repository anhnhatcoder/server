from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from django.views.generic import RedirectView, TemplateView
from django.conf import settings
from django.conf.urls.static import static

# Import views từ app myweb
from myweb import views as garden_views 

urlpatterns = [
    # 1. PORTAL
    path('', include('portal_main.urls')),

    # 2. AI VISION (Đã xóa chữ 'a' bị thừa ở cuối)
    path('esp-ai/', include('myweb.esp_ai.urls')),

    # 3. GARDEN
    path('garden/', include([
        path('', garden_views.home_view, name='home'),
        path('dashboard/<str:node_id>/', garden_views.node_dashboard, name='node_dashboard'),
        path('delete_node/<str:node_id>/', garden_views.delete_node, name='delete_node'),
    ])),
    
    
    
    
    # 4. SMARTHOME
    path('smarthome/', garden_views.smarthome_dashboard, name='smarthome_app'),
    path('smarthome/add-room/', garden_views.add_room, name='add_room'),
    path('smarthome/delete-room/<int:room_id>/', garden_views.delete_room, name='delete_room'),
    path('smarthome/add-device/<int:room_id>/', garden_views.add_device, name='add_device'),
    path('smarthome/delete-device/<int:device_id>/', garden_views.delete_device, name='delete_device'),
    
    # 5. ADMIN & AUTH
    path('admin/', admin.site.urls),
    path('logout/', auth_views.LogoutView.as_view(next_page='/esp-ai/login/'), name='logout'),
    path('login-redirect/', garden_views.login_success, name='login_redirect'),
    path('accounts/login/', RedirectView.as_view(url='/esp-ai/login/', query_string=True)),
    
    # 6. API GARDEN & OTA
    path('api/data/<str:node_id>/', garden_views.get_node_data, name='get_node_data'),
    path('api/control/<str:node_id>/<str:device_id>/<str:state>/', garden_views.control_node_pump, name='control_node'),
    path('ota/', garden_views.ota_view, name='ota'),
    path('api/check_update/', garden_views.check_firmware, name='check_fw'),
    
    # 7. API SMARTHOME (Kết nối tới hàm điều khiển Smart Home trong views.py)
    # Giao diện web sẽ gọi API này, ví dụ: /api/smarthome/control/relay_1/ON/
    path('api/smarthome/control/<str:device_id>/<str:state>/', garden_views.control_smart_home_device, name='control_smarthome'),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)