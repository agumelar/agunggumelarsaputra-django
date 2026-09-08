from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import user_passes_test
from django.contrib import messages
from django.views.decorators.http import require_POST
from django.utils import timezone
from django.http import HttpResponse, JsonResponse
from django.db.models import Count, Avg
import csv
import json

from .models import EnrollmentToken, UserEnrollment
from .forms import EnrollmentTokenForm, TeacherGradeForm, TeacherGradeLiterasiForm
from apps.pembelajaran.models import Modul, UserSubmission, UserProgress
from apps.tka.models import TkaPackage, TkaAttempt
from apps.literasi.models import LiterasiReport
from apps.gamification.models import XPHistory
from django.contrib.auth import get_user_model

User = get_user_model()


def teacher_check(user):
    return user.is_authenticated and (user.is_guru or user.is_staff or user.is_superuser)


@user_passes_test(teacher_check, login_url='accounts:login')
def dashboard_view(request):
    """
    Konsol Terpadu Guru Pengampu RPL (Single-Pane Command Center):
    Monitoring KBM, Token Rombel, Evaluasi LKPD & Refleksi, Data Siswa, Log Ujian TKA, Rabu Literasi, dan Log Modul.
    """
    # 1. Total Pengguna
    all_students = User.objects.filter(role=User.ROLE_SISWA).order_by('kelas', 'first_name')
    total_students = all_students.count()
    total_teachers = User.objects.filter(role=User.ROLE_GURU).count()
    total_superadmins = User.objects.filter(is_superuser=True).count()
    total_enrollments = UserEnrollment.objects.count()

    # 2. Token Sesi
    tokens = EnrollmentToken.objects.prefetch_related('user_enrollments', 'created_by').order_by('-created_at')
    total_tokens = tokens.count()
    active_tokens = sum(1 for t in tokens if t.is_active)
    
    # Map attempt counts per token
    token_exam_counts = dict(
        TkaAttempt.objects.filter(token__isnull=False)
        .values('token_id')
        .annotate(c=Count('id'))
        .values_list('token_id', 'c')
    )
    for t in tokens:
        t.cached_exam_count = token_exam_counts.get(t.id, 0)
        t.cached_enrolled_count = t.user_enrollments.count()

    # 3. Evaluasi LKPD & Jurnal Refleksi (Deduplikasi: submisi teranyar per siswa per modul)
    all_submissions = UserSubmission.objects.select_related('user', 'modul', 'graded_by').order_by('-submitted_at')
    unique_sub_map = {}
    for s in all_submissions:
        key = f"{s.user_id}_{s.modul_id}_{s.submission_type}"
        if key not in unique_sub_map:
            fd = s.form_data or {}
            while isinstance(fd, str):
                try:
                    fd = json.loads(fd)
                except Exception:
                    break
            s.form_data = fd
            s.form_data_json = json.dumps(fd if isinstance(fd, dict) else {})
            unique_sub_map[key] = s

    deduped_submissions = list(unique_sub_map.values())
    lkpd_submissions = [s for s in deduped_submissions if s.submission_type == 'lkpd']
    reflection_submissions = [s for s in deduped_submissions if s.submission_type == 'reflection']

    total_lkpd = len(lkpd_submissions)
    pending_lkpd = sum(1 for s in lkpd_submissions if s.status == 'submitted')
    graded_lkpd = sum(1 for s in lkpd_submissions if s.status == 'graded')

    total_reflections = len(reflection_submissions)
    pending_reflections = sum(1 for s in reflection_submissions if s.status == 'submitted')
    reviewed_reflections = sum(1 for s in reflection_submissions if s.status == 'reviewed')

    # 4. Log Ujian CBT TKA PPLG
    all_exam_logs = TkaAttempt.objects.select_related('user', 'package', 'token').order_by('-completed_at')
    total_tka_attempts = all_exam_logs.count()
    passing_exams = all_exam_logs.filter(score__gte=73).count()
    pass_rate_tka = round((passing_exams / total_tka_attempts) * 100) if total_tka_attempts > 0 else 0
    avg_score_tka = round(all_exam_logs.aggregate(avg=Avg('score'))['avg'] or 0)

    # 5. Rabu Literasi (RESIK)
    all_literasi_reports = LiterasiReport.objects.select_related('user', 'graded_by').prefetch_related('peer_reviews').order_by('-report_date', '-created_at')
    total_literasi = all_literasi_reports.count()
    pending_literasi = all_literasi_reports.filter(status='submitted').count()
    graded_literasi = all_literasi_reports.filter(status='graded').count()

    # 6. Log Modul Pembelajaran (UserProgress)
    all_lesson_logs = UserProgress.objects.select_related('user', 'modul').order_by('-completed_at')[:150]
    total_lessons_completed = UserProgress.objects.count()

    # 7. Metadata Tambahan
    all_modules = Modul.objects.filter(is_published=True).order_by('urutan')
    tka_packages = TkaPackage.objects.filter(is_published=True).order_by('urutan')
    classes = [
        '10 RPL 1', '10 RPL 2', '10 RPL 3', '10 RPL 4',
        '11 RPL 1', '11 RPL 2', '11 RPL 3', '11 RPL 4',
        '12 RPL 1', '12 RPL 2', '12 RPL 3', '12 RPL 4',
        'Kelas Uji Coba'
    ]
    kktp_levels = UserSubmission.LEVEL_CHOICES
    token_form = EnrollmentTokenForm()

    lkpd_data_list = []
    for s in lkpd_submissions:
        lkpd_data_list.append({
            'id': s.id,
            'studentName': s.user.display_name,
            'studentEmail': s.user.email,
            'studentClass': s.user.kelas or '10 RPL',
            'studentNis': s.user.nisn or '-',
            'moduleCode': s.modul.kode,
            'moduleTitle': s.modul.judul,
            'moduleSlug': s.modul.slug,
            'submittedAt': s.submitted_at.strftime('%d %b %Y, %H:%M') if s.submitted_at else '-',
            'teacherScore': s.teacher_score,
            'teacherLevel': s.teacher_level or '',
            'teacherFeedback': s.teacher_feedback or '',
            'driveUrl': s.drive_url or '',
            'status': s.status,
            'formData': s.form_data if isinstance(s.form_data, dict) else {}
        })

    reflection_data_list = []
    for r in reflection_submissions:
        reflection_data_list.append({
            'id': r.id,
            'studentName': r.user.display_name,
            'studentEmail': r.user.email,
            'studentClass': r.user.kelas or '10 RPL',
            'studentNis': r.user.nisn or '-',
            'moduleCode': r.modul.kode,
            'moduleTitle': r.modul.judul,
            'moduleSlug': r.modul.slug,
            'submittedAt': r.submitted_at.strftime('%d %b %Y, %H:%M') if r.submitted_at else '-',
            'teacherFeedback': r.teacher_feedback or '',
            'status': r.status,
            'formData': r.form_data if isinstance(r.form_data, dict) else {}
        })

    literasi_data_list = []
    for rep in all_literasi_reports:
        literasi_data_list.append({
            'id': rep.id,
            'studentName': rep.user.display_name,
            'studentClass': rep.user.kelas or '10 RPL',
            'bookTitle': rep.book_title,
            'author': rep.author,
            'publisher': rep.publisher or '-',
            'pageCount': rep.page_count or '-',
            'weekNumber': rep.week_number,
            'summary': rep.summary or '',
            'moral': rep.moral_message or '',
            'wScore': rep.writing_score or 12,
            'pScore': rep.presentation_score or 15,
            'teacherFeedback': rep.teacher_feedback or ''
        })

    context = {
        'lkpd_data_json': lkpd_data_list,
        'reflection_data_json': reflection_data_list,
        'literasi_data_json': literasi_data_list,
        # Metrics
        'total_students': total_students,
        'total_teachers': total_teachers,
        'total_superadmins': total_superadmins,
        'total_enrollments': total_enrollments,
        'total_tokens': total_tokens,
        'active_tokens': active_tokens,
        'total_lkpd': total_lkpd,
        'pending_lkpd': pending_lkpd,
        'graded_lkpd': graded_lkpd,
        'pending_submissions': pending_lkpd,  # alias
        'total_reflections': total_reflections,
        'pending_reflections': pending_reflections,
        'reviewed_reflections': reviewed_reflections,
        'total_tka_attempts': total_tka_attempts,
        'pass_rate_tka': pass_rate_tka,
        'avg_score_tka': avg_score_tka,
        'total_literasi': total_literasi,
        'pending_literasi': pending_literasi,
        'graded_literasi': graded_literasi,
        'total_lessons_completed': total_lessons_completed,

        # Tab Datasets
        'tokens': tokens,
        'lkpd_submissions': lkpd_submissions,
        'reflection_submissions': reflection_submissions,
        'all_students': all_students,
        'all_exam_logs': all_exam_logs,
        'all_literasi_reports': all_literasi_reports,
        'all_lesson_logs': all_lesson_logs,

        # Filters & Forms
        'all_modules': all_modules,
        'tka_packages': tka_packages,
        'classes': classes,
        'kktp_levels': kktp_levels,
        'token_form': token_form,
        'active_nav': 'admin_dashboard',
    }
    return render(request, 'admin_panel/dashboard.html', context)


@user_passes_test(teacher_check, login_url='accounts:login')
def token_list_view(request):
    """
    Daftar Lengkap Token Sesi Rombel & Filter Kelas.
    """
    filter_class = request.GET.get('class', '')
    tokens = EnrollmentToken.objects.prefetch_related('user_enrollments', 'created_by').order_by('-created_at')

    if filter_class and filter_class != 'Semua':
        tokens = tokens.filter(target_class=filter_class)

    form = EnrollmentTokenForm()

    context = {
        'tokens': tokens,
        'form': form,
        'selected_class': filter_class,
        'active_nav': 'admin_tokens',
    }
    return render(request, 'admin_panel/tokens.html', context)


@user_passes_test(teacher_check, login_url='accounts:login')
def token_create_view(request):
    """
    Pembuatan Token Sesi Baru oleh Guru.
    """
    if request.method == 'POST':
        form = EnrollmentTokenForm(request.POST)
        if form.is_valid():
            token_obj = form.save(user=request.user)
            messages.success(request, f"Token sesi '{token_obj.token}' ({token_obj.target_class}) berhasil dibuat!")
            return redirect('admin_panel:token_list')
        else:
            messages.error(request, "Terjadi kesalahan pada data form pembuatan token.")
    else:
        form = EnrollmentTokenForm()

    return render(request, 'admin_panel/token_create.html', {'form': form, 'active_nav': 'admin_tokens'})


@user_passes_test(teacher_check, login_url='accounts:login')
@require_POST
def token_toggle_view(request, token_id):
    """
    HTMX Endpoint: Mengaktifkan / Menutup Sesi Token secara real-time.
    """
    token_obj = get_object_or_404(EnrollmentToken, id=token_id)
    token_obj.is_active = not token_obj.is_active
    token_obj.save(update_fields=['is_active'])

    if request.htmx:
        return render(request, 'admin_panel/partials/token_row.html', {'token': token_obj})
    
    messages.success(request, f"Status token {token_obj.token} diubah menjadi {'Aktif' if token_obj.is_active else 'Nonaktif'}.")
    return redirect('admin_panel:token_list')


@user_passes_test(teacher_check, login_url='accounts:login')
def token_detail_view(request, token_id):
    """
    Melihat Daftar Siswa yang Terdaftar pada Token Sesi Tertentu.
    """
    token_obj = get_object_or_404(EnrollmentToken, id=token_id)
    enrollments = token_obj.user_enrollments.select_related('user').order_by('-enrolled_at')

    context = {
        'token': token_obj,
        'enrollments': enrollments,
        'active_nav': 'admin_tokens',
    }
    return render(request, 'admin_panel/token_detail.html', context)


@user_passes_test(teacher_check, login_url='accounts:login')
def submission_list_view(request):
    """
    Hub Penilaian Guru: Memeriksa dan menilai seluruh submisi LKPD & Refleksi siswa secara terpisah dan interaktif.
    """
    filter_status = request.GET.get('status', 'all')
    filter_modul = request.GET.get('modul', '')
    filter_tab = request.GET.get('tab', 'lkpd')

    all_submissions = UserSubmission.objects.select_related('user', 'modul', 'graded_by').order_by('-submitted_at')

    if filter_modul:
        all_submissions = all_submissions.filter(modul__slug=filter_modul)

    # Deduplikasi: Simpan submisi paling mutakhir per siswa per modul per tipe tugas
    unique_map = {}
    for s in all_submissions:
        key = f"{s.user_id}_{s.modul_id}_{s.submission_type}"
        if key not in unique_map:
            unique_map[key] = s

    deduped_submissions = list(unique_map.values())

    lkpd_submissions = [s for s in deduped_submissions if s.submission_type == 'lkpd']
    reflection_submissions = [s for s in deduped_submissions if s.submission_type == 'reflection']

    # Hitung Statistik
    total_lkpd = len(lkpd_submissions)
    pending_lkpd = sum(1 for s in lkpd_submissions if s.status != 'graded' or s.teacher_score is None)
    graded_lkpd = sum(1 for s in lkpd_submissions if s.status == 'graded' and s.teacher_score is not None)

    total_reflections = len(reflection_submissions)
    pending_reflections = sum(1 for s in reflection_submissions if s.status not in ['reviewed', 'graded'])
    reviewed_reflections = sum(1 for s in reflection_submissions if s.status in ['reviewed', 'graded'])

    # Serialisasi payload JSON form data agar aman diproses oleh Alpine.js modal
    for s in lkpd_submissions:
        fd = s.form_data or {}
        while isinstance(fd, str):
            try:
                fd = json.loads(fd)
            except Exception:
                break
        s.form_data = fd
        s.form_data_json = json.dumps(fd if isinstance(fd, dict) else {})
    for s in reflection_submissions:
        fd = s.form_data or {}
        while isinstance(fd, str):
            try:
                fd = json.loads(fd)
            except Exception:
                break
        s.form_data = fd
        s.form_data_json = json.dumps(fd if isinstance(fd, dict) else {})

    lkpd_data_list = []
    for s in lkpd_submissions:
        lkpd_data_list.append({
            'id': s.id,
            'studentName': s.user.display_name,
            'studentEmail': s.user.email,
            'studentClass': s.user.kelas or '10 RPL',
            'studentNis': s.user.nisn or '-',
            'moduleCode': s.modul.kode,
            'moduleTitle': s.modul.judul,
            'moduleSlug': s.modul.slug,
            'submittedAt': s.submitted_at.strftime("%d %b %Y, %H:%M") if s.submitted_at else '',
            'teacherScore': s.teacher_score,
            'teacherLevel': s.teacher_level or '',
            'teacherFeedback': s.teacher_feedback or '',
            'driveUrl': s.drive_url or '',
            'status': s.status,
            'formData': s.form_data if isinstance(s.form_data, dict) else {},
        })

    reflection_data_list = []
    for s in reflection_submissions:
        reflection_data_list.append({
            'id': s.id,
            'studentName': s.user.display_name,
            'studentEmail': s.user.email,
            'studentClass': s.user.kelas or '10 RPL',
            'studentNis': s.user.nisn or '-',
            'moduleCode': s.modul.kode,
            'moduleTitle': s.modul.judul,
            'moduleSlug': s.modul.slug,
            'submittedAt': s.submitted_at.strftime("%d %b %Y, %H:%M") if s.submitted_at else '',
            'teacherFeedback': s.teacher_feedback or '',
            'status': s.status,
            'formData': s.form_data if isinstance(s.form_data, dict) else {},
        })

    all_modules = Modul.objects.filter(is_published=True).order_by('urutan')
    classes = ['10 RPL 1', '10 RPL 2', '11 RPL 1', '11 RPL 2', '12 RPL 1', '12 RPL 2']
    kktp_levels = [
        ('Level 4 (Mahir & Mandiri ★★★)', 'Level 4 (Mahir & Mandiri ★★★) - Sangat Baik'),
        ('Level 3 (Mampu Membimbing ★★)', 'Level 3 (Mampu Membimbing ★★) - Baik'),
        ('Level 2 (Mencoba ★)', 'Level 2 (Mencoba ★) - Cukup (Target Minimal)'),
        ('Level 1 (Mulai Berkembang)', 'Level 1 (Mulai Berkembang) - Perlu Bimbingan'),
        ('Level 0 (Belum Berkembang)', 'Level 0 (Belum Berkembang) - Belum Tuntas'),
    ]

    context = {
        'lkpd_submissions': lkpd_submissions,
        'reflection_submissions': reflection_submissions,
        'lkpd_data_json': lkpd_data_list,
        'reflection_data_json': reflection_data_list,
        'total_lkpd': total_lkpd,
        'pending_lkpd': pending_lkpd,
        'graded_lkpd': graded_lkpd,
        'total_reflections': total_reflections,
        'pending_reflections': pending_reflections,
        'reviewed_reflections': reviewed_reflections,
        'all_modules': all_modules,
        'classes': classes,
        'kktp_levels': kktp_levels,
        'filter_status': filter_status,
        'filter_modul': filter_modul,
        'filter_tab': filter_tab,
        'active_nav': 'admin_submissions',
    }
    return render(request, 'admin_panel/submissions.html', context)


@user_passes_test(teacher_check, login_url='accounts:login')
@require_POST
def grade_submission_api_view(request):
    """
    API Endpoint: Menyimpan penilaian skor dan level KKTP LKPD secara instan (AJAX/Fetch).
    """
    try:
        data = json.loads(request.body.decode('utf-8'))
    except Exception:
        return JsonResponse({'error': 'Format payload tidak valid.'}, status=400)

    submission_id = data.get('submissionId') or data.get('submission_id')
    if not submission_id:
        return JsonResponse({'error': 'ID Submisi diperlukan.'}, status=400)

    submission = get_object_or_404(UserSubmission.objects.select_related('user', 'modul'), id=submission_id)

    raw_score = data.get('teacherScore')
    if raw_score is None:
        raw_score = data.get('teacher_score')

    try:
        score_val = int(raw_score)
        if score_val < 0 or score_val > 100:
            return JsonResponse({'error': 'Skor harus berada di antara 0 dan 100.'}, status=400)
    except (ValueError, TypeError):
        return JsonResponse({'error': 'Skor angka tidak valid.'}, status=400)

    teacher_level = data.get('teacherLevel') or data.get('teacher_level') or ''
    teacher_feedback = (data.get('teacherFeedback') or data.get('teacher_feedback') or '').strip()

    submission.teacher_score = score_val
    submission.teacher_level = teacher_level
    submission.teacher_feedback = teacher_feedback
    submission.status = 'graded'
    submission.graded_by = request.user
    submission.graded_at = timezone.now()
    submission.save()

    return JsonResponse({
        'success': True,
        'message': f'Nilai LKPD {submission.user.display_name} ({score_val}/100) berhasil disimpan!',
        'submission': {
            'id': submission.id,
            'teacherScore': submission.teacher_score,
            'teacherLevel': submission.teacher_level,
            'teacherFeedback': submission.teacher_feedback,
            'status': submission.status,
            'isPassed': submission.teacher_score >= 73,
        }
    })


@user_passes_test(teacher_check, login_url='accounts:login')
@require_POST
def review_reflection_api_view(request):
    """
    API Endpoint: Menandai Jurnal Refleksi siswa selesai ditinjau dan memberikan feedback kualitatif.
    """
    try:
        data = json.loads(request.body.decode('utf-8'))
    except Exception:
        return JsonResponse({'error': 'Format payload tidak valid.'}, status=400)

    submission_id = data.get('submissionId') or data.get('submission_id')
    if not submission_id:
        return JsonResponse({'error': 'ID Submisi diperlukan.'}, status=400)

    submission = get_object_or_404(UserSubmission.objects.select_related('user', 'modul'), id=submission_id)

    teacher_feedback = (data.get('teacherFeedback') or data.get('teacher_feedback') or '').strip()
    if not teacher_feedback:
        teacher_feedback = 'Telah dibaca dan diapresiasi oleh Guru Pengampu RPL.'

    submission.teacher_feedback = teacher_feedback
    submission.status = 'reviewed'
    submission.graded_by = request.user
    submission.graded_at = timezone.now()
    submission.save()

    return JsonResponse({
        'success': True,
        'message': f'Jurnal refleksi {submission.user.display_name} telah selesai ditinjau!',
        'submission': {
            'id': submission.id,
            'teacherFeedback': submission.teacher_feedback,
            'status': submission.status,
        }
    })


@user_passes_test(teacher_check, login_url='accounts:login')
def export_lkpd_excel_view(request):
    """
    Ekspor Rekapitulasi Penilaian LKPD Siswa ke format CSV (Excel Compatible UTF-8 BOM).
    """
    filter_modul = request.GET.get('modul', '')
    filter_class = request.GET.get('class', '')

    submissions = UserSubmission.objects.filter(submission_type='lkpd').select_related('user', 'modul', 'graded_by').order_by('modul__urutan', 'user__first_name')

    if filter_modul:
        submissions = submissions.filter(modul__slug=filter_modul)
    if filter_class and filter_class != 'all' and filter_class != 'Semua Kelas':
        submissions = submissions.filter(user__kelas=filter_class)

    response = HttpResponse(content_type='text/csv; charset=utf-8-sig')
    response['Content-Disposition'] = 'attachment; filename="Rekap_Nilai_LKPD_PPLG_RPL_SMKN1Rongga.csv"'

    writer = csv.writer(response)
    writer.writerow([
        'No',
        'Nama Peserta Didik',
        'NISN',
        'Kelas / Rombel',
        'Modul Pembelajaran',
        'Status Penilaian',
        'Level Capaian KKTP',
        'Nilai Skor (0-100)',
        'Status Ketuntasan (KKM 73)',
        'Tautan Evidence Google Drive',
        'Catatan & Feedback Guru',
        'Waktu Pengumpulan',
        'Guru Penilai'
    ])

    for idx, sub in enumerate(submissions, start=1):
        is_graded = sub.status == 'graded' and sub.teacher_score is not None
        is_passed = is_graded and sub.teacher_score >= 73
        status_kkm = 'TUNTAS (TERKUNCI)' if is_passed else ('REMEDIAL / BELUM TUNTAS' if is_graded else 'MENUNGGU PENILAIAN')
        status_label = 'Sudah Dinilai' if is_graded else 'Menunggu Penilaian'
        drive_link = sub.drive_url or (sub.form_data.get('driveUrl') if isinstance(sub.form_data, dict) else '-') or '-'

        writer.writerow([
            idx,
            sub.user.display_name,
            sub.user.nisn or '-',
            sub.user.kelas or '10 RPL',
            f"[{sub.modul.kode}] {sub.modul.judul}",
            status_label,
            sub.teacher_level or '-',
            sub.teacher_score if sub.teacher_score is not None else '-',
            status_kkm,
            drive_link,
            sub.teacher_feedback or '-',
            sub.submitted_at.strftime('%d/%m/%Y %H:%M') if sub.submitted_at else '-',
            sub.graded_by.display_name if sub.graded_by else '-'
        ])

    return response


@user_passes_test(teacher_check, login_url='accounts:login')
def export_reflections_excel_view(request):
    """
    Ekspor Rekapitulasi Jurnal Refleksi Siswa ke format CSV (Excel Compatible UTF-8 BOM).
    """
    filter_modul = request.GET.get('modul', '')
    filter_class = request.GET.get('class', '')

    submissions = UserSubmission.objects.filter(submission_type='reflection').select_related('user', 'modul', 'graded_by').order_by('modul__urutan', 'user__first_name')

    if filter_modul:
        submissions = submissions.filter(modul__slug=filter_modul)
    if filter_class and filter_class != 'all' and filter_class != 'Semua Kelas':
        submissions = submissions.filter(user__kelas=filter_class)

    response = HttpResponse(content_type='text/csv; charset=utf-8-sig')
    response['Content-Disposition'] = 'attachment; filename="Rekap_Jurnal_Refleksi_RPL_SMKN1Rongga.csv"'

    writer = csv.writer(response)
    writer.writerow([
        'No',
        'Nama Peserta Didik',
        'NISN',
        'Kelas / Rombel',
        'Modul Pembelajaran',
        '1. Hal Baru Dipelajari (Konsep RPL)',
        '2. Urgensi / Penerapan Portofolio',
        '3. Kendala & Solusi Teknis',
        '4. Komitmen Belajar',
        'Status Tinjauan',
        'Catatan Apresiasi Guru',
        'Waktu Pengumpulan',
        'Ditinjau Oleh'
    ])

    for idx, sub in enumerate(submissions, start=1):
        fd = sub.form_data if isinstance(sub.form_data, dict) else {}
        q1 = fd.get('q1') or fd.get('understanding') or '-'
        q2 = fd.get('q2') or '-'
        q3 = fd.get('q3') or fd.get('obstacle') or '-'
        q4 = fd.get('q4') or fd.get('action_plan') or '-'
        status_label = 'Ditinjau' if sub.status in ['reviewed', 'graded'] else 'Menunggu Tinjauan'

        writer.writerow([
            idx,
            sub.user.display_name,
            sub.user.nisn or '-',
            sub.user.kelas or '10 RPL',
            f"[{sub.modul.kode}] {sub.modul.judul}",
            q1,
            q2,
            q3,
            q4,
            status_label,
            sub.teacher_feedback or '-',
            sub.submitted_at.strftime('%d/%m/%Y %H:%M') if sub.submitted_at else '-',
            sub.graded_by.display_name if sub.graded_by else '-'
        ])

    return response


@user_passes_test(teacher_check, login_url='accounts:login')
def grade_submission_view(request, submission_id):
    """
    Form Penilaian Detail Submisi LKPD oleh Guru Pengampu (Fallback URL).
    """
    submission = get_object_or_404(UserSubmission.objects.select_related('user', 'modul'), id=submission_id)
    form = TeacherGradeForm(request.POST or None, instance=submission)

    if request.method == 'POST' and form.is_valid():
        sub = form.save(commit=False)
        sub.status = 'graded'
        sub.graded_by = request.user
        sub.graded_at = timezone.now()
        sub.save()

        messages.success(request, f"Penilaian untuk {submission.user.display_name} pada modul {submission.modul.kode} berhasil disimpan!")
        return redirect('admin_panel:submission_list')

    context = {
        'submission': submission,
        'form': form,
        'active_nav': 'admin_submissions',
    }
    return render(request, 'admin_panel/grade_submission.html', context)


@user_passes_test(teacher_check, login_url='accounts:login')
def tka_results_view(request):
    """
    Monitoring Hasil Tryout CBT TKA Siswa: Rekap skor, passing status, dan riwayat attempt.
    """
    filter_package = request.GET.get('package', '')
    attempts = TkaAttempt.objects.select_related('user', 'package').order_by('-completed_at')

    if filter_package:
        attempts = attempts.filter(package__slug=filter_package)

    packages = TkaPackage.objects.filter(is_published=True).order_by('urutan')

    context = {
        'attempts': attempts,
        'packages': packages,
        'filter_package': filter_package,
        'active_nav': 'admin_tka_results',
    }
    return render(request, 'admin_panel/tka_results.html', context)


@user_passes_test(teacher_check, login_url='accounts:login')
def literasi_list_view(request):
    """
    Hub Penilaian Laporan Rabu Literasi (RESIK) Siswa.
    """
    filter_status = request.GET.get('status', 'all')
    filter_week = request.GET.get('week', '')

    reports = LiterasiReport.objects.select_related('user').prefetch_related('peer_reviews').order_by('-report_date', '-created_at')

    if filter_status == 'pending':
        reports = reports.filter(status='submitted')
    elif filter_status == 'graded':
        reports = reports.filter(status='graded')

    if filter_week:
        reports = reports.filter(week_number=int(filter_week))

    context = {
        'reports': reports,
        'filter_status': filter_status,
        'filter_week': filter_week,
        'active_nav': 'admin_literasi',
    }
    return render(request, 'admin_panel/literasi_list.html', context)


@user_passes_test(teacher_check, login_url='accounts:login')
def literasi_grade_view(request, report_id):
    """
    Form Penilaian Laporan Literasi Siswa oleh Guru Pengampu.
    """
    report = get_object_or_404(LiterasiReport.objects.select_related('user').prefetch_related('peer_reviews', 'peer_reviews__reviewer'), id=report_id)
    form = TeacherGradeLiterasiForm(request.POST or None, instance=report)

    if request.method == 'POST' and form.is_valid():
        rep = form.save(commit=False)
        w_score = rep.writing_score or 0
        p_score = rep.presentation_score or 0
        rep.final_score = round((w_score + p_score) / 2, 1)
        rep.status = 'graded'
        rep.graded_by = request.user
        rep.graded_at = timezone.now()
        rep.save()

        messages.success(request, f"Penilaian Laporan Literasi {report.user.display_name} (Nilai: {rep.final_score}) berhasil disimpan!")
        return redirect('admin_panel:literasi_list')

    context = {
        'report': report,
        'form': form,
        'active_nav': 'admin_literasi',
    }
    return render(request, 'admin_panel/literasi_grade.html', context)


@user_passes_test(teacher_check, login_url='accounts:login')
@require_POST
def reset_student_password_api_view(request):
    """
    API Endpoint: Guru dapat mereset kata sandi akun siswa langsung dari konsol.
    """
    try:
        data = json.loads(request.body.decode('utf-8'))
    except Exception:
        return JsonResponse({'error': 'Format payload tidak valid.'}, status=400)

    target_user_id = data.get('targetUserId') or data.get('target_user_id')
    new_password = (data.get('newPassword') or data.get('new_password') or '').strip()

    if not target_user_id:
        return JsonResponse({'error': 'Target User ID wajib diisi.'}, status=400)

    if len(new_password) < 6:
        return JsonResponse({'error': 'Password baru minimal harus 6 karakter.'}, status=400)

    target_user = get_object_or_404(User, id=target_user_id)

    # Keamanan: Guru tidak boleh mereset sesama guru/superuser kecuali pemanggil adalah superuser
    if (target_user.is_guru or target_user.is_staff or target_user.is_superuser) and not request.user.is_superuser:
        return JsonResponse({'error': 'Hanya Super Admin yang dapat mereset akun Guru / Administrator.'}, status=403)

    target_user.set_password(new_password)
    target_user.save()

    return JsonResponse({
        'success': True,
        'message': f'Kata sandi akun "{target_user.display_name}" ({target_user.username}) berhasil direset!'
    })


@user_passes_test(teacher_check, login_url='accounts:login')
def token_report_api_view(request, token_id):
    """
    API Endpoint: Menyediakan data statistik performa & daftar peserta untuk modal rekap token.
    """
    token = get_object_or_404(EnrollmentToken.objects.select_related('created_by'), id=token_id)
    enrollments = token.user_enrollments.select_related('user').order_by('-enrolled_at')
    
    attempts = TkaAttempt.objects.filter(token=token).select_related('user', 'package').order_by('-completed_at')
    attempt_map = {}
    for a in attempts:
        if a.user_id not in attempt_map:
            attempt_map[a.user_id] = a

    students_data = []
    scores = []
    for e in enrollments:
        user = e.user
        att = attempt_map.get(user.id)
        score = att.score if att else None
        if score is not None:
            scores.append(score)
        students_data.append({
            'userId': user.id,
            'name': user.display_name,
            'email': user.email,
            'nisn': user.nisn or '-',
            'studentClass': user.kelas or token.target_class or '-',
            'enrolledAt': e.enrolled_at.strftime('%d/%m/%Y %H:%M') if e.enrolled_at else '-',
            'hasTakenExam': att is not None,
            'examScore': score,
            'correctAnswers': att.correct_answers if att else None,
            'totalQuestions': att.total_questions if att else None,
            'isPassed': score >= 73 if score is not None else False,
            'completedAt': att.completed_at.strftime('%d/%m/%Y %H:%M') if att and att.completed_at else '-'
        })

    total_enrolled = len(students_data)
    total_taken = len(scores)
    avg_score = round(sum(scores) / total_taken) if total_taken > 0 else 0
    pass_count = sum(1 for s in scores if s >= 73)
    pass_rate = round((pass_count / total_taken) * 100) if total_taken > 0 else 0

    return JsonResponse({
        'success': True,
        'token': {
            'id': token.id,
            'token': token.token,
            'title': token.title,
            'targetClass': token.target_class,
            'targetType': token.get_target_type_display(),
            'isActive': token.is_active,
            'creator': token.created_by.display_name if token.created_by else 'Guru Pengampu'
        },
        'stats': {
            'totalEnrolled': total_enrolled,
            'totalExamTaken': total_taken,
            'avgScore': avg_score,
            'passCount': pass_count,
            'passRate': pass_rate,
        },
        'students': students_data
    })


@user_passes_test(teacher_check, login_url='accounts:login')
def export_token_excel_view(request, token_id):
    """
    Ekspor Rekapitulasi Peserta Sesi Token ke format CSV (Excel Compatible UTF-8 BOM).
    """
    token = get_object_or_404(EnrollmentToken, id=token_id)
    enrollments = token.user_enrollments.select_related('user').order_by('user__first_name')
    attempts = TkaAttempt.objects.filter(token=token).select_related('user')
    attempt_map = {a.user_id: a for a in attempts}

    response = HttpResponse(content_type='text/csv; charset=utf-8-sig')
    response['Content-Disposition'] = f'attachment; filename="Rekap_Sesi_Token_{token.token}.csv"'

    writer = csv.writer(response)
    writer.writerow([
        'No',
        'Nama Peserta Didik',
        'NISN',
        'Kelas / Rombel',
        'Waktu Enrollment',
        'Status Ujian',
        'Nilai CBT TKA',
        'Ketuntasan (KKM 73)',
        'Waktu Selesai Ujian'
    ])

    for idx, e in enumerate(enrollments, start=1):
        u = e.user
        att = attempt_map.get(u.id)
        score = att.score if att else None
        status_ujian = 'Sudah Ujian' if att else 'Belum Ujian'
        status_kkm = 'TUNTAS' if (score is not None and score >= 73) else ('BELUM TUNTAS' if score is not None else '-')
        completed_str = att.completed_at.strftime('%d/%m/%Y %H:%M') if att and att.completed_at else '-'
        enrolled_str = e.enrolled_at.strftime('%d/%m/%Y %H:%M') if e.enrolled_at else '-'

        writer.writerow([
            idx,
            u.display_name,
            u.nisn or '-',
            u.kelas or token.target_class,
            enrolled_str,
            status_ujian,
            score if score is not None else '-',
            status_kkm,
            completed_str
        ])

    return response


@user_passes_test(teacher_check, login_url='accounts:login')
@require_POST
def token_delete_view(request, token_id):
    """
    Menghapus Token Sesi KBM.
    """
    token = get_object_or_404(EnrollmentToken, id=token_id)
    token_title = token.title
    token_code = token.token
    token.delete()
    messages.success(request, f'Token sesi "{token_title}" ({token_code}) berhasil dihapus.')
    return redirect('admin_panel:dashboard')


@user_passes_test(teacher_check, login_url='accounts:login')
@require_POST
def grade_literasi_api_view(request):
    """
    API Endpoint: Menyimpan penilaian 9 rubrik RESIK secara in-place (AJAX/Fetch).
    """
    try:
        data = json.loads(request.body.decode('utf-8'))
    except Exception:
        return JsonResponse({'error': 'Format payload tidak valid.'}, status=400)

    report_id = data.get('reportId') or data.get('report_id')
    if not report_id:
        return JsonResponse({'error': 'ID Laporan diperlukan.'}, status=400)

    report = get_object_or_404(LiterasiReport.objects.select_related('user'), id=report_id)

    try:
        w1 = int(data.get('w1', 3))
        w2 = int(data.get('w2', 3))
        w3 = int(data.get('w3', 3))
        w4 = int(data.get('w4', 3))
        p1 = int(data.get('p1', 3))
        p2 = int(data.get('p2', 3))
        p3 = int(data.get('p3', 3))
        p4 = int(data.get('p4', 3))
        p5 = int(data.get('p5', 3))
    except (ValueError, TypeError):
        return JsonResponse({'error': 'Nilai aspek rubrik harus berupa angka bulat 1-4.'}, status=400)

    total_writing = min(16, max(4, w1 + w2 + w3 + w4))
    total_presentation = min(20, max(5, p1 + p2 + p3 + p4 + p5))
    final_score = min(100.0, max(0.0, round(((total_writing + total_presentation) / 36) * 100, 1)))

    teacher_feedback = (data.get('teacherFeedback') or data.get('teacher_feedback') or '').strip()

    report.writing_score = total_writing
    report.presentation_score = total_presentation
    report.final_score = final_score
    report.teacher_feedback = teacher_feedback
    report.status = 'graded'
    report.graded_by = request.user
    report.graded_at = timezone.now()
    report.save()

    return JsonResponse({
        'success': True,
        'message': f'Penilaian RESIK {report.user.display_name} ({final_score}/100) berhasil disimpan!',
        'report': {
            'id': report.id,
            'writingScore': report.writing_score,
            'presentationScore': report.presentation_score,
            'finalScore': report.final_score,
            'teacherFeedback': report.teacher_feedback,
            'status': report.status,
            'isPassed': report.final_score >= 75
        }
    })


@user_passes_test(teacher_check, login_url='accounts:login')
def export_literasi_excel_view(request):
    """
    Ekspor Rekapitulasi Rabu Literasi RESIK ke format CSV (UTF-8 BOM).
    """
    filter_class = request.GET.get('class', '')
    filter_week = request.GET.get('week', '')

    reports = LiterasiReport.objects.select_related('user', 'graded_by').order_by('week_number', 'user__first_name')
    if filter_class and filter_class != 'all' and filter_class != 'Semua Kelas':
        reports = reports.filter(user__kelas=filter_class)
    if filter_week:
        try:
            reports = reports.filter(week_number=int(filter_week))
        except ValueError:
            pass

    response = HttpResponse(content_type='text/csv; charset=utf-8-sig')
    response['Content-Disposition'] = 'attachment; filename="Rekap_Rabu_Literasi_RESIK_RPL_SMKN1Rongga.csv"'

    writer = csv.writer(response)
    writer.writerow([
        'No',
        'Nama Peserta Didik',
        'NISN',
        'Kelas / Rombel',
        'Minggu Ke-',
        'Tanggal Literasi',
        'Judul Buku / Sumber',
        'Penulis',
        'Penerbit',
        'Halaman',
        'Jumlah Kata',
        'Nilai Menulis (Max 16)',
        'Nilai Presentasi (Max 20)',
        'Nilai Akhir RESIK',
        'Status',
        'Catatan Evaluasi Guru',
        'Guru Penilai'
    ])

    for idx, rep in enumerate(reports, start=1):
        writer.writerow([
            idx,
            rep.user.display_name,
            rep.user.nisn or '-',
            rep.user.kelas or '10 RPL',
            rep.week_number,
            rep.report_date.strftime('%d/%m/%Y') if rep.report_date else '-',
            rep.book_title,
            rep.author,
            rep.publisher or '-',
            rep.page_count or '-',
            rep.word_count,
            rep.writing_score if rep.writing_score is not None else '-',
            rep.presentation_score if rep.presentation_score is not None else '-',
            rep.final_score if rep.final_score is not None else '-',
            rep.get_status_display(),
            rep.teacher_feedback or '-',
            rep.graded_by.display_name if rep.graded_by else '-'
        ])

    return response


@user_passes_test(teacher_check, login_url='accounts:login')
def export_tka_excel_view(request):
    """
    Ekspor Rekapitulasi Hasil Ujian CBT TKA ke CSV (UTF-8 BOM).
    """
    filter_class = request.GET.get('class', '')
    filter_package = request.GET.get('package', '')

    attempts = TkaAttempt.objects.select_related('user', 'package', 'token').order_by('-completed_at')
    if filter_class and filter_class != 'all' and filter_class != 'Semua Kelas':
        attempts = attempts.filter(user__kelas=filter_class)
    if filter_package:
        attempts = attempts.filter(package__slug=filter_package)

    response = HttpResponse(content_type='text/csv; charset=utf-8-sig')
    response['Content-Disposition'] = 'attachment; filename="Rekap_Nilai_CBT_TKA_PPLG_SMKN1Rongga.csv"'

    writer = csv.writer(response)
    writer.writerow([
        'No',
        'Nama Peserta Didik',
        'NISN',
        'Kelas / Rombel',
        'Paket Soal TKA',
        'Percobaan Ke-',
        'Skor Nilai (0-100)',
        'Ketuntasan (KKM 73)',
        'Jawaban Benar',
        'Total Soal',
        'Waktu Pengerjaan (Detik)',
        'Waktu Selesai'
    ])

    for idx, att in enumerate(attempts, start=1):
        status_kkm = 'KOMPETEN (LULUS)' if att.score >= 73 else 'BELUM KOMPETEN'
        writer.writerow([
            idx,
            att.user.display_name,
            att.user.nisn or '-',
            att.user.kelas or '-',
            att.package.judul,
            att.attempt_number,
            att.score,
            status_kkm,
            att.correct_answers,
            att.total_questions,
            att.time_spent_seconds,
            att.completed_at.strftime('%d/%m/%Y %H:%M') if att.completed_at else '-'
        ])

    return response
