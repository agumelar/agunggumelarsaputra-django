from io import StringIO

from django.core.management import call_command
from django.test import TestCase

from apps.cpns.impor_lama import salin_soal_lama
from apps.cpns.models import CpnsPackage, CpnsQuestion, Soal
from apps.cpns.tests.pabrik import buat_soal

_nomor = [0]


def paket(kode="SKD-01", tipe="SKD"):
    return CpnsPackage.objects.create(kode=kode, judul=f"Paket {kode}", slug=kode.lower(), tipe_ujian=tipe)


def lama(pkt, subtes="TWK", **ubah):
    _nomor[0] += 1
    n = _nomor[0]
    data = dict(
        package=pkt,
        subtes=subtes,
        subtopik="Pancasila",
        urutan=n,
        pertanyaan=f"Pertanyaan lama nomor {n} tentang {subtes}",
        opsi_a=f"A{n}",
        opsi_b=f"B{n}",
        opsi_c=f"C{n}",
        opsi_d=f"D{n}",
        opsi_e=f"E{n}",
        kunci_jawaban="C",
        bedah_konsep="Konsep lama.",
        alasan_pengecoh="Pengecoh lama.",
        tips_cepat="Tips lama.",
    )
    data.update(ubah)
    return CpnsQuestion.objects.create(**data)


class ImporLamaTests(TestCase):
    def test_salin_pemetaan_lengkap(self):
        q = lama(paket(), "TIU", subtopik="Deret")
        hasil = salin_soal_lama()
        s = Soal.objects.get()
        self.assertEqual((hasil.masuk, hasil.dilewati_sama, hasil.perlu_cek), (1, 0, 0))
        self.assertEqual(hasil.paket, {"SKD-01": 1})
        self.assertEqual(s.jenis_ujian, "SKD")
        self.assertEqual(s.subtes, "TIU")
        self.assertEqual(s.subtopik, "Deret")
        self.assertEqual(s.teks, q.pertanyaan)
        self.assertEqual([s.opsi_a, s.opsi_e], [q.opsi_a, q.opsi_e])
        self.assertEqual(s.kunci, "C")
        self.assertIsNone(s.bobot)
        self.assertEqual(s.pembahasan_konsep, "Konsep lama.")
        self.assertEqual(s.pembahasan_pengecoh, "Pengecoh lama.")
        self.assertEqual(s.pembahasan_cepat, "Tips lama.")
        self.assertEqual((s.sumber, s.status, s.batch), ("lama", "draf", "lama-SKD-01"))
        self.assertFalse(s.perlu_cek)

    def test_tkp_pakai_bobot(self):
        lama(paket(), "TKP", bobot_tkp={"A": 5, "B": 4, "C": 3, "D": 2, "E": 1})
        salin_soal_lama()
        s = Soal.objects.get()
        self.assertEqual(s.bobot, {"A": 5, "B": 4, "C": 3, "D": 2, "E": 1})
        self.assertEqual(s.kunci, "")
        self.assertFalse(s.perlu_cek)

    def test_tkp_bobot_teks_diubah_ke_angka(self):
        lama(paket(), "TKP", bobot_tkp={"A": "5", "B": "4", "C": "3", "D": "2", "E": "1"})
        salin_soal_lama()
        self.assertEqual(Soal.objects.get().bobot["A"], 5)
        self.assertFalse(Soal.objects.get().perlu_cek)

    def test_skb_guru_jadi_pedagogik_perlu_cek(self):
        lama(paket("SKB-01", "SKB"), "SKB_GURU")
        hasil = salin_soal_lama()
        s = Soal.objects.get()
        self.assertEqual((s.jenis_ujian, s.subtes), ("SKB_GURU", "PEDAGOGIK"))
        self.assertTrue(s.perlu_cek)
        self.assertIn("Subtes asli SKB_GURU. Pilih PEDAGOGIK atau MATERI_RPL.", s.catatan_tinjau)
        self.assertEqual(hasil.perlu_cek, 1)

    def test_subtopik_kosong_jadi_umum(self):
        lama(paket(), "TWK", subtopik="")
        salin_soal_lama()
        s = Soal.objects.get()
        self.assertEqual(s.subtopik, "Umum")
        self.assertFalse(s.perlu_cek)

    def test_tidak_valid_tetap_disalin_perlu_cek_dengan_catatan(self):
        lama(paket(), "TKP", bobot_tkp=None, bedah_konsep="")
        hasil = salin_soal_lama()
        s = Soal.objects.get()
        self.assertTrue(s.perlu_cek)
        self.assertTrue(s.catatan_tinjau.startswith("Pemeriksaan otomatis: "))
        self.assertIn("bobot TKP", s.catatan_tinjau)
        self.assertIn("pembahasan konsep", s.catatan_tinjau)
        self.assertEqual((hasil.masuk, hasil.perlu_cek), (1, 1))

    def test_jalan_dua_kali_tidak_ganda(self):
        pkt = paket()
        lama(pkt)
        lama(pkt, "TIU")
        salin_soal_lama()
        hasil = salin_soal_lama()
        self.assertEqual(Soal.objects.count(), 2)
        self.assertEqual((hasil.masuk, hasil.dilewati_sama), (0, 2))

    def test_sama_dengan_bank_dilewati(self):
        pkt = paket()
        buat_soal("TWK", status="tayang", teks="Teks Yang Sama, Persis!")
        lama(pkt, pertanyaan="teks yang sama persis")
        lama(pkt, pertanyaan="Teks beda sendiri")
        lama(pkt, pertanyaan="Teks beda   sendiri.")
        hasil = salin_soal_lama()
        self.assertEqual(Soal.objects.count(), 2)
        self.assertEqual((hasil.masuk, hasil.dilewati_sama), (1, 2))
        self.assertEqual(Soal.objects.filter(sumber="lama").count(), 1)

    def test_coba_tidak_menyimpan(self):
        lama(paket())
        hasil = salin_soal_lama(coba=True)
        self.assertEqual(hasil.masuk, 1)
        self.assertEqual(Soal.objects.count(), 0)

    def test_tidak_pernah_tayang(self):
        pkt = paket()
        lama(pkt)
        lama(pkt, "TKP", bobot_tkp={"A": 1, "B": 2, "C": 3, "D": 4, "E": 5})
        salin_soal_lama()
        self.assertFalse(Soal.objects.exclude(status="draf").exists())

    def test_tabel_lama_tidak_berubah(self):
        pkt = paket()
        lama(pkt)
        sebelum = list(CpnsQuestion.objects.values())
        salin_soal_lama()
        self.assertEqual(list(CpnsQuestion.objects.values()), sebelum)
        self.assertEqual(CpnsPackage.objects.count(), 1)

    def test_command_ringkasan(self):
        pkt = paket()
        lama(pkt)
        lama(pkt, "TKP", bobot_tkp=None)
        out = StringIO()
        call_command("cpns_impor_soal_lama", stdout=out)
        teks = out.getvalue()
        self.assertIn("Disalin: 2 soal (draf, sumber lama). Dilewati karena sama: 0. Ditandai perlu cek: 1.", teks)
        self.assertIn("SKD-01: 2", teks)
        self.assertEqual(Soal.objects.count(), 2)

    def test_command_coba(self):
        lama(paket())
        out = StringIO()
        call_command("cpns_impor_soal_lama", "--coba", stdout=out)
        self.assertIn("Disalin: 1 soal", out.getvalue())
        self.assertEqual(Soal.objects.count(), 0)
        self.assertIn("Percobaan saja, tidak ada yang disimpan.", out.getvalue())

    def test_command_tanpa_coba_tanpa_baris_percobaan(self):
        lama(paket())
        out = StringIO()
        call_command("cpns_impor_soal_lama", stdout=out)
        self.assertNotIn("Percobaan saja", out.getvalue())

    def test_bobot_angka_unicode_tidak_membuat_crash(self):
        lama(paket(), "TKP", bobot_tkp={"A": "²", "B": "4", "C": "3", "D": "2", "E": "1"})
        hasil = salin_soal_lama()
        s = Soal.objects.get()
        self.assertEqual(hasil.masuk, 1)
        self.assertEqual(s.bobot["A"], "²")
        self.assertEqual(s.bobot["B"], 4)
        self.assertTrue(s.perlu_cek)
