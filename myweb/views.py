import os
import json
import time
import ssl
import tempfile
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
import paho.mqtt.publish as mqtt_publish
from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient

from .models import CamBien, Firmware, Node, Room, Device
from .forms import FirmwareForm, NodeForm

# ==========================================
# HÀM PHỤ TRỢ: GỬI LỆNH XUỐNG SMART GARDEN
# ==========================================
def publish_garden_command(node_id, payload_dict):
    ENDPOINT = "aum3f6pv7yg54-ats.iot.ap-northeast-1.amazonaws.com"
    CLIENT_ID = f"Django_Web_Garden_{int(time.time())}" 
    
    BASE_CERT_PATH = "/app/certs"
    PATH_TO_ROOT = os.path.join(BASE_CERT_PATH, "AmazonRootCA1.pem")
    PATH_TO_KEY = os.path.join(BASE_CERT_PATH, "private.pem.key")
    PATH_TO_CERT = os.path.join(BASE_CERT_PATH, "certificate.pem.crt")
    
    topic = f"esp32/{node_id}/control"

    try:
        mqtt_client = AWSIoTMQTTClient(CLIENT_ID)
        mqtt_client.configureEndpoint(ENDPOINT, 8883)
        mqtt_client.configureCredentials(PATH_TO_ROOT, PATH_TO_KEY, PATH_TO_CERT)
        
        mqtt_client.configureConnectDisconnectTimeout(5)
        mqtt_client.configureMQTTOperationTimeout(5)
        
        mqtt_client.connect()
        mqtt_client.publish(topic, json.dumps(payload_dict), 1) 
        mqtt_client.disconnect()
        return True, ""
    except Exception as e:
        return False, str(e)

# ==========================================
# HÀM PHỤ TRỢ: GỬI LỆNH XUỐNG SMART HOME
# ==========================================
def publish_home_command(device_name, state):
    HOME_ENDPOINT = "azi4l8ersx95s-ats.iot.ap-southeast-2.amazonaws.com"
    TOPIC = "gateway/control/device"
    
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

    def create_temp_file(cert_string):
        fd, path = tempfile.mkstemp(suffix=".pem", text=True)
        with os.fdopen(fd, 'w') as f:
            f.write(cert_string.strip())
        return path

    ca_path = create_temp_file(AWS_CERT_CA)
    cert_path = create_temp_file(AWS_CERT_CRT)
    key_path = create_temp_file(AWS_CERT_PRIVATE)
    
    payload = json.dumps({device_name: state.upper()})

    try:
        mqtt_publish.single(
            topic=TOPIC,
            payload=payload,
            qos=1,
            hostname=HOME_ENDPOINT,
            port=8883,
            client_id=f"Django_Web_Home_{int(time.time())}",
            tls={'ca_certs': ca_path, 'certfile': cert_path, 'keyfile': key_path, 'tls_version': ssl.PROTOCOL_TLSv1_2}
        )
        success = True
        error_msg = ""
    except Exception as e:
        success = False
        error_msg = str(e)
    finally:
        os.remove(ca_path)
        os.remove(cert_path)
        os.remove(key_path)

    return success, error_msg


# ==========================================
# 1. ĐIỀU HƯỚNG & QUẢN LÝ (SMART GARDEN)
# ==========================================
@login_required
def login_success(request):
    next_url = request.GET.get('next') or request.POST.get('next')
    if next_url: return redirect(next_url)
    if request.user.is_superuser: return redirect('/admin/')
    return redirect('portal_home')

@login_required
def home_view(request):
    nodes = Node.objects.all()
    if request.method == 'POST':
        form = NodeForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('home')
    else:
        form = NodeForm()
    return render(request, 'home.html', {'nodes': nodes, 'form': form})

@login_required
def delete_node(request, node_id):
    node = get_object_or_404(Node, node_id=node_id)
    node.delete()
    return redirect('home')

@login_required
def node_dashboard(request, node_id):
    node = get_object_or_404(Node, node_id=node_id)
    du_lieu = CamBien.objects.filter(node=node).order_by('-thoi_gian')[:10]
    return render(request, 'dashboard.html', {'node': node, 'danh_sach_cam_bien': du_lieu})


# ==========================================
# 2. ĐIỀU HƯỚNG & QUẢN LÝ (SMART HOME)
# ==========================================
@login_required(login_url='/accounts/login/') 
def smarthome_dashboard(request):
    rooms = Room.objects.all()
    context = {
        'rooms': rooms,
    }
    return render(request, 'smarthome_dashboard.html', context)

@login_required
def add_room(request):
    if request.method == 'POST':
        room_name = request.POST.get('room_name')
        if room_name:
            # Lưu phòng mới vào database
            Room.objects.get_or_create(name=room_name)
    # Xong việc thì tải lại trang Smart Home
    return redirect('smarthome_app')

@login_required
def delete_room(request, room_id):
    if request.method == 'POST':
        room = get_object_or_404(Room, id=room_id)
        room.delete()
    return redirect('smarthome_app')

@login_required
def add_device(request, room_id):
    if request.method == 'POST':
        room = get_object_or_404(Room, id=room_id)
        device_name = request.POST.get('device_name')
        device_key = request.POST.get('device_key')
        
        if device_name and device_key:
            Device.objects.create(
                room=room,
                name=device_name,
                device_key=device_key
            )
    return redirect('smarthome_app')

@login_required
def delete_device(request, device_id):
    if request.method == 'POST':
        device = get_object_or_404(Device, id=device_id)
        device.delete()
    return redirect('smarthome_app')


# ==========================================
# 3. API DỮ LIỆU & ĐIỀU KHIỂN
# ==========================================
def get_node_data(request, node_id):
    try:
        node = Node.objects.get(node_id=node_id)
        du_lieu = CamBien.objects.filter(node=node).order_by('-thoi_gian')[:20]
        data = list(du_lieu.values('ten', 'gia_tri', 'don_vi', 'thoi_gian'))
        return JsonResponse({'danh_sach': data})
    except Node.DoesNotExist:
        return JsonResponse({'danh_sach': []})

def control_node_pump(request, node_id, device_id, state):
    """
    Điều khiển thiết bị của Smart Garden.
    """
    try:
        node = Node.objects.get(node_id=node_id)
        payload = {device_id: state.upper()}
        success, error_msg = publish_garden_command(node_id, payload)
        
        if success:
            return JsonResponse({'status': 'success', 'message': f'GARDEN: Đã gửi lệnh {state} tới {device_id}'})
        else:
            return JsonResponse({'status': 'error', 'message': f'Lỗi Garden MQTT: {error_msg}'}, status=500)
    except Node.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Node không tồn tại'}, status=404)

def control_smart_home_device(request, device_id, state):
    """
    Điều khiển thiết bị của Smart Home.
    """
    success, error_msg = publish_home_command(device_id, state)
    if success:
        return JsonResponse({'status': 'success', 'message': f'HOME: Đã gửi lệnh {state} tới {device_id}'})
    return JsonResponse({'status': 'error', 'message': f'Lỗi Home MQTT: {error_msg}'}, status=500)


# ==========================================
# 4. OTA UPDATE 
# ==========================================
@login_required
def ota_view(request):
    latest_fw = Firmware.objects.last()
    if request.method == 'POST':
        form = FirmwareForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('ota')
    else:
        form = FirmwareForm()
    return render(request, 'ota.html', {'form': form, 'latest_fw': latest_fw})

def check_firmware(request):
    latest = Firmware.objects.last()
    if latest:
        return JsonResponse({"version": latest.version, "url": request.build_absolute_uri(latest.file_bin.url)})
    return JsonResponse({"error": "No firmware"}, status=404)