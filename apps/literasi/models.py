from django.db import models
from django.conf import settings


class LaporanLiterasi(models.Model):
    """
    Laporan kegiatan literasi mingguan (Rabu Literasi - RESIK).
    """
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='laporan_literasi')
    judul_bacaan = models.CharField(max_length=255, verbose_name='Judul Buku / Artikel')
    penulis = models.CharField(max_length=200, blank=True, verbose_name='Penulis / Sumber')
    rangkuman = models.TextField(verbose_name='Rangkuman / Refleksi')
    word_count = models.PositiveIntegerField(default=0, verbose_name='Jumlah Kata')
    is_verified = models.BooleanField(default=False, verbose_name='Diverifikasi Guru')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Laporan Literasi RESIK'
        verbose_name_plural = 'Daftar Laporan Literasi RESIK'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.display_name} - {self.judul_bacaan} ({self.created_at.strftime('%d/%m/%Y')})"
