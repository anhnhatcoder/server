from django.urls import re_path
from . import consumers

# Định nghĩa các đường dẫn dành riêng cho WebSocket
websocket_urlpatterns = [
    # Đường dẫn này phải khớp chính xác trên ESP32: /ws/esp-ai/stream/
    re_path(r'ws/esp-ai/stream/$', consumers.CameraConsumer.as_asgi()),
]
