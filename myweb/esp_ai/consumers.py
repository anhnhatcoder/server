import json
from channels.generic.websocket import AsyncWebsocketConsumer

class CameraConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_group_name = 'camera_stream'
        # Thêm client (ESP32 hoặc Web) vào nhóm nhận ảnh
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        # Xóa client khỏi nhóm khi ngắt kết nối
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data=None, bytes_data=None):
        if bytes_data:
            # PHÁT TÁN NHỊ PHÂN THÔ (Cực nhanh, không tốn CPU server)
            # Khi ESP32 gửi bytes, server chỉ việc đẩy tiếp bytes đó đi
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'stream_binary',
                    'bytes': bytes_data
                }
            )

    async def stream_binary(self, event):
        # Gửi dữ liệu nhị phân trực tiếp xuống trình duyệt người xem
        await self.send(bytes_data=event['bytes'])