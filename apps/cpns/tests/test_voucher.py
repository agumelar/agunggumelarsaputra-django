import re
from datetime import timedelta

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone

from apps.cpns.akses import akses_untuk
from apps.cpns.models import PercobaanVoucher, Voucher
from apps.cpns.voucher import (
    VoucherDitolak,
    buat_kode,
    buat_voucher,
    normalisasi_kode,
    pakai_voucher,
    sisa_percobaan,
)

User = get_user_model()
POLA = re.compile(r"^[A-HJKMNP-Z2-9]{4}-[A-HJKMNP-Z2-9]{4}$")


def buat_user(nama):
    return User.objects.create_user(
        username=nama, email=f"{nama}@contoh.id", password="x-pass-123"
    )


class VoucherTest(TestCase):
    def setUp(self):
        self.now = timezone.now()
        self.user = buat_user("peserta1")

    def test_format_kode(self):
        for _ in range(200):
            self.assertRegex(buat_kode(), POLA)

    def test_buat_voucher_jumlah_dan_validasi(self):
        hasil = buat_voucher(3, 30)
        self.assertEqual(len(hasil), 3)
        self.assertEqual(Voucher.objects.count(), 3)
        with self.assertRaises(ValueError):
            buat_voucher(0, 30)
        with self.assertRaises(ValueError):
            buat_voucher(101, 30)
        with self.assertRaises(ValueError):
            buat_voucher(1, 0)

    def test_normalisasi(self):
        self.assertEqual(normalisasi_kode(" k7pm 3qxr "), "K7PM-3QXR")
        self.assertEqual(normalisasi_kode("k7pm-3qxr"), "K7PM-3QXR")
        self.assertEqual(normalisasi_kode("abc"), "ABC")

    def test_pakai_dengan_huruf_kecil(self):
        v = buat_voucher(1, 30)[0]
        akses = pakai_voucher(self.user, v.kode.lower().replace("-", " "), now=self.now)
        self.assertEqual(akses.premium_sampai, self.now + timedelta(days=30))

    def test_pakai_mulai_dari_sekarang(self):
        v = buat_voucher(1, 30)[0]
        akses = pakai_voucher(self.user, v.kode, now=self.now)
        self.assertEqual(akses.premium_sampai, self.now + timedelta(days=30))
        v.refresh_from_db()
        self.assertEqual(v.dipakai_oleh, self.user)
        self.assertEqual(v.dipakai_pada, self.now)

    def test_pakai_menambah_masa_aktif(self):
        akses = akses_untuk(self.user)
        akses.premium_sampai = self.now + timedelta(days=10)
        akses.save()
        v = buat_voucher(1, 30)[0]
        akses = pakai_voucher(self.user, v.kode, now=self.now)
        self.assertEqual(akses.premium_sampai, self.now + timedelta(days=40))

    def test_premium_kedaluwarsa_mulai_dari_sekarang(self):
        akses = akses_untuk(self.user)
        akses.premium_sampai = self.now - timedelta(days=5)
        akses.save()
        v = buat_voucher(1, 30)[0]
        akses = pakai_voucher(self.user, v.kode, now=self.now)
        self.assertEqual(akses.premium_sampai, self.now + timedelta(days=30))

    def test_voucher_sekali_pakai(self):
        v = buat_voucher(1, 30)[0]
        pakai_voucher(self.user, v.kode, now=self.now)
        lain = buat_user("peserta2")
        with self.assertRaises(VoucherDitolak) as ctx:
            pakai_voucher(lain, v.kode, now=self.now)
        self.assertEqual(ctx.exception.alasan, "tidak_valid")
        self.assertIsNone(akses_untuk(lain).premium_sampai)

    def test_voucher_tidak_bisa_dipakai_ulang_setelah_pemakai_dihapus(self):
        v = buat_voucher(1, 30)[0]
        pakai_voucher(self.user, v.kode, now=self.now)
        self.user.delete()
        v.refresh_from_db()
        self.assertIsNone(v.dipakai_oleh)
        self.assertEqual(v.status, "dipakai")
        lain = buat_user("peserta2")
        with self.assertRaises(VoucherDitolak) as ctx:
            pakai_voucher(lain, v.kode, now=self.now)
        self.assertEqual(ctx.exception.alasan, "tidak_valid")
        self.assertIsNone(akses_untuk(lain).premium_sampai)

    def test_voucher_dibatalkan_ditolak(self):
        v = buat_voucher(1, 30)[0]
        v.dibatalkan = True
        v.save()
        with self.assertRaises(VoucherDitolak) as ctx:
            pakai_voucher(self.user, v.kode, now=self.now)
        self.assertEqual(ctx.exception.alasan, "tidak_valid")
        self.assertIsNone(akses_untuk(self.user).premium_sampai)

    def test_batas_lima_gagal(self):
        for harapan in (4, 3, 2, 1, 0):
            with self.assertRaises(VoucherDitolak) as ctx:
                pakai_voucher(self.user, "SALAH-KODE", now=self.now)
            self.assertEqual(ctx.exception.alasan, "tidak_valid")
            self.assertEqual(ctx.exception.sisa, harapan)
        with self.assertRaises(VoucherDitolak) as ctx:
            pakai_voucher(self.user, "SALAH-KODE", now=self.now)
        self.assertEqual(ctx.exception.alasan, "terlalu_sering")
        self.assertEqual(ctx.exception.sisa, 0)
        self.assertEqual(PercobaanVoucher.objects.filter(user=self.user).count(), 5)

        nanti = self.now + timedelta(minutes=61)
        v = buat_voucher(1, 30)[0]
        akses = pakai_voucher(self.user, v.kode, now=nanti)
        self.assertEqual(akses.premium_sampai, nanti + timedelta(days=30))

    def test_berhasil_tidak_mengurangi_sisa(self):
        v = buat_voucher(1, 30)[0]
        pakai_voucher(self.user, v.kode, now=self.now)
        self.assertEqual(sisa_percobaan(self.user, now=self.now), 5)
        self.assertEqual(
            PercobaanVoucher.objects.filter(user=self.user, berhasil=True).count(), 1
        )
