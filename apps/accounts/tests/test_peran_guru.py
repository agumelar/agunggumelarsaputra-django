import importlib
import os
from unittest import mock

from django.test import SimpleTestCase, override_settings
from apps.accounts.views import _is_teacher_email


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
    def _muat(self, nilai):
        # settings/base.py membaca env saat diimpor, jadi dimuat ulang di bawah env palsu.
        from config.settings import base

        def pulihkan():
            importlib.reload(base)

        self.addCleanup(pulihkan)
        env = {"GURU_EMAILS": nilai} if nilai is not None else {}
        with mock.patch.dict(os.environ, env):
            if nilai is None:
                os.environ.pop("GURU_EMAILS", None)
            importlib.reload(base)
        return base.GURU_EMAILS

    def test_parsing_guru_emails(self):
        self.assertEqual(self._muat("a@x.id, B@x.id,"), ["a@x.id", "B@x.id"])

    def test_parsing_guru_emails_kosong_jadi_daftar_kosong(self):
        self.assertEqual(self._muat(" , ,"), [])

    def test_parsing_guru_emails_bawaan_bila_env_tidak_ada(self):
        self.assertEqual(
            self._muat(None),
            ["agung@smkn1rongga.sch.id", "agunggumelar@smkn1rongga.sch.id"],
        )
