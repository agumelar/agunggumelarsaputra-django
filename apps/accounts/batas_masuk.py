"""Batas percobaan login yang dipakai bersama oleh login CPNS dan login sekolah.

Kunci memakai identitas yang diketik (strip + huruf kecil), bukan IP: di balik
nginx dan Docker, REMOTE_ADDR selalu alamat proxy. Hitungan disimpan di database
agar semua worker gunicorn berbagi angka yang sama.
"""
from datetime import timedelta

from django.utils import timezone

from .models import PercobaanMasuk

BATAS_GAGAL = 5
JEDA = timedelta(minutes=15)
UMUR_BARIS = timedelta(days=1)
PESAN_TERKUNCI = "Terlalu banyak percobaan masuk. Coba lagi dalam 15 menit."


def kunci_identitas(identitas):
    return identitas.strip().lower()[:254]


def terkunci(identitas, now=None):
    now = now or timezone.now()
    jumlah = PercobaanMasuk.objects.filter(
        kunci=kunci_identitas(identitas), waktu__gt=now - JEDA
    ).count()
    return jumlah >= BATAS_GAGAL


def catat_gagal(identitas, now=None):
    now = now or timezone.now()
    PercobaanMasuk.objects.filter(waktu__lt=now - UMUR_BARIS).delete()
    PercobaanMasuk.objects.create(kunci=kunci_identitas(identitas), waktu=now)


def bersihkan(identitas):
    PercobaanMasuk.objects.filter(kunci=kunci_identitas(identitas)).delete()
