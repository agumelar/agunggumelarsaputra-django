from django.conf import settings
from django.db import models
from django.db.models import Q


class Sesi(models.Model):
    MODE_CHOICES = [("cat", "CAT"), ("belajar", "Belajar")]
    STATUS_CHOICES = [("berjalan", "Berjalan"), ("selesai", "Selesai")]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="sesi_cpns",
    )
    mode = models.CharField(max_length=10, choices=MODE_CHOICES)
    skema = models.ForeignKey(
        "cpns.SkemaUjian",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="sesi",
    )
    paket = models.ForeignKey(
        "cpns.PaketBelajar",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="sesi",
    )
    filter_subtopik = models.JSONField(null=True, blank=True)
    status = models.CharField(
        max_length=10, choices=STATUS_CHOICES, default="berjalan"
    )
    dimulai_pada = models.DateTimeField(auto_now_add=True)
    batas_waktu = models.DateTimeField(null=True, blank=True)
    selesai_pada = models.DateTimeField(null=True, blank=True)
    skor_bagian = models.JSONField(default=list, blank=True)
    total = models.IntegerField(default=0)
    lulus = models.BooleanField(default=False)

    class Meta:
        ordering = ["-dimulai_pada"]
        constraints = [
            models.UniqueConstraint(
                fields=["user"],
                condition=Q(mode="cat", status="berjalan"),
                name="satu_cat_berjalan_per_user",
            )
        ]

    def __str__(self):
        return f"Sesi {self.mode} #{self.pk} ({self.status})"

    def sisa_detik(self, now):
        if self.batas_waktu is None:
            return 0
        return max(0, int((self.batas_waktu - now).total_seconds()))


class SesiSoal(models.Model):
    sesi = models.ForeignKey(Sesi, on_delete=models.CASCADE, related_name="butir")
    soal = models.ForeignKey(
        "cpns.Soal", on_delete=models.PROTECT, related_name="di_sesi"
    )
    nomor = models.PositiveIntegerField()
    urutan_opsi = models.CharField(max_length=5)
    jawaban = models.CharField(max_length=1, blank=True)
    ragu = models.BooleanField(default=False)
    dijawab_pada = models.DateTimeField(null=True, blank=True)
    poin = models.IntegerField(null=True, blank=True)

    class Meta:
        ordering = ["nomor"]
        unique_together = [("sesi", "nomor")]

    def __str__(self):
        return f"Butir {self.nomor} sesi {self.sesi_id}"
