from django.test import SimpleTestCase

from apps.cpns.validasi import sidik_teks, validasi_soal


def data_dasar():
    return {
        "jenis_ujian": "SKD",
        "subtes": "TIU",
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

    def test_tayang_wajib_ditinjau(self):
        d = data_dasar()
        self.assertTrue(any("ditinjau" in m for m in validasi_soal(d, untuk_tayang=True)))
        d["ditinjau_oleh"] = 1
        self.assertEqual(validasi_soal(d, untuk_tayang=True), [])


class SidikTeksTest(SimpleTestCase):
    def test_sidik_teks_abaikan_spasi_dan_tanda_baca(self):
        self.assertEqual(sidik_teks("2, 5,  11 ..."), sidik_teks("2 5 11"))
