from django.contrib import admin
from .models import Modul


@admin.register(Modul)
class ModulAdmin(admin.ModelAdmin):
    list_display = ('kode', 'judul', 'urutan', 'xp_reward', 'is_published', 'created_at')
    list_filter = ('is_published',)
    search_fields = ('kode', 'judul', 'deskripsi')
    prepopulated_fields = {'slug': ('judul',)}
