from django.db import models
from django.db.models import Q

from apps.cpns import validasi


def _pilihan(nilai):
    return [(n, n) for n in nilai]


CARA_NILAI = ("benar_salah", "bobot_opsi")


class SkemaUjian(models.Model):
    kode = models.CharField(max_length=30, unique=True)
    nama = models.CharField(max_length=150)
    jenis_ujian = models.CharField(max_length=20, choices=_pilihan(validasi.JENIS))
    durasi_menit = models.PositiveIntegerField()
    aktif = models.BooleanField(default=True)
    keterangan = models.TextField(blank=True)

    class Meta:
        verbose_name = "skema ujian"
        verbose_name_plural = "skema ujian"
        ordering = ["kode"]

    def __str__(self):
        return self.kode

    @property
    def total_soal(self):
        return sum(b.jumlah_soal for b in self.bagian.all())


class SkemaBagian(models.Model):
    CARA_NILAI = CARA_NILAI

    skema = models.ForeignKey(SkemaUjian, on_delete=models.CASCADE, related_name="bagian")
    urutan = models.PositiveSmallIntegerField()
    subtes = models.CharField(max_length=20, choices=_pilihan(validasi.SUBTES))
    jumlah_soal = models.PositiveIntegerField()
    cara_nilai = models.CharField(max_length=20, choices=_pilihan(CARA_NILAI))
    poin_benar = models.PositiveSmallIntegerField(default=5)
    poin_salah = models.SmallIntegerField(default=0)
    ambang_batas = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name = "bagian skema"
        verbose_name_plural = "bagian skema"
        ordering = ["urutan"]
        unique_together = [("skema", "urutan")]

    def __str__(self):
        return f"{self.skema_id} #{self.urutan} {self.subtes}"


class PaketBelajar(models.Model):
    nama = models.CharField(max_length=150)
    jenis_ujian = models.CharField(max_length=20, choices=_pilihan(validasi.JENIS))
    untuk_trial = models.BooleanField(default=False)
    aktif = models.BooleanField(default=True)

    class Meta:
        verbose_name = "paket belajar"
        verbose_name_plural = "paket belajar"
        constraints = [
            models.UniqueConstraint(
                fields=["jenis_ujian"],
                condition=Q(untuk_trial=True, aktif=True),
                name="satu_paket_trial_aktif_per_jenis",
            )
        ]

    def __str__(self):
        return self.nama


class PaketSoal(models.Model):
    paket = models.ForeignKey(PaketBelajar, on_delete=models.CASCADE, related_name="isi")
    soal = models.ForeignKey("cpns.Soal", on_delete=models.PROTECT, related_name="di_paket")
    urutan = models.PositiveIntegerField()

    class Meta:
        verbose_name = "isi paket"
        verbose_name_plural = "isi paket"
        ordering = ["urutan"]
        unique_together = [("paket", "urutan")]

    def __str__(self):
        return f"{self.paket_id} #{self.urutan}"
