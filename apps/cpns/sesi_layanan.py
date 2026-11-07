from datetime import timedelta

from django.db import transaction
from django.utils import timezone

from apps.cpns.models import Sesi, SesiSoal
from apps.cpns.penilaian import nilai_sesi
from apps.cpns.perakitan import opsi_tampil_ke_asli

TOLERANSI_DETIK = 30


class WaktuHabis(Exception):
    pass


class SesiSudahSelesai(Exception):
    pass


def _lewat_toleransi(sesi, now):
    return (
        sesi.mode == "cat"
        and sesi.batas_waktu is not None
        and now > sesi.batas_waktu + timedelta(seconds=TOLERANSI_DETIK)
    )


def simpan_jawaban(sesi, nomor, jawaban_tampil, ragu, now=None) -> SesiSoal:
    now = now or timezone.now()
    with transaction.atomic():
        terkunci = Sesi.objects.select_for_update().get(pk=sesi.pk)
        if terkunci.status == "selesai":
            raise SesiSudahSelesai(f"Sesi {terkunci.pk} sudah selesai")
        if _lewat_toleransi(terkunci, now):
            raise WaktuHabis(f"Waktu sesi {terkunci.pk} sudah habis")
        if jawaban_tampil not in ("", "A", "B", "C", "D", "E"):
            raise ValueError(f"Jawaban tidak valid: {jawaban_tampil!r}")
        try:
            butir = terkunci.butir.get(nomor=nomor)
        except SesiSoal.DoesNotExist:
            raise ValueError(f"Nomor {nomor} tidak ada di sesi ini") from None
        butir.jawaban = (
            ""
            if jawaban_tampil == ""
            else opsi_tampil_ke_asli(butir.urutan_opsi, jawaban_tampil)
        )
        butir.ragu = bool(ragu)
        butir.dijawab_pada = now
        butir.save(update_fields=["jawaban", "ragu", "dijawab_pada"])
        return butir


def kumpulkan(sesi, now=None) -> Sesi:
    now = now or timezone.now()
    with transaction.atomic():
        terkunci = Sesi.objects.select_for_update().get(pk=sesi.pk)
        if terkunci.status == "selesai":
            return terkunci
        nilai_sesi(terkunci)
        terkunci.status = "selesai"
        terkunci.selesai_pada = now
        terkunci.save(update_fields=["status", "selesai_pada"])
        return terkunci


def selesaikan_jika_kedaluwarsa(sesi, now=None) -> bool:
    now = now or timezone.now()
    if sesi.status != "berjalan" or not _lewat_toleransi(sesi, now):
        return False
    kumpulkan(sesi, now=now)
    return True
