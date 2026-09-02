import os
import sys
import json
import csv
import django

# Setup Django environment
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
django.setup()

from django.contrib.auth import get_user_model
from apps.pembelajaran.models import Modul, UserProgress, UserSubmission
from apps.admin_panel.models import EnrollmentToken, UserEnrollment
from apps.gamification.models import XPHistory

User = get_user_model()


def import_from_json(json_file_path):
    """
    Import data dari file JSON yang diekspor manual (berisi dictionary per tabel atau list).
    Format contoh:
    {
        "users": [...],
        "enrollment_tokens": [...],
        "user_enrollments": [...],
        "user_progress": [...],
        "user_submissions": [...]
    }
    """
    print(f"[*] Membaca data JSON dari: {json_file_path}")
    with open(json_file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    user_map = {}

    # 1. Users
    users_data = data.get('users', [])
    print(f"[1/4] Mengimpor {len(users_data)} Akun Pengguna...")
    for u in users_data:
        email = u.get('email')
        if not email:
            continue
        name = u.get('name') or email.split('@')[0]
        parts = name.split(' ', 1)
        first_name = parts[0]
        last_name = parts[1] if len(parts) > 1 else ''
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
                'xp': u.get('xp', 0),
                'level': u.get('level', 1),
            }
        )
        user_map[u.get('id', email)] = django_user
        user_map[email] = django_user

    # 2. Tokens & Enrollments
    tokens_data = data.get('enrollment_tokens', [])
    token_map = {}
    print(f"[2/4] Mengimpor {len(tokens_data)} Token Sesi...")
    for t in tokens_data:
        code = t.get('token')
        if not code:
            continue
        token_obj, _ = EnrollmentToken.objects.get_or_create(
            token=code,
            defaults={
                'title': t.get('title') or f"Sesi {code}",
                'description': t.get('description', ''),
                'target_type': t.get('target_type') or 'all',
                'target_class': t.get('target_class') or 'Semua Kelas',
                'is_active': t.get('is_active', True),
            }
        )
        token_map[t.get('id', code)] = token_obj

    # 3. User Progress
    progress_data = data.get('user_progress', [])
    print(f"[3/4] Mengimpor {len(progress_data)} Progres Modul Selesai...")
    for p in progress_data:
        u_key = p.get('user_id') or p.get('userId') or p.get('email')
        slug = p.get('lesson_slug') or p.get('lessonSlug')
        user = user_map.get(u_key)
        if user and slug:
            modul = Modul.objects.filter(slug__icontains=slug.replace('orientasi-pplg-', '')).first() or Modul.objects.filter(slug=slug).first()
            if modul:
                UserProgress.objects.get_or_create(user=user, modul=modul)

    # 4. Submissions LKPD / Refleksi
    subs_data = data.get('user_submissions', [])
    print(f"[4/4] Mengimpor {len(subs_data)} Submisi LKPD & Refleksi...")
    for s in subs_data:
        u_key = s.get('user_id') or s.get('userId') or s.get('email')
        slug = s.get('lesson_slug') or s.get('lessonSlug')
        user = user_map.get(u_key)
        if user and slug:
            modul = Modul.objects.filter(slug__icontains=slug.replace('orientasi-pplg-', '')).first() or Modul.objects.filter(slug=slug).first()
            if modul:
                UserSubmission.objects.update_or_create(
                    user=user,
                    modul=modul,
                    submission_type=s.get('submission_type', 'lkpd'),
                    defaults={
                        'form_data': s.get('form_data') or {},
                        'drive_url': s.get('drive_url'),
                        'score': s.get('score'),
                        'teacher_score': s.get('teacher_score'),
                        'teacher_level': s.get('teacher_level'),
                        'teacher_feedback': s.get('teacher_feedback'),
                        'status': s.get('status', 'submitted'),
                    }
                )

    print("\n[+] IMPORT MANUAL DATA JSON BERHASIL SELESAI!")


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Penggunaan: python scripts/import_manual.py <path_file.json>")
        sys.exit(1)
    
    file_path = sys.argv[1]
    if not os.path.exists(file_path):
        print(f"File tidak ditemukan: {file_path}")
        sys.exit(1)

    import_from_json(file_path)
