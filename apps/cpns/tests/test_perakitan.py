import random

from django.contrib.auth import get_user_model
from django.test import TestCase

from apps.cpns.models import PaketBelajar, PaketSoal, Sesi, SkemaUjian
from apps.cpns.perakitan import (
    BankSoalKurang,
    acak_urutan_opsi,
    opsi_tampil_ke_asli,
    rakit_sesi_belajar,
    rakit_sesi_cat,
)
from apps.cpns.tests.pabrik import buat_sesi_cat, buat_soal, isi_bank_skd


class PerakitanCatTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(username="peserta", password="x")
        self.skema = SkemaUjian.objects.get(kode="SKD-CAT")
        self.rng = random.Random(1)

    def test_komposisi_sesi_sesuai_skema(self):
        isi_bank_skd()
        sesi = rakit_sesi_cat(self.user, self.skema, rng=self.rng)
        butir = list(sesi.butir.select_related("soal"))
        self.assertEqual(len(butir), 110)
        self.assertEqual([b.nomor for b in butir], list(range(1, 111)))
        self.assertTrue(all(b.soal.subtes == "TWK" for b in butir[:30]))
        self.assertTrue(all(b.soal.subtes == "TIU" for b in butir[30:65]))
        self.assertTrue(all(b.soal.subtes == "TKP" for b in butir[65:]))
        self.assertTrue(all(sorted(b.urutan_opsi) == list("ABCDE") for b in butir))
        self.assertEqual(sesi.mode, "cat")
        self.assertEqual(sesi.status, "berjalan")

    def test_batas_waktu_memakai_durasi_skema(self):
        from datetime import timedelta

        from django.utils import timezone

        isi_bank_skd()
        sekarang = timezone.now()
        sesi = rakit_sesi_cat(self.user, self.skema, rng=self.rng, now=sekarang)
        self.assertEqual(sesi.batas_waktu, sekarang + timedelta(minutes=100))

    def test_bank_kurang_tidak_membuat_sesi(self):
        isi_bank_skd(tiu=34)
        with self.assertRaises(BankSoalKurang) as ctx:
            rakit_sesi_cat(self.user, self.skema, rng=self.rng)
        self.assertEqual(ctx.exception.subtes, "TIU")
        self.assertEqual(ctx.exception.tersedia, 34)
        self.assertEqual(ctx.exception.dibutuhkan, 35)
        self.assertIn("34 dari 35", str(ctx.exception))
        self.assertEqual(Sesi.objects.count(), 0)

    def test_utamakan_soal_belum_dikerjakan(self):
        bank = isi_bank_skd(twk=40)
        sesi1 = rakit_sesi_cat(self.user, self.skema, rng=self.rng)
        sesi1.status = "selesai"
        sesi1.save()
        dipakai = {b.soal_id for b in sesi1.butir.all() if b.soal.subtes == "TWK"}
        belum = {s.id for s in bank["TWK"]} - dipakai
        self.assertEqual(len(belum), 10)
        sesi2 = rakit_sesi_cat(self.user, self.skema, rng=self.rng)
        dipakai2 = {b.soal_id for b in sesi2.butir.all() if b.soal.subtes == "TWK"}
        self.assertTrue(belum <= dipakai2)

    def test_bank_pas_semua_pernah_tetap_berhasil(self):
        bank = isi_bank_skd()
        semua = bank["TWK"] + bank["TIU"] + bank["TKP"]
        lama = buat_sesi_cat(self.user, self.skema, semua, ["A"] * 110)
        lama.status = "selesai"
        lama.save()
        sesi = rakit_sesi_cat(self.user, self.skema, rng=self.rng)
        self.assertEqual(sesi.butir.count(), 110)

    def test_hanya_soal_tayang(self):
        isi_bank_skd()
        buruk = [buat_soal("TWK", status="draf") for _ in range(5)]
        buruk += [buat_soal("TIU", status="ditolak") for _ in range(5)]
        sesi = rakit_sesi_cat(self.user, self.skema, rng=self.rng)
        dipilih = set(sesi.butir.values_list("soal_id", flat=True))
        self.assertFalse(dipilih & {s.id for s in buruk})


class OpsiTests(TestCase):
    def test_opsi_tampil_ke_asli(self):
        self.assertEqual(opsi_tampil_ke_asli("CAEBD", "A"), "C")
        self.assertEqual(opsi_tampil_ke_asli("CAEBD", "E"), "D")
        with self.assertRaises(ValueError):
            opsi_tampil_ke_asli("CAEBD", "F")

    def test_acak_urutan_opsi_permutasi(self):
        self.assertEqual(sorted(acak_urutan_opsi(random.Random(1))), list("ABCDE"))


class PerakitanBelajarTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(username="siswa", password="x")
        self.rng = random.Random(1)

    def test_subtopik_kurang_pakai_semua(self):
        for _ in range(4):
            buat_soal("TWK", subtopik="Pancasila")
        buat_soal("TWK", subtopik="Lain")
        sesi = rakit_sesi_belajar(
            self.user, subtes="TWK", subtopik="Pancasila", jumlah=10, rng=self.rng
        )
        self.assertEqual(sesi.butir.count(), 4)
        self.assertEqual(sesi.mode, "belajar")
        self.assertIsNone(sesi.batas_waktu)
        self.assertEqual(sesi.filter_subtopik["subtopik"], "Pancasila")

    def test_subtopik_kosong_melempar(self):
        with self.assertRaises(BankSoalKurang) as ctx:
            rakit_sesi_belajar(self.user, subtes="TWK", jumlah=10, rng=self.rng)
        self.assertEqual((ctx.exception.tersedia, ctx.exception.dibutuhkan), (0, 10))

    def test_paket_mengikuti_urutan(self):
        soal = [buat_soal("TIU") for _ in range(3)]
        paket = PaketBelajar.objects.create(nama="Paket uji", jenis_ujian="SKD")
        for urutan, s in zip((3, 1, 2), soal):
            PaketSoal.objects.create(paket=paket, soal=s, urutan=urutan)
        sesi = rakit_sesi_belajar(self.user, paket=paket, rng=self.rng)
        self.assertEqual(
            list(sesi.butir.values_list("soal_id", flat=True)),
            [soal[1].id, soal[2].id, soal[0].id],
        )
        self.assertEqual(sesi.paket, paket)

    def test_harus_satu_sumber(self):
        with self.assertRaises(ValueError):
            rakit_sesi_belajar(self.user, rng=self.rng)
        paket = PaketBelajar.objects.create(nama="P", jenis_ujian="SKD")
        with self.assertRaises(ValueError):
            rakit_sesi_belajar(self.user, paket=paket, subtes="TWK", rng=self.rng)
