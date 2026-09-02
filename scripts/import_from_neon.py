import os
import sys
import django
import psycopg2
from psycopg2.extras import RealDictCursor

# Setup Django environment
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
django.setup()

from django.contrib.auth import get_user_model
from django.utils import timezone
from apps.pembelajaran.models import Modul, UserProgress, UserSubmission
from apps.admin_panel.models import EnrollmentToken, UserEnrollment
from apps.tka.models import TKAPackage, TKAQuestion, TKAAttempt
from apps.gamification.models import XPHistory

User = get_user_model()


def run_migration(pg_url):
    print(f"[*] Menghubungkan ke Neon PostgreSQL...")
    try:
        conn = psycopg2.connect(pg_url, cursor_factory=RealDictCursor)
        cur = conn.cursor()
        print("[+] Koneksi berhasil!\n")
    except Exception as e:
        print(f"[-] Gagal terhubung ke database: {e}")
        return False

    # 1. Migrasi Users
    print("[1/5] Memeriksa & Mengimpor Data Pengguna (Users)...")
    try:
        cur.execute("SELECT * FROM users")
        legacy_users = cur.fetchall()
        user_map = {} # legacy_id -> django_user
        imported_users = 0

        for u in legacy_users:
            email = u.get('email')
            if not email:
                continue

            name = u.get('name') or email.split('@')[0]
            name_parts = name.split(' ', 1)
            first_name = name_parts[0]
            last_name = name_parts[1] if len(name_parts) > 1 else ''
            is_teacher = (u.get('role') == 'admin')
            student_class = u.get('student_class') or u.get('studentClass') or '10 RPL 1'

            django_user, created = User.objects.get_or_create(
                email=email,
                defaults={
                    'username': email.split('@')[0],
                    'first_name': first_name,
                    'last_name': last_name,
                    'role': 'guru' if is_teacher else 'siswa',
                    'is_staff': is_teacher,
                    'is_superuser': is_teacher,
                    'is_siswa': not is_teacher,
                    'is_guru': is_teacher,
                    'kelas': student_class,
                }
            )

            # Jika sudah ada, update kelas jika belum diset
            if not created and not django_user.kelas:
                django_user.kelas = student_class
                django_user.save(update_fields=['kelas'])

            user_map[u['id']] = django_user
            imported_users += 1

        print(f"    -> Berhasil memetakan {imported_users} akun pengguna.")
    except Exception as e:
        print(f"    [-] Lewati tabel users: {e}")

    # 2. Migrasi Gamifikasi (XP & Level)
    print("\n[2/5] Mengimpor Data Gamifikasi (XP, Level, Streak)...")
    try:
        cur.execute("SELECT * FROM user_gamification")
        gamifications = cur.fetchall()
        for g in gamifications:
            u_id = g.get('user_id') or g.get('userId')
            if u_id in user_map:
                django_user = user_map[u_id]
                django_user.xp = g.get('xp', 0)
                django_user.level = g.get('level', 1)
                django_user.streak_days = g.get('streak_days') or g.get('streakDays') or 1
                django_user.save(update_fields=['xp', 'level', 'streak_days'])
        print(f"    -> Berhasil memperbarui data gamifikasi {len(gamifications)} pengguna.")
    except Exception as e:
        print(f"    [-] Info: {e}")

    # 3. Migrasi Enrollment Tokens & User Enrollments
    print("\n[3/5] Mengimpor Token Sesi & Enrollment Siswa...")
    token_map = {} # legacy_id -> django_token
    try:
        cur.execute("SELECT * FROM enrollment_tokens")
        tokens = cur.fetchall()
        for t in tokens:
            code = t.get('token')
            token_obj, _ = EnrollmentToken.objects.get_or_create(
                token=code,
                defaults={
                    'title': t.get('title') or f"Sesi {code}",
                    'description': t.get('description', ''),
                    'target_type': t.get('target_type') or t.get('targetType') or 'all',
                    'target_slug': t.get('target_slug') or t.get('targetSlug'),
                    'target_class': t.get('target_class') or t.get('targetClass') or 'Semua Kelas',
                    'is_active': t.get('is_active', True) if t.get('is_active') is not None else True,
                }
            )
            token_map[t['id']] = token_obj
        print(f"    -> Berhasil mengimpor {len(token_map)} token sesi.")

        cur.execute("SELECT * FROM user_enrollments")
        enrollments = cur.fetchall()
        enrolled_count = 0
        for en in enrollments:
            u_id = en.get('user_id') or en.get('userId')
            t_id = en.get('token_id') or en.get('tokenId')
            if u_id in user_map and t_id in token_map:
                UserEnrollment.objects.get_or_create(
                    user=user_map[u_id],
                    token=token_map[t_id]
                )
                enrolled_count += 1
        print(f"    -> Berhasil mencatat {enrolled_count} relasi enrollment siswa.")
    except Exception as e:
        print(f"    [-] Info: {e}")

    # 4. Migrasi Progres Modul (UserProgress)
    print("\n[4/5] Mengimpor Riwayat Progres Modul Siswa...")
    try:
        cur.execute("SELECT * FROM user_progress")
        progresses = cur.fetchall()
        prog_count = 0
        for p in progresses:
            u_id = p.get('user_id') or p.get('userId')
            slug = p.get('lesson_slug') or p.get('lessonSlug')
            if u_id in user_map and slug:
                # Normalisasi slug
                modul = Modul.objects.filter(slug__icontains=slug.replace('orientasi-pplg-', '')).first() or Modul.objects.filter(slug=slug).first()
                if modul:
                    UserProgress.objects.get_or_create(
                        user=user_map[u_id],
                        modul=modul
                    )
                    prog_count += 1
        print(f"    -> Berhasil mengimpor {prog_count} riwayat modul selesai.")
    except Exception as e:
        print(f"    [-] Info: {e}")

    # 5. Migrasi Submisi LKPD & Refleksi (UserSubmission)
    print("\n[5/5] Mengimpor Submisi LKPD, Refleksi & Penilaian Guru...")
    try:
        cur.execute("SELECT * FROM user_submissions")
        subs = cur.fetchall()
        sub_count = 0
        for s in subs:
            u_id = s.get('user_id') or s.get('userId')
            slug = s.get('lesson_slug') or s.get('lessonSlug')
            sub_type = s.get('submission_type') or s.get('submissionType') or 'lkpd'
            if u_id in user_map and slug:
                modul = Modul.objects.filter(slug__icontains=slug.replace('orientasi-pplg-', '')).first() or Modul.objects.filter(slug=slug).first()
                if modul:
                    UserSubmission.objects.update_or_create(
                        user=user_map[u_id],
                        modul=modul,
                        submission_type=sub_type,
                        defaults={
                            'form_data': s.get('form_data') or s.get('formData') or {},
                            'drive_url': s.get('drive_url') or s.get('driveUrl'),
                            'score': s.get('score'),
                            'teacher_score': s.get('teacher_score') or s.get('teacherScore'),
                            'teacher_level': s.get('teacher_level') or s.get('teacherLevel'),
                            'teacher_feedback': s.get('teacher_feedback') or s.get('teacherFeedback'),
                            'status': s.get('status', 'submitted'),
                        }
                    )
                    sub_count += 1
        print(f"    -> Berhasil mengimpor {sub_count} submisi LKPD/Refleksi.")
    except Exception as e:
        print(f"    [-] Info: {e}")

    cur.close()
    conn.close()
    print("\n" + "="*60)
    print("MIGRASI DATA NEON SELESAI DENGAN SUKSES!")
    print("="*60)
    return True


if __name__ == '__main__':
    if len(sys.argv) > 1:
        target_url = sys.argv[1]
    else:
        target_url = os.environ.get('DATABASE_URL') or os.environ.get('NEON_DATABASE_URL')

    if not target_url:
        print("Usage: python scripts/import_from_neon.py <POSTGRES_CONNECTION_URL>")
        sys.exit(1)

    run_migration(target_url)
