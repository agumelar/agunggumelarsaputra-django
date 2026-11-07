from datetime import timedelta

from django.contrib.auth import get_user_model
from django.db import IntegrityError, transaction
from django.test import TestCase
from django.utils import timezone

from apps.cpns.models import Sesi


class SesiModelTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="peserta", password="x"
        )

    def test_satu_sesi_cat_berjalan_per_user(self):
        Sesi.objects.create(user=self.user, mode="cat", status="berjalan")
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                Sesi.objects.create(user=self.user, mode="cat", status="berjalan")

    def test_sesi_cat_selesai_tidak_dihitung(self):
        Sesi.objects.create(user=self.user, mode="cat", status="selesai")
        Sesi.objects.create(user=self.user, mode="cat", status="berjalan")
        self.assertEqual(Sesi.objects.filter(user=self.user).count(), 2)

    def test_sisa_detik_tidak_negatif(self):
        now = timezone.now()
        sesi = Sesi.objects.create(
            user=self.user, mode="cat", batas_waktu=now - timedelta(seconds=10)
        )
        self.assertEqual(sesi.sisa_detik(now), 0)
