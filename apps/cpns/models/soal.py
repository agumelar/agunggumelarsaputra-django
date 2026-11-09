from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models

from apps.cpns import validasi
from apps.cpns.validasi import sidik_teks, validasi_soal


def _pilihan(nilai):
    return [(n, n) for n in nilai]


class Soal(models.Model):
    JENIS = validasi.JENIS
    SUBTES = validasi.SUBTES
    TINGKAT = validasi.TINGKAT
    STATUS = validasi.STATUS
    SUMBER = validasi.SUMBER

    jenis_ujian = models.CharField(max_length=20, choices=_pilihan(JENIS))
    subtes = models.CharField(max_length=20, choices=_pilihan(SUBTES))
    subtopik = models.CharField(max_length=120)
    tingkat = models.CharField(max_length=20, choices=_pilihan(TINGKAT), default="sedang")
    teks = models.TextField()
    opsi_a = models.TextField()
    opsi_b = models.TextField()
    opsi_c = models.TextField()
    opsi_d = models.TextField()
    opsi_e = models.TextField()
    kunci = models.CharField(max_length=1, blank=True)
    bobot = models.JSONField(null=True, blank=True)
    pembahasan_konsep = models.TextField(blank=True)
    pembahasan_pengecoh = models.TextField(blank=True)
    pembahasan_cepat = models.TextField(blank=True)
    rujukan = models.TextField(blank=True)
    perlu_cek = models.BooleanField(default=False)
    status = models.CharField(max_length=20, choices=_pilihan(STATUS), default="draf")
    catatan_tinjau = models.TextField(blank=True)
    ditinjau_oleh = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="soal_ditinjau",
    )
    ditinjau_pada = models.DateTimeField(null=True, blank=True)
    sumber = models.CharField(max_length=20, choices=_pilihan(SUMBER), default="draf_ai")
    batch = models.CharField(max_length=100, blank=True)
    sidik_teks = models.CharField(max_length=64, db_index=True, editable=False)
    dibuat_pada = models.DateTimeField(auto_now_add=True)
    diubah_pada = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "soal"
        verbose_name_plural = "soal"
        ordering = ["-dibuat_pada"]

    def __str__(self):
        return f"[{self.subtes}] {self.teks[:60]}"

    def clean(self):
        data = {
            f.name: getattr(self, f.name)
            for f in self._meta.concrete_fields
            if f.name != "ditinjau_oleh"
        }
        data["ditinjau_oleh"] = self.ditinjau_oleh_id
        pesan = validasi_soal(data, untuk_tayang=self.status == "tayang")
        if pesan:
            raise ValidationError(pesan)

    def hitung_sidik(self):
        return sidik_teks(self.teks)

    def save(self, *args, **kwargs):
        self.sidik_teks = self.hitung_sidik()
        campur = kwargs.get("update_fields")
        if campur is not None and "teks" in campur and "sidik_teks" not in campur:
            kwargs["update_fields"] = [*campur, "sidik_teks"]
        super().save(*args, **kwargs)
