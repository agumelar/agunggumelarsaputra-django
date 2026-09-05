import os
import sys
import json
import django
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import dotenv_values

# Setup Django Environment
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
django.setup()

from django.contrib.auth import get_user_model
from django.utils import timezone
from apps.admin_panel.models import EnrollmentToken, UserEnrollment
from apps.pembelajaran.models import Modul, UserProgress, UserSubmission
from apps.tka.models import TkaPackage, TkaAttempt
from apps.literasi.models import LiterasiReport, LiterasiPeerReview

User = get_user_model()


def to_aware(dt):
    if dt is None:
        return None
    if timezone.is_naive(dt):
        return timezone.make_aware(dt, timezone.get_current_timezone())
    return dt


def get_connections():
    base_env = dotenv_values(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '.env'))
    url1 = os.getenv('NEON_DB1_URL') or base_env.get('NEON_DB1_URL')
    url2 = os.getenv('NEON_DB2_URL') or base_env.get('NEON_DB2_URL')

    if not url1 or not url2:
        raise ValueError("NEON_DB1_URL and NEON_DB2_URL must be defined in environment or .env file!")

    print(f"[*] Menghubungkan ke Neon DB 1...")
    conn1 = psycopg2.connect(url1, cursor_factory=RealDictCursor)
    print("[+] DB 1 Terhubung!")

    print(f"[*] Menghubungkan ke Neon DB 2...")
    conn2 = psycopg2.connect(url2, cursor_factory=RealDictCursor)
    print("[+] DB 2 Terhubung!\n")

    return conn1, conn2


def consolidate_and_import():
    conn1, conn2 = get_connections()
    cur1 = conn1.cursor()
    cur2 = conn2.cursor()

    # Pastikan guru utama ada
    guru_utama, _ = User.objects.get_or_create(
        email="agumelarsaputra@gmail.com",
        defaults={
            'username': 'agumelarsaputra',
            'first_name': 'Agung Gumelar',
            'last_name': 'Saputra, S.Tr.T.',
            'role': User.ROLE_GURU,
            'is_staff': True,
            'is_superuser': True,
            'kelas': 'Guru / Staf Pengampu',
        }
    )
    guru_utama.set_password("RPL@Rongga2026")
    guru_utama.save()

    # -------------------------------------------------------------
    # 1. ENROLLMENT TOKENS
    # -------------------------------------------------------------
    print("=== [1/7] Mengonsolidasikan Enrollment Tokens ===")
    token_map = {} # (db_num, legacy_token_id) -> django_token_obj

    for db_num, cur in [(1, cur1), (2, cur2)]:
        cur.execute("SELECT * FROM enrollment_tokens")
        tokens = cur.fetchall()
        for t in tokens:
            t_code = (t.get('token') or '').strip().upper()
            if not t_code:
                continue
            
            django_token, created = EnrollmentToken.objects.get_or_create(
                token=t_code,
                defaults={
                    'title': t.get('title') or f"Sesi {t_code}",
                    'description': t.get('description') or '',
                    'target_class': t.get('target_class') or t.get('targetClass') or 'Semua Kelas',
                    'target_type': t.get('target_type') or 'orientasi',
                    'is_active': t.get('is_active', True) if t.get('is_active') is not None else True,
                    'created_by': guru_utama,
                    'created_at': to_aware(t.get('created_at')) or timezone.now(),
                    'expires_at': to_aware(t.get('expires_at')),
                }
            )
            token_map[(db_num, t['id'])] = django_token

    print(f"    [OK] Total EnrollmentToken di Django: {EnrollmentToken.objects.count()}")

    # -------------------------------------------------------------
    # 2. USERS & GAMIFIKASI
    # -------------------------------------------------------------
    print("\n=== [2/7] Mengonsolidasikan Akun Siswa & Gamifikasi ===")
    gamif_map = {} # (db_num, user_id) -> dict
    for db_num, cur in [(1, cur1), (2, cur2)]:
        cur.execute("SELECT * FROM user_gamification")
        for g in cur.fetchall():
            gamif_map[(db_num, g['user_id'])] = g

    user_map = {} # (db_num, legacy_user_id) -> django_user

    for db_num, cur in [(1, cur1), (2, cur2)]:
        cur.execute("SELECT * FROM users ORDER BY id ASC")
        users = cur.fetchall()
        for u in users:
            email = (u.get('email') or '').strip().lower()
            if not email:
                continue

            name = (u.get('name') or email.split('@')[0]).strip()
            name_parts = name.split(' ', 1)
            first_name = name_parts[0]
            last_name = name_parts[1] if len(name_parts) > 1 else ''

            is_teacher = (
                email in ['agumelarsaputra@gmail.com', 'agung@smkn1rongga.sch.id']
                or u.get('role') == 'admin'
                or 'agung' in email
            )
            student_class = u.get('student_class') or '10 RPL 1'

            django_user = User.objects.filter(email__iexact=email).first()
            if not django_user:
                base_uname = email.split('@')[0].replace('.', '_').replace('-', '_')
                uname = base_uname
                cnt = 1
                while User.objects.filter(username__iexact=uname).exists():
                    uname = f"{base_uname}{cnt}"
                    cnt += 1

                django_user = User(
                    email=email,
                    username=uname,
                    first_name=first_name,
                    last_name=last_name,
                    role=User.ROLE_GURU if is_teacher else User.ROLE_SISWA,
                    is_staff=is_teacher,
                    is_superuser=is_teacher,
                    kelas='Guru / Staf Pengampu' if is_teacher else student_class,
                )
                
                pwd_hash = u.get('password_hash')
                if pwd_hash and pwd_hash.startswith('$2'):
                    django_user.password = f"bcrypt${pwd_hash}"
                elif is_teacher:
                    django_user.set_password("RPL@Rongga2026")
                else:
                    django_user.set_password("RPL@Rongga2026")

                django_user.save()
            else:
                if student_class and (django_user.kelas in ['10 RPL 1', '', None]) and not django_user.is_guru:
                    django_user.kelas = student_class
                    django_user.save(update_fields=['kelas'])

            g_data = gamif_map.get((db_num, u['id']))
            if g_data:
                xp = g_data.get('xp', 0)
                level = g_data.get('level', 1)
                streak = g_data.get('streak_days', 1)
                last_act = g_data.get('last_active_date')

                if xp > django_user.xp:
                    django_user.xp = xp
                if level > django_user.level:
                    django_user.level = level
                if streak > django_user.streak_count:
                    django_user.streak_count = streak
                if last_act and (not django_user.last_active_date or last_act.date() > django_user.last_active_date):
                    django_user.last_active_date = last_act.date()
                django_user.save(update_fields=['xp', 'level', 'streak_count', 'last_active_date'])

            user_map[(db_num, u['id'])] = django_user

    print(f"    [OK] Total Pengguna Berhasil Terkonsolidasi: {User.objects.count()} akun")

    # -------------------------------------------------------------
    # 3. USER ENROLLMENTS
    # -------------------------------------------------------------
    print("\n=== [3/7] Mengonsolidasikan User Enrollments ===")
    for db_num, cur in [(1, cur1), (2, cur2)]:
        cur.execute("SELECT * FROM user_enrollments")
        enrollments = cur.fetchall()
        for e in enrollments:
            d_user = user_map.get((db_num, e['user_id']))
            d_token = token_map.get((db_num, e['token_id']))
            if d_user and d_token:
                UserEnrollment.objects.get_or_create(
                    user=d_user,
                    token=d_token,
                    defaults={'enrolled_at': to_aware(e.get('enrolled_at')) or timezone.now()}
                )

    print(f"    [OK] Total UserEnrollments Aktif: {UserEnrollment.objects.count()} entri")

    # -------------------------------------------------------------
    # 4. USER PROGRESS (Modul Selesai)
    # -------------------------------------------------------------
    print("\n=== [4/7] Mengonsolidasikan User Progress ===")
    for db_num, cur in [(1, cur1), (2, cur2)]:
        cur.execute("SELECT * FROM user_progress")
        progresses = cur.fetchall()
        for p in progresses:
            d_user = user_map.get((db_num, p['user_id']))
            if not d_user:
                continue

            slug = p.get('lesson_slug')
            if not slug or not slug.startswith('orientasi-'):
                continue

            d_modul = Modul.objects.filter(slug=slug).first()
            if d_modul:
                comp_at = to_aware(p.get('completed_at')) or timezone.now()
                UserProgress.objects.get_or_create(
                    user=d_user,
                    modul=d_modul,
                    defaults={'completed_at': comp_at}
                )

    print(f"    [OK] Total UserProgress Modul: {UserProgress.objects.count()} catatan tuntas")

    # -------------------------------------------------------------
    # 5. USER SUBMISSIONS (LKPD & Refleksi)
    # -------------------------------------------------------------
    print("\n=== [5/7] Mengonsolidasikan Pengumpulan Tugas / Submisi ===")
    for db_num, cur in [(1, cur1), (2, cur2)]:
        cur.execute("SELECT * FROM user_submissions ORDER BY id ASC")
        submissions = cur.fetchall()
        for s in submissions:
            d_user = user_map.get((db_num, s['user_id']))
            if not d_user:
                continue

            slug = s.get('lesson_slug')
            if not slug or not slug.startswith('orientasi-'):
                continue

            d_modul = Modul.objects.filter(slug=slug).first()
            if not d_modul:
                continue

            sub_type = s.get('submission_type') or 'lkpd'
            d_token = token_map.get((db_num, s.get('token_id')))

            raw_form = s.get('form_data')
            if isinstance(raw_form, str):
                try:
                    payload = json.loads(raw_form)
                except Exception:
                    payload = {'raw_text': raw_form}
            elif isinstance(raw_form, dict):
                payload = raw_form
            else:
                payload = {}

            existing_sub = UserSubmission.objects.filter(
                user=d_user,
                modul=d_modul,
                submission_type=sub_type
            ).first()

            s_sub_at = to_aware(s.get('submitted_at')) or timezone.now()
            s_grad_at = to_aware(s.get('graded_at'))

            if not existing_sub:
                UserSubmission.objects.create(
                    user=d_user,
                    modul=d_modul,
                    token=d_token,
                    submission_type=sub_type,
                    form_data=payload,
                    drive_url=s.get('drive_url'),
                    score=s.get('score'),
                    teacher_score=s.get('teacher_score'),
                    teacher_level=s.get('teacher_level'),
                    teacher_feedback=s.get('teacher_feedback'),
                    status=s.get('status') or 'submitted',
                    graded_by=guru_utama if s.get('teacher_score') is not None else None,
                    graded_at=s_grad_at,
                    submitted_at=s_sub_at,
                )
            else:
                if s.get('teacher_score') is not None and existing_sub.teacher_score is None:
                    existing_sub.teacher_score = s.get('teacher_score')
                    existing_sub.teacher_level = s.get('teacher_level')
                    existing_sub.teacher_feedback = s.get('teacher_feedback')
                    existing_sub.status = s.get('status') or 'graded'
                    existing_sub.graded_by = guru_utama
                    existing_sub.graded_at = s_grad_at
                    existing_sub.save()
                elif s_sub_at and existing_sub.submitted_at and s_sub_at > existing_sub.submitted_at:
                    existing_sub.form_data = payload
                    existing_sub.drive_url = s.get('drive_url') or existing_sub.drive_url
                    existing_sub.save()

    print(f"    [OK] Total Submisi Tugas Tervalidasi: {UserSubmission.objects.count()} pengumpulan")

    # -------------------------------------------------------------
    # 6. TKA ATTEMPTS (Riwayat Simulasi CBT TKA)
    # -------------------------------------------------------------
    print("\n=== [6/7] Mengonsolidasikan Riwayat Simulasi CBT TKA ===")
    for db_num, cur in [(1, cur1), (2, cur2)]:
        cur.execute("SELECT * FROM tka_attempts ORDER BY id ASC")
        attempts = cur.fetchall()
        for a in attempts:
            d_user = user_map.get((db_num, a['user_id']))
            if not d_user:
                continue

            slug = a.get('lesson_slug')
            if not slug:
                slug = 'tka-01-algoritma-logika'

            d_pkg = TkaPackage.objects.filter(slug=slug).first()
            if not d_pkg:
                continue

            d_token = token_map.get((db_num, a.get('token_id')))
            score = float(a.get('score') or 0.0)
            total_q = a.get('total_questions') or 30
            correct_q = a.get('correct_answers') or 0
            wrong_q = max(0, total_q - correct_q)
            xp_earned = a.get('xp_earned') or 0
            comp_at = to_aware(a.get('created_at')) or timezone.now()

            # Hindari duplikat yang persis sama
            existing_att = TkaAttempt.objects.filter(
                user=d_user,
                package=d_pkg,
                attempt_number=a.get('attempt_number') or 1,
                completed_at=comp_at
            ).first()

            if not existing_att:
                TkaAttempt.objects.create(
                    user=d_user,
                    package=d_pkg,
                    token=d_token,
                    attempt_number=a.get('attempt_number') or 1,
                    score=score,
                    total_questions=total_q,
                    correct_answers=correct_q,
                    wrong_answers=wrong_q,
                    xp_earned=xp_earned,
                    is_passed=(score >= 75.0),
                    completed_at=comp_at
                )

    print(f"    [OK] Total Riwayat Ujian CBT TKA: {TkaAttempt.objects.count()} sesi ujian")

    # -------------------------------------------------------------
    # 7. RABU LITERASI (RESIK) & PEER REVIEWS
    # -------------------------------------------------------------
    print("\n=== [7/7] Mengonsolidasikan Laporan Rabu Literasi (RESIK) ===")
    report_map = {}

    for db_num, cur in [(1, cur1), (2, cur2)]:
        cur.execute("SELECT * FROM literasi_reports ORDER BY id ASC")
        reports = cur.fetchall()
        for r in reports:
            d_user = user_map.get((db_num, r['user_id']))
            if not d_user:
                continue

            book_title = (r.get('book_title') or 'Laporan Literasi').strip()
            week_no = r.get('week_number') or 1

            existing_report = LiterasiReport.objects.filter(
                user=d_user,
                week_number=week_no,
                book_title__iexact=book_title
            ).first()

            raw_check = r.get('self_checklist')
            if isinstance(raw_check, str):
                try:
                    checklist = json.loads(raw_check)
                except Exception:
                    checklist = {}
            elif isinstance(raw_check, dict):
                checklist = raw_check
            else:
                checklist = {}

            rep_date = r.get('report_date')
            if hasattr(rep_date, 'date'):
                rep_date = rep_date.date()
            elif not rep_date:
                rep_date = timezone.now().date()

            if not existing_report:
                rep = LiterasiReport.objects.create(
                    user=d_user,
                    token=None,
                    week_number=week_no,
                    report_date=rep_date,
                    book_title=book_title[:250],
                    author=(r.get('author') or '-')[:250],
                    publisher=(r.get('publisher') or '')[:250],
                    city=(r.get('city') or '')[:100],
                    year=str(r.get('year') or '')[:10],
                    page_count=str(r.get('page_count') or '')[:50],
                    edition=str(r.get('edition') or '')[:50],
                    source_type='Buku Fisik',
                    summary=r.get('summary') or '-',
                    moral_message=r.get('moral_message') or '-',
                    word_count=len((r.get('summary') or '').split()),
                    self_checklist=checklist,
                    writing_score=r.get('writing_score'),
                    presentation_score=r.get('presentation_score'),
                    final_score=r.get('final_score'),
                    teacher_feedback=r.get('teacher_feedback'),
                    graded_by=guru_utama if r.get('final_score') is not None else None,
                    graded_at=to_aware(r.get('graded_at')),
                    status=r.get('status') or 'submitted',
                )
                report_map[(db_num, r['id'])] = rep
            else:
                report_map[(db_num, r['id'])] = existing_report

    # Peer reviews
    for db_num, cur in [(1, cur1), (2, cur2)]:
        cur.execute("SELECT * FROM literasi_peer_reviews")
        reviews = cur.fetchall()
        for rv in reviews:
            d_rep = report_map.get((db_num, rv['report_id']))
            d_reviewer = user_map.get((db_num, rv['reviewer_id']))
            if d_rep and d_reviewer:
                LiterasiPeerReview.objects.get_or_create(
                    report=d_rep,
                    reviewer=d_reviewer,
                    defaults={
                        'rating': rv.get('rating') or 5,
                        'comment': rv.get('comment') or 'Bagus dan inspiratif',
                    }
                )

    print(f"    [OK] Total Laporan Literasi RESIK: {LiterasiReport.objects.count()} laporan")
    print(f"    [OK] Total Peer Reviews: {LiterasiPeerReview.objects.count()} ulasan")

    cur1.close()
    conn1.close()
    cur2.close()
    conn2.close()

    print("\n==================================================")
    print("[SUCCESS] KONSOLIDASI & SINKRONISASI DATA NEON 100% SUKSES!")
    print("==================================================")


if __name__ == '__main__':
    consolidate_and_import()
