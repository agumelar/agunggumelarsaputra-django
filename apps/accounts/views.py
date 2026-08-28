from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate, get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.views.decorators.http import require_POST
from django.http import HttpResponse

from .forms import StudentRegistrationForm, UserLoginForm, UserProfileForm, ClaimTokenForm
from apps.admin_panel.models import EnrollmentToken, UserEnrollment
from apps.gamification.models import XPHistory

User = get_user_model()


def check_token_view(request):
    """
    HTMX Endpoint: Validasi live token sesi yang diketik siswa di form pendaftaran.
    """
    token_code = request.POST.get('token', '').strip().upper()
    if not token_code:
        return HttpResponse('')

    try:
        token_obj = EnrollmentToken.objects.get(token__iexact=token_code)
        if not token_obj.is_active:
            status = 'inactive'
            message = 'Sesi token ini telah dinonaktifkan oleh guru.'
        elif token_obj.expires_at and token_obj.expires_at < timezone.now():
            status = 'expired'
            message = 'Masa berlaku token ini sudah kadaluarsa.'
        elif token_obj.is_full:
            status = 'full'
            message = f'Kuota peserta sesi ini sudah penuh ({token_obj.max_uses} siswa).'
        else:
            status = 'valid'
            message = f'Token Valid: {token_obj.title} ({token_obj.target_class})'
    except EnrollmentToken.DoesNotExist:
        token_obj = None
        status = 'not_found'
        message = 'Kode token tidak ditemukan. Pastikan kode benar.'

    context = {
        'status': status,
        'message': message,
        'token_obj': token_obj,
    }
    return render(request, 'accounts/partials/token_feedback.html', context)


def register_view(request):
    """
    Pendaftaran Siswa Baru dengan Validasi Token Sesi & Reward +50 XP.
    """
    if request.user.is_authenticated:
        return redirect('core:home')

    # Prefill token jika ada query param ?token=...
    initial_token = request.GET.get('token', '')
    form = StudentRegistrationForm(request.POST or None, initial={'token': initial_token})

    if request.method == 'POST' and form.is_valid():
        token_obj = form.cleaned_data['token']
        name = form.cleaned_data['name'].strip()
        email = form.cleaned_data['email'].strip().lower()
        password = form.cleaned_data['password']

        # Pisahkan nama depan dan belakang
        name_parts = name.split(' ', 1)
        first_name = name_parts[0]
        last_name = name_parts[1] if len(name_parts) > 1 else ''

        # Gunakan email prefix atau random string untuk username unik
        base_username = email.split('@')[0]
        username = base_username
        counter = 1
        while User.objects.filter(username=username).exists():
            username = f"{base_username}{counter}"
            counter += 1

        # Buat User baru (Role: Siswa)
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
            role=User.ROLE_SISWA,
            kelas=token_obj.target_class if token_obj.target_class != 'Semua Kelas' else '',
            xp=50,  # Welcome Bonus
            level=1,
            streak_count=1,
            last_active_date=timezone.now().date(),
        )

        # Buat relasi UserEnrollment
        UserEnrollment.objects.create(user=user, token=token_obj)

        # Catat Riwayat XP
        XPHistory.objects.create(
            user=user,
            amount=50,
            category='modul',
            description='Bonus Pendaftaran & Aktivasi Token Sesi'
        )

        # Otomatis Login
        login(request, user)
        messages.success(request, f"Selamat datang di RPL Learning Hub, {user.display_name}! Bonus +50 XP telah ditambahkan.")
        return redirect('core:home')

    return render(request, 'accounts/register.html', {'form': form})


def login_view(request):
    """
    Login Universal (Email, NISN, atau Username + Password).
    """
    if request.user.is_authenticated:
        return redirect('admin_panel:dashboard' if request.user.is_guru else 'core:home')

    form = UserLoginForm(request.POST or None)

    if request.method == 'POST' and form.is_valid():
        identifier = form.cleaned_data['identifier'].strip()
        password = form.cleaned_data['password']

        # Cari user berdasarkan email, username, nisn, atau nip
        matched_user = None
        if '@' in identifier:
            matched_user = User.objects.filter(email__iexact=identifier).first()
        else:
            matched_user = User.objects.filter(username__iexact=identifier).first()
            if not matched_user:
                matched_user = User.objects.filter(nisn__iexact=identifier).first()
            if not matched_user:
                matched_user = User.objects.filter(nip__iexact=identifier).first()

        if matched_user:
            user = authenticate(request, username=matched_user.username, password=password)
            if user is not None:
                login(request, user)
                
                # Update Daily Streak & Last Active Date
                today = timezone.now().date()
                if user.last_active_date != today:
                    if user.last_active_date and (today - user.last_active_date).days == 1:
                        user.streak_count += 1
                    elif not user.last_active_date or (today - user.last_active_date).days > 1:
                        user.streak_count = 1
                    user.last_active_date = today
                    user.save(update_fields=['streak_count', 'last_active_date'])

                messages.success(request, f"Selamat datang kembali, {user.display_name}!")
                
                next_url = request.GET.get('next')
                if next_url:
                    return redirect(next_url)
                return redirect('admin_panel:dashboard' if user.is_guru else 'core:home')
            else:
                messages.error(request, "Kata sandi yang Anda masukkan salah.")
        else:
            messages.error(request, "Akun dengan identifier tersebut tidak ditemukan.")

    return render(request, 'accounts/login.html', {'form': form})


def logout_view(request):
    """
    Logout pengguna.
    """
    logout(request)
    messages.info(request, "Anda telah berhasil keluar dari akun.")
    return redirect('core:home')


@login_required
def profile_view(request):
    """
    Halaman Profil Siswa / Guru, Riwayat Enrollment, dan Pengaturan Akun.
    """
    user = request.user
    profile_form = UserProfileForm(request.POST or None, request.FILES or None, instance=user)
    claim_form = ClaimTokenForm()

    if request.method == 'POST' and 'update_profile' in request.POST:
        if profile_form.is_valid():
            profile_form.save()
            messages.success(request, "Profil Anda berhasil diperbarui.")
            return redirect('accounts:profile')

    user_enrollments = user.enrollments.select_related('token').order_by('-enrolled_at')
    xp_logs = user.xp_history.all()[:10]

    context = {
        'user': user,
        'profile_form': profile_form,
        'claim_form': claim_form,
        'enrollments': user_enrollments,
        'xp_logs': xp_logs,
        'active_nav': 'profile',
    }
    return render(request, 'accounts/profile.html', context)


@login_required
@require_POST
def claim_token_view(request):
    """
    Endpoint untuk siswa yang sudah login untuk klaim/enroll ke token sesi baru.
    """
    form = ClaimTokenForm(request.POST)
    if form.is_valid():
        token_code = form.cleaned_data['token_code'].strip().upper()
        try:
            token_obj = EnrollmentToken.objects.get(token__iexact=token_code)
            
            if not token_obj.is_active:
                messages.error(request, "Sesi untuk token ini sudah ditutup/dinonaktifkan oleh guru.")
            elif token_obj.expires_at and token_obj.expires_at < timezone.now():
                messages.error(request, "Masa berlaku token ini sudah kadaluarsa.")
            elif token_obj.is_full and not UserEnrollment.objects.filter(user=request.user, token=token_obj).exists():
                messages.error(request, f"Kuota kelas untuk sesi ini sudah penuh ({token_obj.max_uses} siswa).")
            else:
                enrollment, created = UserEnrollment.objects.get_or_create(user=request.user, token=token_obj)
                if created:
                    messages.success(request, f"Berhasil bergabung ke sesi: '{token_obj.title}' ({token_obj.target_class})!")
                else:
                    messages.info(request, f"Anda sudah terdaftar di sesi '{token_obj.title}'.")
        except EnrollmentToken.DoesNotExist:
            messages.error(request, "Kode token tidak valid atau tidak ditemukan.")
    else:
        messages.error(request, "Format token tidak valid.")

    return redirect('accounts:profile')
