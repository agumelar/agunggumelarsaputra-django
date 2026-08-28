from django.db import models
from django.conf import settings


class PaketUjian(models.Model):
    """
    Paket Simulasi CBT TKA (Tes Kemampuan Akademik / Kejuruan) PPLG.
    """
    judul = models.CharField(max_length=200, verbose_name='Judul Paket Ujian')
    slug = models.SlugField(max_length=200, unique=True)
    deskripsi = models.TextField(blank=True, verbose_name='Petunjuk Pengerjaan')
    durasi_menit = models.PositiveIntegerField(default=60, verbose_name='Durasi (Menit)')
    kkm = models.PositiveIntegerField(default=75, verbose_name='KKM (Kriteria Ketercapaian Tujuan Pembelajaran)')
    is_active = models.BooleanField(default=True, verbose_name='Status Aktif')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Paket Ujian TKA'
        verbose_name_plural = 'Daftar Paket Ujian TKA'

    def __str__(self):
        return self.judul
