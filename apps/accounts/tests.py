from django.test import TestCase
from django.contrib.auth import get_user_model

User = get_user_model()


class UserModelTestCase(TestCase):
    def test_create_guru_user(self):
        """Test membuat akun guru pengampu RPL."""
        user = User.objects.create_user(
            username='guru_agung',
            first_name='Agung Gumelar',
            last_name='Saputra',
            role=User.ROLE_GURU,
            nip='199001012020011001'
        )
        self.assertTrue(user.is_guru)
        self.assertFalse(user.is_siswa)
        self.assertEqual(user.display_name, 'Agung Gumelar Saputra')

    def test_create_siswa_user(self):
        """Test membuat akun siswa RPL."""
        user = User.objects.create_user(
            username='siswa_test',
            first_name='Asep',
            last_name='Sunandar',
            role=User.ROLE_SISWA,
            nisn='0081234567',
            kelas='XI RPL 1'
        )
        self.assertTrue(user.is_siswa)
        self.assertFalse(user.is_guru)
        self.assertEqual(user.kelas, 'XI RPL 1')
