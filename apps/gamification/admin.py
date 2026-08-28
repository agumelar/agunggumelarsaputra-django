from django.contrib import admin
from .models import XPHistory


@admin.register(XPHistory)
class XPHistoryAdmin(admin.ModelAdmin):
    list_display = ('user', 'amount', 'category', 'description', 'created_at')
    list_filter = ('category', 'created_at')
    search_fields = ('user__username', 'user__first_name', 'description')
