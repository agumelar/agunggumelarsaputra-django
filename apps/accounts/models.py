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
    def display_name(self):
        if self.first_name or self.last_name:
            return f"{self.first_name} {self.last_name}".strip()
        return self.username

    def __str__(self):
        return f"{self.display_name} ({self.get_role_display()})"
