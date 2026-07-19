Yêu cầu hệ thống (Prerequisites)
Hệ điều hành: Linux (Ubuntu/Debian), macOS hoặc Windows (có cài đặt WSL2).

Đã cài đặt Docker và Docker Compose.

### Các bước cài đặt (Installation)
**Bước 0: Cài đặt Docker & Docker Compose**
Nếu máy bạn chưa có Docker, hãy làm theo hướng dẫn sau tùy thuộc vào hệ điều hành đang sử dụng:

*👉 Dành cho Windows / macOS:*
1. Tải và cài đặt **Docker Desktop** từ trang chủ chính thức: [https://www.docker.com/products/docker-desktop/](https://www.docker.com/products/docker-desktop/)
2. Chạy ứng dụng Docker Desktop (trên Windows, hãy đảm bảo tính năng WSL2 đã được bật theo hướng dẫn của trình cài đặt).
3. Chờ Docker khởi động
Quá trình khởi động có thể mất từ 1-2 phút (đặc biệt là nếu dùng WSL2). Bạn hãy để ý góc dưới bên trái của cửa sổ Docker Desktop:
Nó sẽ hiện màu cam hoặc chữ Starting...
Khi nào nó chuyển sang màu xanh lá cây và báo Engine running, nghĩa là Docker đã sẵn sàng.

*👉 Dành cho Linux (Ubuntu / Debian / Raspberry Pi OS):*
Mở Terminal và chạy lần lượt các lệnh sau để tự động cài đặt bản Docker mới nhất:
```bash
curl -fsSL [https://get.docker.com](https://get.docker.com) -o get-docker.sh
sudo sh get-docker.sh
```
**Bước 1: Tải mã nguồn về máy**

```Bash
cd ten-kho-chua-cua-ban
git clone https://github.com/anhnhatcoder/server.git
```
**Bước 2: Cấu hình chứng chỉ AWS IoT**
Người dùng cần tạo chứng chỉ trên AWS IoT Core của riêng họ và đặt vào hệ thống:

Copy các file chứng chỉ (RootCA, Certificate, Private Key) vào thư mục certs/.

Hoặc điền nội dung chứng chỉ vào các biến tương ứng trong mã nguồn (nếu có).

**Bước 3: Khởi chạy hệ thống bằng Docker**
Build và chạy các container ngầm (bao gồm web server và các service đi kèm):
```bash
//linux
cd server
sudo docker compose up -d --build
//window
cd server
docker compose up -d --build
```
**Bước 4: Cấp quyền cho Cơ sở dữ liệu (Đặc biệt quan trọng trên Linux)**
Để tránh lỗi readonly khi ghi dữ liệu vào SQLite, người dùng cần cấp quyền cho file database:
```bash
//linux
sudo chmod 666 db.sqlite3
```
**Bước 5: Khởi tạo Database và Tạo tài khoản quản trị**
Chạy lệnh migrate để tạo các bảng (như Room, Device, Node...) trong database:
```bash
//linux
sudo docker compose exec web python manage.py makemigrations
sudo docker compose exec web python manage.py migrate
//window
docker compose exec web python manage.py makemigrations
docker compose exec web python manage.py migrate
```
Sau đó, tạo tài khoản Admin để đăng nhập vào hệ thống:
```bash
//linux
sudo docker compose exec web python manage.py createsuperuser
//window
docker compose exec web python manage.py createsuperuser
```
(Điền username, email và password theo hướng dẫn trên màn hình)

Sử dụng (Usage)
Mở trình duyệt và truy cập vào địa chỉ: http://localhost:8000 (hoặc IP của máy chủ/Raspberry Pi). Đăng nhập bằng tài khoản Superuser vừa tạo để trải nghiệm các chức năng Smart Garden và Smart Home.
