from django.contrib import admin as dj_admin
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from apps.cpns.models import (
    PaketBelajar,
    PaketSoal,
    PengaturanCPNS,
    SkemaBagian,
    SkemaUjian,
    Voucher,
)
from apps.cpns.tests.pabrik import buat_soal

User = get_user_model()


class AdminCpnsBase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.admin = User.objects.create_superuser(
            username="adm", email="adm@x.id", password="x", role="guru"
        )

    def setUp(self):
        self.client.force_login(self.admin)


class VoucherAdminTests(AdminCpnsBase):
    def setUp(self):
        super().setUp()
        p = PengaturanCPNS.ambil()
        p.teks_harga = {"30": "x", "90": "y"}
        p.save()

    def test_buat_banyak_menghasilkan_kode(self):
        url = reverse("admin:cpns_voucher_buat_banyak")
        r = self.client.post(url, {"jumlah": 3, "durasi_hari": "30", "catatan": "batch"})
        self.assertEqual(r.status_code, 200)
        vouchers = Voucher.objects.all()
        self.assertEqual(vouchers.count(), 3)
        for v in vouchers:
            self.assertContains(r, v.kode)
            self.assertEqual(v.durasi_hari, 30)
            self.assertEqual(v.dibuat_oleh, self.admin)
        self.assertContains(r, "<textarea")
        self.assertContains(r, "readonly")

    def test_buat_banyak_form_tampil(self):
        r = self.client.get(reverse("admin:cpns_voucher_buat_banyak"))
        self.assertEqual(r.status_code, 200)

    def test_buat_banyak_durasi_lain(self):
        url = reverse("admin:cpns_voucher_buat_banyak")
        self.client.post(
            url, {"jumlah": 1, "durasi_hari": "lain", "durasi_lain": "45", "catatan": ""}
        )
        self.assertEqual(Voucher.objects.get().durasi_hari, 45)

    def test_buat_banyak_tolak_jumlah_101(self):
        url = reverse("admin:cpns_voucher_buat_banyak")
        r = self.client.post(url, {"jumlah": 101, "durasi_hari": "30", "catatan": ""})
        self.assertEqual(r.status_code, 200)
        self.assertEqual(Voucher.objects.count(), 0)
        self.assertTrue(r.context["form"].errors)

    def test_changelist_ada_tombol_buat(self):
        r = self.client.get(reverse("admin:cpns_voucher_changelist"))
        self.assertContains(r, reverse("admin:cpns_voucher_buat_banyak"))

    def test_tidak_bisa_tambah_satuan(self):
        r = self.client.get(reverse("admin:cpns_voucher_add"))
        self.assertEqual(r.status_code, 403)

    def test_aksi_batalkan_hanya_yang_belum_dipakai(self):
        pakai = User.objects.create_user(username="p1", email="p1@x.id", password="x")
        baru = Voucher.objects.create(kode="AAAA-AAAA", durasi_hari=30)
        dipakai = Voucher.objects.create(kode="BBBB-BBBB", durasi_hari=30, dipakai_oleh=pakai)
        r = self.client.post(
            reverse("admin:cpns_voucher_changelist"),
            {
                "action": "batalkan_belum_dipakai",
                "_selected_action": [baru.pk, dipakai.pk],
            },
        )
        self.assertEqual(r.status_code, 302)
        baru.refresh_from_db()
        dipakai.refresh_from_db()
        self.assertTrue(baru.dibatalkan)
        self.assertFalse(dipakai.dibatalkan)

    def test_filter_status(self):
        Voucher.objects.create(kode="AAAA-AAAA", durasi_hari=30)
        Voucher.objects.create(kode="BBBB-BBBB", durasi_hari=30, dibatalkan=True)
        url = reverse("admin:cpns_voucher_changelist")
        r = self.client.get(url, {"status": "dibatalkan"})
        self.assertContains(r, "BBBB-BBBB")
        self.assertNotContains(r, "AAAA-AAAA")
        r = self.client.get(url, {"status": "belum_dipakai"})
        self.assertContains(r, "AAAA-AAAA")
        self.assertNotContains(r, "BBBB-BBBB")


class SkemaAdminTests(AdminCpnsBase):
    def _post(self, jenis, bagian):
        data = {
            "kode": "S1",
            "nama": "Skema satu",
            "jenis_ujian": jenis,
            "durasi_menit": 100,
            "aktif": "on",
            "urutan": 0,
            "keterangan": "",
            "bagian-TOTAL_FORMS": "1",
            "bagian-INITIAL_FORMS": "0",
            "bagian-MIN_NUM_FORMS": "0",
            "bagian-MAX_NUM_FORMS": "1000",
        }
        for k, v in bagian.items():
            data[f"bagian-0-{k}"] = str(v)
        return self.client.post(reverse("admin:cpns_skemaujian_add"), data)

    def _bagian(self, **kw):
        dasar = dict(
            urutan=1, subtes="TWK", jumlah_soal=10, cara_nilai="benar_salah",
            poin_benar=5, poin_salah=0, ambang_batas=0,
        )
        dasar.update(kw)
        return dasar

    def test_bagian_subtes_tidak_cocok_ditolak(self):
        r = self._post("SKD", self._bagian(subtes="PEDAGOGIK"))
        self.assertEqual(r.status_code, 200)
        self.assertFalse(SkemaUjian.objects.filter(kode="S1").exists())
        self.assertContains(r, "tidak cocok")

    def test_bagian_skb_materi_rpl_diterima(self):
        r = self._post("SKB_GURU", self._bagian(subtes="MATERI_RPL", ambang_batas=20))
        self.assertEqual(r.status_code, 302)
        self.assertEqual(SkemaBagian.objects.filter(skema__kode="S1").count(), 1)

    def test_bagian_ambang_melebihi_maks_ditolak(self):
        r = self._post("SKD", self._bagian(ambang_batas=51))
        self.assertEqual(r.status_code, 200)
        self.assertFalse(SkemaUjian.objects.filter(kode="S1").exists())
        self.assertContains(r, "melebihi")

    def test_bagian_ambang_bobot_pakai_lima(self):
        r = self._post(
            "SKD",
            self._bagian(subtes="TKP", cara_nilai="bobot_opsi", poin_benar=1, ambang_batas=50),
        )
        self.assertEqual(r.status_code, 302)


class PaketAdminTests(AdminCpnsBase):
    def test_kolom_jumlah_tayang(self):
        from apps.cpns.admin import PaketBelajarAdmin

        paket = PaketBelajar.objects.create(nama="Paket A", jenis_ujian="SKD")
        PaketSoal.objects.create(paket=paket, soal=buat_soal("TWK"), urutan=1)
        PaketSoal.objects.create(paket=paket, soal=buat_soal("TWK", status="draf"), urutan=2)
        r = self.client.get(reverse("admin:cpns_paketbelajar_changelist"))
        self.assertEqual(r.status_code, 200)
        ma = PaketBelajarAdmin(PaketBelajar, dj_admin.site)
        self.assertEqual(ma.jumlah_tayang(paket), 1)

    def test_form_tambah_tampil(self):
        r = self.client.get(reverse("admin:cpns_paketbelajar_add"))
        self.assertEqual(r.status_code, 200)


class PengaturanAdminTests(AdminCpnsBase):
    def test_pengaturan_tidak_bisa_ditambah_dua(self):
        r = self.client.get(reverse("admin:cpns_pengaturancpns_add"))
        self.assertEqual(r.status_code, 200)
        PengaturanCPNS.ambil()
        r = self.client.get(reverse("admin:cpns_pengaturancpns_add"))
        self.assertEqual(r.status_code, 403)

    def test_pengaturan_tidak_bisa_dihapus(self):
        p = PengaturanCPNS.ambil()
        r = self.client.post(
            reverse("admin:cpns_pengaturancpns_delete", args=[p.pk]), {"post": "yes"}
        )
        self.assertEqual(r.status_code, 403)
        self.assertTrue(PengaturanCPNS.objects.filter(pk=p.pk).exists())

    def _data(self, pesan):
        return {"nomor_wa": "0812", "teks_harga": "{}", "pesan_wa": pesan}

    def test_pengaturan_pesan_wa_rusak_ditolak(self):
        p = PengaturanCPNS.ambil()
        r = self.client.post(
            reverse("admin:cpns_pengaturancpns_change", args=[p.pk]), self._data("Halo {nama}")
        )
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, "Template pesan tidak valid. Gunakan hanya {durasi} dan {email}.")
        p.refresh_from_db()
        self.assertNotEqual(p.pesan_wa, "Halo {nama}")

    def test_pengaturan_pesan_wa_valid_disimpan(self):
        p = PengaturanCPNS.ambil()
        r = self.client.post(
            reverse("admin:cpns_pengaturancpns_change", args=[p.pk]),
            self._data("Beli {durasi} hari {email}"),
        )
        self.assertEqual(r.status_code, 302)
        p.refresh_from_db()
        self.assertEqual(p.pesan_wa, "Beli {durasi} hari {email}")


class AksesAdminTests(TestCase):
    def test_non_staff_tidak_bisa_buka(self):
        siswa = User.objects.create_user(
            username="s", email="s@x.id", password="x", role="siswa"
        )
        self.client.force_login(siswa)
        for nama in ("admin:cpns_voucher_changelist", "admin:cpns_voucher_buat_banyak"):
            r = self.client.get(reverse(nama))
            self.assertEqual(r.status_code, 302)
            self.assertIn("/login", r["Location"])

    def test_anonim_dialihkan(self):
        r = self.client.get(reverse("admin:cpns_voucher_buat_banyak"))
        self.assertEqual(r.status_code, 302)
