"""Batas percobaan login yang dipakai bersama oleh login CPNS dan login sekolah.

Kunci memakai akun yang ditemukan (u:<pk>) atau identitas yang diketik, bukan IP: di balik
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


def kunci_untuk(user, identitas):
    """Akun yang ditemukan dihitung per pk, apa pun cara mengetik identitasnya
    (email, username, NISN, NIP). Identitas tak dikenal dihitung per ketikan.
    Awalan u: dan i: mencegah dua jenis kunci saling bertabrakan."""
    if user is not None:
        return f"u:{user.pk}"
    return f"i:{kunci_identitas(identitas)}"


def terkunci(kunci, now=None):
    now = now or timezone.now()
    jumlah = PercobaanMasuk.objects.filter(
        kunci=kunci, waktu__gt=now - JEDA
    ).count()
    return jumlah >= BATAS_GAGAL


def catat_gagal(kunci, now=None):
    now = now or timezone.now()
    PercobaanMasuk.objects.filter(waktu__lt=now - UMUR_BARIS).delete()
    PercobaanMasuk.objects.create(kunci=kunci, waktu=now)


def bersihkan(kunci):
    PercobaanMasuk.objects.filter(kunci=kunci).delete()
