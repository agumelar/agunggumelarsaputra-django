from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.db.models import Count
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_GET, require_POST

from apps.cpns.akses import boleh_belajar_paket, boleh_belajar_subtopik
from apps.cpns.models import PaketBelajar, Sesi, Soal
from apps.cpns.penilaian import POIN_MAKS_BOBOT, adalah_benar
from apps.cpns.perakitan import BankSoalKurang, rakit_sesi_belajar
from apps.cpns.sesi_layanan import SesiSudahSelesai, kumpulkan, simpan_jawaban
from apps.cpns.validasi import SUBTES

from ._bantu import HURUF, LABEL_JENIS, ke_posisi_tampil, opsi_ulasan, teks_opsi

PILIHAN_JUMLAH = (10, 20, 30)


def _sesi_milik(request, sesi_id):
    return get_object_or_404(
        Sesi.objects.select_related("paket"), pk=sesi_id, user=request.user, mode="belajar"
    )


def _butir(sesi, nomor):
    return get_object_or_404(sesi.butir.select_related("soal"), nomor=nomor)


def _judul_sesi(sesi):
    if sesi.paket_id:
        return sesi.paket.nama
    saring = sesi.filter_subtopik or {}
    return " ".join(b for b in (saring.get("subtes"), saring.get("subtopik")) if b) or "Belajar"


def _subtopik_per_subtes():
    pasangan = (
        Soal.objects.filter(status="tayang")
        .values_list("subtes", "subtopik")
        .distinct()
        .order_by("subtes", "subtopik")
    )
    kelompok = {s: [] for s in SUBTES}
    for subtes, subtopik in pasangan:
        kelompok.setdefault(subtes, []).append(subtopik)
    return [{"subtes": s, "subtopik": daftar} for s, daftar in kelompok.items() if daftar]


@login_required
@require_GET
def pilih_belajar(request):
    paket_list = PaketBelajar.objects.filter(aktif=True).annotate(jumlah_soal=Count("isi"))
    paket_list = paket_list.order_by("-untuk_trial", "nama")
    paket = [
        {
            "paket": p,
            "label_jenis": LABEL_JENIS.get(p.jenis_ujian, p.jenis_ujian),
            "boleh": boleh_belajar_paket(request.user, p),
        }
        for p in paket_list
    ]
    premium = boleh_belajar_subtopik(request.user)
    konteks = {
        "daftar_paket": paket,
        "boleh_subtopik": premium,
        "daftar_subtes": SUBTES,
        "subtopik_per_subtes": _subtopik_per_subtes() if premium else [],
        "pilihan_jumlah": PILIHAN_JUMLAH,
    }
    return render(request, "cpns/belajar/pilih.html", konteks)


def _mulai_paket(request, paket_id):
    paket = get_object_or_404(PaketBelajar, pk=paket_id, aktif=True)
    if not boleh_belajar_paket(request.user, paket):
        return HttpResponseForbidden("Paket ini khusus Premium.")
    if not paket.isi.exists():
        messages.error(request, "Belum ada soal untuk pilihan ini.")
        return redirect("cpns:belajar_pilih")
    sesi = rakit_sesi_belajar(request.user, paket=paket)
    return redirect("cpns:belajar_soal", sesi_id=sesi.pk, nomor=1)


def _mulai_subtopik(request):
    if not boleh_belajar_subtopik(request.user):
        return HttpResponseForbidden("Belajar per subtopik khusus Premium.")
    subtes = request.POST.get("subtes", "")
    subtopik = request.POST.get("subtopik", "").strip()
    try:
        jumlah = int(request.POST.get("jumlah", ""))
    except ValueError:
        jumlah = None
    if subtes not in SUBTES or jumlah not in PILIHAN_JUMLAH:
        return HttpResponseBadRequest("Pilihan belajar tidak valid.")
    try:
        sesi = rakit_sesi_belajar(
            request.user, subtes=subtes, subtopik=subtopik or None, jumlah=jumlah
        )
    except BankSoalKurang:
        messages.error(request, "Belum ada soal untuk pilihan ini.")
        return redirect("cpns:belajar_pilih")
    tersedia = sesi.butir.count()
    if tersedia < jumlah:
        messages.info(request, f"Tersedia {tersedia} soal untuk pilihan ini.")
    return redirect("cpns:belajar_soal", sesi_id=sesi.pk, nomor=1)


@login_required
@require_POST
def mulai_belajar(request):
    paket_id = request.POST.get("paket_id", "")
    if paket_id:
        if not paket_id.isdigit():
            return HttpResponseBadRequest("Paket tidak valid.")
        return _mulai_paket(request, int(paket_id))
    if "subtes" in request.POST:
        return _mulai_subtopik(request)
    return HttpResponseBadRequest("Pilih paket atau subtopik.")


def _bobot(soal, huruf_asli):
    return int((soal.bobot or {}).get(huruf_asli, 0))


def _kalimat_hasil(butir):
    soal = butir.soal
    urutan = butir.urutan_opsi
    dipilih = ke_posisi_tampil(urutan, butir.jawaban)
    if soal.bobot:
        terbaik = next(h for h in urutan if _bobot(soal, h) == POIN_MAKS_BOBOT)
        kunci = f"Pilihan terbaik {ke_posisi_tampil(urutan, terbaik)} (bobot {POIN_MAKS_BOBOT})."
        if not dipilih:
            return f"Soal ini tidak dijawab. {kunci}"
        return f"Kamu memilih {dipilih} (bobot {_bobot(soal, butir.jawaban)}). {kunci}"
    kunci = f"Kunci jawabannya {ke_posisi_tampil(urutan, soal.kunci)}."
    if not dipilih:
        return f"Soal ini tidak dijawab. {kunci}"
    return f"Kamu memilih {dipilih}. {kunci}"


def _konteks_soal(sesi, butir):
    jumlah = sesi.butir.count()
    soal = butir.soal
    return {
        "sesi": sesi,
        "butir": butir,
        "soal": soal,
        "jumlah": jumlah,
        "judul_sesi": _judul_sesi(sesi),
        "persen_maju": round(butir.nomor * 100 / jumlah) if jumlah else 0,
        "opsi_tampil": [
            {"huruf": HURUF[i], "teks": teks_opsi(soal, asli)}
            for i, asli in enumerate(butir.urutan_opsi)
        ],
        "sudah_dijawab": bool(butir.jawaban) or sesi.status == "selesai",
        "soal_terakhir": butir.nomor >= jumlah,
    }


def _konteks_umpan_balik(sesi, butir):
    konteks = _konteks_soal(sesi, butir)
    konteks.update(
        {
            "benar": adalah_benar(butir.soal, butir.jawaban),
            "dijawab": bool(butir.jawaban),
            "kalimat_hasil": _kalimat_hasil(butir),
            "opsi": opsi_ulasan(butir),
            "pakai_bobot": bool(butir.soal.bobot),
        }
    )
    return konteks


@login_required
@require_GET
def soal_belajar(request, sesi_id, nomor):
    sesi = _sesi_milik(request, sesi_id)
    butir = _butir(sesi, nomor)
    if butir.jawaban or sesi.status == "selesai":
        konteks = _konteks_umpan_balik(sesi, butir)
    else:
        konteks = _konteks_soal(sesi, butir)
    return render(request, "cpns/belajar/soal.html", konteks)


@login_required
@require_POST
def jawab_belajar(request, sesi_id, nomor):
    sesi = _sesi_milik(request, sesi_id)
    _butir(sesi, nomor)
    jawaban = request.POST.get("jawaban", "")
    if len(jawaban) != 1 or jawaban not in HURUF:
        return HttpResponseBadRequest("Jawaban tidak valid.")
    try:
        with transaction.atomic():
            # Kunci sesi dulu agar klik kedua tidak menimpa jawaban pertama.
            terkunci = Sesi.objects.select_for_update().get(pk=sesi.pk)
            if terkunci.status == "selesai":
                raise SesiSudahSelesai(f"Sesi {sesi.pk} sudah selesai")
            if sesi.butir.filter(nomor=nomor, jawaban="").exists():
                simpan_jawaban(sesi, nomor, jawaban, False)
    except SesiSudahSelesai:
        return HttpResponse("Sesi belajar ini sudah selesai.", status=409)
    if request.headers.get("HX-Request") != "true":
        return redirect("cpns:belajar_soal", sesi_id=sesi.pk, nomor=nomor)
    sesi.refresh_from_db()
    konteks = _konteks_umpan_balik(sesi, _butir(sesi, nomor))
    konteks["baru_dijawab"] = True
    return render(request, "cpns/belajar/_umpan_balik.html", konteks)


def _persen(benar, dijawab):
    # Pembulatan setengah ke atas, bukan pembulatan bankir bawaan round().
    return (benar * 200 + dijawab) // (2 * dijawab)


def _rekap_subtopik(butir_semua):
    rekap = {}
    for butir in butir_semua:
        soal = butir.soal
        baris = rekap.setdefault(
            (soal.subtes, soal.subtopik),
            {"subtes": soal.subtes, "subtopik": soal.subtopik, "benar": 0, "dijawab": 0, "total": 0},
        )
        baris["total"] += 1
        if butir.jawaban:
            baris["dijawab"] += 1
            baris["benar"] += adalah_benar(soal, butir.jawaban)
    for baris in rekap.values():
        baris["persen"] = _persen(baris["benar"], baris["dijawab"]) if baris["dijawab"] else None
    return list(rekap.values())


def _paket_bisa_diulang(user, sesi):
    if not sesi.paket_id or not sesi.paket.aktif:
        return None
    return sesi.paket if boleh_belajar_paket(user, sesi.paket) else None


@login_required
@require_GET
def ringkasan_belajar(request, sesi_id):
    sesi = kumpulkan(_sesi_milik(request, sesi_id))
    butir_semua = list(sesi.butir.select_related("soal"))
    dijawab = [b for b in butir_semua if b.jawaban]
    saring = sesi.filter_subtopik or {}
    konteks = {
        "sesi": sesi,
        "judul_sesi": _judul_sesi(sesi),
        "jumlah": len(butir_semua),
        "jumlah_dijawab": len(dijawab),
        "jumlah_benar": sum(adalah_benar(b.soal, b.jawaban) for b in dijawab),
        "rekap": _rekap_subtopik(butir_semua),
        "belum_dijawab": [b for b in butir_semua if not b.jawaban],
        "ulangi_paket": _paket_bisa_diulang(request.user, sesi),
        "ulangi_saring": (
            saring if saring.get("subtes") and boleh_belajar_subtopik(request.user) else None
        ),
    }
    return render(request, "cpns/belajar/ringkasan.html", konteks)
