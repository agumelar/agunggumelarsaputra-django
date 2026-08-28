from django.db import models
from django.conf import settings


class TkaPackage(models.Model):
    """
    10 Paket Drilling & Simulator CBT TKA PPLG / Rekayasa Perangkat Lunak.
    """
    kode = models.CharField(max_length=20, unique=True, verbose_name='Kode Paket (e.g. TKA-01)')
    judul = models.CharField(max_length=255, verbose_name='Judul Paket Drilling')
    slug = models.SlugField(max_length=255, unique=True)
    kategori = models.CharField(max_length=100, default='Drilling TKA PPLG', verbose_name='Kategori Soal')
    level = models.CharField(max_length=50, default='Lanjutan', verbose_name='Tingkat Kesulitan')
    durasi_menit = models.PositiveIntegerField(default=60, verbose_name='Durasi Ujian (Menit)')
    passing_grade = models.PositiveIntegerField(default=75, verbose_name='KKM / Passing Grade')
    deskripsi = models.TextField(blank=True, verbose_name='Petunjuk & Cakupan Materi')
    content_materi = models.TextField(blank=True, verbose_name='Bedah Materi & Konsep Inti')
    teacher_tip = models.TextField(blank=True, null=True, verbose_name='Tips & Catatan Guru')
    urutan = models.PositiveIntegerField(default=1, verbose_name='Urutan')
    xp_base = models.PositiveIntegerField(default=25, verbose_name='Base Reward XP')
    is_published = models.BooleanField(default=True, verbose_name='Status Publikasi')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Paket Soal TKA'
        verbose_name_plural = 'Daftar Paket Soal TKA'
        ordering = ['urutan']

    @property
    def total_questions_count(self):
        return self.questions.count()

    def __str__(self):
        return f"[{self.kode}] {self.judul}"


class TkaQuestion(models.Model):
    """
    Butir Soal Pilihan Ganda A - E untuk CBT TKA PPLG.
    """
    ANSWER_CHOICES = [
        ('A', 'A'),
        ('B', 'B'),
        ('C', 'C'),
        ('D', 'D'),
        ('E', 'E'),
    ]

    package = models.ForeignKey(
        TkaPackage,
        on_delete=models.CASCADE,
        related_name='questions',
        verbose_name='Paket Soal'
    )
    question_text = models.TextField(verbose_name='Teks Soal / Pertanyaan')
    option_a = models.TextField(verbose_name='Pilihan A')
    option_b = models.TextField(verbose_name='Pilihan B')
    option_c = models.TextField(verbose_name='Pilihan C')
    option_d = models.TextField(verbose_name='Pilihan D')
    option_e = models.TextField(verbose_name='Pilihan E')
    correct_answer = models.CharField(
        max_length=1,
        choices=ANSWER_CHOICES,
        verbose_name='Kunci Jawaban Benar'
    )
    explanation = models.TextField(
        blank=True,
        verbose_name='Pembahasan Soal & Kunci'
    )
    category = models.CharField(
        max_length=100,
        blank=True,
        verbose_name='Subtopik / Topik'
    )
    urutan = models.PositiveIntegerField(default=1, verbose_name='Nomor Soal')

    class Meta:
        verbose_name = 'Butir Soal TKA'
        verbose_name_plural = 'Daftar Butir Soal TKA'
        ordering = ['urutan']
        unique_together = ('package', 'urutan')

    def __str__(self):
        return f"{self.package.kode} - Soal No. {self.urutan}"


class TkaAttempt(models.Model):
    """
    Riwayat pengerjaan simulasi CBT TKA oleh siswa beserta hasil skor dan review jawaban.
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='tka_attempts',
        verbose_name='Siswa'
    )
    package = models.ForeignKey(
        TkaPackage,
        on_delete=models.CASCADE,
        related_name='attempts',
        verbose_name='Paket Soal'
    )
    token = models.ForeignKey(
        'admin_panel.EnrollmentToken',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='tka_attempts',
        verbose_name='Sesi Token (Opsional)'
    )
    attempt_number = models.PositiveIntegerField(default=1, verbose_name='Percobaan Ke-')
    score = models.FloatField(default=0.0, verbose_name='Skor Akhir (0 - 100)')
    total_questions = models.PositiveIntegerField(default=0, verbose_name='Total Soal')
    correct_answers = models.PositiveIntegerField(default=0, verbose_name='Jawaban Benar')
    wrong_answers = models.PositiveIntegerField(default=0, verbose_name='Jawaban Salah')
    user_answers = models.JSONField(
        default=dict,
        blank=True,
        verbose_name='Pilihan Jawaban Siswa {question_id: answer_choice}'
    )
    xp_earned = models.PositiveIntegerField(default=0, verbose_name='Reward XP Didapat')
    is_passed = models.BooleanField(default=False, verbose_name='Status Lulus (Skor >= KKM)')
    time_spent_seconds = models.PositiveIntegerField(default=0, verbose_name='Waktu Pengerjaan (Detik)')
    completed_at = models.DateTimeField(auto_now_add=True, verbose_name='Waktu Selesai')

    class Meta:
        verbose_name = 'Riwayat Ujian CBT TKA'
        verbose_name_plural = 'Daftar Riwayat Ujian CBT TKA'
        ordering = ['-completed_at']

    def __str__(self):
        return f"{self.user.display_name} - {self.package.kode} (Skor: {self.score})"
