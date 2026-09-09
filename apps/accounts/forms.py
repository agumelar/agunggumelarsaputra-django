from django import forms
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.utils import timezone
from apps.admin_panel.models import EnrollmentToken, UserEnrollment

User = get_user_model()


class StudentRegistrationForm(forms.Form):
    """
    Form Pendaftaran Siswa Baru dengan Validasi Token Sesi / Rombel.
    """
    token = forms.CharField(
        max_length=32,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'm3-input font-mono uppercase tracking-wider',
            'placeholder': 'Contoh: RPL-7K9A',
            'hx-post': '/accounts/api/check-token/',
            'hx-trigger': 'keyup changed delay:400ms',
            'hx-target': '#token-feedback',
            'autocomplete': 'off',
        })
    )
    name = forms.CharField(
        max_length=150,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'm3-input',
            'placeholder': 'Masukkan nama lengkap siswa...'
        })
    )
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'm3-input font-mono',
            'placeholder': 'nama@smkn1rongga.sch.id'
        })
    )
    password = forms.CharField(
        min_length=6,
        required=True,
        widget=forms.PasswordInput(attrs={
            'class': 'm3-input font-mono',
            'placeholder': 'Minimal 6 karakter...'
        })
    )
    password_confirm = forms.CharField(
        min_length=6,
        required=True,
        widget=forms.PasswordInput(attrs={
            'class': 'm3-input font-mono',
            'placeholder': 'Ulangi kata sandi...'
        })
    )

    def clean_email(self):
        email = self.cleaned_data.get('email', '').strip().lower()
        if User.objects.filter(email__iexact=email).exists():
            raise ValidationError("Alamat email ini sudah terdaftar. Silakan gunakan email lain atau masuk.")
        return email

    def clean_token(self):
        token_code = self.cleaned_data.get('token', '').strip().upper()
        try:
            token_obj = EnrollmentToken.objects.get(token__iexact=token_code)
        except EnrollmentToken.DoesNotExist:
            raise ValidationError("Kode token tidak ditemukan. Pastikan kode yang Anda masukkan benar.")

        if not token_obj.is_active:
            raise ValidationError("Sesi untuk token ini telah dinonaktifkan atau ditutup oleh guru.")

        if token_obj.expires_at and token_obj.expires_at < timezone.now():
            raise ValidationError("Masa berlaku token ini sudah kadaluarsa.")

        if token_obj.is_full:
            raise ValidationError(f"Kuota peserta untuk sesi ini sudah penuh (Maksimal {token_obj.max_uses} siswa).")

        return token_obj

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        password_confirm = cleaned_data.get('password_confirm')

        if password and password_confirm and password != password_confirm:
            self.add_error('password_confirm', "Konfirmasi kata sandi tidak cocok.")

        return cleaned_data


class UserLoginForm(forms.Form):
    """
    Form Login Universal: Mendukung Email, NISN, atau Username.
    """
    identifier = forms.CharField(
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'm3-input',
            'placeholder': 'Email, NISN, atau Username...',
            'autofocus': 'true',
        })
    )
    password = forms.CharField(
        required=True,
        widget=forms.PasswordInput(attrs={
            'class': 'm3-input font-mono',
            'placeholder': 'Masukkan kata sandi...',
        })
    )


class UserProfileForm(forms.ModelForm):
    """
    Form Update Profil Pengguna (Siswa / Guru).
    """
    kelas = forms.ChoiceField(
        choices=[('', '-- Pilih Kelas / Rombel --')] + User.KELAS_CHOICES,
        required=False,
        widget=forms.Select(attrs={
            'class': 'm3-input font-mono text-sm',
            'id': 'kelas-select',
        })
    )

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'kelas', 'bio', 'github_username', 'avatar']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'm3-input', 'placeholder': 'Nama depan'}),
            'last_name': forms.TextInput(attrs={'class': 'm3-input', 'placeholder': 'Nama belakang'}),
            'bio': forms.Textarea(attrs={'class': 'm3-input', 'rows': 3, 'placeholder': 'Deskripsi singkat tentang Anda...'}),
            'github_username': forms.TextInput(attrs={'class': 'm3-input font-mono', 'placeholder': 'Username GitHub tanpa @'}),
            'avatar': forms.FileInput(attrs={'class': 'hidden', 'id': 'avatar-input', 'accept': 'image/jpeg,image/png,image/webp,image/jpg'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and getattr(self.instance, 'is_siswa', False):
            self.fields['kelas'].required = True


class ClaimTokenForm(forms.Form):
    """
    Form Siswa untuk Enroll ke Token Sesi Tambahan dari Dashboard/Profil.
    """
    token_code = forms.CharField(
        max_length=32,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'm3-input font-mono uppercase tracking-wider text-center',
            'placeholder': 'Contoh: RPL-7K9A',
            'autocomplete': 'off',
        })
    )
