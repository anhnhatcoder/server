import os
import sys
import json
import time
import ssl
import tempfile
import django

# --- 1. CẤU HÌNH MÔI TRƯỜNG DJANGO ---
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(CURRENT_DIR)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myweb.settings') 
try:
    django.setup()
except Exception as e:
    print(f"⚠️ Lỗi cấu hình Django: {e}")

from myweb.models import CamBien, Node
from dashboard.models import SensorData, DeviceStatus

from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient
import paho.mqtt.client as mqtt

# ========================================================
# PHẦN A: CẤU HÌNH SMART GARDEN
# ========================================================
GARDEN_ENDPOINT = "aum3f6pv7yg54-ats.iot.ap-northeast-1.amazonaws.com"
GARDEN_CLIENT_ID = "Django_Worker_MultiNode_MultiPump"
TOPIC_DATA_WILDCARD = "esp32/+/data"

BASE_CERT_PATH = "/app/certs"
PATH_TO_ROOT = os.path.join(BASE_CERT_PATH, "AmazonRootCA1.pem")
PATH_TO_KEY = os.path.join(BASE_CERT_PATH, "private.pem.key")
PATH_TO_CERT = os.path.join(BASE_CERT_PATH, "certificate.pem.crt")

def customCallback(client, userdata, message):
    try:
        payload = message.payload.decode('utf-8')
        topic = message.topic
        print(f"\n📩 [GARDEN] Nhận tin từ Topic: {topic}")
        
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

            count = CamBien.objects.filter(node=node_obj).count()
            if count > 600:
                ids_to_keep = CamBien.objects.filter(node=node_obj).order_by('-thoi_gian').values_list('id', flat=True)[:500]
                CamBien.objects.filter(node=node_obj).exclude(id__in=list(ids_to_keep)).delete()

    except Exception as e:
        print(f"❌ [GARDEN] Lỗi xử lý: {e}")

def run_garden_client():
    if not os.path.exists(PATH_TO_ROOT):
        print(f"❌ LỖI: Không tìm thấy file {PATH_TO_ROOT}")
        print(f"Hãy đảm bảo thư mục certs trên EC2 chứa đúng 3 file chứng chỉ.")
        return
    
    myMQTTClient = AWSIoTMQTTClient(GARDEN_CLIENT_ID)
    myMQTTClient.configureEndpoint(GARDEN_ENDPOINT, 8883)
    myMQTTClient.configureCredentials(PATH_TO_ROOT, PATH_TO_KEY, PATH_TO_CERT)
    
    myMQTTClient.configureAutoReconnectBackoffTime(1, 32, 20)
    myMQTTClient.configureConnectDisconnectTimeout(15) 
    myMQTTClient.configureMQTTOperationTimeout(10) 

    print(f"🔄 [GARDEN] Đang kết nối tới AWS Endpoint: {GARDEN_ENDPOINT}")
    if myMQTTClient.connect():
        print("✅ [GARDEN] KẾT NỐI AWS THÀNH CÔNG!")
        myMQTTClient.subscribe(TOPIC_DATA_WILDCARD, 1, customCallback)
        print(f"📡 [GARDEN] Đang lắng nghe: {TOPIC_DATA_WILDCARD}")
    else:
        print("❌ [GARDEN] KẾT NỐI THẤT BẠI!")

# ========================================================
# PHẦN B: CẤU HÌNH SMART HOME
# ========================================================
HOME_ENDPOINT = "azi4l8ersx95s-ats.iot.ap-southeast-2.amazonaws.com"
HOME_PORT = 8883
HOME_CLIENT_ID = "Django_Server_Client"

TOPIC_SENSOR_SUB = "gateway/sensor/data"
TOPIC_STATUS_SUB = "gateway/status/#"

AWS_CERT_CA = """-----BEGIN CERTIFICATE-----
MIIDQTCCAimgAwIBAgITBmyfz5m/jAo54vB4ikPmljZbyjANBgkqhkiG9w0BAQsF
ADA5MQswCQYDVQQGEwJVUzEPMA0GA1UEChMGQW1hem9uMRkwFwYDVQQDExBBbWF6
b24gUm9vdCBDQSAxMB4XDTE1MDUyNjAwMDAwMFoXDTM4MDExNzAwMDAwMFowOTEL
MAkGA1UEBhMCVVMxDzANBgNVBAoTBkFtYXpvbjEZMBcGA1UEAxMQQW1hem9uIFJv
b3QgQ0EgMTCCASIwDQYJKoZIhvcNAQEBBQADggEPADCCAQoCggEBALJ4gHHKeNXj
ca9HgFB0fW7Y14h29Jlo91ghYPl0hAEvrAIthtOgQ3pOsqTQNroBvo3bSMgHFzZM
9O6II8c+6zf1tRn4SWiw3te5djgdYZ6k/oI2peVKVuRF4fn9tBb6dNqcmzU5L/qw
IFAGbHrQgLKm+a/sRxmPUDgH3KKHOVj4utWp+UhnMJbulHheb4mjUcAwhmahRWa6
VOujw5H5SNz/0egwLX0tdHA114gk957EWW67c4cX8jJGKLhD+rcdqsq08p8kDi1L
93FcXmn/6pUCyziKrlA4b9v7LWIbxcceVOF34GfID5yHI9Y/QCB/IIDEgEw+OyQm
jgSubJrIqg0CAwEAAaNCMEAwDwYDVR0TAQH/BAUwAwEB/zAOBgNVHQ8BAf8EBAMC
AYYwHQYDVR0OBBYEFIQYzIU07LwMlJQuCFmcx7IQTgoIMA0GCSqGSIb3DQEBCwUA
A4IBAQCY8jdaQZChGsV2USggNiMOruYou6r4lK5IpDB/G/wkjUu0yKGX9rbxenDI
U5PMCCjjmCXPI6T53iHTfIUJrU6adTrCC2qJsZjl3bepXFlSlzwPZPIlz3/N6qoM
P0CZFlrIlElOOnt+IgEEFCSRsQikGQIG4J7FqjWAC1R90R03Zt+l7zX9c6p0GjPG
yD6L6k5D3aPndJOTLzO7tB9lq9xY2cWJ7H0oG7Kk1B72b7V723oF9Fm7yJbJ9aU6
w+y1G8/uQnO7i1q44r+4zFvL9+E11rNvwBw9z1bQG/2R0U/a1OAKiI/F0iB1b/4B
rA97A8R/93jUj48+o/6+O/2oWc04
-----END CERTIFICATE-----"""

AWS_CERT_CRT = """-----BEGIN CERTIFICATE-----
MIIDWTCCAkGgAwIBAgIUSw///ohm2Lkgs5qxv404HP9zwCIwDQYJKoZIhvcNAQEL
BQAwTTFLMEkGA1UECwxCQW1hem9uIFdlYiBTZXJ2aWNlcyBPPUFtYXpvbi5jb20g
SW5jLiBMPVNlYXR0bGUgU1Q9V2FzaGluZ3RvbiBDPVVTMB4XDTI2MDcwODE2MTQy
NVoXDTQ5MTIzMTIzNTk1OVowHjEcMBoGA1UEAwwTQVdTIElvVCBDZXJ0aWZpY2F0
ZTCCASIwDQYJKoZIhvcNAQEBBQADggEPADCCAQoCggEBAMoa2sZInvTBdYnNb9wq
CTvvrI8qKznKk1BU7/0YoldzlkJCetwgr1ApjBdPdfiUe3XigInqELl+L9NLgGGm
wRxILTVMEXmBzidKztgm+c/6Ip3qnAp5sXWc0+AZX7KR2fv0ZnAGuEfB8kj/tfQS
5DfYff11oxJfisMGlZrStH5cLiKtagSVVrVE6tupH52+3gt4AkJgBu2taxY6YGo/
1MF5l8ZHlq67+xWQmHdVQmq1PqL02vCwq0XwONEkL2Z2hs5Er92iw3Kp+r6OOoRz
iE/+CVfRUVoFIPRMCmw3lrImsaDLK1gLeA7H8fFnJnioBvwgpNNWfVOKLsA7+O1J
sAcCAwEAAaNgMF4wHwYDVR0jBBgwFoAUQWhtHAPE5ENouipeRm+M5lPdr7UwHQYD
VR0OBBYEFOc9fbcjvwl2Gm3HIng8GizAtpnwMAwGA1UdEwEB/wQCMAAwDgYDVR0P
AQH/BAQDAgeAMA0GCSqGSIb3DQEBCwUAA4IBAQBhP6ulxen+S4u1MOPTxw16WT78
2+Uh5ssemB2MW5Kns+XYM94fricyyTJKYV7GexZ7VdV/TAJUpz8TGXfmQdCdQb6j
oyun0RS+zu6KwC8txnoFJk6Pvz5Gaxk4nE4DfiYNyMy2t2LSN9/VsK2pImpX6kic
wXbltbAr5WOTbnQWEp6kBcVei1kNblmuJDQAQITf6e6A0hAz2zx9ET1W1/cknazm
DEcv27CHfxObyqqpE5ok+PQ9bc/36kAnq8NeqqOUIhscKpGfIAoPgzzdE/qiokBc
YIP+Izz58fKXbZMttGPrqfHC9PfI1XRCvA02VtIpZKc5a6kTzVOtFe6AsvgQ
-----END CERTIFICATE-----"""

AWS_CERT_PRIVATE = """-----BEGIN RSA PRIVATE KEY-----
MIIEowIBAAKCAQEAyhraxkie9MF1ic1v3CoJO++sjyorOcqTUFTv/RiiV3OWQkJ6
3CCvUCmMF091+JR7deKAieoQuX4v00uAYabBHEgtNUwReYHOJ0rO2Cb5z/oineqc
CnmxdZzT4BlfspHZ+/RmcAa4R8HySP+19BLkN9h9/XWjEl+KwwaVmtK0flwuIq1q
BJVWtUTq26kfnb7eC3gCQmAG7a1rFjpgaj/UwXmXxkeWrrv7FZCYd1VCarU+ovTa
8LCrRfA40SQvZnaGzkSv3aLDcqn6vo46hHOIT/4JV9FRWgUg9EwKbDeWsiaxoMsr
WAt4Dsfx8WcmeKgG/CCk01Z9U4ouwDv47UmwBwIDAQABAoIBAHSXH2RJ2qFZxWO0
xvYcre0Mq+B/NCaHrYonJbc9cdG/VYxt65B3rosxHKcJ6QV5KuvrublV9UX8/LwJ
D0vGNhsJrELV2jLdZj8WkdLyUSTgqP2urUwBvhUaXsQl/yX1q+oEqN+xkLectBfW
pHHkQBHTa4M/TM65nUQ61S1WpldJ8BIZG40ofOT9ZImf+d7IyMuh5eVGqwGoxxDQ
MQzr7V+SzVlxDaAXCycXRv9G2OpnjPerHWR4WDy1AvGD0yEUfmVxCJDKgLzGwNN8
r+0Q6WCoPi7LBZijDwmM+LG144PwDZY1tdAGQHuRep0sBTdpZgOGx83kfeyA+VUz
4a3u2EkCgYEA/uqDqcDRei/GbyYTTh8Qe8cMJ2LLuPIZLdj4C49hYjGOs4MAlVJ9
c/8Ot7eycjTniAEYed8Ya310XNXi4eEacleJyGmb66MPVLawZpQXu2f/Tt2Pn6Yr
qRcL6aR43ep86kyyTrNcKCjaPELiDHZoir1sFlUNniYsYGQkMWzZZD0CgYEAyvba
dJug2pFvxAodI1jdvqT1+k+efJSD/Xh4x6WbSBpoi8LZ97sM7vwcM1On/Diy0MgC
aavHCJjk18XhCCZ6GbEN+TqZdPnk1j2C8siV4YxBETk85AWZ1ZngbbXbtTnpDWAI
ZOOaSLOZJjjTKGGVMVXWVEv47o4Bk4Q7NsZOtZMCgYBrg4ueeBWhvC6sSFnSFCYG
npAQuImF6o4WGTGc5o9DM/Wk3rbLQ+xnlQanE9IuewPAB/5DwIVzKImAcjFr5V4b
JbKWFXzOqIpZx2elDAbqYtV6dNYTlqlJes/qbhUQO8sNouV9bgaLZZeN3QOsD/DN
u1CwJpVEw4Lp8LKXKfqSXQKBgE4pHhuFyz4gf+AI3Qu9rzc5o5hPjQMA1ouIF0sb
FV+A+/3GfdYO7H4kDGAfuTNCSmpoe7Vh93XyGz6U74IJ/z9hlbYCwRHxIhT2/zSr
1jxTnMMbPb26AnHlni3huMhjksIZ12Gy3LleoH29qGOGoMOtAKrZzvVfLnA2ne8M
E0eNAoGBAOOqDn+WimDw2yvgEvkd/7YwQsQCeuJemTSdpNMRD9d7z+RAG9bnDhk0
dqH8lQ6vAMFcUBVvsOP7qd16woozefWIP1QWGYVANp6hzNaG9+RWncZk+nJ8UXZf
FURyReQftLapDjLhI39n2fw/RKwPbneU63Ryza/RuDLfVH/v97fd
-----END RSA PRIVATE KEY-----"""

def create_temp_cert_file(cert_string):
    fd, path = tempfile.mkstemp(suffix=".pem", text=True)
    with os.fdopen(fd, 'w') as f:
        f.write(cert_string.strip())
    return path

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("✅ [HOME] Kết nối thành công tới AWS IoT Core!")
        client.subscribe(TOPIC_SENSOR_SUB, qos=1)
        client.subscribe(TOPIC_STATUS_SUB, qos=1)
        print(f"📡 [HOME] Đã subscribe: {TOPIC_SENSOR_SUB} & {TOPIC_STATUS_SUB}")
    else:
        print(f"❌ [HOME] Kết nối thất bại. Mã lỗi (rc): {rc}")

def on_disconnect(client, userdata, rc):
    print("⚠️ [HOME] Đã ngắt kết nối. Đang thử kết nối lại...")
    while True:
        try:
            client.reconnect()
            break
        except Exception as e:
            time.sleep(5)

def on_message(client, userdata, msg):
    try:
        topic = msg.topic
        payload = msg.payload.decode('utf-8')
        data = json.loads(payload)

        if topic == TOPIC_SENSOR_SUB:
            latest_record = SensorData.objects.order_by('-timestamp').first()
            temp_val = data.get("temperature")
            hum_val = data.get("humidity")
            
            if temp_val is not None and hum_val is None:
                hum_val = latest_record.humidity if latest_record else 0.0
            elif hum_val is not None and temp_val is None:
                temp_val = latest_record.temperature if latest_record else 0.0
                
            SensorData.objects.create(temperature=temp_val or 0.0, humidity=hum_val or 0.0)
            print(f"   ✅ [HOME DB] Đã lưu đầy đủ: {temp_val}°C - {hum_val}%")

        elif topic.startswith("gateway/status"):
            try:
                device_name = list(data.keys())[0]
                status_val = data[device_name]
                if isinstance(status_val, str):
                    status_val = 1 if status_val.upper() in ["ON", "1", "TRUE"] else 0
                else:
                    status_val = int(status_val)
                
                DeviceStatus.objects.update_or_create(device_name=device_name, defaults={'status': status_val})
                print(f"   ✅ [HOME DB] Đã cập nhật: {device_name} -> {'ON' if status_val == 1 else 'OFF'}")
            except Exception as e:
                print(f"❌ [HOME] Lỗi cấu trúc JSON: {e}")

    except Exception as e:
        pass

def run_home_client():
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1, HOME_CLIENT_ID)
    
    print("⚙️ [HOME] Đang nạp chứng chỉ vào bộ nhớ tạm...")
    ca_path = create_temp_cert_file(AWS_CERT_CA)
    cert_path = create_temp_cert_file(AWS_CERT_CRT)
    key_path = create_temp_cert_file(AWS_CERT_PRIVATE)

    try:
        client.tls_set(ca_certs=ca_path, certfile=cert_path, keyfile=key_path, tls_version=ssl.PROTOCOL_TLSv1_2)
    except Exception as e:
        print(f"❌ [HOME LỖI] Cấu hình bảo mật thất bại: {e}")
        return

    client.on_connect = on_connect
    client.on_disconnect = on_disconnect
    client.on_message = on_message

    print(f"🔄 [HOME] Đang khởi tạo kết nối AWS: {HOME_ENDPOINT}")
    client.connect(HOME_ENDPOINT, HOME_PORT, keepalive=60)
    
    try:
        os.remove(ca_path)
        os.remove(cert_path)
        os.remove(key_path)
        print("🧹 [HOME] Đã dọn dẹp file chứng chỉ tạm.")
    except Exception:
        pass

    client.loop_forever()

# ========================================================
# CHƯƠNG TRÌNH CHÍNH
# ========================================================
if __name__ == '__main__':
    print("🚀 Đang khởi động Multi-MQTT Worker (Garden + Home)...")
    
    # 1. Kích hoạt Garden trên background thread (AWSIoTPythonSDK lo liệu)
    run_garden_client()
    
    # 2. Kích hoạt Home và khóa main thread lại bằng loop_forever()
    run_home_client()