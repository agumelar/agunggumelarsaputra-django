from django.db import models
from django.conf import settings


class Modul(models.Model):
    """
    16 Modul Orientasi PPLG / Konsentrasi Keahlian RPL SMKN 1 Rongga.
    """
    kode = models.CharField(max_length=20, unique=True, verbose_name='Kode Modul (e.g. OR-01)')
    judul = models.CharField(max_length=255, verbose_name='Judul Modul')
    slug = models.SlugField(max_length=255, unique=True)
    kategori = models.CharField(max_length=100, default='Orientasi PPLG', verbose_name='Kategori / Elemen')
    level = models.CharField(max_length=50, default='Pemula', verbose_name='Tingkat Kesulitan')
    durasi = models.CharField(max_length=50, default='2 JP (90 Menit)', verbose_name='Estimasi Durasi')
    deskripsi = models.TextField(verbose_name='Deskripsi Singkat')
    content_materi = models.TextField(blank=True, verbose_name='Konten Materi (Markdown / HTML)')
    teacher_tip = models.TextField(blank=True, null=True, verbose_name='Tips & Catatan Pak Agung')
    urutan = models.PositiveIntegerField(default=1, verbose_name='Urutan')
    xp_materi = models.PositiveIntegerField(default=10, verbose_name='Reward XP Baca Materi')
    xp_lkpd = models.PositiveIntegerField(default=25, verbose_name='Reward XP Submisi LKPD')
    xp_reflection = models.PositiveIntegerField(default=15, verbose_name='Reward XP Jurnal Refleksi')
    is_published = models.BooleanField(default=True, verbose_name='Status Publikasi')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Modul Pembelajaran'
        verbose_name_plural = 'Daftar Modul Pembelajaran'
        ordering = ['urutan']

    @property
    def total_xp(self):
        return self.xp_materi + self.xp_lkpd + self.xp_reflection

    def __str__(self):
        return f"[{self.kode}] {self.judul}"


class UserSubmission(models.Model):
    """
    Submisi tugas LKPD, Jurnal Refleksi, dan Self-Assessment KKTP oleh siswa.
    Mirroring user_submissions dari legacy Neon DB.
    """
    SUBMISSION_TYPE_CHOICES = [
        ('lkpd', 'Lembar Kerja Peserta Didik (LKPD)'),
        ('reflection', 'Jurnal Refleksi Pembelajaran'),
        ('kktp_self_assessment', 'Self-Assessment KKTP'),
    ]

    LEVEL_CHOICES = [
        ('Level 4 (Mahir & Mandiri ★★★)', 'Level 4 (Mahir & Mandiri ★★★) - Sangat Baik'),
        ('Level 3 (Mampu Membimbing ★★)', 'Level 3 (Mampu Membimbing ★★) - Baik'),
        ('Level 2 (Mencoba ★)', 'Level 2 (Mencoba ★) - Cukup (Target Minimal)'),
        ('Level 1 (Mulai Berkembang)', 'Level 1 (Mulai Berkembang) - Perlu Bimbingan'),
        ('Level 0 (Belum Berkembang)', 'Level 0 (Belum Berkembang) - Belum Tuntas'),
        ('Level 4', 'Level 4 - Mahir / Standar Industri'),
        ('Level 3', 'Level 3 - Mandiri'),
        ('Level 2', 'Level 2 - Mencoba (Target Minimal Sem. 1)'),
        ('Level 1', 'Level 1 - Mengenal'),
        ('Level 0', 'Level 0 - Belum Terlihat'),
    ]

    STATUS_CHOICES = [
        ('submitted', 'Terkirim / Menunggu Penilaian'),
        ('graded', 'Sudah Dinilai Guru'),
        ('reviewed', 'Telah Ditinjau Guru'),
        ('verified', 'Terverifikasi'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='submissions',
        verbose_name='Siswa'
    )
    modul = models.ForeignKey(
        Modul,
        on_delete=models.CASCADE,
        related_name='submissions',
        verbose_name='Modul'
    )
    token = models.ForeignKey(
        'admin_panel.EnrollmentToken',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='submissions',
        verbose_name='Sesi Token (Opsional)'
    )
    submission_type = models.CharField(
        max_length=30,
        choices=SUBMISSION_TYPE_CHOICES,
        verbose_name='Tipe Submisi'
    )
    form_data = models.JSONField(
        default=dict,
        blank=True,
        verbose_name='Payload Jawaban Form'
    )
    drive_url = models.URLField(
        max_length=500,
        blank=True,
        null=True,
        verbose_name='Link Folder Google Drive Evidence'
    )
    score = models.IntegerField(
        null=True,
        blank=True,
        verbose_name='Skor Otomatis / Poin'
    )
    teacher_score = models.IntegerField(
        null=True,
        blank=True,
        verbose_name='Nilai Guru (0-100)'
    )
    teacher_level = models.CharField(
        max_length=60,
        choices=LEVEL_CHOICES,
        blank=True,
        null=True,
        verbose_name='Level Capaian KKTP'
    )
    teacher_feedback = models.TextField(
        blank=True,
        null=True,
        verbose_name='Catatan Evaluasi Guru'
    )
    graded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='graded_submissions',
        verbose_name='Dinilai Oleh'
    )
    graded_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Waktu Penilaian'
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='submitted',
        verbose_name='Status Penilaian'
    )
    submitted_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Waktu Submisi'
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Waktu Diperbarui'
    )

    class Meta:
        verbose_name = 'Submisi Siswa (LKPD/Refleksi)'
        verbose_name_plural = 'Daftar Submisi Siswa'
        unique_together = ('user', 'modul', 'submission_type')
        ordering = ['-submitted_at']

    def __str__(self):
        return f"{self.user.display_name} - {self.modul.kode} ({self.get_submission_type_display()})"


class UserProgress(models.Model):
    """
    Pencatatan progres penyelesaian modul materi oleh siswa.
    Mirroring user_progress dari legacy Neon DB.
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='lesson_progress',
        verbose_name='Siswa'
    )
    modul = models.ForeignKey(
        Modul,
        on_delete=models.CASCADE,
        related_name='user_progress',
        verbose_name='Modul'
    )
    token = models.ForeignKey(
        'admin_panel.EnrollmentToken',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='progress_records',
        verbose_name='Sesi Token'
    )
    completed_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Waktu Ditandai Selesai'
    )

    class Meta:
        verbose_name = 'Progres Modul Siswa'
        verbose_name_plural = 'Daftar Progres Modul Siswa'
        unique_together = ('user', 'modul')
        ordering = ['-completed_at']

    def __str__(self):
        return f"{self.user.display_name} selesai {self.modul.kode}"
