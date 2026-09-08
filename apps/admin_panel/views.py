from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import user_passes_test
from django.contrib import messages
from django.views.decorators.http import require_POST
from django.utils import timezone
from django.http import HttpResponse, JsonResponse
import csv
import json

from .models import EnrollmentToken, UserEnrollment
from .forms import EnrollmentTokenForm, TeacherGradeForm, TeacherGradeLiterasiForm
from apps.pembelajaran.models import Modul, UserSubmission
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
    Dashboard Guru Pengampu RPL: Monitoring KBM, Token Rombel, dan Aktivitas Siswa.
    """
    total_tokens = EnrollmentToken.objects.count()
    active_tokens = EnrollmentToken.objects.filter(is_active=True).count()
    total_students = User.objects.filter(role=User.ROLE_SISWA).count()
    total_enrollments = UserEnrollment.objects.count()
    pending_submissions = UserSubmission.objects.filter(status='submitted', submission_type='lkpd').count()
    total_tka_attempts = TkaAttempt.objects.count()
    pending_literasi = LiterasiReport.objects.filter(status='submitted').count()

    recent_tokens = EnrollmentToken.objects.prefetch_related('user_enrollments').order_by('-created_at')[:5]
    recent_submissions = UserSubmission.objects.select_related('user', 'modul').order_by('-submitted_at')[:6]
    recent_attempts = TkaAttempt.objects.select_related('user', 'package').order_by('-completed_at')[:6]

    context = {
        'total_tokens': total_tokens,
        'active_tokens': active_tokens,
        'total_students': total_students,
        'total_enrollments': total_enrollments,
        'pending_submissions': pending_submissions,
        'total_tka_attempts': total_tka_attempts,
        'pending_literasi': pending_literasi,
        'recent_tokens': recent_tokens,
        'recent_submissions': recent_submissions,
        'recent_attempts': recent_attempts,
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
        s.form_data_json = json.dumps(s.form_data or {})
    for s in reflection_submissions:
        s.form_data_json = json.dumps(s.form_data or {})

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
