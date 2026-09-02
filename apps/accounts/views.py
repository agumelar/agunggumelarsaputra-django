import secrets
import json
import urllib.parse
import urllib.request
import urllib.error

from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.conf import settings
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

    initial_token = request.GET.get('token', '')
    form = StudentRegistrationForm(request.POST or None, initial={'token': initial_token})

    if request.method == 'POST' and form.is_valid():
        token_obj = form.cleaned_data['token']
        name = form.cleaned_data['name'].strip()
        email = form.cleaned_data['email'].strip().lower()
        password = form.cleaned_data['password']

        name_parts = name.split(' ', 1)
        first_name = name_parts[0]
        last_name = name_parts[1] if len(name_parts) > 1 else ''

        base_username = email.split('@')[0]
        username = base_username
        counter = 1
        while User.objects.filter(username=username).exists():
            username = f"{base_username}{counter}"
            counter += 1

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

        UserEnrollment.objects.create(user=user, token=token_obj)

        XPHistory.objects.create(
            user=user,
            amount=50,
            category='modul',
            description='Bonus Pendaftaran & Aktivasi Token Sesi'
        )

        login(request, user, backend='django.contrib.auth.backends.ModelBackend')
        messages.success(request, f"Selamat datang di RPL Learning Hub, {user.display_name}! Bonus +50 XP telah ditambahkan.")
        return redirect('core:home')

    return render(request, 'accounts/register.html', {'form': form})


def login_view(request):
    """
    Login Universal (Email, NISN, NIP, atau Username + Password).
    """
    if request.user.is_authenticated:
        return redirect('admin_panel:dashboard' if request.user.is_guru else 'core:home')

    form = UserLoginForm(request.POST or None)

    if request.method == 'POST' and form.is_valid():
        identifier = form.cleaned_data['identifier'].strip()
        password = form.cleaned_data['password']

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
                form.add_error(None, "Kombinasi kata sandi tidak cocok. Silakan periksa kembali kata sandi Anda.")
        else:
            form.add_error(None, f"Akun dengan identifier '{identifier}' tidak ditemukan. Pastikan Anda telah mendaftar.")

    return render(request, 'accounts/login.html', {'form': form})


def google_oauth_login_view(request):
    """
    Inisialisasi Google OAuth 2.0: Mengarahkan pengguna ke Google Consent Screen.
    """
    client_id = getattr(settings, 'GOOGLE_CLIENT_ID', '')
    client_secret = getattr(settings, 'GOOGLE_CLIENT_SECRET', '')

    if not client_id or not client_secret:
        messages.warning(
            request,
            "Google OAuth belum dikonfigurasi. Variabel GOOGLE_CLIENT_ID & GOOGLE_CLIENT_SECRET belum diisi di file .env."
        )
        return redirect('accounts:login')

    state = secrets.token_urlsafe(32)
    request.session['google_oauth_state'] = state

    redirect_uri = request.build_absolute_uri(reverse('accounts:google_callback'))
    params = {
        'client_id': client_id,
        'redirect_uri': redirect_uri,
        'response_type': 'code',
        'scope': 'openid profile email',
        'state': state,
        'access_type': 'online',
        'prompt': 'select_account',
    }
    google_auth_url = f"https://accounts.google.com/o/oauth2/v2/auth?{urllib.parse.urlencode(params)}"
    return redirect(google_auth_url)


def google_oauth_callback_view(request):
    """
    Callback Google OAuth 2.0: Menerima authorization code, mengambil data profil, dan login/registrasi otomatis.
    """
    client_id = getattr(settings, 'GOOGLE_CLIENT_ID', '')
    client_secret = getattr(settings, 'GOOGLE_CLIENT_SECRET', '')

    if not client_id or not client_secret:
        messages.error(request, "Google OAuth belum dikonfigurasi di server.")
        return redirect('accounts:login')

    code = request.GET.get('code')
    state = request.GET.get('state')
    stored_state = request.session.get('google_oauth_state')

    if not code or not state or not stored_state or state != stored_state:
        messages.error(request, "Verifikasi sesi OAuth gagal atau kadaluarsa. Silakan ulangi proses masuk.")
        return redirect('accounts:login')

    # Hapus state dari session setelah diverifikasi
    request.session.pop('google_oauth_state', None)

    try:
        # 1. Exchange Code for Access Token
        redirect_uri = request.build_absolute_uri(reverse('accounts:google_callback'))
        token_data = urllib.parse.urlencode({
            'code': code,
            'client_id': client_id,
            'client_secret': client_secret,
            'redirect_uri': redirect_uri,
            'grant_type': 'authorization_code',
        }).encode('utf-8')

        token_req = urllib.request.Request(
            'https://oauth2.googleapis.com/token',
            data=token_data,
            headers={'Content-Type': 'application/x-www-form-urlencoded'}
        )
        with urllib.request.urlopen(token_req, timeout=10) as token_res:
            token_json = json.loads(token_res.read().decode('utf-8'))

        access_token = token_json.get('access_token')
        if not access_token:
            messages.error(request, "Gagal mendapatkan token akses dari Google.")
            return redirect('accounts:login')

        # 2. Get User Info from Google OpenID Endpoint
        userinfo_req = urllib.request.Request(
            'https://openidconnect.googleapis.com/v1/userinfo',
            headers={'Authorization': f"Bearer {access_token}"}
        )
        with urllib.request.urlopen(userinfo_req, timeout=10) as userinfo_res:
            google_user = json.loads(userinfo_res.read().decode('utf-8'))

        email = google_user.get('email', '').strip().lower()
        if not email:
            messages.error(request, "Gagal mendapatkan alamat email dari akun Google.")
            return redirect('accounts:login')

        google_name = google_user.get('name', 'Siswa RPL')
        name_parts = google_name.split(' ', 1)
        first_name = name_parts[0]
        last_name = name_parts[1] if len(name_parts) > 1 else ''

        # 3. Check or Create User
        user = User.objects.filter(email__iexact=email).first()

        # Deteksi otomatis apakah akun guru / admin
        is_teacher_email = email in ['agung@smkn1rongga.sch.id', 'agunggumelar@smkn1rongga.sch.id'] or 'agung' in email

        if not user:
            # Generate username unik dari email
            base_username = email.split('@')[0]
            username = base_username
            counter = 1
            while User.objects.filter(username=username).exists():
                username = f"{base_username}{counter}"
                counter += 1

            assigned_role = User.ROLE_GURU if is_teacher_email else User.ROLE_SISWA
            initial_xp = 0 if assigned_role == User.ROLE_GURU else 50

            user = User.objects.create_user(
                username=username,
                email=email,
                password=secrets.token_urlsafe(16),
                first_name=first_name,
                last_name=last_name,
                role=assigned_role,
                xp=initial_xp,
                level=1,
                streak_count=1,
                last_active_date=timezone.now().date(),
            )

            if assigned_role == User.ROLE_SISWA:
                XPHistory.objects.create(
                    user=user,
                    amount=50,
                    category='modul',
                    description='Bonus Akun Baru (Google OAuth)'
                )

            messages.success(request, f"Selamat datang di RPL Learning Hub, {user.display_name}! Akun Google Anda telah terhubung.")
        else:
            # Update role jika guru
            if is_teacher_email and not user.is_guru:
                user.role = User.ROLE_GURU
                user.is_staff = True
                user.save(update_fields=['role', 'is_staff'])

            # Update streak
            today = timezone.now().date()
            if user.last_active_date != today:
                if user.last_active_date and (today - user.last_active_date).days == 1:
                    user.streak_count += 1
                elif not user.last_active_date or (today - user.last_active_date).days > 1:
                    user.streak_count = 1
                user.last_active_date = today
                user.save(update_fields=['streak_count', 'last_active_date'])

            messages.success(request, f"Selamat datang kembali, {user.display_name}!")

        # 4. Login User
        login(request, user, backend='django.contrib.auth.backends.ModelBackend')
        return redirect('admin_panel:dashboard' if user.is_guru else 'core:home')

    except Exception as err:
        messages.error(request, f"Gagal masuk dengan Google: {str(err)}")
        return redirect('accounts:login')


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
