from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import user_passes_test
from django.contrib import messages
from django.views.decorators.http import require_POST
from django.http import HttpResponse

from .models import EnrollmentToken, UserEnrollment
from .forms import EnrollmentTokenForm
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

    recent_tokens = EnrollmentToken.objects.prefetch_related('user_enrollments').order_by('-created_at')[:5]
    recent_students = User.objects.filter(role=User.ROLE_SISWA).order_by('-date_joined')[:5]

    context = {
        'total_tokens': total_tokens,
        'active_tokens': active_tokens,
        'total_students': total_students,
        'total_enrollments': total_enrollments,
        'recent_tokens': recent_tokens,
        'recent_students': recent_students,
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
