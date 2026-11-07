from urllib.parse import quote

from django.conf import settings
from django.db import models
from django.utils import timezone

PESAN_WA_BAWAAN = (
    "Halo Admin CPNS Hub, saya ingin membeli Premium {durasi} hari. "
    "Email akun saya: {email}"
)


class PengaturanCPNS(models.Model):
    nomor_wa = models.CharField(max_length=20, blank=True)
    teks_harga = models.JSONField(default=dict, blank=True)
    pesan_wa = models.TextField(default=PESAN_WA_BAWAAN)

    class Meta:
        verbose_name = "pengaturan CPNS"
        verbose_name_plural = "pengaturan CPNS"

    def __str__(self):
        return "Pengaturan CPNS"

    @classmethod
    def ambil(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj

    def durasi_tersedia(self):
        return sorted(int(k) for k in self.teks_harga if str(k).isdigit())

    def tautan_wa(self, durasi, email):
        nomor = "".join(c for c in self.nomor_wa if c.isdigit())
        if not nomor:
            return None
        try:
            pesan = self.pesan_wa.format(durasi=durasi, email=email)
        except (KeyError, IndexError, ValueError):
            pesan = PESAN_WA_BAWAAN.format(durasi=durasi, email=email)
        return f"https://wa.me/{nomor}?text={quote(pesan, safe='')}"


class Voucher(models.Model):
    kode = models.CharField(max_length=9, unique=True)
    durasi_hari = models.PositiveIntegerField()
    catatan = models.CharField(max_length=200, blank=True)
    dibuat_oleh = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="voucher_dibuat",
    )
    dibuat_pada = models.DateTimeField(auto_now_add=True)
    dipakai_oleh = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="voucher_dipakai",
    )
    dipakai_pada = models.DateTimeField(null=True, blank=True)
    dibatalkan = models.BooleanField(default=False)

    class Meta:
        verbose_name = "voucher"
        verbose_name_plural = "voucher"
        ordering = ["-dibuat_pada"]

    def __str__(self):
        return self.kode

    @property
    def status(self):
        if self.dibatalkan:
            return "dibatalkan"
        if self.dipakai_oleh_id or self.dipakai_pada:
            return "dipakai"
        return "belum_dipakai"


class PercobaanVoucher(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="percobaan_voucher",
    )
    waktu = models.DateTimeField(default=timezone.now, db_index=True)
    berhasil = models.BooleanField()

    def __str__(self):
        return f"Percobaan {self.user_id} {self.waktu:%Y-%m-%d %H:%M}"
