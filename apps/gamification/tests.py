from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from apps.gamification.models import XPHistory
from apps.pembelajaran.models import Modul, UserProgress
from apps.tka.models import TkaPackage, TkaAttempt
from apps.literasi.models import LiterasiReport

User = get_user_model()


class GamificationModuleTestCase(TestCase):
    def setUp(self):
        # Create Teacher
        self.teacher = User.objects.create_user(
            username='guru_agung',
            email='agung@smkn1rongga.sch.id',
            password='password123',
            first_name='Agung Gumelar',
            last_name='Saputra',
            role=User.ROLE_GURU,
            nip='199001012020011001'
        )

        # Create Students with distinct XP and Classes
        self.student1 = User.objects.create_user(
            username='siswa_fauzi',
            email='fauzi@smkn1rongga.sch.id',
            password='password123',
            first_name='Ahmad',
            last_name='Fauzi',
            role=User.ROLE_SISWA,
            kelas='10 RPL 1',
            xp=350,
            level=3,
            streak_count=5
        )

        self.student2 = User.objects.create_user(
            username='siswa_budi',
            email='budi@smkn1rongga.sch.id',
            password='password123',
            first_name='Budi',
            last_name='Santoso',
            role=User.ROLE_SISWA,
            kelas='10 RPL 2',
            xp=500,
            level=4,
            streak_count=7
        )

        self.student3 = User.objects.create_user(
            username='siswa_citra',
            email='citra@smkn1rongga.sch.id',
            password='password123',
            first_name='Citra',
            last_name='Lestari',
            role=User.ROLE_SISWA,
            kelas='10 RPL 1',
            xp=150,
            level=2,
            streak_count=2
        )

        # Create XP History Records
        XPHistory.objects.create(
            user=self.student1,
            amount=50,
            category='modul',
            description='Menyelesaikan Modul OR-01'
        )
        XPHistory.objects.create(
            user=self.student1,
            amount=35,
            category='literasi',
            description='Setoran Rabu Literasi Minggu 1'
        )

    def test_leaderboard_view_global(self):
        """Test global leaderboard displays ranked students correctly by XP."""
        response = self.client.get(reverse('gamification:leaderboard'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Live Leaderboard Siswa RPL')
        # Student 2 has highest XP (500) -> Rank 1
        self.assertContains(response, 'Budi Santoso')
        self.assertContains(response, 'Ahmad Fauzi')

    def test_leaderboard_view_htmx_partial(self):
        """Test HTMX request to leaderboard returns partial table."""
        response = self.client.get(reverse('gamification:leaderboard'), HTTP_HX_REQUEST='true')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'gamification/partials/leaderboard_table.html')

    def test_leaderboard_view_filter_by_class(self):
        """Test filtering leaderboard by rombel class."""
        response = self.client.get(reverse('gamification:leaderboard') + '?class=10 RPL 1')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Ahmad Fauzi')
        self.assertContains(response, 'Citra Lestari')
        self.assertNotContains(response, 'Budi Santoso')  # 10 RPL 2 should be filtered out

    def test_leaderboard_view_filter_by_subject_tka(self):
        """Test subject sorting by CBT TKA scores."""
        package = TkaPackage.objects.create(
            kode='TKA-01', judul='Paket 1', slug='tka-01', passing_grade=75, is_published=True
        )
        # Citra scores 95% on TKA
        TkaAttempt.objects.create(
            user=self.student3,
            package=package,
            score=95.0,
            total_questions=10,
            correct_answers=9,
            wrong_answers=1,
            is_passed=True,
            time_spent_seconds=120
        )

        response = self.client.get(reverse('gamification:leaderboard') + '?subject=tka')
        self.assertEqual(response.status_code, 200)
        # Citra should be top ranked for TKA subject
        leaderboard = response.context['leaderboard']
        self.assertEqual(leaderboard[0].id, self.student3.id)

    def test_xp_history_view_requires_login(self):
        """Test unauthenticated user is redirected from xp history."""
        response = self.client.get(reverse('gamification:xp_history'))
        self.assertEqual(response.status_code, 302)

    def test_xp_history_view_authenticated(self):
        """Test authenticated student can view level progression and history."""
        self.client.login(username='siswa_fauzi', password='password123')
        response = self.client.get(reverse('gamification:xp_history'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Profil Gamifikasi')
        self.assertContains(response, 'Frontend Crafter')  # Level 3 title
        self.assertContains(response, 'Menyelesaikan Modul OR-01')

    def test_projector_leaderboard_requires_teacher(self):
        """Test student cannot access teacher projector leaderboard."""
        self.client.login(username='siswa_fauzi', password='password123')
        response = self.client.get(reverse('gamification:projector_leaderboard'))
        self.assertEqual(response.status_code, 302)

    def test_projector_leaderboard_teacher_access(self):
        """Test teacher can access fullscreen projector classroom scoreboard."""
        self.client.login(username='guru_agung', password='password123')
        response = self.client.get(reverse('gamification:projector_leaderboard'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'LIVE SCOREBOARD KELAS RPL')
        self.assertContains(response, 'Real-time Sync Active')
