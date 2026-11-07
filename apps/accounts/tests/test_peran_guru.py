from django.test import SimpleTestCase, override_settings
from apps.accounts.views import _is_teacher_email
from config.settings.base import GURU_EMAILS_BAWAAN, parse_guru_emails


@override_settings(GURU_EMAILS=["agung@smkn1rongga.sch.id"])
class PeranGuruTest(SimpleTestCase):
    def test_email_terdaftar_jadi_guru(self):
        self.assertTrue(_is_teacher_email("Agung@SMKN1Rongga.sch.id"))

    def test_email_berisi_kata_agung_bukan_guru(self):
        self.assertFalse(_is_teacher_email("agung123@gmail.com"))
        self.assertFalse(_is_teacher_email("siswa.agung@gmail.com"))


@override_settings(GURU_EMAILS=["agung@smkn1rongga.sch.id"])
class IsTeacherEmailKasusTepiTest(SimpleTestCase):
    def test_is_teacher_email_kasus_tepi(self):
        self.assertFalse(_is_teacher_email(None))
        self.assertFalse(_is_teacher_email(""))
        self.assertFalse(_is_teacher_email("   "))
        self.assertTrue(_is_teacher_email("  agung@smkn1rongga.sch.id \n"))


class ParsingGuruEmailsTest(SimpleTestCase):
    def test_parsing_guru_emails(self):
        self.assertEqual(parse_guru_emails("a@x.id, B@x.id,"), ["a@x.id", "b@x.id"])

    def test_parsing_guru_emails_kosong_jadi_daftar_kosong(self):
        self.assertEqual(parse_guru_emails(""), [])
        self.assertEqual(parse_guru_emails(" , ,"), [])

    def test_parsing_guru_emails_nilai_bawaan(self):
        self.assertEqual(
            parse_guru_emails(GURU_EMAILS_BAWAAN),
            ["agung@smkn1rongga.sch.id", "agunggumelar@smkn1rongga.sch.id"],
        )
