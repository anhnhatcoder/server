import os
import django
from django.core.asgi import get_asgi_application

# Bước 1: Thiết lập môi trường Django ngay lập tức
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myweb.settings')
django.setup()

# Bước 2: Khởi tạo ứng dụng ASGI của Django trước khi import routing
# Việc khởi tạo sớm giúp giảm độ trễ khi bắt đầu các kết nối mới
django_asgi_app = get_asgi_application()

from channels.routing import ProtocolTypeRouter, URLRouter
import myweb.esp_ai.routing 

application = ProtocolTypeRouter({
    # Xử lý các yêu cầu HTTP (Giao diện Dashboard)
    "http": django_asgi_app,
    
    # Xử lý WebSocket (Stream ảnh AI)
    # BỎ QUA HOÀN TOÀN AuthMiddlewareStack để đạt hiệu suất tối đa.
    # Việc không phải giải mã Session/Cookie cho mỗi khung hình giúp CPU rảnh tay hơn
    # để trung chuyển dữ liệu nhị phân (Binary) từ ESP32.
    "websocket": URLRouter(
        myweb.esp_ai.routing.websocket_urlpatterns
    ),
})