from django.test import SimpleTestCase, override_settings
from apps.accounts.views import _is_teacher_email


@override_settings(GURU_EMAILS=["agung@smkn1rongga.sch.id"])
class PeranGuruTest(SimpleTestCase):
    def test_email_terdaftar_jadi_guru(self):
        self.assertTrue(_is_teacher_email("Agung@SMKN1Rongga.sch.id"))

    def test_email_berisi_kata_agung_bukan_guru(self):
        self.assertFalse(_is_teacher_email("agung123@gmail.com"))
        self.assertFalse(_is_teacher_email("siswa.agung@gmail.com"))
