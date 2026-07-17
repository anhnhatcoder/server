from django.shortcuts import render

def portal_home(request):
    """
    Hàm xử lý hiển thị trang chủ Portal (Trang cổng dịch vụ tổng hợp).
    
    LƯU Ý ĐIỀU HƯỚNG:
    - Trang này hiện đang được cấu hình làm trang gốc (ROOT URL).
    - Truy cập tại: http://anhnhatiot.cloud/
    - Nếu truy cập /home/, hệ thống sẽ báo lỗi 404 trừ khi bạn cấu hình thêm trong urls.py.
    
    Chức năng:
    - Trả về giao diện chính chứa danh sách các dự án IoT (Smart Garden, AI Vision, IIoT...).
    - Hỗ trợ truyền dữ liệu động vào giao diện thông qua context.
    - Template mục tiêu: portal_main/templates/portal_main/home.html
    """
    
    # Khởi tạo context để truyền các biến vào template
    context = {
        'page_title': 'Anh Nhật IoT Ecosystem - Gateway',
        'status': 'System Online',
        'active_projects': 4, # Số lượng dự án đang hiển thị
    }
    
    # Thực hiện render template
    return render(request, 'portal_main/home.html', context)