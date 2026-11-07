import random
from datetime import timedelta

from django.db import transaction
from django.utils import timezone

from apps.cpns.models import Sesi, SesiSoal, Soal

_HURUF = "ABCDE"


class BankSoalKurang(Exception):
    def __init__(self, subtes, tersedia, dibutuhkan):
        self.subtes = subtes
        self.tersedia = tersedia
        self.dibutuhkan = dibutuhkan
        super().__init__(
            f"Bank soal untuk bagian {subtes} belum cukup ({tersedia} dari {dibutuhkan})"
        )


def acak_urutan_opsi(rng):
    return "".join(rng.sample(_HURUF, 5))


def opsi_tampil_ke_asli(urutan_opsi, posisi):
    if posisi not in _HURUF or len(posisi) != 1:
        raise ValueError(f"Posisi opsi tidak valid: {posisi!r}")
    return urutan_opsi[_HURUF.index(posisi)]


def _butir(sesi, soal_list, rng):
    return [
        SesiSoal(sesi=sesi, soal=soal, nomor=nomor, urutan_opsi=acak_urutan_opsi(rng))
        for nomor, soal in enumerate(soal_list, start=1)
    ]


def rakit_sesi_cat(user, skema, rng=None, now=None):
    rng = rng or random.Random()
    now = now or timezone.now()
    pernah = set(
        SesiSoal.objects.filter(sesi__user=user).values_list("soal_id", flat=True)
    )
    terpilih = []
    for bagian in skema.bagian.all():
        tayang = list(
            Soal.objects.filter(
                status="tayang", subtes=bagian.subtes, jenis_ujian=skema.jenis_ujian
            )
        )
        if len(tayang) < bagian.jumlah_soal:
            raise BankSoalKurang(bagian.subtes, len(tayang), bagian.jumlah_soal)
        baru = [s for s in tayang if s.id not in pernah]
        lama = [s for s in tayang if s.id in pernah]
        rng.shuffle(baru)
        rng.shuffle(lama)
        terpilih.extend((baru + lama)[: bagian.jumlah_soal])
    with transaction.atomic():
        sesi = Sesi.objects.create(
            user=user,
            mode="cat",
            skema=skema,
            status="berjalan",
            batas_waktu=now + timedelta(minutes=skema.durasi_menit),
        )
        SesiSoal.objects.bulk_create(_butir(sesi, terpilih, rng))
    return sesi


def rakit_sesi_belajar(
    user, *, paket=None, subtes=None, subtopik=None, jumlah=10, rng=None
):
    if (paket is None) == (subtes is None):
        raise ValueError("Isi tepat salah satu: paket atau subtes.")
    rng = rng or random.Random()
    if paket is not None:
        isi = paket.isi.select_related("soal")
        soal_list = [p.soal for p in isi.filter(soal__status="tayang")]
        if not soal_list:
            pertama = isi.first()
            raise BankSoalKurang(pertama.soal.subtes if pertama else "paket", 0, isi.count())
        filter_subtopik = None
    else:
        qs = Soal.objects.filter(status="tayang", subtes=subtes)
        if subtopik:
            qs = qs.filter(subtopik=subtopik)
        soal_list = list(qs)
        if not soal_list:
            raise BankSoalKurang(subtes, 0, jumlah)
        rng.shuffle(soal_list)
        soal_list = soal_list[:jumlah]
        filter_subtopik = {"subtes": subtes, "subtopik": subtopik, "jumlah": jumlah}
    with transaction.atomic():
        sesi = Sesi.objects.create(
            user=user,
            mode="belajar",
            paket=paket,
            filter_subtopik=filter_subtopik,
            status="berjalan",
            batas_waktu=None,
        )
        SesiSoal.objects.bulk_create(_butir(sesi, soal_list, rng))
    return sesi
