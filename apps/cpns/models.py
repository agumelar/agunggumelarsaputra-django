from django.db import models
from django.conf import settings


class CpnsPackage(models.Model):
    """
    Paket Drilling & Simulator CAT BKN untuk SKD dan SKB Guru.
    """
    EXAM_TYPE_CHOICES = [
        ('SKD', 'Seleksi Kompetensi Dasar (SKD)'),
        ('SKB', 'Seleksi Kompetensi Bidang (SKB)'),
    ]

    CATEGORY_CHOICES = [
        ('SIMULASI_LENGKAP', 'Simulasi Lengkap SKD BKN (110 Soal)'),
        ('SKB_GURU', 'SKB Guru & Tenaga Pendidik'),
        ('TWK', 'Drilling Khusus TWK'),
        ('TIU', 'Drilling Khusus TIU'),
        ('TKP', 'Drilling Khusus TKP'),
    ]

    kode = models.CharField(max_length=30, unique=True, verbose_name='Kode Paket (e.g. SKD-BKN-01)')
    judul = models.CharField(max_length=255, verbose_name='Judul Paket Ujian')
    slug = models.SlugField(max_length=255, unique=True)
    tipe_ujian = models.CharField(max_length=10, choices=EXAM_TYPE_CHOICES, default='SKD', verbose_name='Tipe Seleksi')
    kategori = models.CharField(max_length=50, choices=CATEGORY_CHOICES, default='SIMULASI_LENGKAP', verbose_name='Kategori Ujian')
    durasi_menit = models.PositiveIntegerField(default=100, verbose_name='Durasi Ujian (Menit)')
    
    # Passing Grade / Ambang Batas Resmi BKN
    passing_grade_twk = models.PositiveIntegerField(default=65, verbose_name='Ambang Batas TWK')
    passing_grade_tiu = models.PositiveIntegerField(default=80, verbose_name='Ambang Batas TIU')
    passing_grade_tkp = models.PositiveIntegerField(default=166, verbose_name='Ambang Batas TKP')
    passing_grade_skb = models.PositiveIntegerField(default=70, verbose_name='Ambang Batas SKB')

    deskripsi = models.TextField(blank=True, verbose_name='Deskripsi & Cakupan Materi')
    urutan = models.PositiveIntegerField(default=1, verbose_name='Urutan Tampil')
    xp_base = models.PositiveIntegerField(default=35, verbose_name='Base Reward XP')
    is_published = models.BooleanField(default=True, verbose_name='Status Publikasi')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Paket Soal CPNS'
        verbose_name_plural = 'Daftar Paket Soal CPNS'
        ordering = ['urutan']

    @property
    def total_questions_count(self):
        return self.questions.count()

    def __str__(self):
        return f"[{self.kode}] {self.judul}"


class CpnsQuestion(models.Model):
    """
    Butir Soal CPNS (TWK, TIU, TKP, SKB Guru) dengan Pembahasan 3 Tingkat (Konsep, Pengecoh, Tips Cepat).
    """
    SUBTEST_CHOICES = [
        ('TWK', 'Tes Wawasan Kebangsaan'),
        ('TIU', 'Tes Inteligensi Umum'),
        ('TKP', 'Tes Karakteristik Pribadi'),
        ('SKB_GURU', 'SKB Guru & Tenaga Pendidik'),
    ]

    ANSWER_CHOICES = [
        ('A', 'A'),
        ('B', 'B'),
        ('C', 'C'),
        ('D', 'D'),
        ('E', 'E'),
    ]

    package = models.ForeignKey(
        CpnsPackage,
        on_delete=models.CASCADE,
        related_name='questions',
        verbose_name='Paket Soal'
    )
    subtes = models.CharField(max_length=20, choices=SUBTEST_CHOICES, default='TWK', verbose_name='Subtes')
    subtopik = models.CharField(max_length=100, blank=True, verbose_name='Subtopik / Pokok Bahasan')
    urutan = models.PositiveIntegerField(default=1, verbose_name='Nomor Soal')
    pertanyaan = models.TextField(verbose_name='Narasi Pertanyaan / Soal')
    opsi_a = models.TextField(verbose_name='Pilihan A')
    opsi_b = models.TextField(verbose_name='Pilihan B')
    opsi_c = models.TextField(verbose_name='Pilihan C')
    opsi_d = models.TextField(verbose_name='Pilihan D')
    opsi_e = models.TextField(verbose_name='Pilihan E')
    kunci_jawaban = models.CharField(max_length=1, choices=ANSWER_CHOICES, default='A', verbose_name='Kunci Jawaban')
    
    # Skala bobot nilai 1 - 5 khusus TKP (e.g. {"A": 5, "B": 4, "C": 3, "D": 2, "E": 1})
    bobot_tkp = models.JSONField(
        null=True,
        blank=True,
        verbose_name='Bobot Nilai TKP (1 - 5)'
    )

    # Pembahasan 3 Tingkat ("Konsep Tuntas")
    bedah_konsep = models.TextField(blank=True, verbose_name='Bedah Konsep & Landasan Teori')
    alasan_pengecoh = models.TextField(blank=True, verbose_name='Analisis Opsi Pengecoh')
    tips_cepat = models.TextField(blank=True, verbose_name='Tips Cepat & Pola Kata Kunci')

    class Meta:
        verbose_name = 'Butir Soal CPNS'
        verbose_name_plural = 'Daftar Butir Soal CPNS'
        ordering = ['urutan']
        unique_together = ('package', 'urutan')

    def __str__(self):
        return f"{self.package.kode} - No. {self.urutan} [{self.subtes}]"


class CpnsAttempt(models.Model):
    """
    Riwayat Sesi Ujian / Drilling Peserta Beserta Akumulasi Skor dan Status Kelulusan Passing Grade.
    """
    MODE_CHOICES = [
        ('SIMULASI_CAT', 'Simulasi CAT Resmi (100 Menit)'),
        ('DRILLING_BEBAS', 'Drilling Fleksibel Mandiri'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='cpns_attempts',
        verbose_name='Peserta'
    )
    session_key = models.CharField(max_length=64, blank=True, verbose_name='ID Sesi Tamu')
    package = models.ForeignKey(
        CpnsPackage,
        on_delete=models.CASCADE,
        related_name='attempts',
        verbose_name='Paket Soal'
    )
    mode = models.CharField(max_length=20, choices=MODE_CHOICES, default='SIMULASI_CAT', verbose_name='Mode Ujian')

    # Skor Rinci Per Subtes
    skor_twk = models.PositiveIntegerField(default=0, verbose_name='Skor TWK')
    skor_tiu = models.PositiveIntegerField(default=0, verbose_name='Skor TIU')
    skor_tkp = models.PositiveIntegerField(default=0, verbose_name='Skor TKP')
    skor_skb = models.PositiveIntegerField(default=0, verbose_name='Skor SKB')
    total_skor = models.PositiveIntegerField(default=0, verbose_name='Total Skor Akhir')

    # Status Ambang Batas Kelulusan Multi-Threshold BKN
    lulus_twk = models.BooleanField(default=False, verbose_name='Lolos PG TWK')
    lulus_tiu = models.BooleanField(default=False, verbose_name='Lolos PG TIU')
    lulus_tkp = models.BooleanField(default=False, verbose_name='Lolos PG TKP')
    status_lulus = models.BooleanField(default=False, verbose_name='Status Lulus Passing Grade')

    jawaban_peserta = models.JSONField(
        default=dict,
        blank=True,
        verbose_name='Jawaban Peserta {question_id: selected_key}'
    )
    waktu_detik = models.PositiveIntegerField(default=0, verbose_name='Waktu Pengerjaan (Detik)')
    completed_at = models.DateTimeField(auto_now_add=True, verbose_name='Waktu Selesai')

    class Meta:
        verbose_name = 'Riwayat Ujian CPNS'
        verbose_name_plural = 'Daftar Riwayat Ujian CPNS'
        ordering = ['-completed_at']

    def __str__(self):
        nama = self.user.display_name if self.user else f"Guest ({self.session_key[:8]})"
        return f"{nama} - {self.package.kode} (Total Skor: {self.total_skor})"

    @classmethod
    def evaluate_and_create(cls, user, package, mode, answers, time_spent_seconds, session_key=''):
        """
        Kalkulator Skor Otomatis CAT BKN:
        - TWK & TIU: Benar = 5, Salah/Kosong = 0.
        - TKP: Gradasi 1 - 5 berdasarkan bobot_tkp per opsi.
        - SKB Guru: Benar = 5, Salah = 0.
        - Evaluasi ambang batas multi-subtes (TWK >= PG_TWK AND TIU >= PG_TIU AND TKP >= PG_TKP).
        """
        questions = package.questions.all()
        skor_twk = 0
        skor_tiu = 0
        skor_tkp = 0
        skor_skb = 0

        for q in questions:
            q_id_str = str(q.id)
            selected = answers.get(q_id_str, '').upper()

            if q.subtes == 'TWK':
                if selected == q.kunci_jawaban:
                    skor_twk += 5
            elif q.subtes == 'TIU':
                if selected == q.kunci_jawaban:
                    skor_tiu += 5
            elif q.subtes == 'TKP':
                if q.bobot_tkp and isinstance(q.bobot_tkp, dict) and selected in q.bobot_tkp:
                    skor_tkp += int(q.bobot_tkp[selected])
                elif selected == q.kunci_jawaban:
                    skor_tkp += 5
            elif q.subtes == 'SKB_GURU':
                if selected == q.kunci_jawaban:
                    skor_skb += 5

        if package.tipe_ujian == 'SKD':
            total_skor = skor_twk + skor_tiu + skor_tkp
            lulus_twk = skor_twk >= package.passing_grade_twk
            lulus_tiu = skor_tiu >= package.passing_grade_tiu
            lulus_tkp = skor_tkp >= package.passing_grade_tkp
            status_lulus = lulus_twk and lulus_tiu and lulus_tkp
        else:
            total_skor = skor_skb
            lulus_twk = False
            lulus_tiu = False
            lulus_tkp = False
            status_lulus = skor_skb >= package.passing_grade_skb

        attempt = cls.objects.create(
            user=user if getattr(user, 'is_authenticated', False) else None,
            session_key=session_key if not getattr(user, 'is_authenticated', False) else '',
            package=package,
            mode=mode,
            skor_twk=skor_twk,
            skor_tiu=skor_tiu,
            skor_tkp=skor_tkp,
            skor_skb=skor_skb,
            total_skor=total_skor,
            lulus_twk=lulus_twk,
            lulus_tiu=lulus_tiu,
            lulus_tkp=lulus_tkp,
            status_lulus=status_lulus,
            jawaban_peserta=answers,
            waktu_detik=time_spent_seconds
        )
        return attempt
