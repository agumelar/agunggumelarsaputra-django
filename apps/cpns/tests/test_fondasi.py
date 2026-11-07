from django.contrib.auth import get_user_model
from django.test import TestCase


class PeranPesertaTests(TestCase):
    def test_peran_peserta(self):
        user = get_user_model().objects.create_user(
            username='peserta1', password='x', role='peserta',
        )
        self.assertTrue(user.is_peserta)
        self.assertFalse(user.is_siswa)
