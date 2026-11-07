import json

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.http import require_GET, require_POST

from apps.cpns.akses import boleh_lihat_pembahasan, boleh_mulai_cat
from apps.cpns.models import Sesi, SkemaUjian
from apps.cpns.penilaian import adalah_benar
from apps.cpns.perakitan import BankSoalKurang, rakit_sesi_cat
from apps.cpns.sesi_layanan import (
    SesiSudahSelesai,
    WaktuHabis,
    kumpulkan,
    selesaikan_jika_kedaluwarsa,
    simpan_jawaban,
)

from ._bantu import HURUF, LABEL_JENIS, ke_posisi_tampil, opsi_ulasan, teks_opsi

JAWABAN_SAH = ("",) + tuple(HURUF)


def _sesi_milik(request, sesi_id):
    return get_object_or_404(
        Sesi.objects.select_related("skema"), pk=sesi_id, user=request.user, mode="cat"
    )


def _label_jenis(sesi):
    return LABEL_JENIS.get(sesi.skema.jenis_ujian, sesi.skema.jenis_ujian)


def _gabung(bagian):
    if len(bagian) <= 1:
        return "".join(bagian)
    if len(bagian) == 2:
        return f"{bagian[0]} dan {bagian[1]}"
    return f"{', '.join(bagian[:-1])}, dan {bagian[-1]}"


@login_required
@require_POST
def mulai_cat(request, kode):
    skema = get_object_or_404(SkemaUjian, kode__iexact=kode)
    boleh, alasan = boleh_mulai_cat(request.user, skema)
    if not boleh:
        messages.error(request, alasan)
        return redirect("cpns:dasbor")
    try:
        sesi = rakit_sesi_cat(request.user, skema)
    except BankSoalKurang as e:
        messages.error(
            request,
            f"Bank soal untuk bagian {e.subtes} belum cukup ({e.tersedia} dari {e.dibutuhkan}).",
        )
        return redirect("cpns:dasbor")
    return redirect("cpns:cat_ruang", sesi_id=sesi.pk)


@login_required
@require_GET
def ruang_cat(request, sesi_id):
    sesi = _sesi_milik(request, sesi_id)
    if selesaikan_jika_kedaluwarsa(sesi) or sesi.status == "selesai":
        return redirect("cpns:cat_hasil", sesi_id=sesi.pk)
    soal = []
    for butir in sesi.butir.select_related("soal"):
        soal.append(
            {
                "nomor": butir.nomor,
                "subtes": butir.soal.subtes,
                "subtopik": butir.soal.subtopik,
                "teks": butir.soal.teks,
                "opsi": [
                    {"key": HURUF[i], "text": teks_opsi(butir.soal, asli)}
                    for i, asli in enumerate(butir.urutan_opsi)
                ],
                "jawaban": ke_posisi_tampil(butir.urutan_opsi, butir.jawaban),
                "ragu": butir.ragu,
            }
        )
    data = {
        "sesi_id": sesi.pk,
        "sisa_detik": sesi.sisa_detik(timezone.now()),
        "url_simpan": reverse("cpns:cat_simpan", args=[sesi.pk]),
        "soal": soal,
    }
    return render(
        request,
        "cpns/cat/ruang.html",
        {"sesi": sesi, "label_jenis": _label_jenis(sesi), "data_ruang": data},
    )


def _baca_simpan(body):
    try:
        data = json.loads(body)
    except ValueError:
        return None
    if not isinstance(data, dict):
        return None
    nomor, jawaban, ragu = data.get("nomor"), data.get("jawaban"), data.get("ragu")
    if not isinstance(nomor, int) or isinstance(nomor, bool):
        return None
    if not isinstance(jawaban, str) or jawaban not in JAWABAN_SAH:
        return None
    if not isinstance(ragu, bool):
        return None
    return nomor, jawaban, ragu


def _gagal(status, alasan):
    return JsonResponse({"ok": False, "alasan": alasan}, status=status)


@require_POST
def simpan_cat(request, sesi_id):
    # Endpoint JSON: jangan redirect ke login, supaya klien tahu jawabannya belum tersimpan.
    if not request.user.is_authenticated:
        return _gagal(401, "belum_masuk")
    sesi = _sesi_milik(request, sesi_id)
    data = _baca_simpan(request.body)
    if data is None:
        return _gagal(400, "data_tidak_valid")
    try:
        butir = simpan_jawaban(sesi, *data)
    except WaktuHabis:
        return _gagal(409, "waktu_habis")
    except SesiSudahSelesai:
        return _gagal(409, "sudah_selesai")
    except ValueError:
        return _gagal(400, "data_tidak_valid")
    return JsonResponse({"ok": True, "tersimpan_pada": butir.dijawab_pada.isoformat()})


@login_required
@require_POST
def kumpulkan_cat(request, sesi_id):
    sesi = _sesi_milik(request, sesi_id)
    kumpulkan(sesi)
    return redirect("cpns:cat_hasil", sesi_id=sesi.pk)


def _durasi(sesi):
    akhir = sesi.selesai_pada or timezone.now()
    if sesi.batas_waktu is not None:
        akhir = min(akhir, sesi.batas_waktu)
    detik = max(0, int((akhir - sesi.dimulai_pada).total_seconds()))
    return f"{detik // 60} menit {detik % 60} detik"


def _penjelasan(skor_bagian):
    kurang = [b for b in skor_bagian if not b["lulus"]]
    lolos = [b["subtes"] for b in skor_bagian if b["lulus"] and b["ambang"]]
    if not kurang:
        return "Semua bagian mencapai ambang batas." if lolos else ""
    kalimat = _gabung([f"{b['subtes']} kurang {b['ambang'] - b['skor']} poin" for b in kurang]) + "."
    if lolos:
        kalimat += f" {_gabung(lolos)} sudah mencapai ambang batas."
    return kalimat


def _status_butir(butir, pakai_bobot):
    if not butir.jawaban:
        return "Tidak dijawab"
    if pakai_bobot:
        return f"Poin {butir.poin or 0}"
    return "Benar" if adalah_benar(butir.soal, butir.jawaban) else "Salah"


def _ulasan(sesi):
    ulasan = []
    for butir in sesi.butir.select_related("soal"):
        soal = butir.soal
        pakai_bobot = bool(soal.bobot)
        ulasan.append(
            {
                "nomor": butir.nomor,
                "soal": soal,
                "subtes": soal.subtes,
                "teks": soal.teks,
                "status": _status_butir(butir, pakai_bobot),
                "pakai_bobot": pakai_bobot,
                "opsi": opsi_ulasan(butir),
                "konsep": soal.pembahasan_konsep,
                "pengecoh": soal.pembahasan_pengecoh,
                "cepat": soal.pembahasan_cepat,
            }
        )
    return ulasan


@login_required
@require_GET
def hasil_cat(request, sesi_id):
    sesi = _sesi_milik(request, sesi_id)
    if sesi.status == "berjalan":
        if not selesaikan_jika_kedaluwarsa(sesi):
            return redirect("cpns:cat_ruang", sesi_id=sesi.pk)
        sesi.refresh_from_db()
    lihat_pembahasan = boleh_lihat_pembahasan(request.user, sesi)
    konteks = {
        "sesi": sesi,
        "label_jenis": _label_jenis(sesi),
        "penjelasan": _penjelasan(sesi.skor_bagian),
        "total_maks": sum(b["maks"] for b in sesi.skor_bagian),
        "ada_ambang": any(b["ambang"] for b in sesi.skor_bagian),
        "durasi": _durasi(sesi),
        "jumlah_soal": sesi.butir.count(),
        "lihat_pembahasan": lihat_pembahasan,
        "ulasan": _ulasan(sesi) if lihat_pembahasan else [],
    }
    return render(request, "cpns/cat/hasil.html", konteks)
