import copy
import json
import tempfile
from io import StringIO
from pathlib import Path

from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import TestCase

from apps.cpns.impor import impor_batch
from apps.cpns.models import Soal
from apps.cpns.tests.pabrik import buat_soal

CONTOH = Path(__file__).parent / "data" / "batch_contoh.json"


def contoh():
    return json.loads(CONTOH.read_text(encoding="utf-8"))


def tiu(**ubah):
    d = copy.deepcopy(contoh()[0])
    d.update(ubah)
    return d


def jalankan(isi, nama="uji.json", *args):
    folder = Path(tempfile.mkdtemp())
    berkas = folder / nama
    berkas.write_text(isi if isinstance(isi, str) else json.dumps(isi), encoding="utf-8")
    out = StringIO()
    kode = 0
    try:
        call_command("cpns_impor_soal", str(berkas), *args, stdout=out)
    except SystemExit as e:
        kode = e.code
    return kode, out.getvalue()


class ImporTest(TestCase):
    def test_impor_contoh_masuk_sebagai_draf(self):
        hasil = impor_batch(contoh(), "batch-contoh")
        self.assertEqual(hasil.masuk, [1, 2, 3, 4, 5])
        self.assertEqual(hasil.gagal, [])
        self.assertEqual(Soal.objects.filter(status="draf", batch="batch-contoh").count(), 5)
        for s in Soal.objects.all():
            self.assertEqual(s.sumber, "draf_ai")
            self.assertEqual(s.sidik_teks, s.hitung_sidik())

    def test_opsi_angka_json_diterima(self):
        hasil = impor_batch([tiu(opsi_a=85, opsi_b=90.5)], "b")
        self.assertEqual(hasil.gagal, [])
        s = Soal.objects.get()
        self.assertEqual((s.opsi_a, s.opsi_b), ("85", "90.5"))

    def test_ganda_dalam_file_ditolak_dengan_baris(self):
        hasil = impor_batch([tiu(), tiu(teks="LANJUTKAN deret berikut 2 4 8 16")], "b")
        self.assertEqual(hasil.masuk, [1])
        self.assertEqual(hasil.gagal[0][0], 2)
        self.assertIn("baris 1", hasil.gagal[0][1][0])
        self.assertEqual(Soal.objects.count(), 1)

    def test_sama_dengan_bank_ditolak(self):
        buat_soal("TIU", teks="Teks di bank.", status="ditolak")
        hasil = impor_batch([tiu(teks="Teks di bank.")], "b")
        self.assertEqual(hasil.masuk, [])
        self.assertEqual(hasil.gagal[0][0], 1)
        self.assertIn("sudah ada di bank", hasil.gagal[0][1][0])
        self.assertEqual(Soal.objects.count(), 1)

    def test_twk_tanpa_rujukan_wajib_perlu_cek(self):
        twk = copy.deepcopy(contoh()[2])
        twk["perlu_cek"] = False
        hasil = impor_batch([twk], "b")
        self.assertIn(
            "Soal TWK tanpa rujukan harus diberi perlu_cek=true. Jangan mengarang rujukan.",
            hasil.gagal[0][1],
        )
        twk["rujukan"] = "UUD 1945 Pembukaan"
        self.assertEqual(impor_batch([twk], "b").gagal, [])

    def test_subtopik_di_luar_kisi_kisi_ditolak(self):
        hasil = impor_batch([tiu(subtopik="Tidak Ada")], "b")
        self.assertIn("kisi-kisi", hasil.gagal[0][1][0])
        self.assertEqual(Soal.objects.count(), 0)

    def test_field_tak_dikenal_ditolak(self):
        hasil = impor_batch([tiu(kunchi="A")], "b")
        self.assertIn("Field tidak dikenal: kunchi.", hasil.gagal[0][1])

    def test_tipe_field_salah_ditolak(self):
        for nama, nilai in (
            ("jenis_ujian", ["SKD"]),
            ("subtes", {"a": 1}),
            ("subtopik", 5),
            ("teks", None),
        ):
            hasil = impor_batch([tiu(**{nama: nilai})], "b")
            self.assertIn(f"Field {nama} harus berupa teks.", hasil.gagal[0][1], nama)
        self.assertEqual(Soal.objects.count(), 0)

    def test_bobot_perlu_cek_dan_baris_bukan_objek(self):
        self.assertIn("Field bobot harus berupa objek.", impor_batch([tiu(bobot=[1])], "b").gagal[0][1])
        self.assertTrue(impor_batch([tiu(perlu_cek="ya")], "b").gagal)
        hasil = impor_batch(["teks", 5, None, []], "b")
        self.assertEqual([n for n, _ in hasil.gagal], [1, 2, 3, 4])
        for _, pesan in hasil.gagal:
            self.assertEqual(pesan, ["Baris ini bukan objek soal."])

    def test_coba_tidak_menyimpan(self):
        hasil = impor_batch(contoh(), "b", coba=True)
        self.assertEqual(len(hasil.masuk), 5)
        self.assertEqual(Soal.objects.count(), 0)

    def test_baris_gagal_tidak_menggagalkan_baris_lain(self):
        hasil = impor_batch([tiu(), tiu(teks="Lain", subtopik="X")], "b")
        self.assertEqual((hasil.masuk, [n for n, _ in hasil.gagal]), ([1], [2]))
        self.assertEqual(Soal.objects.count(), 1)

    def test_command_kode_keluar_dan_ringkasan(self):
        kode, out = jalankan(contoh(), "2026-11-contoh.json")
        self.assertEqual(kode, 0)
        self.assertIn("Masuk: 5 soal (draf). Gagal: 0 baris.", out)
        self.assertEqual(Soal.objects.filter(batch="2026-11-contoh").count(), 5)
        kode, out = jalankan([tiu(teks="Baru"), tiu(teks="Baru2", subtopik="X")], "lain.json")
        self.assertEqual(kode, 1)
        self.assertIn("Masuk: 1 soal (draf). Gagal: 1 baris.", out)
        self.assertIn("Baris 2: Subtopik X", out)

    def test_command_coba(self):
        kode, out = jalankan(contoh(), "c.json", "--coba")
        self.assertEqual(kode, 0)
        self.assertEqual(Soal.objects.count(), 0)

    def test_command_file_rusak(self):
        with self.assertRaisesMessage(CommandError, "bukan JSON"):
            jalankan("{rusak", "r.json")
        with self.assertRaisesMessage(CommandError, "daftar soal"):
            jalankan("{}", "r.json")
        with self.assertRaisesMessage(CommandError, "tidak ditemukan"):
            call_command("cpns_impor_soal", "tidak-ada.json")

    def test_command_lama_sudah_dihapus(self):
        for nama in ("import_cpns", "seed_cpns_starter", "scrape_cpns"):
            with self.assertRaisesMessage(CommandError, "Unknown command"):
                call_command(nama)
