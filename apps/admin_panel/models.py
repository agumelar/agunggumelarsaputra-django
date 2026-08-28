from django.db import models
from django.conf import settings
import secrets


def generate_token_code():
    return secrets.token_hex(4).upper()


class EnrollmentToken(models.Model):
    """
    Token pendaftaran / aktivasi akun siswa untuk kelas tertentu.
    """
    code = models.CharField(max_length=16, default=generate_token_code, unique=True, verbose_name='Kode Token')
    kelas_target = models.CharField(max_length=50, verbose_name='Kelas Target (e.g. X RPL 1)')
    max_uses = models.PositiveIntegerField(default=36, verbose_name='Maksimal Penggunaan (Kapasitas Kelas)')
    used_count = models.PositiveIntegerField(default=0, verbose_name='Jumlah Digunakan')
    is_active = models.BooleanField(default=True, verbose_name='Status Aktif')
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='tokens_created')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Token Enrollment Siswa'
        verbose_name_plural = 'Daftar Token Enrollment'

    def __str__(self):
        return f"{self.code} ({self.kelas_target} - {self.used_count}/{self.max_uses})"
