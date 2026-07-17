from django.db import models

# 1. Bảng quản lý các Node (Khu vườn)
class Node(models.Model):
    node_id = models.CharField(max_length=50, unique=True) # VD: "vuon_sau_nha"
    name = models.CharField(max_length=100) # VD: "Vườn Sân Sau"
    location = models.CharField(max_length=200, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.node_id})"

# 2. Bảng dữ liệu Cảm biến (Gắn với Node)
class CamBien(models.Model):
    # Liên kết dữ liệu với Node cụ thể
    node = models.ForeignKey(Node, on_delete=models.CASCADE, related_name='sensors')
    ten = models.CharField(max_length=50)
    gia_tri = models.FloatField()
    don_vi = models.CharField(max_length=10)
    thoi_gian = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"[{self.node.node_id}] {self.ten}: {self.gia_tri}"

# 3. Bảng Firmware (Giữ nguyên)
class Firmware(models.Model):
    version = models.CharField(max_length=20)
    file_bin = models.FileField(upload_to='firmware/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    description = models.TextField(blank=True)