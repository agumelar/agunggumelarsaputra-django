from io import StringIO
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.db import connection
from django.test import TestCase, override_settings
from django.test.utils import CaptureQueriesContext

from apps.cpns.models import PengaturanCPNS, SkemaUjian
from apps.cpns.tests.pabrik import buat_soal
from apps.cpns.tests.test_impor_lama import lama, paket

User = get_user_model()
KISI_DRAF = "# Kisi-kisi" + chr(10) + "Draf, menunggu persetujuan pemilik."
KISI_OK = "# Kisi-kisi" + chr(10) + "Disetujui pemilik."
MODUL = "apps.cpns.management.commands.cpns_cek_produksi"


def jalankan():
    out = StringIO()
    call_command("cpns_cek_produksi", stdout=out)
    return out.getvalue()


def blok(teks, awal):
    """Baris judul butir yang memuat teks awal, plus baris rincian di bawahnya."""
    baris = teks.splitlines()
    for i, b in enumerate(baris):
        if b.startswith("[") and awal in b:
            hasil = [b]
            for lanjut in baris[i + 1 :]:
                if not lanjut.startswith("    "):
                    break
                hasil.append(lanjut)
            return "\n".join(hasil)
    raise AssertionError(f"Butir {awal!r} tidak ada di keluaran:\n{teks}")


class RingkasanTests(TestCase):
    def test_ringkasan_dan_label(self):
        teks = jalankan()
        self.assertEqual(teks.count("[OK]") + teks.count("[PERLU TINDAKAN]"), 7)
        n = teks.count("[PERLU TINDAKAN]")
        self.assertIn(f"Ringkasan: {n} butir perlu tindakan.", teks)

    def test_tidak_menulis(self):
        User.objects.create_user("u1", "Dobel@x.id", "rahasia-uji")
        User.objects.create_user("u2", "dobel@x.id", "rahasia-uji")
        lama(paket())
        buat_soal("TWK")
        with CaptureQueriesContext(connection) as ctx:
            jalankan()
        self.assertTrue(ctx.captured_queries)
        for q in ctx.captured_queries:
            awal = q["sql"].lstrip().upper()
            self.assertFalse(awal.startswith(("INSERT", "UPDATE", "DELETE")), q["sql"])

    def test_tidak_membuat_pengaturan(self):
        self.assertFalse(PengaturanCPNS.objects.exists())
        jalankan()
        self.assertFalse(PengaturanCPNS.objects.exists())


class KetahananTests(TestCase):
    def test_butir_gagal_tidak_menghentikan_yang_lain(self):
        with patch(f"{MODUL}.Command.email_ganda", side_effect=RuntimeError("rusak")):
            teks = jalankan()
        self.assertIn("[PERLU TINDAKAN] Email ganda: gagal diperiksa (RuntimeError).", teks)
        self.assertEqual(teks.count("[OK]") + teks.count("[PERLU TINDAKAN]"), 7)
        self.assertIn("Soal lama", teks)
        n = teks.count("[PERLU TINDAKAN]")
        self.assertIn(f"Ringkasan: {n} butir perlu tindakan.", teks)


class GuruTests(TestCase):
    @override_settings(GURU_EMAILS=["guru@contoh.id"])
    def test_guru_dengan_sandi_aktif(self):
        User.objects.create_user("bu_guru", "Guru@Contoh.id", "rahasia-uji")
        User.objects.create_user("murid", "murid@contoh.id", "rahasia-uji")
        b = blok(jalankan(), "akun guru")
        self.assertTrue(b.startswith("[PERLU TINDAKAN]"))
        self.assertIn("bu_guru", b)
        self.assertNotIn("murid", b)
        self.assertIn("nonaktifkan kata sandinya lewat admin.", b)

    @override_settings(GURU_EMAILS=["guru@contoh.id"])
    def test_guru_tanpa_sandi_ok(self):
        u = User.objects.create_user("bu_guru", "guru@contoh.id")
        u.set_unusable_password()
        u.save()
        self.assertTrue(blok(jalankan(), "akun guru").startswith("[OK]"))

    @override_settings(GURU_EMAILS=["guru@contoh.id"])
    def test_tanpa_email_di_keluaran(self):
        User.objects.create_user("bu_guru", "guru@contoh.id", "rahasia-uji")
        User.objects.create_user("a", "Dobel@x.id", "rahasia-uji")
        User.objects.create_user("b", "dobel@x.id", "rahasia-uji")
        teks = jalankan().lower()
        self.assertNotIn("guru@contoh.id", teks)
        self.assertNotIn("dobel@x.id", teks)
        self.assertNotIn("@", teks)


class EmailGandaTests(TestCase):
    def test_ganda_beda_huruf(self):
        User.objects.create_user("ani1", "Ani@x.id", "rahasia-uji")
        User.objects.create_user("ani2", "ani@X.id", "rahasia-uji")
        User.objects.create_user("budi", "budi@x.id", "rahasia-uji")
        b = blok(jalankan(), "email ganda")
        self.assertTrue(b.startswith("[PERLU TINDAKAN]"))
        self.assertIn("1 email ganda", b)
        self.assertIn("ani1", b)
        self.assertIn("ani2", b)
        self.assertNotIn("budi", b)

    def test_email_kosong_tidak_dihitung(self):
        User.objects.create_user("k1", "", "rahasia-uji")
        User.objects.create_user("k2", "unik@x.id", "rahasia-uji")
        self.assertTrue(blok(jalankan(), "email ganda").startswith("[OK]"))


class PengaturanTests(TestCase):
    def test_belum_dibuat(self):
        self.assertTrue(blok(jalankan(), "Pengaturan CPNS").startswith("[PERLU TINDAKAN]"))

    def test_kosong(self):
        PengaturanCPNS.objects.create(pk=1)
        b = blok(jalankan(), "Pengaturan CPNS")
        self.assertTrue(b.startswith("[PERLU TINDAKAN]"))
        self.assertIn("Nomor WA masih kosong", b)
        self.assertIn("Daftar harga masih kosong", b)

    def test_lengkap(self):
        PengaturanCPNS.objects.create(pk=1, nomor_wa="081234", teks_harga={"1": "Rp 10.000"})
        self.assertTrue(blok(jalankan(), "Nomor WA").startswith("[OK]"))


class TemplatHukumTests(TestCase):
    def test_placeholder_dan_draf_terdeteksi(self):
        draf = "Draf, menunggu tinjauan pengelola. [KEBIJAKAN PENGEMBALIAN DANA] [NAMA DAN KONTAK PENGELOLA]"
        with patch(f"{MODUL}._teks_templat", return_value=draf):
            b = blok(jalankan(), "syarat dan privasi")
        self.assertTrue(b.startswith("[PERLU TINDAKAN]"))
        self.assertIn("[KEBIJAKAN PENGEMBALIAN DANA]", b)
        self.assertIn("[NAMA DAN KONTAK PENGELOLA]", b)
        self.assertIn("Draf, menunggu tinjauan pengelola.", b)

    def test_bersih_ok(self):
        with patch(f"{MODUL}._teks_templat", return_value="<p>Isi final.</p>"):
            self.assertTrue(blok(jalankan(), "syarat dan privasi").startswith("[OK]"))


class KisiTests(TestCase):
    def test_draf_perlu_tindakan(self):
        with patch(f"{MODUL}._awal_kisi", return_value=KISI_DRAF), patch(
            f"{MODUL}.baca_kisi_kisi", return_value=[object()]
        ):
            b = blok(jalankan(), "Kisi-kisi")
        self.assertTrue(b.startswith("[PERLU TINDAKAN]"))
        self.assertIn("belum disetujui", b)

    def test_disetujui_ok(self):
        with patch(f"{MODUL}._awal_kisi", return_value="# Kisi-kisi\n\nDisetujui pemilik."):
            self.assertTrue(blok(jalankan(), "Kisi-kisi").startswith("[OK]"))

    def test_tidak_terbaca(self):
        with patch(f"{MODUL}.baca_kisi_kisi", side_effect=ValueError("Kisi-kisi baris 3: rusak.")):
            b = blok(jalankan(), "kisi-kisi")
        self.assertTrue(b.startswith("[PERLU TINDAKAN]"))
        self.assertIn("baris 3", b)


class CukupSoalTests(TestCase):
    def test_bank_kosong(self):
        b = blok(jalankan(), "SKD-CAT")
        self.assertTrue(b.startswith("[PERLU TINDAKAN]"))
        self.assertIn("Cukup untuk 0 simulasi", b)

    def test_cukup_untuk_n_simulasi(self):
        skema = SkemaUjian.objects.get(kode="SKD-CAT")
        for bagian in skema.bagian.all():
            for _ in range(bagian.jumlah_soal * 2):
                buat_soal(bagian.subtes)
        buat_soal("TWK", status="draf")
        b = blok(jalankan(), "SKD-CAT")
        self.assertTrue(b.startswith("[OK]"))
        self.assertIn("Cukup untuk 2 simulasi", b)
        self.assertIn("TWK:", b)


class SoalLamaTests(TestCase):
    def test_tidak_ada_soal_lama(self):
        b = blok(jalankan(), "soal lama")
        self.assertTrue(b.startswith("[OK]"))
        self.assertIn("Soal lama: 0", b)

    def test_ada_soal_lama(self):
        pkt = paket()
        lama(pkt)
        lama(pkt, "TIU")
        b = blok(jalankan(), "soal lama")
        self.assertTrue(b.startswith("[PERLU TINDAKAN]"))
        self.assertIn("Soal lama: 2", b)
        self.assertIn("Perkiraan masuk: 2", b)
