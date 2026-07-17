import os
import json
import time
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.conf import settings
from django.contrib.auth.decorators import login_required

# YÊU CẦU ĐĂNG NHẬP ĐỂ XEM DASHBOARD
@login_required
def ai_dashboard(request):
    """Chỉ người dùng đã đăng nhập mới có thể vào trang này"""
    return render(request, 'esp_ai/dashboard.html')

@csrf_exempt
def upload_capture(request):
    """API này vẫn để mở cho ESP32 POST ảnh lên (không yêu cầu login session)"""
    if request.method == 'POST':
        try:
            image_file = request.FILES.get('image')
            name = request.POST.get('name', 'Unknown')
            conf = request.POST.get('confidence', '0')
            
            if image_file:
                capture_dir = os.path.join(settings.MEDIA_ROOT, 'captures')
                os.makedirs(capture_dir, exist_ok=True)
                
                save_path = 'captures/latest.jpg'
                if default_storage.exists(save_path):
                    default_storage.delete(save_path)
                
                default_storage.save(save_path, ContentFile(image_file.read()))
                
                status_path = os.path.join(capture_dir, 'status.json')
                status_data = {
                    'name': name, 
                    'confidence': conf,
                    'timestamp': time.time() 
                }
                with open(status_path, 'w') as f:
                    json.dump(status_data, f)

                return JsonResponse({'status': 'success'})
            return JsonResponse({'status': 'error'}, status=400)
        except Exception as e:
            return JsonResponse({'status': 'error', 'msg': str(e)}, status=500)
    return JsonResponse({'status': 'error'}, status=405)

def get_ai_status(request):
    """Dữ liệu trạng thái cho Dashboard (được bảo vệ bởi login ở client side)"""
    try:
        status_path = os.path.join(settings.MEDIA_ROOT, 'captures/status.json')
        if os.path.exists(status_path):
            with open(status_path, 'r') as f:
                data = json.load(f)
        else:
            data = {'name': 'Unknown', 'confidence': '0', 'timestamp': 0}
        
        data['image_url'] = settings.MEDIA_URL + 'captures/latest.jpg'
        return JsonResponse(data)
    except:
        return JsonResponse({'name': 'Error', 'confidence': '0', 'timestamp': 0})