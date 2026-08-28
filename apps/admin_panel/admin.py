from django.contrib import admin
from .models import EnrollmentToken


@admin.register(EnrollmentToken)
class EnrollmentTokenAdmin(admin.ModelAdmin):
    list_display = ('code', 'kelas_target', 'used_count', 'max_uses', 'is_active', 'created_by', 'created_at')
    list_filter = ('is_active', 'kelas_target')
    search_fields = ('code', 'kelas_target')
