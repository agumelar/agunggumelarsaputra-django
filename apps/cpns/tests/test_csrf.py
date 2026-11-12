"""POST tanpa token CSRF harus ditolak 403, juga untuk pengguna yang sudah masuk.

Klien memakai enforce_csrf_checks=True karena klien tes bawaan melewati
pemeriksaan CSRF. Pengguna dimasukkan lewat force_login supaya permintaan
sampai ke lapisan CSRF dan lolos pemeriksaan akses.
"""
import json

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from apps.cpns.models import SkemaUjian
from apps.cpns.tests.pabrik import buat_sesi_cat, buat_soal



class CsrfTest(TestCase):
    def setUp(self):
        user_model = get_user_model()
        self.peserta = user_model.objects.create_user(
            username="peserta", email="peserta@contoh.id", password="x"
        )
        self.admin = user_model.objects.create_superuser(
            username="admin", email="admin@contoh.id", password="x"
        )
        self.soal = buat_soal("TIU")
        skema = SkemaUjian.objects.get(kode="SKD-CAT")
        self.sesi = buat_sesi_cat(self.peserta, skema, [self.soal], [""])

    def klien(self, user=None):
        klien = Client(enforce_csrf_checks=True)
        if user is not None:
            klien.force_login(user)
        return klien

    def test_post_tanpa_token_ditolak(self):
        kasus = [
            ("masuk", reverse("cpns:masuk"), None),
            ("daftar", reverse("cpns:daftar"), None),
            ("tukar_voucher", reverse("cpns:tukar_voucher"), self.peserta),
            ("cat_kumpulkan", reverse("cpns:cat_kumpulkan", args=[self.sesi.pk]), self.peserta),
            ("laporkan", reverse("cpns:laporkan", args=[self.soal.pk]), self.peserta),
            ("kelola_aksi", reverse("cpns:kelola_aksi", args=[self.soal.pk]), self.admin),
            ("logout", reverse("accounts:logout"), self.peserta),
        ]
        for nama, url, user in kasus:
            with self.subTest(endpoint=nama):
                r = self.klien(user).post(url, {"x": "y"})
                self.assertEqual(r.status_code, 403)

    def test_simpan_jawaban_json_tanpa_header_ditolak(self):
        # ruang.html mengirim token lewat header X-CSRFToken.
        url = reverse("cpns:cat_simpan", args=[self.sesi.pk])
        isi = json.dumps({"nomor": 1, "jawaban": "A"})
        r = self.klien(self.peserta).post(
            url, isi, content_type="application/json"
        )
        self.assertEqual(r.status_code, 403)

    def test_simpan_jawaban_json_dengan_header_melewati_csrf(self):
        klien = self.klien(self.peserta)
        klien.get(reverse("cpns:cat_ruang", args=[self.sesi.pk]))
        token = klien.cookies["csrftoken"].value
        r = klien.post(
            reverse("cpns:cat_simpan", args=[self.sesi.pk]),
            json.dumps({"nomor": 1, "jawaban": "A"}),
            content_type="application/json",
            HTTP_X_CSRFTOKEN=token,
        )
        self.assertNotEqual(r.status_code, 403)
