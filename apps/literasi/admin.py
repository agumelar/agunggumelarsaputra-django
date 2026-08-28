from django.contrib import admin
from .models import LiterasiReport, LiterasiPeerReview


class LiterasiPeerReviewInline(admin.TabularInline):
    model = LiterasiPeerReview
    extra = 0
    fields = ('reviewer', 'rating', 'comment', 'created_at')
    readonly_fields = ('created_at',)


@admin.register(LiterasiReport)
class LiterasiReportAdmin(admin.ModelAdmin):
    list_display = ('user', 'week_number', 'report_date', 'book_title', 'author', 'word_count', 'final_score', 'status')
    list_filter = ('week_number', 'status', 'source_type', 'report_date')
    search_fields = ('user__username', 'user__first_name', 'user__last_name', 'book_title', 'author')
    inlines = [LiterasiPeerReviewInline]


@admin.register(LiterasiPeerReview)
class LiterasiPeerReviewAdmin(admin.ModelAdmin):
    list_display = ('reviewer', 'report', 'rating', 'created_at')
    list_filter = ('rating', 'created_at')
    search_fields = ('reviewer__username', 'reviewer__first_name', 'report__book_title')
