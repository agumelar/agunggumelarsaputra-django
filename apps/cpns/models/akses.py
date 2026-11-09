from django.conf import settings
from django.db import models


class AksesPeserta(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="akses_cpns",
    )
    premium_sampai = models.DateTimeField(null=True, blank=True)
    via_google = models.BooleanField(default=False)

    def __str__(self):
        return f"Akses {self.user_id}"


class LaporanSoal(models.Model):
    ALASAN_CHOICES = [
        ("kunci_salah", "Kunci salah"),
        ("ambigu", "Soal ambigu"),
        ("typo", "Salah ketik"),
        ("lainnya", "Lainnya"),
    ]
    STATUS_CHOICES = [("baru", "Baru"), ("selesai", "Selesai")]

    soal = models.ForeignKey(
        "cpns.Soal", on_delete=models.CASCADE, related_name="laporan"
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="laporan_soal_cpns",
    )
    alasan = models.CharField(max_length=20, choices=ALASAN_CHOICES)
    catatan = models.TextField(blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="baru")
    dibuat_pada = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-dibuat_pada"]
        constraints = [
            models.UniqueConstraint(
                fields=["soal", "user"],
                condition=models.Q(status="baru"),
                name="satu_laporan_baru_per_user",
            )
        ]

    def __str__(self):
        return f"Laporan {self.alasan} soal {self.soal_id}"
