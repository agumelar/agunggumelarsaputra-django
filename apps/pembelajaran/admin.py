from django.contrib import admin
from .models import Modul, UserSubmission, UserProgress


@admin.register(Modul)
class ModulAdmin(admin.ModelAdmin):
    list_display = ('kode', 'judul', 'kategori', 'urutan', 'total_xp_display', 'is_published', 'created_at')
    list_filter = ('kategori', 'level', 'is_published')
    search_fields = ('kode', 'judul', 'deskripsi')
    prepopulated_fields = {'slug': ('judul',)}

    def total_xp_display(self, obj):
        return f"{obj.total_xp} XP"
    total_xp_display.short_description = 'Total XP'


@admin.register(UserSubmission)
class UserSubmissionAdmin(admin.ModelAdmin):
    list_display = ('user', 'modul', 'submission_type', 'status', 'teacher_level', 'teacher_score', 'submitted_at')
    list_filter = ('submission_type', 'status', 'teacher_level', 'modul')
    search_fields = ('user__username', 'user__first_name', 'user__last_name', 'modul__judul', 'drive_url')


@admin.register(UserProgress)
class UserProgressAdmin(admin.ModelAdmin):
    list_display = ('user', 'modul', 'token', 'completed_at')
    list_filter = ('modul', 'completed_at')
    search_fields = ('user__username', 'user__first_name', 'user__last_name', 'modul__judul')
