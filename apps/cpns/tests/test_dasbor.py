import re
from datetime import timedelta

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from django.utils.dateformat import format as format_tanggal

from apps.cpns.models import (
    AksesPeserta,
    LaporanSoal,
    PaketBelajar,
    PaketSoal,
    Sesi,
    SesiSoal,
    SkemaUjian,
)
from apps.cpns.tests.pabrik import buat_sesi_cat, buat_soal

HOST_CPNS = "cpns.agunggumelarsaputra.com"
HX = {"HTTP_HX_REQUEST": "true"}
KOSONG_JUDUL = "Belum ada simulasi"
KOSONG_ISI = "Setelah simulasi pertama, skor TWK, TIU, TKP dan jarak ke ambang batas muncul di sini."


def buat_user(username, *, google=True, premium=False, akses=True, **ekstra):
    user = get_user_model().objects.create_user(
        username=username, email=f"{username}@contoh.id", password="x", **ekstra
    )
    if akses:
        AksesPeserta.objects.create(
            user=user,
            via_google=google,
            premium_sampai=timezone.now() + timedelta(days=30) if premium else None,
        )
    return user


def sesi_cat_selesai(user, *, total=300, lulus=False, hari_lalu=0):
    skema = SkemaUjian.objects.get(kode="SKD-CAT")
    soal = buat_soal("TWK")
    sesi = buat_sesi_cat(user, skema, [soal], ["A"])
    sesi.status = "selesai"
    sesi.selesai_pada = timezone.now() - timedelta(days=hari_lalu)
    sesi.total = total
    sesi.lulus = lulus
    sesi.skor_bagian = [
        {"subtes": "TWK", "skor": 60, "maks": 150, "ambang": 65, "lulus": False},
        {"subtes": "TIU", "skor": 90, "maks": 175, "ambang": 80, "lulus": True},
        {"subtes": "TKP", "skor": 150, "maks": 225, "ambang": 166, "lulus": False},
    ]
    sesi.save()
    return sesi


def sesi_cat_berjalan(user, *, menit=90):
    skema = SkemaUjian.objects.get(kode="SKD-CAT")
    sesi = buat_sesi_cat(user, skema, [buat_soal("TWK")], [""])
    sesi.batas_waktu = timezone.now() + timedelta(minutes=menit)
    sesi.save(update_fields=["batas_waktu"])
    return sesi


def buat_paket_trial(jumlah=3):
    paket = PaketBelajar.objects.create(nama="Paket gratis SKD", jenis_ujian="SKD", untuk_trial=True)
    soal = [buat_soal("TIU") for _ in range(jumlah)]
    for urutan, s in enumerate(soal, start=1):
        PaketSoal.objects.create(paket=paket, soal=s, urutan=urutan)
    return paket, soal


def sesi_belajar(user, soal_list, jawaban_list, *, paket=None, status="berjalan"):
    sesi = Sesi.objects.create(user=user, mode="belajar", paket=paket, status=status)
    for nomor, (soal, jawaban) in enumerate(zip(soal_list, jawaban_list), start=1):
        SesiSoal.objects.create(sesi=sesi, soal=soal, nomor=nomor, urutan_opsi="ABCDE", jawaban=jawaban)
    return sesi


class DasborTest(TestCase):
    def setUp(self):
        self.user = buat_user("peserta", first_name="Agung")
        self.client.force_login(self.user)

    def _dasbor(self):
        resp = self.client.get(reverse("cpns:dasbor"))
        self.assertEqual(resp.status_code, 200)
        return resp

    def test_dasbor_keadaan_kosong(self):
        resp = self._dasbor()
        self.assertContains(resp, "Halo, Agung")
        self.assertContains(resp, "Akun Trial")
        self.assertContains(resp, KOSONG_JUDUL)
        self.assertContains(resp, KOSONG_ISI)
        self.assertNotContains(resp, "Lanjutkan ujian")
        # Modal onboarding siswa SMK dari base.html tidak ikut ke CPNS Hub.
        self.assertNotContains(resp, 'id="mandatory-profile-modal"', html=False)

    def test_dasbor_sapa_username_tanpa_nama_depan(self):
        user = buat_user("tanpanama")
        self.client.force_login(user)
        self.assertContains(self._dasbor(), "Halo, tanpanama")

    def test_dasbor_ada_lanjutkan_ujian(self):
        sesi = sesi_cat_berjalan(self.user, menit=90)
        resp = self._dasbor()
        self.assertContains(resp, "Lanjutkan ujian")
        self.assertContains(resp, reverse("cpns:cat_ruang", args=[sesi.pk]))
        self.assertContains(resp, "Simulasi SKD CAT")
        self.assertRegex(resp.content.decode(), r"(89:5\d|90:00)")

    def test_dasbor_cat_kedaluwarsa_tidak_ada_lanjutkan(self):
        sesi = sesi_cat_berjalan(self.user, menit=-5)
        resp = self._dasbor()
        self.assertNotContains(resp, "Lanjutkan ujian")
        sesi.refresh_from_db()
        self.assertEqual(sesi.status, "selesai")

    def test_dasbor_skb_segera_tersedia(self):
        resp = self._dasbor()
        self.assertContains(resp, "Segera tersedia")
        self.assertNotContains(resp, reverse("cpns:cat_mulai", args=["skb-guru-latihan"]))

    def test_dasbor_superuser_skb_nonaktif_tetap_ada_tombol(self):
        admin = get_user_model().objects.create_superuser(username="adm", email="adm@contoh.id", password="x")
        self.client.force_login(admin)
        resp = self._dasbor()
        self.assertContains(resp, reverse("cpns:cat_mulai", args=["skb-guru-latihan"]))
        self.assertContains(resp, "Mulai simulasi SKB Guru")

    def test_dasbor_skb_aktif_non_premium(self):
        SkemaUjian.objects.filter(kode="SKB-GURU-LATIHAN").update(aktif=True)
        resp = self._dasbor()
        self.assertContains(resp, "Simulasi SKB Guru khusus Premium.")
        self.assertNotContains(resp, reverse("cpns:cat_mulai", args=["skb-guru-latihan"]))
        self.assertContains(resp, ">Premium</span>", html=False)

    def test_dasbor_skd_boleh_mulai(self):
        resp = self._dasbor()
        self.assertContains(resp, "Mulai simulasi SKD")
        self.assertContains(resp, reverse("cpns:cat_mulai", args=["skd-cat"]))
        self.assertContains(resp, "110 soal")
        self.assertContains(resp, "100 menit")

    def test_dasbor_skd_trial_non_google_tanpa_tombol(self):
        user = buat_user("nongoogle", google=False)
        self.client.force_login(user)
        resp = self._dasbor()
        self.assertContains(resp, "Simulasi gratis hanya untuk akun Google.")
        self.assertNotContains(resp, "Mulai simulasi SKD")
        self.assertNotContains(resp, reverse("cpns:cat_mulai", args=["skd-cat"]))

    def test_dasbor_user_lama_tanpa_akses_200(self):
        user = buat_user("lama", akses=False)
        self.client.force_login(user)
        resp = self._dasbor()
        self.assertContains(resp, "Akun Trial")

    def test_dasbor_lencana_premium(self):
        user = buat_user("premium", premium=True)
        self.client.force_login(user)
        sampai = user.akses_cpns.premium_sampai
        resp = self._dasbor()
        self.assertContains(resp, f"Premium sampai {format_tanggal(timezone.localtime(sampai), 'd M Y')}")
        self.assertNotContains(resp, "Akun Trial")

    def test_dasbor_paket_trial_belum_mulai(self):
        paket, _ = buat_paket_trial(3)
        resp = self._dasbor()
        self.assertContains(resp, "Paket gratis SKD")
        self.assertContains(resp, "0/3")
        self.assertContains(resp, "Mulai belajar")
        self.assertContains(resp, f'name="paket_id" value="{paket.pk}"', html=False)
        self.assertContains(resp, reverse("cpns:belajar_pilih"))
        self.assertContains(resp, "Lihat semua pilihan belajar")

    def test_dasbor_paket_trial_progres(self):
        paket, soal = buat_paket_trial(3)
        sesi = sesi_belajar(self.user, soal, ["A", "", ""], paket=paket)
        resp = self._dasbor()
        self.assertContains(resp, "1/3")
        self.assertContains(resp, "Lanjut ke soal 2")
        self.assertContains(resp, reverse("cpns:belajar_soal", args=[sesi.pk, 2]))

    def test_dasbor_paket_trial_pakai_sesi_terbaru(self):
        paket, soal = buat_paket_trial(3)
        lama = sesi_belajar(self.user, soal, ["A", "B", "C"], paket=paket, status="selesai")
        baru = sesi_belajar(self.user, soal, ["A", "", ""], paket=paket)
        Sesi.objects.filter(pk=lama.pk).update(dimulai_pada=timezone.now() - timedelta(days=2))
        resp = self._dasbor()
        self.assertContains(resp, "1/3")
        self.assertNotContains(resp, "3/3")
        self.assertContains(resp, "Lanjut ke soal 2")
        self.assertContains(resp, reverse("cpns:belajar_soal", args=[baru.pk, 2]))
        self.assertNotContains(resp, "Mulai belajar")

    def test_dasbor_paket_trial_selesai_mulai_lagi(self):
        paket, soal = buat_paket_trial(2)
        sesi_belajar(self.user, soal, ["A", "B"], paket=paket, status="selesai")
        resp = self._dasbor()
        self.assertContains(resp, "2/2")
        self.assertContains(resp, "Mulai belajar")
        self.assertNotContains(resp, "Lanjut ke soal")

    def test_dasbor_paket_trial_hitung_hanya_soal_tayang(self):
        paket, _ = buat_paket_trial(3)
        PaketSoal.objects.create(paket=paket, soal=buat_soal("TIU", status="draf"), urutan=4)
        PaketSoal.objects.create(paket=paket, soal=buat_soal("TIU", status="ditolak"), urutan=5)
        resp = self._dasbor()
        self.assertContains(resp, "0/3")
        self.assertNotContains(resp, "0/5")

    def test_dasbor_pesan_tampil_sekali(self):
        # Bank soal kosong: pesan galat hanya ada di flash, tidak di kartu skema.
        resp = self.client.post(reverse("cpns:cat_mulai", args=["skd-cat"]), follow=True)
        self.assertContains(resp, "Bank soal untuk bagian TWK belum cukup", count=1)
        self.assertNotContains(resp, "Pemberitahuan Sistem")

    def test_situs_utama_tetap_pakai_toast(self):
        self.client.post(reverse("cpns:cat_mulai", args=["skd-cat"]))
        resp = self.client.get(reverse("core:home"))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "Pemberitahuan Sistem", count=1)
        self.assertContains(resp, "Bank soal untuk bagian TWK belum cukup", count=1)

    def test_dasbor_skor_terakhir(self):
        lama = sesi_cat_selesai(self.user, total=250, hari_lalu=3)
        baru = sesi_cat_selesai(self.user, total=300, lulus=False)
        resp = self._dasbor()
        self.assertNotContains(resp, KOSONG_JUDUL)
        self.assertContains(resp, "300 / 550")
        self.assertContains(resp, "250 / 550")
        self.assertContains(resp, "Belum lolos")
        self.assertContains(resp, reverse("cpns:cat_hasil", args=[baru.pk]))
        self.assertContains(resp, reverse("cpns:cat_hasil", args=[lama.pk]))
        self.assertContains(resp, "Kurang 5 (ambang 65)")
        self.assertContains(resp, "Lolos (ambang 80)")

    def test_dasbor_skor_maksimal_lima(self):
        sesi = [sesi_cat_selesai(self.user, hari_lalu=h) for h in range(6)]
        resp = self._dasbor()
        for s in sesi[:5]:
            self.assertContains(resp, reverse("cpns:cat_hasil", args=[s.pk]))
        self.assertNotContains(resp, reverse("cpns:cat_hasil", args=[sesi[5].pk]))

    def test_dasbor_bagian_premium(self):
        resp = self._dasbor()
        self.assertContains(resp, 'id="premium"', html=False)
        self.assertContains(resp, 'id="simulasi"', html=False)
        self.assertContains(resp, f'href="{reverse("cpns:premium")}"')
        self.assertNotContains(resp, "segera tersedia")

    def test_judul_halaman(self):
        self.assertContains(self._dasbor(), "<title>Dasbor | CPNS Hub</title>", html=False)
        resp = self.client.get(reverse("cpns:riwayat"))
        self.assertContains(resp, "<title>Riwayat | CPNS Hub</title>", html=False)

    def test_tanpa_klaim_resmi(self):
        sesi_cat_selesai(self.user)
        for url in (reverse("cpns:dasbor"), reverse("cpns:riwayat")):
            html = self.client.get(url).content.decode()
            for kata in ("resmi", "Resmi", "soal asli"):
                self.assertNotIn(kata, html, f"{kata!r} muncul di {url}")


class NavigasiTest(TestCase):
    def setUp(self):
        self.user = buat_user("nav")
        self.client.force_login(self.user)

    def test_nav_pakai_url_di_host_cpns(self):
        resp = self.client.get("/dasbor/", HTTP_HOST=HOST_CPNS)
        html = resp.content.decode()
        self.assertIn('href="/belajar/"', html)
        self.assertIn('href="/riwayat/"', html)
        self.assertIn('href="/dasbor/#simulasi"', html)
        self.assertIn('href="/premium/"', html)

    def test_nav_pakai_url_di_domain_utama(self):
        resp = self.client.get("/cpns/dasbor/")
        self.assertEqual(resp.status_code, 200)
        html = resp.content.decode()
        self.assertIn('href="/cpns/belajar/"', html)
        self.assertIn('href="/cpns/riwayat/"', html)
        self.assertIn('href="/cpns/dasbor/#simulasi"', html)
        self.assertNotIn('href="/belajar/"', html)
        self.assertNotIn('href="/riwayat/"', html)

    def test_menu_mobile_tertutup_saat_klik_dan_fokus_kembali(self):
        html = self.client.get(reverse("cpns:dasbor")).content.decode()
        panel = html[html.index('id="cpns-mobile-menu"'):]
        panel = panel[: panel.index("</nav>")]
        self.assertEqual(panel.count("<a "), panel.count('@click="menuOpen = false"'))
        self.assertIn('x-ref="tombolMenu"', html)
        self.assertIn("$refs.tombolMenu.focus()", html)

    def test_nav_aktif_punya_penanda_selain_warna(self):
        html = self.client.get(reverse("cpns:riwayat")).content.decode()
        aktif = re.findall(r'<a [^>]*aria-current="page"[^>]*>', html)
        self.assertTrue(aktif)
        for tag in aktif:
            self.assertRegex(tag, r"underline|border-l-")


class RiwayatTest(TestCase):
    def setUp(self):
        self.user = buat_user("pemilik")
        self.client.force_login(self.user)

    def test_riwayat_kosong(self):
        resp = self.client.get(reverse("cpns:riwayat"))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "Belum ada riwayat latihan.")

    def test_riwayat_hanya_milik_sendiri(self):
        milik = sesi_cat_selesai(self.user)
        lain = buat_user("lain")
        punya_lain = sesi_cat_selesai(lain)
        belajar_lain = sesi_belajar(lain, [buat_soal("TIU")], [""])
        resp = self.client.get(reverse("cpns:riwayat"))
        self.assertContains(resp, reverse("cpns:cat_hasil", args=[milik.pk]))
        self.assertNotContains(resp, reverse("cpns:cat_hasil", args=[punya_lain.pk]))
        self.assertNotContains(resp, reverse("cpns:belajar_soal", args=[belajar_lain.pk, 1]))

    def test_riwayat_tautan_dan_status(self):
        cat_selesai = sesi_cat_selesai(self.user, total=300, hari_lalu=2)
        cat_jalan = sesi_cat_berjalan(self.user)
        soal = [buat_soal("TIU") for _ in range(3)]
        belajar_jalan = sesi_belajar(self.user, soal, ["A", "", ""])
        belajar_selesai = sesi_belajar(self.user, soal[:2], ["A", "B"], status="selesai")
        resp = self.client.get(reverse("cpns:riwayat"))
        self.assertContains(resp, reverse("cpns:cat_hasil", args=[cat_selesai.pk]))
        self.assertContains(resp, reverse("cpns:cat_ruang", args=[cat_jalan.pk]))
        self.assertContains(resp, reverse("cpns:belajar_soal", args=[belajar_jalan.pk, 2]))
        self.assertContains(resp, reverse("cpns:belajar_ringkasan", args=[belajar_selesai.pk]))
        self.assertContains(resp, "Berjalan")
        self.assertContains(resp, "Selesai")
        self.assertContains(resp, "300 / 550")
        self.assertContains(resp, "1/3 dijawab")
        html = resp.content.decode()
        # Terbaru dulu: sesi belajar selesai dibuat terakhir.
        self.assertLess(
            html.index(reverse("cpns:belajar_ringkasan", args=[belajar_selesai.pk])),
            html.index(reverse("cpns:cat_hasil", args=[cat_selesai.pk])),
        )


class LaporkanSoalTest(TestCase):
    def setUp(self):
        self.user = buat_user("pelapor")
        self.client.force_login(self.user)
        self.soal = buat_soal("TIU")

    def _laporkan(self, soal=None, data=None, hx=True, **ekstra):
        soal = soal or self.soal
        data = data if data is not None else {"alasan": "kunci_salah", "catatan": "Kunci seharusnya C."}
        return self.client.post(
            reverse("cpns:laporkan", args=[soal.pk]), data, **(HX if hx else {}), **ekstra
        )

    def test_laporkan_soal_tersimpan(self):
        sesi_belajar(self.user, [self.soal], ["A"])
        resp = self._laporkan()
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "Terima kasih, laporan terkirim.")
        self.assertNotContains(resp, 'role="status"', html=False)
        laporan = LaporanSoal.objects.get()
        self.assertEqual(laporan.soal, self.soal)
        self.assertEqual(laporan.user, self.user)
        self.assertEqual(laporan.alasan, "kunci_salah")
        self.assertEqual(laporan.catatan, "Kunci seharusnya C.")
        self.assertEqual(laporan.status, "baru")

    def test_laporkan_soal_bukan_miliknya_403(self):
        lain = buat_user("lain")
        sesi_belajar(lain, [self.soal], ["A"])
        resp = self._laporkan()
        self.assertEqual(resp.status_code, 403)
        self.assertFalse(LaporanSoal.objects.exists())

    def test_laporkan_soal_tidak_pernah_didapat_403(self):
        self.assertEqual(self._laporkan().status_code, 403)

    def test_laporkan_belajar_belum_dijawab_403(self):
        sesi_belajar(self.user, [self.soal], [""])
        self.assertEqual(self._laporkan().status_code, 403)
        self.assertFalse(LaporanSoal.objects.exists())

    def test_laporkan_cat_berjalan_403(self):
        skema = SkemaUjian.objects.get(kode="SKD-CAT")
        buat_sesi_cat(self.user, skema, [self.soal], ["A"])
        self.assertEqual(self._laporkan().status_code, 403)
        self.assertFalse(LaporanSoal.objects.exists())

    def test_laporkan_cat_selesai_boleh(self):
        skema = SkemaUjian.objects.get(kode="SKD-CAT")
        sesi = buat_sesi_cat(self.user, skema, [self.soal], [""])
        Sesi.objects.filter(pk=sesi.pk).update(status="selesai")
        resp = self._laporkan(data={"alasan": "typo"})
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(LaporanSoal.objects.get().catatan, "")

    def test_laporkan_duplikat_tidak_dobel(self):
        sesi_belajar(self.user, [self.soal], ["A"])
        self._laporkan()
        resp = self._laporkan(data={"alasan": "ambigu"})
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "Laporan untuk soal ini sudah kami terima.")
        self.assertEqual(LaporanSoal.objects.count(), 1)

    def test_laporkan_lagi_setelah_laporan_lama_selesai(self):
        sesi_belajar(self.user, [self.soal], ["A"])
        self._laporkan()
        LaporanSoal.objects.update(status="selesai")
        self.assertContains(self._laporkan(), "Terima kasih, laporan terkirim.")
        self.assertEqual(LaporanSoal.objects.count(), 2)

    def test_laporkan_alasan_tidak_valid_400(self):
        sesi_belajar(self.user, [self.soal], ["A"])
        self.assertEqual(self._laporkan(data={"alasan": "asal"}).status_code, 400)
        self.assertEqual(self._laporkan(data={}).status_code, 400)
        self.assertFalse(LaporanSoal.objects.exists())

    def test_laporkan_catatan_terlalu_panjang_400(self):
        sesi_belajar(self.user, [self.soal], ["A"])
        resp = self._laporkan(data={"alasan": "lainnya", "catatan": "x" * 1001})
        self.assertEqual(resp.status_code, 400)
        self.assertFalse(LaporanSoal.objects.exists())

    def test_laporkan_get_405(self):
        sesi_belajar(self.user, [self.soal], ["A"])
        resp = self.client.get(reverse("cpns:laporkan", args=[self.soal.pk]))
        self.assertEqual(resp.status_code, 405)

    def test_laporkan_anonim_ke_login(self):
        self.client.logout()
        resp = self._laporkan()
        self.assertEqual(resp.status_code, 302)
        self.assertIn(reverse("cpns:masuk"), resp["Location"])

    def test_laporkan_non_htmx_kembali_ke_perujuk(self):
        sesi = sesi_belajar(self.user, [self.soal], ["A"])
        asal = reverse("cpns:belajar_soal", args=[sesi.pk, 1])
        resp = self._laporkan(hx=False, HTTP_REFERER=f"http://testserver{asal}")
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp["Location"], f"http://testserver{asal}")
        pesan = [str(m) for m in resp.wsgi_request._messages]
        self.assertIn("Terima kasih, laporan terkirim.", pesan)

    def test_laporkan_non_htmx_perujuk_luar_ke_dasbor(self):
        sesi_belajar(self.user, [self.soal], ["A"])
        resp = self._laporkan(hx=False, HTTP_REFERER="https://jahat.example/")
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp["Location"], reverse("cpns:dasbor"))

    def test_laporkan_wadah_status_ada_sejak_awal(self):
        sesi_belajar(self.user, [self.soal], ["A"])
        sesi = Sesi.objects.get(user=self.user)
        html = self.client.get(reverse("cpns:belajar_soal", args=[sesi.pk, 1])).content.decode()
        pola = rf'<div id="laporan-status-{self.soal.pk}" role="status"[^>]*></div>'
        self.assertRegex(html, pola)
        self.assertIn(f'hx-target="#laporan-status-{self.soal.pk}"', html)
        self.assertIn('hx-swap="innerHTML"', html)
        # Handler global untuk 4xx dan galat jaringan HTMX ada di kerangka cpns.
        self.assertIn("htmx:responseError", html)
        self.assertIn("htmx:sendError", html)
        self.assertIn("Permintaan gagal. Muat ulang halaman lalu coba lagi.", html)

    def test_laporkan_4xx_berteks_indonesia(self):
        # Teks inilah yang ditampilkan handler htmx:responseError.
        resp = self._laporkan()
        self.assertEqual(resp.status_code, 403)
        self.assertEqual(resp.content.decode(), "Soal ini belum bisa kamu laporkan.")
        sesi_belajar(self.user, [self.soal], ["A"])
        resp = self._laporkan(data={"alasan": "asal"})
        self.assertEqual(resp.status_code, 400)
        self.assertEqual(resp.content.decode(), "Pilih alasan laporan.")


class SlotLaporkanTest(TestCase):
    def setUp(self):
        self.soal = buat_soal("TIU", kunci="B")

    def test_slot_di_umpan_balik_belajar(self):
        user = buat_user("belajar")
        self.client.force_login(user)
        sesi = sesi_belajar(user, [self.soal], ["A"])
        resp = self.client.get(reverse("cpns:belajar_soal", args=[sesi.pk, 1]))
        self.assertContains(resp, "Ada yang salah di soal ini? Laporkan")
        self.assertContains(resp, reverse("cpns:laporkan", args=[self.soal.pk]))
        for label in ("Kunci salah", "Soal ambigu", "Salah ketik", "Lainnya", "Kirim laporan"):
            self.assertContains(resp, label)

    def test_slot_di_hasil_cat_premium(self):
        user = buat_user("prem", premium=True)
        self.client.force_login(user)
        skema = SkemaUjian.objects.get(kode="SKD-CAT")
        sesi = buat_sesi_cat(user, skema, [self.soal], ["B"])
        Sesi.objects.filter(pk=sesi.pk).update(status="selesai", selesai_pada=timezone.now())
        resp = self.client.get(reverse("cpns:cat_hasil", args=[sesi.pk]))
        self.assertContains(resp, reverse("cpns:laporkan", args=[self.soal.pk]))

    def test_slot_tidak_ada_di_hasil_cat_trial(self):
        user = buat_user("trial")
        self.client.force_login(user)
        skema = SkemaUjian.objects.get(kode="SKD-CAT")
        sesi = buat_sesi_cat(user, skema, [self.soal], ["B"])
        Sesi.objects.filter(pk=sesi.pk).update(status="selesai", selesai_pada=timezone.now())
        resp = self.client.get(reverse("cpns:cat_hasil", args=[sesi.pk]))
        self.assertNotContains(resp, reverse("cpns:laporkan", args=[self.soal.pk]))


class JawabBelajarPadaCatTest(TestCase):
    def test_jawab_belajar_pada_cat_berjalan_404(self):
        user = buat_user("penyusup")
        self.client.force_login(user)
        skema = SkemaUjian.objects.get(kode="SKD-CAT")
        sesi = buat_sesi_cat(user, skema, [buat_soal("TIU", kunci="B")], [""])
        sesi.batas_waktu = timezone.now() + timedelta(minutes=60)
        sesi.save(update_fields=["batas_waktu"])
        resp = self.client.post(
            reverse("cpns:belajar_jawab", args=[sesi.pk, 1]), {"jawaban": "A"}, **HX
        )
        self.assertEqual(resp.status_code, 404)
        self.assertNotContains(resp, "Kunci jawaban", status_code=404)
        self.assertEqual(SesiSoal.objects.get(sesi=sesi).jawaban, "")


class KelemahanDasborTest(TestCase):
    def _soal_lemah(self, user):
        soal = [buat_soal("TIU", subtopik="Silogisme", kunci="A") for _ in range(5)]
        sesi_belajar(user, soal, ["A", "A", "B", "B", "B"])

    def test_dasbor_premium_tampil_kelemahan(self):
        user = buat_user("prem", premium=True)
        self.client.force_login(user)
        self._soal_lemah(user)
        resp = self.client.get(reverse("cpns:dasbor"))
        self.assertContains(resp, "Subtopik yang perlu dilatih")
        self.assertContains(resp, "TIU")
        self.assertContains(resp, "Silogisme")
        self.assertContains(resp, "40%")
        self.assertContains(resp, "(2/5)")
        self.assertContains(resp, "Latih subtopik ini")
        html = resp.content.decode()
        self.assertIn(f'action="{reverse("cpns:belajar_mulai")}"', html)
        self.assertIn('name="subtes" value="TIU"', html)
        self.assertIn('name="subtopik" value="Silogisme"', html)
        self.assertIn('name="jumlah" value="10"', html)

    def test_dasbor_tombol_latih_membuka_sesi(self):
        user = buat_user("prem2", premium=True)
        self.client.force_login(user)
        self._soal_lemah(user)
        for _ in range(5):
            buat_soal("TIU", subtopik="Silogisme")
        resp = self.client.post(
            reverse("cpns:belajar_mulai"), {"subtes": "TIU", "subtopik": "Silogisme", "jumlah": "10"}
        )
        self.assertEqual(resp.status_code, 302)

    def test_dasbor_trial_kartu_terkunci(self):
        user = buat_user("trial")
        self.client.force_login(user)
        self._soal_lemah(user)
        resp = self.client.get(reverse("cpns:dasbor"))
        self.assertContains(resp, "Ringkasan subtopik yang masih lemah khusus Premium.")
        self.assertContains(resp, "Khusus Premium")
        self.assertNotContains(resp, "Latih subtopik ini")
        self.assertNotContains(resp, "Silogisme")

    def test_dasbor_premium_belum_cukup_data(self):
        user = buat_user("prem3", premium=True)
        self.client.force_login(user)
        resp = self.client.get(reverse("cpns:dasbor"))
        self.assertContains(
            resp, "Belum cukup data. Jawab minimal 3 soal per subtopik di Mode Belajar."
        )
        self.assertNotContains(resp, "Latih subtopik ini")


class RiwayatKedaluwarsaTest(TestCase):
    def test_riwayat_cat_kedaluwarsa_tampil_selesai(self):
        user = buat_user("telat")
        self.client.force_login(user)
        sesi = sesi_cat_berjalan(user, menit=-5)
        resp = self.client.get(reverse("cpns:riwayat"))
        self.assertNotContains(resp, "Berjalan")
        self.assertContains(resp, "Selesai")
        self.assertContains(resp, reverse("cpns:cat_hasil", args=[sesi.pk]))
        sesi.refresh_from_db()
        self.assertEqual(sesi.status, "selesai")


class LaporkanBalapanTest(TestCase):
    def test_integrity_error_dibalas_pesan_sudah_ada(self):
        from unittest import mock

        from django.db import IntegrityError

        user = buat_user("balapan")
        self.client.force_login(user)
        soal = buat_soal("TIU")
        sesi_belajar(user, [soal], ["A"])
        with mock.patch.object(
            LaporanSoal.objects, "create", side_effect=IntegrityError
        ):
            resp = self.client.post(
                reverse("cpns:laporkan", args=[soal.pk]), {"alasan": "typo"}, **HX
            )
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "Laporan untuk soal ini sudah kami terima.")
