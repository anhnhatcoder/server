import os
import json
import time
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient
from .models import CamBien, Firmware, Node
from .forms import FirmwareForm, NodeForm

# --- 1. ĐIỀU HƯỚNG & QUẢN LÝ ---
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

# --- 2. DỰ ÁN CNC PCB ---
@login_required
def cnc_view(request):
    return render(request, 'cnc_pcb_app.html')

@csrf_exempt
@login_required
def send_cnc_data(request):
    """API gửi tọa độ CNC kèm cơ chế START/END markers ổn định"""
    if request.method == 'POST':
        try:
            body = json.loads(request.body)
            coords = body.get('coords', [])
            if not coords: return JsonResponse({'status': 'error', 'message': 'Trống'})
            
            BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            PATH_TO_CERT = os.path.join(BASE_DIR, "certs", "certificate.pem.crt")
            PATH_TO_KEY = os.path.join(BASE_DIR, "certs", "private.pem.key")
            PATH_TO_ROOT = os.path.join(BASE_DIR, "certs", "AmazonRootCA1.pem")
            
            # Khởi tạo Client với ID duy nhất để tránh xung đột session
            client_id = f"Web_CNC_Pub_{int(time.time())}"
            client = AWSIoTMQTTClient(client_id)
            client.configureEndpoint("aum3f6pv7yg54-ats.iot.ap-northeast-1.amazonaws.com", 8883)
            client.configureCredentials(PATH_TO_ROOT, PATH_TO_KEY, PATH_TO_CERT)
            
            # Cấu hình để đảm bảo tin nhắn không bị drop khi disconnect nhanh
            client.configureAutoReconnectBackoffTime(1, 32, 20)
            client.configureOfflinePublishQueueing(-1)
            client.configureDrainingFrequency(2)
            client.configureConnectDisconnectTimeout(10)
            client.configureMQTTOperationTimeout(5)

            if client.connect():
                # CHỜ 0.5s ĐỂ CONNECTION ỔN ĐỊNH TRƯỚC KHI GỬI LỆNH ĐẦU TIÊN
                time.sleep(0.5) 
                
                # 1. Gửi lệnh BẮT ĐẦU (Dùng QoS 1 để đảm bảo đến nơi)
                client.publish("esp32/cnc/data", "START_JOB", 1)
                time.sleep(0.3) # Đợi một chút để Broker xử lý START_JOB

                # 2. Gửi dữ liệu G-Code theo từng gói
                chunk_size = 100 
                for i in range(0, len(coords), chunk_size):
                    chunk = coords[i:i + chunk_size]
                    payload = "|".join([f"X{p['x']}Y{p['y']}" for p in chunk])
                    client.publish("esp32/cnc/data", payload, 1)
                    time.sleep(0.1) # Tăng lên 100ms để ổn định đường truyền

                # 3. Gửi lệnh KẾT THÚC
                time.sleep(0.5)
                client.publish("esp32/cnc/data", "END_JOB", 1)
                
                # CHỜ 1s ĐỂ TẤT CẢ TIN NHẮN TRONG QUEUE ĐƯỢC GỬI XONG TRƯỚC KHI NGẮT
                time.sleep(1.0)
                
                client.disconnect()
                return JsonResponse({'status': 'success', 'message': f'Đã truyền {len(coords)} điểm thành công'})
                
            return JsonResponse({'status': 'error', 'message': 'Không thể kết nối AWS IoT'})
        except Exception as e: 
            return JsonResponse({'status': 'error', 'message': str(e)})
    return JsonResponse({'status': 'error', 'message': 'Yêu cầu không hợp lệ'})

# --- 3. API DỮ LIỆU & ĐIỀU KHIỂN ---
def get_node_data(request, node_id):
    try:
        node = Node.objects.get(node_id=node_id)
        du_lieu = CamBien.objects.filter(node=node).order_by('-thoi_gian')[:20]
        data = list(du_lieu.values('ten', 'gia_tri', 'don_vi', 'thoi_gian'))
        return JsonResponse({'danh_sach': data})
    except Node.DoesNotExist:
        return JsonResponse({'danh_sach': []})

def control_node_pump(request, node_id, device_id, state):
    return JsonResponse({'status': 'success'})

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