from django.contrib import admin
from .models import LaporanLiterasi


@admin.register(LaporanLiterasi)
class LaporanLiterasiAdmin(admin.ModelAdmin):
    list_display = ('user', 'judul_bacaan', 'word_count', 'is_verified', 'created_at')
    list_filter = ('is_verified', 'created_at')
    search_fields = ('user__username', 'user__first_name', 'judul_bacaan', 'rangkuman')
