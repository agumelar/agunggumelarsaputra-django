import tempfile
from pathlib import Path

from django.test import SimpleTestCase

from apps.cpns.kisi_kisi import Subtopik, baca_kisi_kisi
from apps.cpns.validasi import SUBTES

KEPALA = "| Jenis | Subtes | Subtopik | Target |\n| --- | --- | --- | --- |\n"


def _tulis(isi):
    folder = Path(tempfile.mkdtemp())
    berkas = folder / "kisi.md"
    berkas.write_text(isi, encoding="utf-8")
    return berkas


class KisiKisiTest(SimpleTestCase):
    def test_baca_kisi_kisi_repo(self):
        hasil = baca_kisi_kisi()
        self.assertTrue(hasil)
        self.assertIsInstance(hasil[0], Subtopik)
        for subtes in SUBTES:
            self.assertTrue(
                [s for s in hasil if s.subtes == subtes], f"{subtes} kosong"
            )

    def test_baca_baris_valid(self):
        berkas = _tulis("Teks bebas.\n\n" + KEPALA + "| SKD | TWK | Pancasila | 60 |\n")
        self.assertEqual(baca_kisi_kisi(berkas), [Subtopik("SKD", "TWK", "Pancasila", 60)])

    def test_baris_tidak_valid_menyebut_nomor(self):
        kasus = {
            "| SKD | XYZ | A | 60 |": "XYZ",
            "| SKD | TWK | A | abc |": "abc",
            "| SKD | TWK | A | 0 |": "0",
            "| SKD | TWK | A | ² |": "²",
            "| SKD | PEDAGOGIK | A | 60 |": "PEDAGOGIK",
        }
        for baris in kasus:
            berkas = _tulis(KEPALA + baris + "\n")
            with self.assertRaises(ValueError) as konteks:
                baca_kisi_kisi(berkas)
            self.assertIn("baris 3", str(konteks.exception), baris)
            self.assertIn(kasus[baris], str(konteks.exception), baris)

    def test_file_hilang_list_kosong(self):
        self.assertEqual(baca_kisi_kisi(Path(tempfile.gettempdir()) / "tidak-ada-kisi.md"), [])

    def test_duplikat_ditolak(self):
        baris = "| SKD | TWK | Pancasila | 60 |\n"
        berkas = _tulis(KEPALA + baris + baris)
        with self.assertRaises(ValueError) as konteks:
            baca_kisi_kisi(berkas)
        self.assertIn("baris 4", str(konteks.exception))
        self.assertIn("Pancasila", str(konteks.exception))

    def test_hanya_tabel_pertama_dibaca(self):
        isi = (
            KEPALA + "| SKD | TWK | Pancasila | 60 |\n\n"
            "Catatan bebas.\n| bukan data |\n\n"
            + KEPALA + "| SKD | XYZ | Lain | 1 |\n"
        )
        self.assertEqual(
            baca_kisi_kisi(_tulis(isi)), [Subtopik("SKD", "TWK", "Pancasila", 60)]
        )
