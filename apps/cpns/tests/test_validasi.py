from django.test import SimpleTestCase

from apps.cpns import admin as admin_cpns
from apps.cpns import penilaian, validasi
from apps.cpns.validasi import sidik_teks, validasi_soal


def data_dasar():
    return {
        "jenis_ujian": "SKD",
        "subtes": "TIU",
        "subtopik": "Hitungan",
        "teks": "Berapa hasil 2 + 3?",
        "opsi_a": "1",
        "opsi_b": "2",
        "opsi_c": "5",
        "opsi_d": "7",
        "opsi_e": "9",
        "kunci": "C",
        "pembahasan_konsep": "Penjumlahan dasar.",
        "pembahasan_pengecoh": "Pilihan lain keliru hitung.",
        "pembahasan_cepat": "2 tambah 3 sama dengan 5.",
    }


class ValidasiSoalTest(SimpleTestCase):
    def test_soal_valid_tanpa_error(self):
        self.assertEqual(validasi_soal(data_dasar()), [])

    def test_opsi_kosong_ditolak(self):
        d = data_dasar()
        d["opsi_c"] = ""
        self.assertTrue(any("opsi C" in m for m in validasi_soal(d)))

    def test_opsi_ganda_ditolak(self):
        d = data_dasar()
        d["opsi_b"] = d["opsi_a"]
        self.assertTrue(any("sama" in m for m in validasi_soal(d)))

    def test_kunci_wajib_untuk_benar_salah(self):
        d = data_dasar()
        d["kunci"] = ""
        self.assertTrue(any("kunci" in m for m in validasi_soal(d)))

    def test_bobot_tkp_harus_1_sampai_5_berbeda(self):
        d = data_dasar()
        d["subtes"] = "TKP"
        d["kunci"] = ""
        d["bobot"] = {"A": 3, "B": 1, "C": 5, "D": 2, "E": 1}
        self.assertTrue(any("bobot" in m for m in validasi_soal(d)))
        d["bobot"] = {"A": 3, "B": 1, "C": 5, "D": 2, "E": 4}
        self.assertEqual(validasi_soal(d), [])

    def test_pembahasan_wajib(self):
        d = data_dasar()
        d["pembahasan_cepat"] = ""
        self.assertTrue(any("pembahasan" in m for m in validasi_soal(d)))

    def test_teks_dan_subtopik_wajib(self):
        for nilai in ("", "   ", None):
            d = data_dasar()
            d["teks"] = nilai
            d["subtopik"] = nilai
            pesan = validasi_soal(d)
            self.assertIn("Isi teks soal.", pesan, repr(nilai))
            self.assertIn("Isi subtopik.", pesan, repr(nilai))
        d = data_dasar()
        del d["subtopik"]
        self.assertEqual(validasi_soal(d), ["Isi subtopik."])

    def test_tayang_wajib_ditinjau(self):
        d = data_dasar()
        self.assertTrue(any("ditinjau" in m for m in validasi_soal(d, untuk_tayang=True)))
        d["ditinjau_oleh"] = 1
        self.assertEqual(validasi_soal(d, untuk_tayang=True), [])

    def test_opsi_angka_diterima(self):
        d = data_dasar()
        d.update(opsi_a=85, opsi_b=90, opsi_c=95, opsi_d=100, opsi_e=105, kunci="C")
        self.assertEqual(validasi_soal(d), [])
        d["opsi_b"] = 85
        self.assertTrue(any("sama" in m for m in validasi_soal(d)))

    def test_pesan_bobot_tanpa_kata_kunci(self):
        d = data_dasar()
        d["subtes"] = "TKP"
        d["bobot"] = {"A": 1, "B": 1, "C": 1, "D": 1, "E": 1}
        self.assertIn(
            "Isi bobot TKP untuk opsi A sampai E dengan nilai 1, 2, 3, 4, 5 yang semuanya berbeda.",
            validasi_soal(d),
        )

    def test_subtes_tidak_cocok_jenis(self):
        d = data_dasar()
        d["subtes"] = "PEDAGOGIK"
        self.assertIn(
            "Subtes PEDAGOGIK tidak cocok dengan jenis ujian SKD.", validasi_soal(d)
        )

    def test_jenis_kosong_atau_tidak_dikenal_ditolak(self):
        d = data_dasar()
        d["jenis_ujian"] = ""
        self.assertIn("Jenis ujian (kosong) tidak dikenal.", validasi_soal(d))
        del d["jenis_ujian"]
        self.assertIn("Jenis ujian (kosong) tidak dikenal.", validasi_soal(d))
        d["jenis_ujian"] = "XYZ"
        self.assertIn("Jenis ujian XYZ tidak dikenal.", validasi_soal(d))

    def test_nilai_bukan_teks_dianggap_kosong(self):
        d = data_dasar()
        d["opsi_a"] = True
        self.assertIn("Isi opsi A.", validasi_soal(d))
        d = data_dasar()
        d["pembahasan_konsep"] = []
        self.assertIn("Isi pembahasan konsep.", validasi_soal(d))
        d = data_dasar()
        d.update(opsi_a=85, opsi_b=90.5, opsi_c=95, opsi_d=100, opsi_e=105)
        self.assertEqual(validasi_soal(d), [])

    def test_admin_dan_penilaian_pakai_konstanta_validasi(self):
        self.assertIs(admin_cpns.SUBTES_PER_JENIS, validasi.SUBTES_PER_JENIS)
        self.assertIs(penilaian.POIN_MAKS_BOBOT, validasi.POIN_MAKS_BOBOT)


class SidikTeksTest(SimpleTestCase):
    def test_sidik_teks_abaikan_spasi_dan_tanda_baca(self):
        self.assertEqual(sidik_teks("2, 5,  11 ..."), sidik_teks("2 5 11"))
