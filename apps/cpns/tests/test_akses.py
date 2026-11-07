from datetime import timedelta

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone

from apps.cpns.akses import (
    akses_untuk,
    boleh_belajar_paket,
    boleh_belajar_subtopik,
    boleh_lihat_pembahasan,
    boleh_mulai_cat,
    is_premium,
)
from apps.cpns.models import AksesPeserta, PaketBelajar, Sesi, SkemaUjian

User = get_user_model()


def buat_user(nama, **kw):
    return User.objects.create_user(username=nama, email=f"{nama}@x.id", password="x", role="peserta", **kw)


def beri_akses(user, premium=False, via_google=False):
    akses = akses_untuk(user)
    akses.via_google = via_google
    if premium:
        akses.premium_sampai = timezone.now() + timedelta(days=30)
    akses.save()
    return akses


class PremiumTests(TestCase):
    def test_premium_aktif_dan_kedaluwarsa(self):
        user = buat_user("p1")
        akses = akses_untuk(user)
        self.assertFalse(is_premium(user))
        now = timezone.now()
        akses.premium_sampai = now + timedelta(days=1)
        akses.save()
        self.assertTrue(is_premium(user, now))
        self.assertFalse(is_premium(user, now + timedelta(days=2)))

    def test_superuser_selalu_premium(self):
        admin = User.objects.create_superuser(username="adm", email="adm@x.id", password="x", role="guru")
        self.assertTrue(is_premium(admin))

    def test_user_lama_tanpa_akses_dibuat_otomatis(self):
        user = User.objects.create_user(username="lama", email="lama@x.id", password="x", role="siswa")
        AksesPeserta.objects.filter(user=user).delete()
        akses = akses_untuk(user)
        self.assertFalse(akses.via_google)
        self.assertFalse(is_premium(user))


class MulaiCatTests(TestCase):
    def setUp(self):
        self.skd = SkemaUjian.objects.get(kode="SKD-CAT")
        self.skb = SkemaUjian.objects.get(kode="SKB-GURU-LATIHAN")

    def sesi_cat(self, user, status):
        return Sesi.objects.create(user=user, mode="cat", skema=self.skd, status=status)

    def test_skema_nonaktif(self):
        user = buat_user("a")
        beri_akses(user, premium=True, via_google=True)
        self.assertEqual(boleh_mulai_cat(user, self.skb), (False, "Skema ini belum tersedia."))

    def test_skema_nonaktif_boleh_untuk_superuser(self):
        admin = User.objects.create_superuser(username="adm", email="adm@x.id", password="x", role="guru")
        self.assertEqual(boleh_mulai_cat(admin, self.skb), (True, ""))

    def test_skb_khusus_premium(self):
        self.skb.aktif = True
        self.skb.save()
        user = buat_user("b")
        beri_akses(user, via_google=True)
        self.assertEqual(
            boleh_mulai_cat(user, self.skb), (False, "Simulasi SKB Guru khusus Premium.")
        )

    def test_trial_bukan_google(self):
        user = buat_user("c")
        self.assertEqual(
            boleh_mulai_cat(user, self.skd), (False, "Simulasi gratis hanya untuk akun Google.")
        )

    def test_kuota_trial_terpakai(self):
        user = buat_user("d")
        beri_akses(user, via_google=True)
        self.sesi_cat(user, "selesai")
        self.assertEqual(
            boleh_mulai_cat(user, self.skd), (False, "Kuota simulasi gratis sudah terpakai.")
        )

    def test_cat_berjalan(self):
        user = buat_user("e")
        beri_akses(user, premium=True)
        self.sesi_cat(user, "berjalan")
        self.assertEqual(
            boleh_mulai_cat(user, self.skd),
            (False, "Selesaikan dulu simulasi yang sedang berjalan."),
        )

    def test_trial_google_dengan_cat_berjalan_diarahkan_ke_sesi(self):
        user = buat_user("f")
        beri_akses(user, via_google=True)
        self.sesi_cat(user, "berjalan")
        self.assertEqual(
            boleh_mulai_cat(user, self.skd),
            (False, "Selesaikan dulu simulasi yang sedang berjalan."),
        )

    def test_trial_google_pertama_kali_boleh(self):
        user = buat_user("g")
        beri_akses(user, via_google=True)
        self.assertEqual(boleh_mulai_cat(user, self.skd), (True, ""))

    def test_premium_boleh_ulang(self):
        user = buat_user("h")
        beri_akses(user, premium=True)
        self.sesi_cat(user, "selesai")
        self.assertEqual(boleh_mulai_cat(user, self.skd), (True, ""))


class BelajarTests(TestCase):
    def test_paket_trial_dan_premium(self):
        user = buat_user("i")
        trial = PaketBelajar(nama="T", jenis_ujian="SKD", untuk_trial=True)
        biasa = PaketBelajar(nama="B", jenis_ujian="SKD", untuk_trial=False)
        self.assertTrue(boleh_belajar_paket(user, trial))
        self.assertFalse(boleh_belajar_paket(user, biasa))
        beri_akses(user, premium=True)
        self.assertTrue(boleh_belajar_paket(user, biasa))

    def test_subtopik_khusus_premium(self):
        user = buat_user("j")
        self.assertFalse(boleh_belajar_subtopik(user))
        beri_akses(user, premium=True)
        self.assertTrue(boleh_belajar_subtopik(user))

    def test_trial_tidak_lihat_pembahasan_cat(self):
        user = buat_user("k")
        sesi = Sesi.objects.create(user=user, mode="cat", status="selesai")
        self.assertFalse(boleh_lihat_pembahasan(user, sesi))

    def test_trial_lihat_pembahasan_belajar(self):
        user = buat_user("l")
        sesi = Sesi.objects.create(user=user, mode="belajar", status="selesai")
        self.assertTrue(boleh_lihat_pembahasan(user, sesi))

    def test_pembahasan_bukan_milik_user(self):
        pemilik, lain = buat_user("m"), buat_user("n")
        sesi = Sesi.objects.create(user=pemilik, mode="belajar", status="selesai")
        self.assertFalse(boleh_lihat_pembahasan(lain, sesi))

    def test_premium_lihat_pembahasan_cat(self):
        user = buat_user("o")
        beri_akses(user, premium=True)
        sesi = Sesi.objects.create(user=user, mode="cat", status="selesai")
        self.assertTrue(boleh_lihat_pembahasan(user, sesi))
