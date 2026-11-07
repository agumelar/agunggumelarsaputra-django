import secrets
from datetime import timedelta

from django.db import IntegrityError, transaction
from django.utils import timezone

from apps.cpns.models import AksesPeserta, PercobaanVoucher, Voucher

ALFABET = "ABCDEFGHJKMNPQRSTUVWXYZ23456789"
BATAS_GAGAL_PER_JAM = 5


class VoucherDitolak(Exception):
    def __init__(self, alasan, sisa):
        super().__init__(alasan)
        self.alasan = alasan
        self.sisa = sisa


def buat_kode():
    huruf = "".join(secrets.choice(ALFABET) for _ in range(8))
    return f"{huruf[:4]}-{huruf[4:]}"


def buat_voucher(jumlah, durasi_hari, catatan="", oleh=None):
    if not 1 <= jumlah <= 100:
        raise ValueError("Jumlah voucher harus 1 sampai 100.")
    if durasi_hari < 1:
        raise ValueError("Durasi harus minimal 1 hari.")
    hasil = []
    while len(hasil) < jumlah:
        try:
            with transaction.atomic():
                hasil.append(
                    Voucher.objects.create(
                        kode=buat_kode(),
                        durasi_hari=durasi_hari,
                        catatan=catatan,
                        dibuat_oleh=oleh,
                    )
                )
        except IntegrityError:
            continue
    return hasil


def normalisasi_kode(teks):
    bersih = "".join(teks.upper().split()).replace("-", "")
    if len(bersih) == 8:
        return f"{bersih[:4]}-{bersih[4:]}"
    return bersih


def sisa_percobaan(user, now=None):
    now = now or timezone.now()
    gagal = PercobaanVoucher.objects.filter(
        user=user, berhasil=False, waktu__gt=now - timedelta(hours=1)
    ).count()
    return max(0, BATAS_GAGAL_PER_JAM - gagal)


def pakai_voucher(user, kode, now=None):
    now = now or timezone.now()
    if sisa_percobaan(user, now) == 0:
        raise VoucherDitolak("terlalu_sering", 0)
    kode = normalisasi_kode(kode)
    with transaction.atomic():
        voucher = (
            Voucher.objects.select_for_update()
            .filter(kode=kode, dibatalkan=False, dipakai_oleh__isnull=True)
            .first()
        )
        if voucher is not None:
            AksesPeserta.objects.get_or_create(user=user)
            akses = AksesPeserta.objects.select_for_update().get(user=user)
            voucher.dipakai_oleh = user
            voucher.dipakai_pada = now
            voucher.save(update_fields=["dipakai_oleh", "dipakai_pada"])
            akses.premium_sampai = max(now, akses.premium_sampai or now) + timedelta(
                days=voucher.durasi_hari
            )
            akses.save(update_fields=["premium_sampai"])
            PercobaanVoucher.objects.create(user=user, waktu=now, berhasil=True)
            return akses
    # Dicatat di luar atomic supaya tidak ikut dibatalkan.
    PercobaanVoucher.objects.create(user=user, waktu=now, berhasil=False)
    raise VoucherDitolak("tidak_valid", sisa_percobaan(user, now))
