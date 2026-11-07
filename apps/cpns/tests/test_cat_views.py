import json
from datetime import timedelta
from unittest import mock

from django.contrib.auth import get_user_model
from django.db import IntegrityError
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from apps.cpns.models import AksesPeserta, Sesi, SkemaUjian
from apps.cpns.tests.pabrik import buat_sesi_cat, buat_soal, isi_bank_skd


RAHASIA = ("PEMBAHASAN-RAHASIA-KONSEP", "PEMBAHASAN-RAHASIA-PENGECOH", "PEMBAHASAN-RAHASIA-CEPAT")


def buat_user(username, *, google=True, premium=False):
    user = get_user_model().objects.create_user(username=username, email=f"{username}@contoh.id", password="x")
    AksesPeserta.objects.create(
        user=user,
        via_google=google,
        premium_sampai=timezone.now() + timedelta(days=30) if premium else None,
    )
    return user


def soal_rahasia(subtes, kunci="A"):
    soal = buat_soal(subtes, kunci=kunci)
    soal.pembahasan_konsep = f"{RAHASIA[0]}-{soal.pk}"
    soal.pembahasan_pengecoh = f"{RAHASIA[1]}-{soal.pk}"
    soal.pembahasan_cepat = f"{RAHASIA[2]}-{soal.pk}"
    soal.save()
    return soal


class CatViewsTest(TestCase):
    def setUp(self):
        self.skema = SkemaUjian.objects.get(kode="SKD-CAT")
        self.user = buat_user("peserta")
        self.client.force_login(self.user)

    def _sesi_berjalan(self, user=None, soal=None, menit=60):
        soal = soal or [soal_rahasia("TWK"), soal_rahasia("TIU"), soal_rahasia("TKP")]
        sesi = buat_sesi_cat(user or self.user, self.skema, soal, [""] * len(soal))
        sesi.status = "berjalan"
        sesi.batas_waktu = timezone.now() + timedelta(minutes=menit)
        sesi.save(update_fields=["status", "batas_waktu"])
        return sesi

    def _simpan(self, sesi, data):
        return self.client.post(
            reverse("cpns:cat_simpan", args=[sesi.pk]),
            data=json.dumps(data) if not isinstance(data, str) else data,
            content_type="application/json",
        )

    # mulai

    def test_mulai_ditolak_tampilkan_alasan(self):
        trial = buat_user("trial", google=False)
        self.client.force_login(trial)
        resp = self.client.post(
            reverse("cpns:cat_mulai", args=["skd-cat"]), follow=True
        )
        self.assertRedirects(resp, reverse("cpns:dasbor"))
        self.assertContains(resp, "Simulasi gratis hanya untuk akun Google.")
        self.assertFalse(Sesi.objects.filter(user=trial).exists())

    def test_mulai_bank_kurang_pesan(self):
        isi_bank_skd(tiu=10)
        resp = self.client.post(
            reverse("cpns:cat_mulai", args=["skd-cat"]), follow=True
        )
        self.assertRedirects(resp, reverse("cpns:dasbor"))
        self.assertContains(resp, "Bank soal untuk bagian TIU belum cukup")
        self.assertFalse(Sesi.objects.filter(user=self.user).exists())

    def test_mulai_sukses_ke_ruang(self):
        isi_bank_skd()
        resp = self.client.post(reverse("cpns:cat_mulai", args=["skd-cat"]))
        sesi = Sesi.objects.get(user=self.user)
        self.assertRedirects(
            resp, reverse("cpns:cat_ruang", args=[sesi.pk]), fetch_redirect_response=False
        )

    def test_mulai_bentrok_integrity_ke_sesi_berjalan(self):
        berjalan = self._sesi_berjalan()
        with mock.patch("apps.cpns.views.cat.boleh_mulai_cat", return_value=(True, "")), \
                mock.patch("apps.cpns.views.cat.rakit_sesi_cat", side_effect=IntegrityError("bentrok")):
            resp = self.client.post(reverse("cpns:cat_mulai", args=["skd-cat"]))
        self.assertRedirects(
            resp, reverse("cpns:cat_ruang", args=[berjalan.pk]), fetch_redirect_response=False
        )

    def test_mulai_bentrok_integrity_tanpa_sesi_ke_dasbor(self):
        with mock.patch("apps.cpns.views.cat.rakit_sesi_cat", side_effect=IntegrityError("bentrok")):
            resp = self.client.post(reverse("cpns:cat_mulai", args=["skd-cat"]), follow=True)
        self.assertRedirects(resp, reverse("cpns:dasbor"))
        self.assertContains(resp, "Simulasi gagal dimulai. Coba lagi.")

    def test_mulai_tutup_sesi_kedaluwarsa_dulu(self):
        premium = buat_user("premium", premium=True)
        self.client.force_login(premium)
        isi_bank_skd()
        lama = self._sesi_berjalan(user=premium, menit=-10)
        resp = self.client.post(reverse("cpns:cat_mulai", args=["skd-cat"]))
        lama.refresh_from_db()
        self.assertEqual(lama.status, "selesai")
        baru = Sesi.objects.get(user=premium, status="berjalan")
        self.assertNotEqual(baru.pk, lama.pk)
        self.assertRedirects(
            resp, reverse("cpns:cat_ruang", args=[baru.pk]), fetch_redirect_response=False
        )

    def test_mulai_get_ditolak(self):
        resp = self.client.get(reverse("cpns:cat_mulai", args=["skd-cat"]))
        self.assertEqual(resp.status_code, 405)

    def test_mulai_skema_tidak_ada_404(self):
        resp = self.client.post(reverse("cpns:cat_mulai", args=["tidak-ada"]))
        self.assertEqual(resp.status_code, 404)

    # ruang

    def test_ruang_tidak_bocorkan_kunci(self):
        sesi = self._sesi_berjalan()
        resp = self.client.get(reverse("cpns:cat_ruang", args=[sesi.pk]))
        self.assertEqual(resp.status_code, 200)
        html = resp.content.decode()
        for butir in sesi.butir.select_related("soal"):
            self.assertNotIn(butir.soal.pembahasan_konsep, html)
            self.assertNotIn(butir.soal.pembahasan_pengecoh, html)
            self.assertNotIn(butir.soal.pembahasan_cepat, html)
        for rahasia in RAHASIA:
            self.assertNotIn(rahasia, html)
        self.assertNotIn("data-kunci", html)
        payload = json.loads(_json_script(html, "data-ruang"))
        teks_payload = json.dumps(payload)
        self.assertNotIn("bobot", teks_payload)
        self.assertNotIn("kunci", teks_payload)
        self.assertEqual(len(payload["soal"]), 3)
        self.assertEqual(set(payload["soal"][0]), {"nomor", "subtes", "subtopik", "teks", "opsi", "jawaban", "ragu"})

    def test_ruang_opsi_urutan_tampil_dan_jawaban_tampil(self):
        sesi = self._sesi_berjalan()
        butir = sesi.butir.get(nomor=1)
        butir.urutan_opsi = "CAEBD"
        butir.jawaban = "E"
        butir.ragu = True
        butir.save()
        resp = self.client.get(reverse("cpns:cat_ruang", args=[sesi.pk]))
        payload = json.loads(_json_script(resp.content.decode(), "data-ruang"))
        pertama = payload["soal"][0]
        self.assertEqual([o["key"] for o in pertama["opsi"]], list("ABCDE"))
        self.assertEqual(pertama["opsi"][0]["text"], butir.soal.opsi_c)
        self.assertEqual(pertama["opsi"][2]["text"], butir.soal.opsi_e)
        self.assertEqual(pertama["jawaban"], "C")
        self.assertTrue(pertama["ragu"])
        self.assertGreater(payload["sisa_detik"], 3500)
        self.assertContains(resp, "<title>Ruang Ujian SKD | CPNS Hub</title>", html=False)

    def test_ruang_sesi_orang_lain_404(self):
        lain = buat_user("lain")
        sesi = self._sesi_berjalan(user=lain)
        resp = self.client.get(reverse("cpns:cat_ruang", args=[sesi.pk]))
        self.assertEqual(resp.status_code, 404)
        self.assertEqual(self._simpan(sesi, {"nomor": 1, "jawaban": "A", "ragu": False}).status_code, 404)
        resp = self.client.get(reverse("cpns:cat_hasil", args=[sesi.pk]))
        self.assertEqual(resp.status_code, 404)
        resp = self.client.post(reverse("cpns:cat_kumpulkan", args=[sesi.pk]))
        self.assertEqual(resp.status_code, 404)

    def test_ruang_butuh_login(self):
        sesi = self._sesi_berjalan()
        self.client.logout()
        resp = self.client.get(reverse("cpns:cat_ruang", args=[sesi.pk]))
        self.assertEqual(resp.status_code, 302)
        self.assertIn(reverse("cpns:masuk"), resp["Location"])

    def test_ruang_setelah_waktu_habis_redirect_hasil(self):
        sesi = self._sesi_berjalan()
        sesi.batas_waktu = timezone.now() - timedelta(minutes=5)
        sesi.save(update_fields=["batas_waktu"])
        resp = self.client.get(reverse("cpns:cat_ruang", args=[sesi.pk]))
        self.assertRedirects(
            resp, reverse("cpns:cat_hasil", args=[sesi.pk]), fetch_redirect_response=False
        )
        sesi.refresh_from_db()
        self.assertEqual(sesi.status, "selesai")

    def test_ruang_sesi_selesai_redirect_hasil(self):
        sesi = self._sesi_berjalan()
        self.client.post(reverse("cpns:cat_kumpulkan", args=[sesi.pk]))
        resp = self.client.get(reverse("cpns:cat_ruang", args=[sesi.pk]))
        self.assertRedirects(
            resp, reverse("cpns:cat_hasil", args=[sesi.pk]), fetch_redirect_response=False
        )

    # simpan

    def test_simpan_json_valid_200(self):
        sesi = self._sesi_berjalan()
        butir = sesi.butir.get(nomor=2)
        butir.urutan_opsi = "CAEBD"
        butir.save(update_fields=["urutan_opsi"])
        resp = self._simpan(sesi, {"nomor": 2, "jawaban": "A", "ragu": True})
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertTrue(data["ok"])
        self.assertIn("tersimpan_pada", data)
        butir.refresh_from_db()
        self.assertEqual(butir.jawaban, "C")
        self.assertTrue(butir.ragu)

    def test_simpan_anonim_401_json(self):
        sesi = self._sesi_berjalan()
        self.client.logout()
        resp = self._simpan(sesi, {"nomor": 1, "jawaban": "A", "ragu": False})
        self.assertEqual(resp.status_code, 401)
        self.assertEqual(resp.json(), {"ok": False, "alasan": "belum_masuk"})
        self.assertEqual(sesi.butir.get(nomor=1).jawaban, "")

    def test_simpan_jawaban_F_400(self):
        sesi = self._sesi_berjalan()
        resp = self._simpan(sesi, {"nomor": 1, "jawaban": "F", "ragu": False})
        self.assertEqual(resp.status_code, 400)
        self.assertEqual(resp.json(), {"ok": False, "alasan": "data_tidak_valid"})

    def test_simpan_nomor_999_400(self):
        sesi = self._sesi_berjalan()
        resp = self._simpan(sesi, {"nomor": 999, "jawaban": "A", "ragu": False})
        self.assertEqual(resp.status_code, 400)
        self.assertEqual(resp.json(), {"ok": False, "alasan": "data_tidak_valid"})

    def test_simpan_tipe_salah_400(self):
        sesi = self._sesi_berjalan()
        for data in (
            "bukan json",
            [1, 2],
            {"nomor": "1", "jawaban": "A", "ragu": False},
            {"nomor": True, "jawaban": "A", "ragu": False},
            {"nomor": 1, "jawaban": 1, "ragu": False},
            {"nomor": 1, "jawaban": "A", "ragu": "ya"},
            {"nomor": 1, "jawaban": "A"},
        ):
            with self.subTest(data=data):
                self.assertEqual(self._simpan(sesi, data).status_code, 400)

    def test_simpan_setelah_waktu_409(self):
        sesi = self._sesi_berjalan()
        sesi.batas_waktu = timezone.now() - timedelta(minutes=5)
        sesi.save(update_fields=["batas_waktu"])
        resp = self._simpan(sesi, {"nomor": 1, "jawaban": "A", "ragu": False})
        self.assertEqual(resp.status_code, 409)
        self.assertEqual(resp.json(), {"ok": False, "alasan": "waktu_habis"})

    def test_simpan_sesi_selesai_409(self):
        sesi = self._sesi_berjalan()
        self.client.post(reverse("cpns:cat_kumpulkan", args=[sesi.pk]))
        resp = self._simpan(sesi, {"nomor": 1, "jawaban": "A", "ragu": False})
        self.assertEqual(resp.status_code, 409)
        self.assertEqual(resp.json(), {"ok": False, "alasan": "sudah_selesai"})

    # kumpulkan dan hasil

    def test_kumpulkan_menilai_dan_redirect_hasil(self):
        sesi = self._sesi_berjalan()
        self._simpan(sesi, {"nomor": 1, "jawaban": "A", "ragu": False})
        resp = self.client.post(reverse("cpns:cat_kumpulkan", args=[sesi.pk]))
        self.assertRedirects(
            resp, reverse("cpns:cat_hasil", args=[sesi.pk]), fetch_redirect_response=False
        )
        sesi.refresh_from_db()
        self.assertEqual(sesi.status, "selesai")
        self.assertEqual(sesi.total, 5)

    def test_hasil_sesi_berjalan_redirect_ruang(self):
        sesi = self._sesi_berjalan()
        resp = self.client.get(reverse("cpns:cat_hasil", args=[sesi.pk]))
        self.assertRedirects(
            resp, reverse("cpns:cat_ruang", args=[sesi.pk]), fetch_redirect_response=False
        )

    def test_hasil_trial_tanpa_pembahasan(self):
        sesi = self._sesi_berjalan()
        self.client.post(reverse("cpns:cat_kumpulkan", args=[sesi.pk]))
        resp = self.client.get(reverse("cpns:cat_hasil", args=[sesi.pk]))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "Pembahasan")
        self.assertContains(resp, "Premium")
        self.assertContains(resp, "Pembahasan 3 soal ada di Premium")
        self.assertContains(resp, f'href="{reverse("cpns:premium")}"')
        self.assertContains(resp, "<title>Hasil Simulasi | CPNS Hub</title>", html=False)
        html = resp.content.decode()
        for rahasia in RAHASIA:
            self.assertNotIn(rahasia, html)
        self.assertNotIn("Kunci jawaban", html)

    def test_hasil_premium_ada_pembahasan(self):
        premium = buat_user("premium", premium=True)
        self.client.force_login(premium)
        sesi = self._sesi_berjalan(user=premium)
        self._simpan(sesi, {"nomor": 1, "jawaban": "B", "ragu": False})
        self.client.post(reverse("cpns:cat_kumpulkan", args=[sesi.pk]))
        resp = self.client.get(reverse("cpns:cat_hasil", args=[sesi.pk]))
        self.assertEqual(resp.status_code, 200)
        for butir in sesi.butir.select_related("soal"):
            self.assertContains(resp, butir.soal.pembahasan_konsep)
            self.assertContains(resp, butir.soal.pembahasan_pengecoh)
            self.assertContains(resp, butir.soal.pembahasan_cepat)
        for label in ("Konsep", "Kenapa opsi lain salah", "Cara cepat", "Jawabanmu", "Kunci jawaban", "Bobot 5"):
            self.assertContains(resp, label)
        self.assertNotContains(resp, "ada di Premium")

    def test_hasil_ringkasan_skor(self):
        soal = [soal_rahasia("TWK", kunci="A") for _ in range(2)]
        sesi = self._sesi_berjalan(soal=soal)
        self._simpan(sesi, {"nomor": 1, "jawaban": "A", "ragu": False})
        self.client.post(reverse("cpns:cat_kumpulkan", args=[sesi.pk]))
        sesi.refresh_from_db()
        sesi.batas_waktu = sesi.dimulai_pada + timedelta(minutes=100)
        sesi.selesai_pada = sesi.dimulai_pada + timedelta(minutes=88, seconds=12)
        sesi.save(update_fields=["batas_waktu", "selesai_pada"])
        resp = self.client.get(reverse("cpns:cat_hasil", args=[sesi.pk]))
        self.assertContains(resp, "Belum lolos ambang batas")
        self.assertContains(resp, "TWK kurang 60 poin")
        self.assertContains(resp, "5 / 550")
        self.assertContains(resp, "88 menit 12 detik")
        self.assertContains(resp, "Kurang 60 (ambang 65)")


class DasborSimulasiTest(TestCase):
    def setUp(self):
        self.user = buat_user("dasbor")
        self.client.force_login(self.user)

    def test_dasbor_daftar_skema_aktif(self):
        resp = self.client.get(reverse("cpns:dasbor"))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "<title>Dasbor | CPNS Hub</title>", html=False)
        self.assertContains(resp, "Mulai simulasi SKD")
        self.assertNotContains(resp, "Mulai simulasi SKB Guru")
        self.assertContains(resp, reverse("cpns:cat_mulai", args=["skd-cat"]))

    def test_dasbor_tombol_mulai_nonaktif_setelah_kirim(self):
        html = self.client.get(reverse("cpns:dasbor")).content.decode()
        form = html[html.index(reverse("cpns:cat_mulai", args=["skd-cat"])):]
        form = form[: form.index("</form>")]
        self.assertIn('@submit="terkirim = true"', form)
        self.assertIn(':disabled="terkirim"', form)

    def test_dasbor_superuser_lihat_skema_nonaktif(self):
        admin = get_user_model().objects.create_superuser(username="adm", email="adm@contoh.id", password="x")
        self.client.force_login(admin)
        resp = self.client.get(reverse("cpns:dasbor"))
        self.assertContains(resp, "Mulai simulasi SKB Guru")

    def test_dasbor_tautan_lanjutkan(self):
        skema = SkemaUjian.objects.get(kode="SKD-CAT")
        sesi = buat_sesi_cat(self.user, skema, [buat_soal("TWK")], [""])
        resp = self.client.get(reverse("cpns:dasbor"))
        self.assertContains(resp, "Lanjutkan ujian")
        self.assertContains(resp, reverse("cpns:cat_ruang", args=[sesi.pk]))


def _json_script(html, element_id):
    awal = html.index(f'id="{element_id}"')
    awal = html.index(">", awal) + 1
    akhir = html.index("</script>", awal)
    return html[awal:akhir]


class RuangCatTeksStatusTest(TestCase):
    _sesi_berjalan = CatViewsTest._sesi_berjalan
    _simpan = CatViewsTest._simpan

    def setUp(self):
        self.skema = SkemaUjian.objects.get(kode="SKD-CAT")
        self.user = buat_user("peserta")
        self.client.force_login(self.user)

    def _html(self):
        sesi = self._sesi_berjalan()
        resp = self.client.get(reverse("cpns:cat_ruang", args=[sesi.pk]))
        return sesi, resp.content.decode()

    def test_ruang_teks_status_baru_ada(self):
        _, html = self._html()
        self.assertIn("Waktu habis, mengumpulkan…", html)
        self.assertIn("Ujian sudah dikumpulkan.", html)
        self.assertIn("Jawaban tidak tersimpan. Coba pilih lagi.", html)

    def test_ruang_memuat_url_hasil_untuk_pengalihan(self):
        sesi, html = self._html()
        payload = json.loads(_json_script(html, "data-ruang"))
        self.assertEqual(payload["url_hasil"], reverse("cpns:cat_hasil", args=[sesi.pk]))

    def test_ruang_dialog_punya_acuan_jebakan_fokus(self):
        _, html = self._html()
        self.assertIn('x-ref="dialogKonfirmasi"', html)
        self.assertIn('x-ref="panelNav"', html)
        self.assertIn("jebakFokus", html)

    def test_simpan_sudah_selesai_dan_waktu_habis_dibedakan(self):
        sesi = self._sesi_berjalan()
        sesi.status = "selesai"
        sesi.save(update_fields=["status"])
        resp = self._simpan(sesi, {"nomor": 1, "jawaban": "A", "ragu": False})
        self.assertEqual((resp.status_code, resp.json()["alasan"]), (409, "sudah_selesai"))
        sesi2 = self._sesi_berjalan(menit=-5)
        resp = self._simpan(sesi2, {"nomor": 1, "jawaban": "A", "ragu": False})
        self.assertEqual((resp.status_code, resp.json()["alasan"]), (409, "waktu_habis"))
