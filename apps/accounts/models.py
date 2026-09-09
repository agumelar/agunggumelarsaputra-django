from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """
    Custom User Model untuk Personal Website & Vocational Learning Hub RPL SMKN 1 Rongga.
    Mendukung dua tipe pengguna utama: Guru Pengampu RPL dan Siswa RPL.
    """
    ROLE_GURU = 'guru'
    ROLE_SISWA = 'siswa'

    ROLE_CHOICES = [
        (ROLE_GURU, 'Guru Pengampu RPL'),
        (ROLE_SISWA, 'Siswa RPL'),
    ]

    KELAS_CHOICES = [
        ('10 RPL 1', '10 RPL 1'),
        ('10 RPL 2', '10 RPL 2'),
        ('10 RPL 3', '10 RPL 3'),
        ('10 RPL 4', '10 RPL 4'),
        ('11 RPL 1', '11 RPL 1'),
        ('11 RPL 2', '11 RPL 2'),
        ('11 RPL 3', '11 RPL 3'),
        ('11 RPL 4', '11 RPL 4'),
        ('12 RPL 1', '12 RPL 1'),
        ('12 RPL 2', '12 RPL 2'),
        ('12 RPL 3', '12 RPL 3'),
        ('12 RPL 4', '12 RPL 4'),
        ('Kelas Uji Coba', 'Kelas Uji Coba (Sandbox)'),
    ]

    # Email dibuat unik untuk kompatibilitas autentikasi & legacy Neon DB
    email = models.EmailField(
        blank=True,
        null=True,
        unique=True,
        verbose_name='Alamat Email'
    )
    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default=ROLE_SISWA,
        verbose_name='Peran / Tipe Akun'
    )
    nisn = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        unique=True,
        verbose_name='NISN (Nomor Induk Siswa Nasional)',
        help_text='Khusus siswa untuk integrasi asesmen & sertifikat'
    )
    nip = models.CharField(
        max_length=30,
        blank=True,
        null=True,
        verbose_name='NIP (Nomor Induk Pegawai)',
        help_text='Khusus guru pengampu'
    )
    kelas = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name='Kelas / Rombel',
        help_text='Contoh: X PPLG 1, XI RPL 1, XII RPL 2'
    )
    avatar = models.ImageField(
        upload_to='avatars/',
        blank=True,
        null=True,
        verbose_name='Foto Profil'
    )
    avatar_url = models.TextField(
        blank=True,
        null=True,
        verbose_name='URL Foto Profil / External Avatar'
    )
    bio = models.TextField(
        blank=True,
        null=True,
        verbose_name='Bio / Deskripsi Singkat'
    )
    github_username = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name='Username GitHub'
    )
    xp = models.PositiveIntegerField(
        default=0,
        verbose_name='Total XP Gamifikasi'
    )
    level = models.PositiveIntegerField(
        default=1,
        verbose_name='Tingkat / Level'
    )
    streak_count = models.PositiveIntegerField(
        default=0,
        verbose_name='Daily Streak Hari'
    )
    last_active_date = models.DateField(
        blank=True,
        null=True,
        verbose_name='Tanggal Terakhir Aktif'
    )

    class Meta:
        verbose_name = 'Pengguna'
        verbose_name_plural = 'Daftar Pengguna'

    @property
    def is_guru(self):
        return self.role == self.ROLE_GURU or self.is_superuser

    @property
    def is_siswa(self):
        return self.role == self.ROLE_SISWA

    @property
    def is_profile_complete(self):
        """
        Mengecek apakah profil siswa sudah lengkap (memiliki kelas dan foto profil aktif).
        Pengguna dengan peran Guru atau Superuser selalu dianggap lengkap.
        """
        if not self.is_siswa:
            return True
        has_class = bool(self.kelas and self.kelas.strip())
        has_avatar = bool(self.avatar or (self.avatar_url and self.avatar_url.strip() and 'dicebear' not in self.avatar_url))
        return has_class and has_avatar

    @property
    def display_name(self):
        if self.first_name or self.last_name:
            return f"{self.first_name} {self.last_name}".strip()
        return self.username

    @property
    def avatar_display(self):
        """Mengembalikan URL foto profil aktif (file upload lokal atau external/Google URL)."""
        if self.avatar:
            return self.avatar.url
        if self.avatar_url:
            return self.avatar_url
        return None

    @property
    def level_title(self):
        """Menghitung gelar keahlian gamifikasi berdasarkan XP / Level."""
        if self.xp >= 1000:
            return "Code Master"
        elif self.xp >= 600:
            return "PPLG Specialist"
        elif self.xp >= 300:
            return "Logic Architect"
        elif self.xp >= 100:
            return "Junior Developer"
        return "Apprentice Coder"

    def recalculate_level(self):
        """Update level berdasarkan perolehan XP."""
        if self.xp >= 1000:
            self.level = 5
        elif self.xp >= 600:
            self.level = 4
        elif self.xp >= 300:
            self.level = 3
        elif self.xp >= 100:
            self.level = 2
        else:
            self.level = 1

    def __str__(self):
        return f"{self.display_name} ({self.get_role_display()})"
