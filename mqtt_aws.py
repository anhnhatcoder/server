import os
import django
import json
import time
import sys
from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient

# --- 1. CẤU HÌNH MÔI TRƯỜNG DJANGO ---
# Dựa trên 'ls' của bạn, file này nằm tại gốc dự án (/app)
# Thư mục 'myweb' cũng nằm tại gốc dự án.
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(CURRENT_DIR)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myweb.settings')
try:
    django.setup()
except Exception as e:
    print(f"⚠️ Lỗi cấu hình Django: {e}")

from myweb.models import CamBien, Node

# --- 2. CẤU HÌNH AWS IOT CORE ---
ENDPOINT = "aum3f6pv7yg54-ats.iot.ap-northeast-1.amazonaws.com"
CLIENT_ID = "Django_Worker_MultiNode_MultiPump"
TOPIC_DATA_WILDCARD = "esp32/+/data"
TOPIC_CONTROL_WILDCARD = "esp32/+/control"

# --- 3. CẤU HÌNH ĐƯỜNG DẪN CHỨNG CHỈ (DỰA TRÊN CẤU TRÚC THẬT) ---
# Thư mục 'certs' nằm tại ~/iot_project/certs -> Trong container là /app/certs/
BASE_CERT_PATH = "/app/certs"

PATH_TO_ROOT = os.path.join(BASE_CERT_PATH, "AmazonRootCA1.pem")
PATH_TO_KEY = os.path.join(BASE_CERT_PATH, "private.pem.key")
PATH_TO_CERT = os.path.join(BASE_CERT_PATH, "certificate.pem.crt")

# --- 4. HÀM XỬ LÝ TIN NHẮN ĐẾN ---
def customCallback(client, userdata, message):
    try:
        payload = message.payload.decode('utf-8')
        topic = message.topic
        print(f"\n📩 Nhận tin từ Topic: {topic}")
        
        parts = topic.split('/')
        if len(parts) < 3: return
            
        node_id_from_topic = parts[1]
        message_type = parts[2] 

        data = json.loads(payload)

        if message_type == 'data':
            try:
                node_obj = Node.objects.get(node_id=node_id_from_topic)
            except Node.DoesNotExist:
                print(f"⚠️ Node '{node_id_from_topic}' chưa đăng ký. Bỏ qua.")
                return

            sensor_map = {
                'temperature': '°C',
                'humidity': '%',
                'rainDigital': '',
                'soilPercent': '%'
            }

            for key, unit in sensor_map.items():
                if key in data:
                    CamBien.objects.create(
                        node=node_obj, 
                        ten=key, 
                        gia_tri=float(data[key]), 
                        don_vi=unit
                    )
                    print(f"   ✅ {key}: {data[key]} {unit}")

            for key, value in data.items():
                if 'pump' in key and 'State' in key:
                    val = 1.0 if value == "ON" else 0.0
                    CamBien.objects.create(node=node_obj, ten=key, gia_tri=val, don_vi="")
                    print(f"   ✅ {key}: {value}")

            # Dọn dẹp dữ liệu cũ (giữ 500 dòng cho mỗi Node)
            count = CamBien.objects.filter(node=node_obj).count()
            if count > 600:
                ids_to_keep = CamBien.objects.filter(node=node_obj).order_by('-thoi_gian').values_list('id', flat=True)[:500]
                CamBien.objects.filter(node=node_obj).exclude(id__in=list(ids_to_keep)).delete()

    except Exception as e:
        print(f"❌ Lỗi xử lý: {e}")

# --- 5. CHƯƠNG TRÌNH CHÍNH ---
if __name__ == '__main__':
    print("🚀 Đang khởi động MQTT Worker...")
    print(f"📂 Sử dụng chứng chỉ tại: {BASE_CERT_PATH}")
    
    # Kiểm tra sự tồn tại của file trước khi kết nối
    if not os.path.exists(PATH_TO_ROOT):
        print(f"❌ LỖI: Không tìm thấy file {PATH_TO_ROOT}")
        print(f"Hãy đảm bảo thư mục certs trên EC2 chứa đúng 3 file chứng chỉ.")
        sys.exit(1)
    
    myMQTTClient = AWSIoTMQTTClient(CLIENT_ID)
    myMQTTClient.configureEndpoint(ENDPOINT, 8883)
    myMQTTClient.configureCredentials(PATH_TO_ROOT, PATH_TO_KEY, PATH_TO_CERT)
    
    myMQTTClient.configureAutoReconnectBackoffTime(1, 32, 20)
    myMQTTClient.configureConnectDisconnectTimeout(15) 
    myMQTTClient.configureMQTTOperationTimeout(10) 

    print(f"🔄 Đang kết nối tới AWS Endpoint: {ENDPOINT}")
    if myMQTTClient.connect():
        print("✅ KẾT NỐI AWS THÀNH CÔNG!")
        myMQTTClient.subscribe(TOPIC_DATA_WILDCARD, 1, customCallback)
        print(f"📡 Đang lắng nghe: {TOPIC_DATA_WILDCARD}")
        
        while True:
            time.sleep(1)
    else:
        print("❌ KẾT NỐI THẤT BẠI!")