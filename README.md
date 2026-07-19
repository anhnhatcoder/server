Yêu cầu hệ thống (Prerequisites)
Hệ điều hành: Linux (Ubuntu/Debian), macOS hoặc Windows (có cài đặt WSL2).

Đã cài đặt Docker và Docker Compose.

Các bước cài đặt (Installation)
Bước 1: Tải mã nguồn về máy

Bash
git clone https://github.com/anhnhatcoder/server.git
cd ten-kho-chua-cua-ban
Bước 2: Cấu hình chứng chỉ AWS IoT
Người dùng cần tạo chứng chỉ trên AWS IoT Core của riêng họ và đặt vào hệ thống:

Copy các file chứng chỉ (RootCA, Certificate, Private Key) vào thư mục certs/.

Hoặc điền nội dung chứng chỉ vào các biến tương ứng trong mã nguồn (nếu có).

Bước 3: Khởi chạy hệ thống bằng Docker
Build và chạy các container ngầm (bao gồm web server và các service đi kèm):
```c
sudo docker compose up -d --build
```
Bước 4: Cấp quyền cho Cơ sở dữ liệu (Đặc biệt quan trọng trên Linux)
Để tránh lỗi readonly khi ghi dữ liệu vào SQLite, người dùng cần cấp quyền cho file database:
```c
sudo chmod 666 db.sqlite3
```
Bước 5: Khởi tạo Database và Tạo tài khoản quản trị
Chạy lệnh migrate để tạo các bảng (như Room, Device, Node...) trong database:
```c
sudo docker compose exec web python manage.py makemigrations
sudo docker compose exec web python manage.py migrate
```
Sau đó, tạo tài khoản Admin để đăng nhập vào hệ thống:
```c
sudo docker compose exec web python manage.py createsuperuser
```
(Điền username, email và password theo hướng dẫn trên màn hình)

Sử dụng (Usage)
Mở trình duyệt và truy cập vào địa chỉ: http://localhost:8000 (hoặc IP của máy chủ/Raspberry Pi). Đăng nhập bằng tài khoản Superuser vừa tạo để trải nghiệm các chức năng Smart Garden và Smart Home.
