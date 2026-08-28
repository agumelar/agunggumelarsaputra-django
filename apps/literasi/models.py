from django.db import models
from django.conf import settings
from django.utils import timezone


class LiterasiReport(models.Model):
    """
    Laporan kegiatan literasi mingguan (Rabu Literasi - RESIK).
    Mirroring literasiReports dari legacy Neon DB.
    """
    SOURCE_TYPE_CHOICES = [
        ('Buku Fisik', 'Buku Fisik'),
        ('E-Book / PDF', 'E-Book / PDF'),
        ('Artikel / Jurnal Teknis', 'Artikel / Jurnal Teknis'),
        ('Dokumentasi Resmi', 'Dokumentasi Resmi / Standard'),
    ]

    STATUS_CHOICES = [
        ('submitted', 'Menunggu Review Guru'),
        ('graded', 'Sudah Dinilai Guru'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='literasi_reports',
        verbose_name='Siswa'
    )
    token = models.ForeignKey(
        'admin_panel.EnrollmentToken',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='literasi_reports',
        verbose_name='Sesi Token (Opsional)'
    )
    week_number = models.PositiveIntegerField(default=1, verbose_name='Minggu Ke-')
    report_date = models.DateField(default=timezone.now, verbose_name='Tanggal Literasi')

    # Identitas Buku / Sumber Bacaan
    book_title = models.CharField(max_length=255, verbose_name='Judul Buku / Sumber Bacaan')
    author = models.CharField(max_length=255, verbose_name='Penulis / Pengarang')
    publisher = models.CharField(max_length=255, blank=True, verbose_name='Penerbit')
    city = models.CharField(max_length=100, blank=True, verbose_name='Kota Terbit')
    year = models.CharField(max_length=10, blank=True, verbose_name='Tahun Terbit')
    page_count = models.CharField(max_length=50, blank=True, verbose_name='Jumlah / Rentang Halaman')
    edition = models.CharField(max_length=50, blank=True, verbose_name='Cetakan / Edisi')
    source_type = models.CharField(max_length=50, default='Buku Fisik', choices=SOURCE_TYPE_CHOICES, verbose_name='Jenis Sumber Bacaan')

    # Konten RESIK
    summary = models.TextField(verbose_name='Rangkuman RESIK (Minimal 100 Kata)')
    moral_message = models.TextField(verbose_name='Pesan Moral / Relevansi Software Engineering')
    word_count = models.PositiveIntegerField(default=0, verbose_name='Jumlah Kata Rangkuman')
    self_checklist = models.JSONField(default=dict, blank=True, verbose_name='Checklist Mandiri Siswa')

    # Penilaian Guru
    writing_score = models.PositiveIntegerField(null=True, blank=True, verbose_name='Nilai Penulisan & Struktur (0-100)')
    presentation_score = models.PositiveIntegerField(null=True, blank=True, verbose_name='Nilai Pemahaman & Presentasi (0-100)')
    final_score = models.FloatField(null=True, blank=True, verbose_name='Nilai Akhir')
    teacher_feedback = models.TextField(blank=True, null=True, verbose_name='Catatan Evaluasi Guru')
    graded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='graded_literasi_reports',
        verbose_name='Dinilai Oleh'
    )
    graded_at = models.DateTimeField(null=True, blank=True, verbose_name='Waktu Penilaian')
    status = models.CharField(max_length=20, default='submitted', choices=STATUS_CHOICES, verbose_name='Status Penilaian')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Laporan Rabu Literasi (RESIK)'
        verbose_name_plural = 'Daftar Laporan Literasi RESIK'
        ordering = ['-report_date', '-created_at']

    @property
    def average_rating(self):
        reviews = self.peer_reviews.all()
        if not reviews.exists():
            return None
        total = sum(r.rating for r in reviews)
        return round(total / len(reviews), 1)

    @property
    def reviews_count(self):
        return self.peer_reviews.count()

    def __str__(self):
        return f"{self.user.display_name} - Minggu {self.week_number} ({self.book_title})"


class LiterasiPeerReview(models.Model):
    """
    Peer review dan rating ulasan literasi antarsiswa.
    Mirroring literasiPeerReviews dari legacy Neon DB.
    """
    report = models.ForeignKey(
        LiterasiReport,
        on_delete=models.CASCADE,
        related_name='peer_reviews',
        verbose_name='Laporan Literasi'
    )
    reviewer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='written_peer_reviews',
        verbose_name='Reviewer (Teman Sekelas)'
    )
    rating = models.PositiveIntegerField(
        default=5,
        verbose_name='Rating Bintang (1 - 5)'
    )
    comment = models.TextField(
        verbose_name='Ulasan / Apresiasi Feedback'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Peer Review Literasi'
        verbose_name_plural = 'Daftar Peer Review Literasi'
        unique_together = ('report', 'reviewer')
        ordering = ['-created_at']

    def __str__(self):
        return f"Review oleh {self.reviewer.display_name} untuk {self.report.book_title} (★{self.rating})"
