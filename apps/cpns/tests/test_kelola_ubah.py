from django.contrib.auth import get_user_model
from django.contrib.messages import get_messages
from django.test import TestCase
from django.urls import reverse

from apps.cpns.models import SkemaUjian, Soal
from apps.cpns.penilaian import nilai_sesi
from apps.cpns.tests.pabrik import buat_sesi_cat, buat_soal


def pesan(response):
    return [str(m) for m in get_messages(response.wsgi_request)]


def data_valid(soal, **ganti):
    data = {
        "subtes": soal.subtes,
        "subtopik": soal.subtopik,
        "tingkat": soal.tingkat,
        "teks": soal.teks,
        "opsi_a": soal.opsi_a,
        "opsi_b": soal.opsi_b,
        "opsi_c": soal.opsi_c,
        "opsi_d": soal.opsi_d,
        "opsi_e": soal.opsi_e,
        "kunci": soal.kunci,
        "pembahasan_konsep": soal.pembahasan_konsep,
        "pembahasan_pengecoh": soal.pembahasan_pengecoh,
        "pembahasan_cepat": soal.pembahasan_cepat,
        "rujukan": soal.rujukan,
    }
    for huruf, nilai in (soal.bobot or {}).items():
        data[f"bobot_{huruf.lower()}"] = nilai
    data.update(ganti)
    return data


class UbahDasar(TestCase):
    def setUp(self):
        self.admin = get_user_model().objects.create_superuser(
            username="agung", email="a@contoh.id", password="x"
        )
        self.client.force_login(self.admin)

    def url(self, soal, query=""):
        url = reverse("cpns:kelola_ubah", args=[soal.id])
        return f"{url}?{query}" if query else url


class UbahTest(UbahDasar):
    def test_form_tampil_dengan_jenis_ujian_hanya_baca(self):
        soal = buat_soal("TIU", status="draf")
        r = self.client.get(self.url(soal, "subtes=TIU"))
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, soal.teks)
        self.assertContains(r, "SKD")
        self.assertNotContains(r, 'name="jenis_ujian"')
        self.assertContains(r, "subtes=TIU")

    def test_ubah_draf_tersimpan(self):
        soal = buat_soal("TIU", status="draf")
        r = self.client.post(
            self.url(soal, "subtes=TIU"),
            data_valid(soal, teks="Teks baru yang diubah", kunci="C"),
        )
        self.assertRedirects(
            r,
            reverse("cpns:kelola_tinjau_soal", args=[soal.id]) + "?subtes=TIU",
            fetch_redirect_response=False,
        )
        self.assertIn("Perubahan disimpan.", pesan(r))
        soal.refresh_from_db()
        self.assertEqual(soal.teks, "Teks baru yang diubah")
        self.assertEqual(soal.kunci, "C")
        self.assertEqual(soal.status, "draf")
        self.assertIsNone(soal.ditinjau_oleh)

    def test_ubah_tidak_valid_tidak_menyimpan(self):
        soal = buat_soal("TIU", status="draf")
        asli = soal.teks
        r = self.client.post(
            self.url(soal),
            data_valid(soal, teks="Berubah", opsi_b=soal.opsi_a, pembahasan_cepat=""),
        )
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, "Ada opsi yang isinya sama persis.")
        self.assertContains(r, "Isi pembahasan cepat.")
        soal.refresh_from_db()
        self.assertEqual(soal.teks, asli)
        self.assertEqual(soal.pembahasan_cepat, "Cara cepat soal.")

    def test_ubah_tayang_tetap_tayang_peninjau_diperbarui(self):
        lama = get_user_model().objects.create_user(username="lama", password="x")
        soal = buat_soal("TIU", status="tayang")
        Soal.objects.filter(pk=soal.pk).update(ditinjau_oleh=lama)
        self.client.post(self.url(soal), data_valid(soal, subtopik="Deret baru"))
        soal.refresh_from_db()
        self.assertEqual(soal.status, "tayang")
        self.assertEqual(soal.subtopik, "Deret baru")
        self.assertEqual(soal.ditinjau_oleh, self.admin)
        self.assertIsNotNone(soal.ditinjau_pada)

    def test_ubah_tayang_tanpa_peninjau_lama_tetap_valid(self):
        soal = buat_soal("TIU", status="tayang")
        r = self.client.post(self.url(soal), data_valid(soal, subtopik="Lain"))
        self.assertEqual(r.status_code, 302)
        soal.refresh_from_db()
        self.assertEqual(soal.ditinjau_oleh, self.admin)

    def test_ubah_tayang_tidak_mengubah_hasil_lama(self):
        user = get_user_model().objects.create_user(username="peserta", password="x")
        skema = SkemaUjian.objects.get(kode="SKD-CAT")
        soal = buat_soal("TWK", kunci="A", status="tayang")
        sesi = buat_sesi_cat(user, skema, [soal], ["A"])
        nilai_sesi(sesi)
        sesi.refresh_from_db()
        skor_awal = sesi.total
        self.assertTrue(sesi.butir.get().benar)

        r = self.client.post(self.url(soal), data_valid(soal, kunci="B"))
        self.assertEqual(r.status_code, 302)
        soal.refresh_from_db()
        self.assertEqual(soal.kunci, "B")
        sesi.refresh_from_db()
        self.assertEqual(sesi.total, skor_awal)
        self.assertTrue(sesi.butir.get().benar)

    def test_bobot_tkp_lewat_form(self):
        soal = buat_soal("TKP", status="draf")
        r = self.client.get(self.url(soal))
        for h in "abcde":
            self.assertContains(r, f'name="bobot_{h}"')
        data = data_valid(soal, bobot_a=5, bobot_b=4, bobot_c=3, bobot_d=2, bobot_e=1)
        r = self.client.post(self.url(soal), data)
        self.assertEqual(r.status_code, 302)
        soal.refresh_from_db()
        self.assertEqual(soal.bobot, {"A": 5, "B": 4, "C": 3, "D": 2, "E": 1})
        self.assertEqual(soal.kunci, "")

        r = self.client.post(self.url(soal), data_valid(soal, bobot_a=5, bobot_b=5))
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, "Isi bobot TKP")
        soal.refresh_from_db()
        self.assertEqual(soal.bobot["B"], 4)

    def test_non_tkp_tidak_menyimpan_bobot(self):
        soal = buat_soal("TIU", status="draf")
        self.client.post(self.url(soal), data_valid(soal, bobot_a=1))
        soal.refresh_from_db()
        self.assertIsNone(soal.bobot)

    def test_ditolak_kembali_ke_draf_dengan_kotak_centang(self):
        soal = buat_soal("TIU", status="ditolak")
        self.client.post(self.url(soal), data_valid(soal))
        soal.refresh_from_db()
        self.assertEqual(soal.status, "ditolak")
        self.client.post(self.url(soal), data_valid(soal, kembalikan_draf="on"))
        soal.refresh_from_db()
        self.assertEqual(soal.status, "draf")

    def test_akses_non_superuser_403(self):
        soal = buat_soal("TIU", status="draf")
        self.client.logout()
        r = self.client.get(self.url(soal))
        self.assertEqual(r.status_code, 302)
        self.assertTrue(r["Location"].startswith(reverse("cpns:masuk")))
        biasa = get_user_model().objects.create_user(username="guru", password="x")
        self.client.force_login(biasa)
        self.assertEqual(self.client.get(self.url(soal)).status_code, 403)
        r = self.client.post(self.url(soal), data_valid(soal, teks="Retas"))
        self.assertEqual(r.status_code, 403)
        soal.refresh_from_db()
        self.assertNotEqual(soal.teks, "Retas")
