from django.contrib import admin
from .models import PaketUjian


@admin.register(PaketUjian)
class PaketUjianAdmin(admin.ModelAdmin):
    list_display = ('judul', 'durasi_menit', 'kkm', 'is_active', 'created_at')
    list_filter = ('is_active',)
    search_fields = ('judul', 'deskripsi')
    prepopulated_fields = {'slug': ('judul',)}
