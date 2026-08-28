from django.contrib import admin
from .models import EnrollmentToken, UserEnrollment


class UserEnrollmentInline(admin.TabularInline):
    model = UserEnrollment
    extra = 0
    readonly_fields = ('user', 'enrolled_at')


@admin.register(EnrollmentToken)
class EnrollmentTokenAdmin(admin.ModelAdmin):
    list_display = ('token', 'title', 'target_class', 'target_type', 'used_count_display', 'max_uses', 'is_active', 'created_at')
    list_filter = ('is_active', 'target_class', 'target_type')
    search_fields = ('token', 'title', 'target_class')
    inlines = [UserEnrollmentInline]

    def used_count_display(self, obj):
        return obj.used_count
    used_count_display.short_description = 'Terdaftar'


@admin.register(UserEnrollment)
class UserEnrollmentAdmin(admin.ModelAdmin):
    list_display = ('user', 'token', 'enrolled_at')
    list_filter = ('token__target_class', 'enrolled_at')
    search_fields = ('user__username', 'user__first_name', 'user__last_name', 'token__token')
