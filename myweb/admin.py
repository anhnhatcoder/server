from django.contrib import admin
from .models import CamBien

class CamBienAdmin(admin.ModelAdmin):
    list_display = ('ten', 'gia_tri', 'don_vi', 'thoi_gian')
    list_filter = ('ten', 'thoi_gian')
    ordering = ('-thoi_gian',)

admin.site.register(CamBien, CamBienAdmin)
