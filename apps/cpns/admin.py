from django.contrib import admin
from .models import CpnsPackage, CpnsQuestion, CpnsAttempt


@admin.register(CpnsPackage)
class CpnsPackageAdmin(admin.ModelAdmin):
    list_display = ('kode', 'judul', 'tipe_ujian', 'kategori', 'durasi_menit', 'urutan', 'is_published')
    list_filter = ('tipe_ujian', 'kategori', 'is_published')
    search_fields = ('kode', 'judul', 'deskripsi')
    prepopulated_fields = {'slug': ('judul',)}
    ordering = ('urutan',)


@admin.register(CpnsQuestion)
class CpnsQuestionAdmin(admin.ModelAdmin):
    list_display = ('package', 'urutan', 'subtes', 'subtopik', 'kunci_jawaban')
    list_filter = ('subtes', 'package')
    search_fields = ('pertanyaan', 'subtopik', 'bedah_konsep', 'alasan_pengecoh', 'tips_cepat')
    ordering = ('package', 'urutan')
    fieldsets = (
        ('Identitas Soal', {
            'fields': ('package', 'subtes', 'subtopik', 'urutan')
        }),
        ('Narasi & Pilihan Jawaban', {
            'fields': ('pertanyaan', 'opsi_a', 'opsi_b', 'opsi_c', 'opsi_d', 'opsi_e', 'kunci_jawaban', 'bobot_tkp')
        }),
        ('Pembahasan Konsep Tuntas (3 Tingkat)', {
            'fields': ('bedah_konsep', 'alasan_pengecoh', 'tips_cepat')
        }),
    )


@admin.register(CpnsAttempt)
class CpnsAttemptAdmin(admin.ModelAdmin):
    list_display = ('get_peserta', 'package', 'mode', 'total_skor', 'skor_twk', 'skor_tiu', 'skor_tkp', 'status_lulus', 'completed_at')
    list_filter = ('status_lulus', 'mode', 'package')
    search_fields = ('user__username', 'user__email', 'session_key', 'package__kode')
    readonly_fields = ('completed_at',)

    def get_peserta(self, obj):
        return obj.user.display_name if obj.user else f"Guest ({obj.session_key[:8]})"
    get_peserta.short_description = 'Peserta'
