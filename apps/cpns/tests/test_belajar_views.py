from datetime import timedelta

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from apps.cpns.models import AksesPeserta, PaketBelajar, PaketSoal, Sesi, SesiSoal
from apps.cpns.tests.pabrik import buat_soal

RAHASIA = ("PEMBAHASAN-RAHASIA-KONSEP", "PEMBAHASAN-RAHASIA-PENGECOH", "PEMBAHASAN-RAHASIA-CEPAT")


def buat_user(username, *, premium=False):
    user = get_user_model().objects.create_user(
        username=username, email=f"{username}@contoh.id", password="x"
    )
    AksesPeserta.objects.create(
        user=user,
        via_google=True,
        premium_sampai=timezone.now() + timedelta(days=30) if premium else None,
    )
    return user


def soal_rahasia(subtes="TIU", kunci="B", subtopik="Silogisme"):
    soal = buat_soal(subtes, kunci=kunci, subtopik=subtopik)
    soal.pembahasan_konsep = f"{RAHASIA[0]}-{soal.pk}"
    soal.pembahasan_pengecoh = f"{RAHASIA[1]}-{soal.pk}"
    soal.pembahasan_cepat = f"{RAHASIA[2]}-{soal.pk}"
    soal.save()
    return soal


def buat_paket(soal_list, *, trial=False, nama="Paket gratis", aktif=True):
    paket = PaketBelajar.objects.create(
        nama=nama, jenis_ujian="SKD", untuk_trial=trial, aktif=aktif
    )
    for urutan, soal in enumerate(soal_list, start=1):
        PaketSoal.objects.create(paket=paket, soal=soal, urutan=urutan)
    return paket


def buat_sesi_belajar(user, soal_list, *, urutan="ABCDE", paket=None):
    sesi = Sesi.objects.create(user=user, mode="belajar", paket=paket, status="berjalan")
    for nomor, soal in enumerate(soal_list, start=1):
        SesiSoal.objects.create(sesi=sesi, soal=soal, nomor=nomor, urutan_opsi=urutan)
    return sesi


HX = {"HTTP_HX_REQUEST": "true"}


class BelajarViewsTest(TestCase):
    def setUp(self):
        self.user = buat_user("pelajar")
        self.client.force_login(self.user)

    def _jawab(self, sesi, nomor, jawaban, hx=True):
        return self.client.post(
            reverse("cpns:belajar_jawab", args=[sesi.pk, nomor]),
            {"jawaban": jawaban},
            **(HX if hx else {}),
        )

    # halaman soal

    def test_halaman_soal_belum_jawab_tanpa_kunci(self):
        soal = soal_rahasia(kunci="B")
        sesi = buat_sesi_belajar(self.user, [soal], urutan="CAEBD")
        resp = self.client.get(reverse("cpns:belajar_soal", args=[sesi.pk, 1]))
        self.assertEqual(resp.status_code, 200)
        html = resp.content.decode()
        for rahasia in RAHASIA:
            self.assertNotIn(rahasia, html)
        self.assertNotIn("Kunci jawaban", html)
        self.assertNotIn("Kunci jawabannya", html)
        self.assertIn(soal.teks, html)
        self.assertIn(soal.opsi_c, html)
        self.assertContains(resp, "<title>Soal 1 dari 1", html=False)
        self.assertContains(resp, 'name="jawaban" value="A"')
        self.assertContains(resp, 'hx-post="' + reverse("cpns:belajar_jawab", args=[sesi.pk, 1]))

    def test_halaman_soal_sudah_dijawab_tampil_umpan_balik(self):
        soal = soal_rahasia(kunci="B")
        sesi = buat_sesi_belajar(self.user, [soal])
        self._jawab(sesi, 1, "D")
        resp = self.client.get(reverse("cpns:belajar_soal", args=[sesi.pk, 1]))
        self.assertContains(resp, "Kunci jawaban")
        self.assertContains(resp, f"{RAHASIA[0]}-{soal.pk}")
        self.assertNotContains(resp, 'name="jawaban"')

    def test_soal_nomor_di_luar_rentang_404(self):
        sesi = buat_sesi_belajar(self.user, [soal_rahasia()])
        resp = self.client.get(reverse("cpns:belajar_soal", args=[sesi.pk, 2]))
        self.assertEqual(resp.status_code, 404)

    def test_soal_sesi_orang_lain_404(self):
        lain = buat_user("lain")
        sesi = buat_sesi_belajar(lain, [soal_rahasia()])
        self.assertEqual(
            self.client.get(reverse("cpns:belajar_soal", args=[sesi.pk, 1])).status_code, 404
        )
        self.assertEqual(self._jawab(sesi, 1, "A").status_code, 404)
        self.assertEqual(
            self.client.get(reverse("cpns:belajar_ringkasan", args=[sesi.pk])).status_code, 404
        )
        self.assertEqual(SesiSoal.objects.get(sesi=sesi).jawaban, "")

    def test_sesi_cat_bukan_belajar_404(self):
        sesi = Sesi.objects.create(user=self.user, mode="cat")
        SesiSoal.objects.create(sesi=sesi, soal=soal_rahasia(), nomor=1, urutan_opsi="ABCDE")
        resp = self.client.get(reverse("cpns:belajar_soal", args=[sesi.pk, 1]))
        self.assertEqual(resp.status_code, 404)

    # jawab

    def test_jawab_balas_kunci_dan_pembahasan(self):
        soal = soal_rahasia(kunci="B")
        # Posisi tampil A memuat opsi asli C, D memuat B (kunci), B memuat A.
        sesi = buat_sesi_belajar(self.user, [soal], urutan="CAEBD")
        resp = self._jawab(sesi, 1, "B")
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "Kunci jawaban")
        self.assertContains(resp, "Jawabanmu")
        for rahasia in RAHASIA:
            self.assertContains(resp, f"{rahasia}-{soal.pk}")
        self.assertContains(resp, "Kurang tepat")
        self.assertContains(resp, "Kamu memilih B. Kunci jawabannya D.")
        self.assertNotContains(resp, "<html")
        self.assertEqual(SesiSoal.objects.get(sesi=sesi).jawaban, "A")

    def test_jawab_benar(self):
        soal = soal_rahasia(kunci="B")
        sesi = buat_sesi_belajar(self.user, [soal, soal_rahasia()], urutan="CAEBD")
        resp = self._jawab(sesi, 1, "D")
        self.assertContains(resp, "Benar")
        self.assertContains(resp, "Kamu memilih D. Kunci jawabannya D.")
        self.assertContains(resp, "Soal berikutnya")
        self.assertContains(resp, reverse("cpns:belajar_soal", args=[sesi.pk, 2]))

    def test_jawab_soal_terakhir_lihat_ringkasan(self):
        sesi = buat_sesi_belajar(self.user, [soal_rahasia()])
        resp = self._jawab(sesi, 1, "A")
        self.assertContains(resp, "Lihat ringkasan")
        self.assertContains(resp, reverse("cpns:belajar_ringkasan", args=[sesi.pk]))

    def test_jawab_tkp_tampil_bobot(self):
        soal = buat_soal("TKP", subtopik="Pelayanan publik")
        sesi = buat_sesi_belajar(self.user, [soal], urutan="EDCBA")
        # Tampil A = asli E (bobot 5), tampil C = asli C (bobot 3).
        resp = self._jawab(sesi, 1, "C")
        self.assertContains(resp, "Kamu memilih C (bobot 3). Pilihan terbaik A (bobot 5).")
        for n in range(1, 6):
            self.assertContains(resp, f"Bobot {n}")
        self.assertContains(resp, "Kurang tepat")

    def test_jawab_tidak_valid_400(self):
        sesi = buat_sesi_belajar(self.user, [soal_rahasia()])
        self.assertEqual(self._jawab(sesi, 1, "F").status_code, 400)
        self.assertEqual(self._jawab(sesi, 1, "").status_code, 400)

    def test_jawab_sesi_selesai_409(self):
        sesi = buat_sesi_belajar(self.user, [soal_rahasia()])
        sesi.status = "selesai"
        sesi.save(update_fields=["status"])
        self.assertEqual(self._jawab(sesi, 1, "A").status_code, 409)

    def test_jawab_tidak_bisa_diulang(self):
        soal = soal_rahasia(kunci="B")
        sesi = buat_sesi_belajar(self.user, [soal])
        self._jawab(sesi, 1, "D")
        resp = self._jawab(sesi, 1, "B")
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "Kamu memilih D.")
        self.assertEqual(SesiSoal.objects.get(sesi=sesi).jawaban, "D")

    def test_jawab_tanpa_htmx_redirect_ke_soal(self):
        sesi = buat_sesi_belajar(self.user, [soal_rahasia()])
        resp = self._jawab(sesi, 1, "C", hx=False)
        self.assertRedirects(resp, reverse("cpns:belajar_soal", args=[sesi.pk, 1]))
        self.assertEqual(SesiSoal.objects.get(sesi=sesi).jawaban, "C")

    # mulai

    def test_trial_tidak_boleh_subtopik(self):
        buat_soal("TIU", subtopik="Silogisme")
        resp = self.client.post(
            reverse("cpns:belajar_mulai"),
            {"subtes": "TIU", "subtopik": "Silogisme", "jumlah": "10"},
        )
        self.assertEqual(resp.status_code, 403)
        self.assertFalse(Sesi.objects.filter(user=self.user).exists())

    def test_trial_boleh_paket_trial(self):
        paket = buat_paket([soal_rahasia(), soal_rahasia()], trial=True)
        resp = self.client.post(reverse("cpns:belajar_mulai"), {"paket_id": paket.pk})
        sesi = Sesi.objects.get(user=self.user)
        self.assertEqual(sesi.mode, "belajar")
        self.assertEqual(sesi.paket, paket)
        self.assertRedirects(resp, reverse("cpns:belajar_soal", args=[sesi.pk, 1]))

    def test_trial_tidak_boleh_paket_premium(self):
        paket = buat_paket([soal_rahasia()], trial=False, nama="Paket premium")
        resp = self.client.post(reverse("cpns:belajar_mulai"), {"paket_id": paket.pk})
        self.assertEqual(resp.status_code, 403)
        self.assertFalse(Sesi.objects.filter(user=self.user).exists())

    def test_premium_subtopik_kurang_beri_info(self):
        premium = buat_user("premium", premium=True)
        self.client.force_login(premium)
        for _ in range(4):
            buat_soal("TIU", subtopik="Silogisme")
        resp = self.client.post(
            reverse("cpns:belajar_mulai"),
            {"subtes": "TIU", "subtopik": "Silogisme", "jumlah": "10"},
            follow=True,
        )
        sesi = Sesi.objects.get(user=premium)
        self.assertRedirects(resp, reverse("cpns:belajar_soal", args=[sesi.pk, 1]))
        self.assertContains(resp, "Tersedia 4 soal untuk pilihan ini.")
        self.assertEqual(sesi.butir.count(), 4)

    def test_premium_subtopik_kosong_pesan_error(self):
        premium = buat_user("premium", premium=True)
        self.client.force_login(premium)
        resp = self.client.post(
            reverse("cpns:belajar_mulai"),
            {"subtes": "TWK", "subtopik": "", "jumlah": "20"},
            follow=True,
        )
        self.assertRedirects(resp, reverse("cpns:belajar_pilih"))
        self.assertContains(resp, "Belum ada soal untuk pilihan ini.")
        self.assertFalse(Sesi.objects.filter(user=premium).exists())

    def test_jumlah_tidak_sah_400(self):
        premium = buat_user("premium", premium=True)
        self.client.force_login(premium)
        buat_soal("TIU")
        resp = self.client.post(
            reverse("cpns:belajar_mulai"), {"subtes": "TIU", "subtopik": "", "jumlah": "15"}
        )
        self.assertEqual(resp.status_code, 400)

    def test_mulai_get_405(self):
        self.assertEqual(self.client.get(reverse("cpns:belajar_mulai")).status_code, 405)

    # pilih

    def test_pilih_trial_lihat_paket_terkunci(self):
        buat_paket([soal_rahasia()], trial=True, nama="Paket gratis SKD")
        buat_paket([soal_rahasia()], trial=False, nama="Paket lanjutan TIU")
        resp = self.client.get(reverse("cpns:belajar_pilih"))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "<title>Belajar", html=False)
        self.assertContains(resp, "Paket gratis SKD")
        self.assertContains(resp, "Paket lanjutan TIU")
        self.assertContains(resp, "Premium")
        self.assertContains(resp, "Belajar per subtopik khusus Premium.")
        self.assertNotContains(resp, 'name="subtopik"')
        self.assertContains(resp, 'name="paket_id"', count=1)

    def test_pilih_premium_lihat_form_subtopik(self):
        premium = buat_user("premium", premium=True)
        self.client.force_login(premium)
        buat_soal("TIU", subtopik="Silogisme")
        buat_soal("TWK", subtopik="Pancasila")
        buat_soal("TWK", subtopik="Rahasia draf", status="draf")
        resp = self.client.get(reverse("cpns:belajar_pilih"))
        self.assertContains(resp, 'name="subtopik"')
        self.assertContains(resp, "Silogisme")
        self.assertContains(resp, "Pancasila")
        self.assertNotContains(resp, "Rahasia draf")
        self.assertContains(resp, "Semua subtopik")
        self.assertNotContains(resp, "Belajar per subtopik khusus Premium.")

    def test_pilih_kosong(self):
        resp = self.client.get(reverse("cpns:belajar_pilih"))
        self.assertContains(resp, "Belum ada paket belajar.")

    # ringkasan

    def test_ringkasan_persen_per_subtopik(self):
        soal = [soal_rahasia(kunci="A", subtopik="Silogisme") for _ in range(4)]
        soal.append(soal_rahasia(kunci="A", subtopik="Deret angka"))
        sesi = buat_sesi_belajar(self.user, soal)
        for nomor, jawaban in zip((1, 2, 3, 4), ("A", "A", "A", "B")):
            self._jawab(sesi, nomor, jawaban)
        resp = self.client.get(reverse("cpns:belajar_ringkasan", args=[sesi.pk]))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "<title>Ringkasan Belajar", html=False)
        self.assertContains(resp, "Silogisme")
        self.assertContains(resp, "3 / 4")
        self.assertContains(resp, "75%")
        self.assertContains(resp, "belum dijawab")
        sesi.refresh_from_db()
        self.assertEqual(sesi.status, "selesai")

    def test_ringkasan_kosong(self):
        sesi = buat_sesi_belajar(self.user, [soal_rahasia()])
        resp = self.client.get(reverse("cpns:belajar_ringkasan", args=[sesi.pk]))
        self.assertContains(resp, "Belum ada soal yang dijawab.")

    def test_ringkasan_ulangi_paket(self):
        soal = soal_rahasia()
        paket = buat_paket([soal], trial=True)
        sesi = buat_sesi_belajar(self.user, [soal], paket=paket)
        resp = self.client.get(reverse("cpns:belajar_ringkasan", args=[sesi.pk]))
        self.assertContains(resp, "Ulangi paket ini")
        self.assertContains(resp, f'name="paket_id" value="{paket.pk}"')
        self.assertContains(resp, "Kembali ke Belajar")

    def test_soal_belum_dijawab_setelah_selesai_tampil_pembahasan(self):
        soal = soal_rahasia(kunci="B")
        sesi = buat_sesi_belajar(self.user, [soal_rahasia(), soal])
        self.client.get(reverse("cpns:belajar_ringkasan", args=[sesi.pk]))
        resp = self.client.get(reverse("cpns:belajar_soal", args=[sesi.pk, 2]))
        self.assertContains(resp, "Tidak dijawab")
        self.assertContains(resp, "Soal ini tidak dijawab. Kunci jawabannya B.")
        self.assertContains(resp, f"{RAHASIA[2]}-{soal.pk}")
        self.assertNotContains(resp, 'name="jawaban"')

    def test_ringkasan_paket_premium_tanpa_ulangi_untuk_trial(self):
        soal = soal_rahasia()
        paket = buat_paket([soal], trial=False, nama="Paket premium")
        sesi = buat_sesi_belajar(self.user, [soal], paket=paket)
        resp = self.client.get(reverse("cpns:belajar_ringkasan", args=[sesi.pk]))
        self.assertNotContains(resp, "Ulangi paket ini")
        self.assertContains(resp, "Kembali ke Belajar")

    def test_umpan_balik_htmx_fokus_ke_hasil(self):
        sesi = buat_sesi_belajar(self.user, [soal_rahasia()])
        resp = self._jawab(sesi, 1, "A")
        self.assertContains(resp, 'id="area-jawab"')
        self.assertContains(resp, "autofocus")
        self.assertContains(resp, "diisi Task 12", count=0)
