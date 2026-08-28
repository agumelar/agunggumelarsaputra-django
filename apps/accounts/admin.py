from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'display_name', 'role', 'kelas', 'nisn', 'xp', 'streak_count', 'is_staff')
    list_filter = ('role', 'kelas', 'is_staff', 'is_superuser', 'is_active')
    search_fields = ('username', 'first_name', 'last_name', 'nisn', 'nip', 'email')
    
    fieldsets = UserAdmin.fieldsets + (
        ('Informasi Vokasi & RPL', {
            'fields': ('role', 'nisn', 'nip', 'kelas', 'avatar', 'bio', 'github_username'),
        }),
        ('Gamifikasi & Aktivitas', {
            'fields': ('xp', 'streak_count', 'last_active_date'),
        }),
    )

    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Informasi Vokasi & RPL', {
            'fields': ('role', 'nisn', 'nip', 'kelas'),
        }),
    )
