from django.contrib import admin
from .models import TkaPackage, TkaQuestion, TkaAttempt


class TkaQuestionInline(admin.TabularInline):
    model = TkaQuestion
    extra = 1
    fields = ('urutan', 'question_text', 'correct_answer', 'category')


@admin.register(TkaPackage)
class TkaPackageAdmin(admin.ModelAdmin):
    list_display = ('kode', 'judul', 'durasi_menit', 'passing_grade', 'total_questions_count', 'is_published', 'created_at')
    list_filter = ('kategori', 'level', 'is_published')
    search_fields = ('kode', 'judul', 'deskripsi')
    prepopulated_fields = {'slug': ('judul',)}
    inlines = [TkaQuestionInline]


@admin.register(TkaQuestion)
class TkaQuestionAdmin(admin.ModelAdmin):
    list_display = ('package', 'urutan', 'short_question', 'correct_answer', 'category')
    list_filter = ('package', 'category')
    search_fields = ('question_text', 'explanation')

    def short_question(self, obj):
        return obj.question_text[:80] + '...' if len(obj.question_text) > 80 else obj.question_text
    short_question.short_description = 'Pertanyaan'


@admin.register(TkaAttempt)
class TkaAttemptAdmin(admin.ModelAdmin):
    list_display = ('user', 'package', 'attempt_number', 'score', 'correct_answers', 'total_questions', 'is_passed', 'xp_earned', 'completed_at')
    list_filter = ('package', 'is_passed', 'completed_at')
    search_fields = ('user__username', 'user__first_name', 'user__last_name', 'package__judul')
