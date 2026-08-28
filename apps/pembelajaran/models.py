from django.db import models
from django.conf import settings


class Modul(models.Model):
    """
    16 Modul Orientasi PPLG / Konsentrasi Keahlian RPL.
    """
    kode = models.CharField(max_length=20, unique=True, verbose_name='Kode Modul (e.g. MOD-01)')
    judul = models.CharField(max_length=255, verbose_name='Judul Modul')
    slug = models.SlugField(max_length=255, unique=True)
    deskripsi = models.TextField(verbose_name='Deskripsi Singkat')
    urutan = models.PositiveIntegerField(default=1, verbose_name='Urutan')
    xp_reward = models.PositiveIntegerField(default=100, verbose_name='Reward XP')
    is_published = models.BooleanField(default=True, verbose_name='Status Publikasi')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Modul Pembelajaran'
        verbose_name_plural = 'Daftar Modul Pembelajaran'
        ordering = ['urutan']

    def __str__(self):
        return f"{self.kode} - {self.judul}"
