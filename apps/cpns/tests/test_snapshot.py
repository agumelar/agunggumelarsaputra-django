from datetime import timedelta
import importlib

from django.apps import apps as apps_global
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from apps.cpns.analitik import kelemahan_subtopik
from apps.cpns.models import Sesi, SesiSoal, SkemaUjian
from apps.cpns.penilaian import nilai_sesi
from apps.cpns.tests.pabrik import buat_sesi_cat, buat_soal
from apps.cpns.tests.test_belajar_views import (
    HX,
    buat_sesi_belajar,
    buat_user as buat_user_belajar,
)
from apps.cpns.tests.test_cat_views import buat_user


class SnapshotCatTest(TestCase):
    def setUp(self):
        self.skema = SkemaUjian.objects.get(kode="SKD-CAT")
        self.user = buat_user("snap_cat", premium=True)
        self.client.force_login(self.user)

    def _sesi(self, soal_list, jawaban_list):
        sesi = buat_sesi_cat(self.user, self.skema, soal_list, jawaban_list)
        sesi.batas_waktu = timezone.now() + timedelta(minutes=60)
        sesi.save(update_fields=["batas_waktu"])
        return sesi

    def test_cat_benar_dibekukan(self):
        soal = buat_soal("TWK", kunci="A")
        sesi = self._sesi([soal], ["A"])
        self.client.post(reverse("cpns:cat_kumpulkan", args=[sesi.pk]))
        sesi.refresh_from_db()
        skor_awal = sesi.total
        soal.kunci = "B"
        soal.save()
        resp = self.client.get(reverse("cpns:cat_hasil", args=[sesi.pk]))
        self.assertEqual(resp.context["ulasan"][0]["status"], "Benar")
        sesi.refresh_from_db()
        self.assertEqual(sesi.total, skor_awal)
        self.assertTrue(sesi.butir.get().benar)

    def test_butir_kosong_benar_false(self):
        sesi = self._sesi([buat_soal("TWK"), buat_soal("TWK")], ["A", ""])
        nilai_sesi(sesi)
        benar = list(sesi.butir.order_by("nomor").values_list("benar", flat=True))
        self.assertEqual(benar, [True, False])

    def test_butir_belum_dinilai_null_dan_cadangan(self):
        soal = buat_soal("TWK", kunci="A")
        sesi = self._sesi([soal], ["A"])
        self.assertIsNone(sesi.butir.get().benar)


class SnapshotBelajarTest(TestCase):
    def setUp(self):
        self.user = buat_user_belajar("snap_belajar")
        self.client.force_login(self.user)

    def test_belajar_benar_dibekukan(self):
        soal = [buat_soal("TIU", kunci="A", subtopik="Beku") for _ in range(3)]
        sesi = buat_sesi_belajar(self.user, soal)
        for nomor in (1, 2, 3):
            self.client.post(
                reverse("cpns:belajar_jawab", args=[sesi.pk, nomor]), {"jawaban": "A"}, **HX
            )
        self.assertEqual(
            list(sesi.butir.order_by("nomor").values_list("benar", flat=True)),
            [True, True, True],
        )
        for s in soal:
            s.kunci = "B"
            s.save()
        resp = self.client.get(reverse("cpns:belajar_ringkasan", args=[sesi.pk]))
        self.assertEqual(resp.context["jumlah_benar"], 3)
        self.assertEqual(resp.context["rekap"][0]["benar"], 3)
        lemah = kelemahan_subtopik(self.user)
        self.assertEqual(lemah[0]["benar"], 3)

    def test_belajar_salah_disimpan_false(self):
        soal = buat_soal("TIU", kunci="A")
        sesi = buat_sesi_belajar(self.user, [soal])
        self.client.post(
            reverse("cpns:belajar_jawab", args=[sesi.pk, 1]), {"jawaban": "B"}, **HX
        )
        self.assertIs(sesi.butir.get().benar, False)


class MigrasiIsiBenarTest(TestCase):
    def test_migrasi_isi_benar(self):
        modul = importlib.import_module("apps.cpns.migrations.0010_isi_benar_butir")
        user = buat_user_belajar("snap_migrasi")
        cat = Sesi.objects.create(user=user, mode="cat", status="selesai")
        belajar = Sesi.objects.create(user=user, mode="belajar", status="berjalan")
        soal = buat_soal("TIU", kunci="A")
        def butir(sesi, nomor, jawaban):
            return SesiSoal.objects.create(
                sesi=sesi, soal=soal, nomor=nomor, urutan_opsi="ABCDE", jawaban=jawaban
            )
        cat_benar = butir(cat, 1, "A")
        cat_salah = butir(cat, 2, "B")
        cat_kosong = butir(cat, 3, "")
        bel_benar = butir(belajar, 1, "A")
        bel_belum = butir(belajar, 2, "")
        modul.isi_benar(apps_global, None)
        for obj in (cat_benar, cat_salah, cat_kosong, bel_benar, bel_belum):
            obj.refresh_from_db()
        self.assertIs(cat_benar.benar, True)
        self.assertIs(cat_salah.benar, False)
        self.assertIs(cat_kosong.benar, False)
        self.assertIs(bel_benar.benar, True)
        self.assertIsNone(bel_belum.benar)
        modul.kosongkan(apps_global, None)
