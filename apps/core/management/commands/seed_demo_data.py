from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone
from apps.admin_panel.models import EnrollmentToken, UserEnrollment
from apps.pembelajaran.models import Modul, UserSubmission, UserProgress
from apps.tka.models import TkaPackage, TkaAttempt
from apps.literasi.models import LiterasiReport, LiterasiPeerReview
from apps.gamification.models import XPHistory

User = get_user_model()


class Command(BaseCommand):
    help = 'Membuat akun demo Guru & Siswa, Token Sesi, serta data interaktif untuk uji coba lokal.'

    def handle(self, *args, **options):
        self.stdout.write('Membuat data demo lokal...')

        # 1. Guru Pengampu / Superuser
        teacher, created = User.objects.get_or_create(
            username='guru_agung',
            defaults={
                'email': 'agung@smkn1rongga.sch.id',
                'first_name': 'Agung Gumelar',
                'last_name': 'Saputra, S.Tr.T.',
                'role': User.ROLE_GURU,
                'nip': '199001012020011001',
                'is_staff': True,
                'is_superuser': True,
            }
        )
        teacher.set_password('admin123')
        teacher.is_staff = True
        teacher.is_superuser = True
        teacher.save()
        self.stdout.write(self.style.SUCCESS('  [+] Akun Guru/Admin: guru_agung (Password: admin123)'))

        # 2. Token Sesi KBM
        token_10rpl, _ = EnrollmentToken.objects.get_or_create(
            token='10RPL1-2026',
            defaults={
                'title': 'KBM Orientasi PPLG & Praktikum RPL Gasal',
                'description': 'Token resmi pendaftaran siswa kelas 10 RPL 1 SMKN 1 Rongga.',
                'target_class': '10 RPL 1',
                'target_type': 'modul',
                'created_by': teacher,
                'is_active': True,
            }
        )
        token_demo, _ = EnrollmentToken.objects.get_or_create(
            token='RPL-DEMO',
            defaults={
                'title': 'Sesi Uji Coba Umum Lab Komputer',
                'description': 'Token sesi demo untuk pengujian seluruh fitur modul.',
                'target_class': 'Semua Kelas',
                'target_type': 'all',
                'created_by': teacher,
                'is_active': True,
            }
        )
        self.stdout.write(self.style.SUCCESS('  [+] Token Sesi: 10RPL1-2026 dan RPL-DEMO'))

        # 3. Siswa Demo
        students_data = [
            {
                'username': 'siswa_fauzi',
                'email': 'fauzi@smkn1rongga.sch.id',
                'nisn': '0061234561',
                'first_name': 'Ahmad',
                'last_name': 'Fauzi',
                'kelas': '10 RPL 1',
                'xp': 425,
                'level': 3,
                'streak_count': 5,
            },
            {
                'username': 'siswa_budi',
                'email': 'budi@smkn1rongga.sch.id',
                'nisn': '0061234562',
                'first_name': 'Budi',
                'last_name': 'Santoso',
                'kelas': '10 RPL 1',
                'xp': 680,
                'level': 4,
                'streak_count': 9,
            },
            {
                'username': 'siswa_citra',
                'email': 'citra@smkn1rongga.sch.id',
                'nisn': '0061234563',
                'first_name': 'Citra',
                'last_name': 'Lestari',
                'kelas': '10 RPL 2',
                'xp': 290,
                'level': 3,
                'streak_count': 3,
            },
            {
                'username': 'siswa_dimas',
                'email': 'dimas@smkn1rongga.sch.id',
                'nisn': '0061234564',
                'first_name': 'Dimas',
                'last_name': 'Pratama',
                'kelas': '11 RPL 1',
                'xp': 890,
                'level': 5,
                'streak_count': 12,
            },
        ]

        created_students = []
        for sd in students_data:
            s, _ = User.objects.get_or_create(
                username=sd['username'],
                defaults={
                    'email': sd['email'],
                    'nisn': sd['nisn'],
                    'first_name': sd['first_name'],
                    'last_name': sd['last_name'],
                    'role': User.ROLE_SISWA,
                    'kelas': sd['kelas'],
                    'xp': sd['xp'],
                    'level': sd['level'],
                    'streak_count': sd['streak_count'],
                }
            )
            s.set_password('password123')
            s.xp = sd['xp']
            s.level = sd['level']
            s.save()
            UserEnrollment.objects.get_or_create(user=s, token=token_10rpl)
            created_students.append(s)
            self.stdout.write(self.style.SUCCESS(f"  [+] Akun Siswa: {s.username} (Password: password123 | Kelas: {s.kelas} | XP: {s.xp})"))

        # 4. Modul Progress & Submissions
        modul_1 = Modul.objects.filter(kode='OR-01').first()

        if modul_1:
            # Fauzi finishes OR-01
            UserProgress.objects.get_or_create(user=created_students[0], modul=modul_1)
            UserSubmission.objects.get_or_create(
                user=created_students[0],
                modul=modul_1,
                submission_type='lkpd',
                defaults={
                    'form_data': {
                        'jawaban': 'Mengidentifikasi profesi Software Engineer, Frontend, Backend, dan Mobile Developer serta menyusun roadmap belajar 3 tahun.',
                        'self_level': 'Level 3',
                    },
                    'drive_url': 'https://drive.google.com/drive/folders/demo-pplg-or01',
                    'status': 'graded',
                    'teacher_score': 92,
                    'teacher_level': 'Level 3',
                    'teacher_feedback': 'Bagus sekali Fauzi, pemetaan minat karier sangat realistis.',
                    'graded_by': teacher,
                    'graded_at': timezone.now(),
                }
            )

        # 5. TKA Attempts
        tka_1 = TkaPackage.objects.filter(kode='TKA-01').first()
        if tka_1:
            TkaAttempt.objects.get_or_create(
                user=created_students[1],  # Budi
                package=tka_1,
                defaults={
                    'score': 93.3,
                    'total_questions': 60,
                    'correct_answers': 56,
                    'wrong_answers': 4,
                    'xp_earned': 72,
                    'is_passed': True,
                    'time_spent_seconds': 2100,
                }
            )
            TkaAttempt.objects.get_or_create(
                user=created_students[0],  # Fauzi
                package=tka_1,
                defaults={
                    'score': 85.0,
                    'total_questions': 60,
                    'correct_answers': 51,
                    'wrong_answers': 9,
                    'xp_earned': 68,
                    'is_passed': True,
                    'time_spent_seconds': 2400,
                }
            )

        # 6. Sample Literasi Report & Peer Review
        summary_text = (
            "Buku 'Clean Code' karya Robert C. Martin mengajarkan prinsip-prinsip fundamental dalam menulis "
            "kode yang bersih, mudah dibaca, dan mudah dipelihara. Kode yang baik bukanlah kode yang cerdas "
            "atau rumit, melainkan kode yang ketika dibaca oleh rekan tim lain dapat langsung dipahami "
            "maksud dan tujuannya tanpa memerlukan penjelasan berbelit-belit. Penulis menekankan pentingnya "
            "penamaan variabel yang bermakna, fungsi yang hanya menjalankan satu tugas spesifik (Single "
            "Responsibility Principle), serta penanganan error yang elegan. Dalam konteks pembelajaran RPL "
            "di SMK, disiplin menulis kode bersih sejak awal akan membentuk etos kerja profesional yang sangat "
            "dihargai di industri perangkat lunak modern."
        )
        report, _ = LiterasiReport.objects.get_or_create(
            user=created_students[0],  # Fauzi
            week_number=1,
            defaults={
                'book_title': 'Clean Code: A Handbook of Agile Software Craftsmanship',
                'author': 'Robert C. Martin (Uncle Bob)',
                'publisher': 'Prentice Hall',
                'year': '2008',
                'source_type': 'Buku Fisik',
                'summary': summary_text,
                'moral_message': 'Menulis kode adalah bentuk komunikasi dengan manusia lain. Jadilah developer yang bertanggung jawab atas setiap baris kode yang Anda rilis.',
                'word_count': 108,
                'status': 'graded',
                'writing_score': 95,
                'presentation_score': 90,
                'final_score': 92.5,
                'teacher_feedback': 'Ulasan yang sangat mendalam dan aplikatif untuk kompetensi software engineer. Pertahankan!',
                'graded_by': teacher,
                'graded_at': timezone.now(),
            }
        )

        # Peer review by Budi
        LiterasiPeerReview.objects.get_or_create(
            report=report,
            reviewer=created_students[1],
            defaults={
                'rating': 5,
                'comment': 'Rangkuman buku Clean Code sangat membuka wawasan tentang pentingnya refactoring!',
            }
        )

        # 7. XP History
        XPHistory.objects.get_or_create(
            user=created_students[0],
            amount=50,
            category='modul',
            description='Menyelesaikan LKPD Modul OR-01'
        )
        XPHistory.objects.get_or_create(
            user=created_students[0],
            amount=68,
            category='tka',
            description='Lulus Simulasi CBT TKA-01 (Skor 85%)'
        )
        XPHistory.objects.get_or_create(
            user=created_students[0],
            amount=35,
            category='literasi',
            description='Setoran Rabu Literasi Minggu 1: Clean Code'
        )

        self.stdout.write(self.style.SUCCESS('\nSemua data demo lokal berhasil dibuat! Anda siap menguji sistem secara lengkap.'))
