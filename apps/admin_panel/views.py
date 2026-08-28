from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import user_passes_test
from django.contrib import messages
from django.views.decorators.http import require_POST
from django.utils import timezone
from django.http import HttpResponse

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
    Hub Penilaian Guru: Memeriksa dan menilai seluruh submisi LKPD & Refleksi siswa.
    """
    filter_status = request.GET.get('status', 'all')
    filter_modul = request.GET.get('modul', '')

    submissions = UserSubmission.objects.select_related('user', 'modul').order_by('-submitted_at')

    if filter_status == 'pending':
        submissions = submissions.filter(status='submitted')
    elif filter_status == 'graded':
        submissions = submissions.filter(status='graded')

    if filter_modul:
        submissions = submissions.filter(modul__slug=filter_modul)

    all_modules = Modul.objects.filter(is_published=True).order_by('urutan')

    context = {
        'submissions': submissions,
        'all_modules': all_modules,
        'filter_status': filter_status,
        'filter_modul': filter_modul,
        'active_nav': 'admin_submissions',
    }
    return render(request, 'admin_panel/submissions.html', context)


@user_passes_test(teacher_check, login_url='accounts:login')
def grade_submission_view(request, submission_id):
    """
    Form Penilaian Detail Submisi LKPD oleh Guru Pengampu.
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
