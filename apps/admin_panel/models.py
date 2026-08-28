from django.db import models
from django.conf import settings
import random
import string


def generate_random_token(prefix='RPL'):
    """Generate token unik 4 karakter alfanumerik bersih (misal: RPL-8F3A)."""
    chars = 'ABCDEFGHJKLMNPQRSTUVWXYZ23456789'
    rand = ''.join(random.choices(chars, k=4))
    return f"{prefix.upper()}-{rand}"


# Backward compatibility alias
generate_token_code = generate_random_token


class EnrollmentToken(models.Model):
    """
    Token pendaftaran / sesi KBM untuk rombel dan materi tertentu.
    Mirroring struktur enrollment_tokens dari arsitektur Neon Legacy.
    """
    TARGET_TYPE_CHOICES = [
        ('all', 'Akses Penuh / Semua Sesi'),
        ('module', 'Modul Pembelajaran Tertentu'),
        ('tka', 'Simulasi CBT TKA'),
    ]

    token = models.CharField(
        max_length=32,
        unique=True,
        verbose_name='Kode Token Sesi',
        help_text='Contoh: RPL-7K9A atau X-RPL-1'
    )
    title = models.CharField(
        max_length=200,
        verbose_name='Judul Sesi / KBM',
        help_text='Contoh: KBM Orientasi PPLG Semester Gasal'
    )
    description = models.TextField(
        blank=True,
        null=True,
        verbose_name='Deskripsi / Catatan Guru'
    )
    target_type = models.CharField(
        max_length=20,
        choices=TARGET_TYPE_CHOICES,
        default='all',
        verbose_name='Tipe Target Akses'
    )
    target_slug = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name='Slug Target (Modul / TKA)'
    )
    target_class = models.CharField(
        max_length=50,
        default='Semua Kelas',
        verbose_name='Rombel / Kelas Sasaran',
        help_text='Contoh: X PPLG 1, XI RPL 1, XII RPL 1, atau Semua Kelas'
    )
    max_uses = models.PositiveIntegerField(
        default=36,
        verbose_name='Kapasitas Maksimal Siswa'
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name='Status Sesi Aktif'
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='tokens_created',
        verbose_name='Dibuat Oleh Guru'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Waktu Dibuat'
    )
    expires_at = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name='Batas Waktu Kadaluarsa'
    )

    class Meta:
        verbose_name = 'Token Sesi / Enrollment'
        verbose_name_plural = 'Daftar Token Sesi'
        ordering = ['-created_at']

    @property
    def used_count(self):
        return self.user_enrollments.count()

    @property
    def is_full(self):
        return self.used_count >= self.max_uses

    def __str__(self):
        return f"{self.token} - {self.title} ({self.target_class})"


class UserEnrollment(models.Model):
    """
    Pencatatan sesi enrollment siswa ke dalam token tertentu.
    Mirroring user_enrollments dari Neon Legacy.
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='enrollments',
        verbose_name='Siswa'
    )
    token = models.ForeignKey(
        EnrollmentToken,
        on_delete=models.CASCADE,
        related_name='user_enrollments',
        verbose_name='Token Sesi'
    )
    enrolled_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Waktu Bergabung'
    )

    class Meta:
        verbose_name = 'User Enrollment'
        verbose_name_plural = 'Daftar User Enrollment'
        unique_together = ('user', 'token')
        ordering = ['-enrolled_at']

    def __str__(self):
        return f"{self.user.display_name} -> {self.token.token}"
