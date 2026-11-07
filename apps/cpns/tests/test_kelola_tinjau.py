from datetime import timedelta

from django.contrib.auth import get_user_model
from django.contrib.messages import get_messages
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from apps.cpns.models import LaporanSoal, Soal
from apps.cpns.tests.pabrik import buat_soal

HOST_CPNS = "cpns.agunggumelarsaputra.com"
PESAN_KONFLIK = "Soal ini sudah diubah di tab lain. Muat ulang untuk melihat keadaan terbaru."


def buat_draf(subtes="TIU", **kw):
    soal = buat_soal(subtes, status="draf", **kw)
    return soal


def pesan(response):
    return [str(m) for m in get_messages(response.wsgi_request)]


class KelolaTinjauDasar(TestCase):
    def setUp(self):
        self.admin = get_user_model().objects.create_superuser(
            username="agung", email="a@contoh.id", password="x"
        )
        self.client.force_login(self.admin)

    def aksi(self, soal, **data):
        data.setdefault("status_awal", soal.status)
        return self.client.post(reverse("cpns:kelola_aksi", args=[soal.id]), data)


class AksesTest(TestCase):
    def test_tamu_ke_masuk_non_superuser_403(self):
        soal = buat_draf()
        urls = [
            reverse("cpns:kelola"),
            reverse("cpns:kelola_tinjau"),
            reverse("cpns:kelola_tinjau_soal", args=[soal.id]),
        ]
        for url in urls:
            r = self.client.get(url)
            self.assertEqual(r.status_code, 302, url)
            self.assertTrue(r["Location"].startswith(reverse("cpns:masuk")), url)
            self.assertIn("next=", r["Location"])
        r = self.client.post(reverse("cpns:kelola_aksi", args=[soal.id]), {"aksi": "setujui"})
        self.assertEqual(r.status_code, 302)

        biasa = get_user_model().objects.create_user(username="guru", password="x")
        self.client.force_login(biasa)
        for url in urls:
            self.assertEqual(self.client.get(url).status_code, 403, url)
        r = self.client.post(
            reverse("cpns:kelola_aksi", args=[soal.id]),
            {"aksi": "setujui", "status_awal": "draf"},
        )
        self.assertEqual(r.status_code, 403)
        soal.refresh_from_db()
        self.assertEqual(soal.status, "draf")

    def test_peserta_403_di_host_cpns(self):
        peserta = get_user_model().objects.create_user(
            username="p1", password="x", role=get_user_model().ROLE_PESERTA
        )
        self.client.force_login(peserta)
        url = reverse("cpns:kelola_tinjau", urlconf="config.cpns_urls")
        r = self.client.get(url, HTTP_HOST=HOST_CPNS)
        self.assertEqual(r.status_code, 403)


class AntreanTest(KelolaTinjauDasar):
    def test_antrean_bawaan_draf_dan_filter(self):
        buat_soal("TWK", status="tayang")
        a = buat_draf("TIU", subtopik="Deret", teks="Soal A")
        b = buat_draf("TWK", subtopik="Pancasila", teks="Soal B")
        Soal.objects.filter(pk=a.pk).update(batch="b1")
        Soal.objects.filter(pk=b.pk).update(batch="b2")

        r = self.client.get(reverse("cpns:kelola_tinjau"))
        self.assertRedirects(
            r, reverse("cpns:kelola_tinjau_soal", args=[a.id]), fetch_redirect_response=False
        )

        r = self.client.get(reverse("cpns:kelola_tinjau"), {"subtes": "TWK"})
        self.assertIn(f"/{b.id}/", r["Location"])
        self.assertIn("subtes=TWK", r["Location"])

        r = self.client.get(reverse("cpns:kelola_tinjau"), {"batch": "b2"})
        self.assertIn(f"/{b.id}/", r["Location"])
        r = self.client.get(reverse("cpns:kelola_tinjau"), {"subtopik": "Deret"})
        self.assertIn(f"/{a.id}/", r["Location"])

        halaman = self.client.get(reverse("cpns:kelola_tinjau_soal", args=[a.id]))
        self.assertEqual(halaman.status_code, 200)
        self.assertContains(halaman, "Soal A")
        self.assertContains(halaman, "Soal 1 dari 1 di batch ini")

    def test_keadaan_kosong(self):
        r = self.client.get(reverse("cpns:kelola_tinjau"))
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, "Tidak ada soal di antrean ini.")

    def test_nav_menghitung_laporan_baru(self):
        soal = buat_draf()
        LaporanSoal.objects.create(soal=soal, user=self.admin, alasan="typo")
        r = self.client.get(reverse("cpns:kelola_tinjau_soal", args=[soal.id]))
        self.assertContains(r, "Laporan Soal (1)")
        self.assertContains(r, reverse("admin:cpns_voucher_changelist"))


class AksiTest(KelolaTinjauDasar):
    def test_setujui_menayangkan_dan_isi_peninjau(self):
        soal = buat_draf()
        r = self.aksi(soal, aksi="setujui")
        self.assertEqual(r.status_code, 302)
        soal.refresh_from_db()
        self.assertEqual(soal.status, "tayang")
        self.assertEqual(soal.ditinjau_oleh, self.admin)
        self.assertIsNotNone(soal.ditinjau_pada)

    def test_setujui_soal_tidak_valid_tetap_draf_dengan_pesan(self):
        soal = buat_draf()
        Soal.objects.filter(pk=soal.pk).update(pembahasan_cepat="")
        r = self.aksi(soal, aksi="setujui")
        self.assertRedirects(
            r, reverse("cpns:kelola_tinjau_soal", args=[soal.id]), fetch_redirect_response=False
        )
        soal.refresh_from_db()
        self.assertEqual(soal.status, "draf")
        self.assertIsNone(soal.ditinjau_oleh)
        halaman = self.client.get(r["Location"])
        self.assertContains(halaman, "Isi pembahasan cepat.")

    def test_tolak_wajib_alasan(self):
        soal = buat_draf()
        r = self.aksi(soal, aksi="tolak", alasan="   ")
        soal.refresh_from_db()
        self.assertEqual(soal.status, "draf")
        self.assertIn("Tulis alasan penolakan.", pesan(r))

    def test_tolak_menyimpan_catatan(self):
        soal = buat_draf()
        self.aksi(soal, aksi="tolak", alasan="kunci salah")
        soal.refresh_from_db()
        self.assertEqual(soal.status, "ditolak")
        self.assertEqual(soal.catatan_tinjau, "kunci salah")
        self.assertEqual(soal.ditinjau_oleh, self.admin)
        self.assertIsNotNone(soal.ditinjau_pada)

    def test_lewati_ke_berikutnya(self):
        a, b = buat_draf(), buat_draf()
        r = self.aksi(a, aksi="lewati", subtes="")
        self.assertIn(f"/{b.id}/", r["Location"])
        a.refresh_from_db()
        self.assertEqual(a.status, "draf")
        self.assertIsNone(a.ditinjau_oleh)

    def test_aksi_berhasil_ke_berikutnya_dengan_filter_dibawa(self):
        a = buat_draf("TIU")
        b = buat_draf("TIU")
        buat_draf("TWK")
        r = self.aksi(a, aksi="setujui", subtes="TIU")
        self.assertIn(f"/{b.id}/", r["Location"])
        self.assertIn("subtes=TIU", r["Location"])
        r = self.aksi(b, aksi="tolak", alasan="x", subtes="TIU")
        self.assertEqual(r["Location"], reverse("cpns:kelola_tinjau") + "?subtes=TIU")

    def test_konflik_tab_lain(self):
        soal = buat_draf()
        self.aksi(soal, aksi="tolak", alasan="kunci salah")
        r = self.aksi(soal, aksi="setujui", status_awal="draf")
        soal.refresh_from_db()
        self.assertEqual(soal.status, "ditolak")
        self.assertEqual(soal.catatan_tinjau, "kunci salah")
        self.assertIn(PESAN_KONFLIK, pesan(r))
        self.assertIn(f"/{soal.id}/", r["Location"])

    def test_setujui_soal_sudah_tayang_ditolak(self):
        soal = buat_draf()
        self.aksi(soal, aksi="setujui")
        soal.refresh_from_db()
        peninjau, waktu = soal.ditinjau_oleh, soal.ditinjau_pada
        lain = get_user_model().objects.create_superuser(username="lain", password="x")
        self.client.force_login(lain)
        r = self.aksi(soal, aksi="setujui", status_awal="tayang")
        self.assertIn("Soal ini sudah tayang.", pesan(r))
        soal.refresh_from_db()
        self.assertEqual(soal.ditinjau_oleh, peninjau)
        self.assertEqual(soal.ditinjau_pada, waktu)

    def test_setujui_menghapus_catatan_tinjau(self):
        soal = buat_draf()
        Soal.objects.filter(pk=soal.pk).update(catatan_tinjau="kunci salah")
        self.aksi(soal, aksi="setujui")
        soal.refresh_from_db()
        self.assertEqual(soal.status, "tayang")
        self.assertEqual(soal.catatan_tinjau, "")

    def test_aksi_harus_post(self):
        soal = buat_draf()
        r = self.client.get(reverse("cpns:kelola_aksi", args=[soal.id]))
        self.assertEqual(r.status_code, 405)


class HalamanSoalTest(KelolaTinjauDasar):
    def test_penghitung_hari_ini_dan_tersisa(self):
        saya, lain = buat_draf(), get_user_model().objects.create_user(username="x", password="x")
        kemarin = buat_soal("TWK", status="tayang")
        orang_lain = buat_soal("TWK", status="tayang")
        Soal.objects.filter(pk=kemarin.pk).update(
            ditinjau_oleh=self.admin, ditinjau_pada=timezone.now() - timedelta(days=2)
        )
        Soal.objects.filter(pk=orang_lain.pk).update(ditinjau_oleh=lain, ditinjau_pada=timezone.now())
        hari_ini = buat_soal("TWK", status="tayang")
        Soal.objects.filter(pk=hari_ini.pk).update(
            ditinjau_oleh=self.admin, ditinjau_pada=timezone.now()
        )
        buat_draf()
        r = self.client.get(reverse("cpns:kelola_tinjau_soal", args=[saya.id]))
        self.assertContains(r, "Hari ini: 1 ditinjau")
        self.assertContains(r, "Draf tersisa: 2")

    def test_pemeriksaan_mirip_soal_lain(self):
        a = buat_draf(teks="Teks yang sama persis")
        b = buat_draf(teks="Teks yang sama persis!")
        c = buat_draf(teks="Teks lain sama sekali")
        url = reverse("cpns:kelola_tinjau_soal", args=[a.id])
        r = self.client.get(url)
        self.assertContains(r, "Tidak mirip soal lain di bank")
        self.assertContains(r, f"Teksnya sama dengan soal nomor {b.id}.")
        r = self.client.get(reverse("cpns:kelola_tinjau_soal", args=[c.id]))
        self.assertNotContains(r, "Teksnya sama dengan soal nomor")

    def test_pemeriksaan_syarat_gagal_ditampilkan(self):
        soal = buat_draf()
        Soal.objects.filter(pk=soal.pk).update(opsi_b="")
        r = self.client.get(reverse("cpns:kelola_tinjau_soal", args=[soal.id]))
        self.assertContains(r, "Isi opsi B.")

    def test_kunci_dan_bobot_tkp_dan_cek_fakta(self):
        soal = buat_draf("TIU", kunci="C")
        r = self.client.get(reverse("cpns:kelola_tinjau_soal", args=[soal.id]))
        self.assertContains(r, ">Kunci<")
        self.assertNotContains(r, "Perlu cek fakta")
        Soal.objects.filter(pk=soal.pk).update(perlu_cek=True)
        r = self.client.get(reverse("cpns:kelola_tinjau_soal", args=[soal.id]))
        self.assertContains(r, "Perlu cek fakta")
        tkp = buat_draf("TKP")
        r = self.client.get(reverse("cpns:kelola_tinjau_soal", args=[tkp.id]))
        self.assertContains(r, "Bobot 5")
        self.assertNotContains(r, ">Kunci<")

    def test_markup_pintasan_abaikan_input(self):
        soal = buat_draf()
        html = self.client.get(reverse("cpns:kelola_tinjau_soal", args=[soal.id])).content.decode()
        for kata in ("tagName", "INPUT", "TEXTAREA", "SELECT", "ctrlKey", "metaKey", "altKey"):
            self.assertIn(kata, html)
        self.assertIn('aria-label="Alasan tolak"', html)
        self.assertIn("@keydown.window", html)

    def test_edit_mengarah_ke_rute_ubah(self):
        soal = buat_draf()
        halaman = self.client.get(reverse("cpns:kelola_tinjau_soal", args=[soal.id]))
        self.assertContains(halaman, reverse("cpns:kelola_ubah", args=[soal.id]))
        r = self.client.get(reverse("cpns:kelola_ubah", args=[soal.id]))
        self.assertEqual(r.status_code, 200)

    def test_markup_pintasan_abaikan_pengulangan_dan_kunci_kirim_ganda(self):
        soal = buat_draf()
        html = self.client.get(reverse("cpns:kelola_tinjau_soal", args=[soal.id])).content.decode()
        self.assertIn("e.repeat", html)
        self.assertIn("terkirim", html)
        self.assertIn(":disabled", html)

    def test_flash_pesan_tidak_hanya_warna(self):
        soal = buat_draf()
        self.aksi(soal, aksi="tolak", alasan=" ")
        r = self.client.get(reverse("cpns:kelola_tinjau_soal", args=[soal.id]))
        self.assertContains(r, 'role="alert"')
        self.assertContains(r, "Gagal:")
        self.aksi(soal, aksi="setujui")
        r = self.client.get(reverse("cpns:kelola_tinjau_soal", args=[soal.id]))
        self.assertContains(r, "Berhasil:")
        self.assertContains(r, "Soal ditayangkan.")
