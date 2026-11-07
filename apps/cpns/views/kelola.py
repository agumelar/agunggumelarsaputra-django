from urllib.parse import urlencode

from django.contrib import messages
from django.core.exceptions import ValidationError
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.http import require_POST

from apps.cpns.cakupan import hitung_cakupan
from apps.cpns.forms import SoalForm
from apps.cpns.models import LaporanSoal, Soal
from apps.cpns.validasi import HURUF, validasi_soal

from ._bantu import wajib_superuser

STATUS_BAWAAN = "draf"
PESAN_KONFLIK = "Soal ini sudah diubah di tab lain. Muat ulang untuk melihat keadaan terbaru."
PESAN_ALASAN = "Tulis alasan penolakan."
PESAN_PERLU_CEK = (
    "Soal ini ditandai perlu cek fakta. Periksa rujukannya, hapus tanda perlu cek lewat Edit, lalu setujui."
)


def konteks_kelola(request, aktif):
    """Konteks header untuk semua halaman kelola: menu aktif dan jumlah laporan baru."""
    return {
        "menu_aktif": aktif,
        "jumlah_laporan_baru": LaporanSoal.objects.filter(status="baru").count(),
    }


def _filter_dari(data):
    status = data.get("status") or STATUS_BAWAAN
    if status not in Soal.STATUS:
        status = STATUS_BAWAAN
    return {
        "status": status,
        "subtes": data.get("subtes", ""),
        "subtopik": data.get("subtopik", ""),
        "batch": data.get("batch", ""),
    }


def _query_filter(filt):
    return urlencode(
        {k: v for k, v in filt.items() if v and not (k == "status" and v == STATUS_BAWAAN)}
    )


def _antrean(filt):
    qs = Soal.objects.filter(status=filt["status"])
    for kunci in ("subtes", "subtopik", "batch"):
        if filt[kunci]:
            qs = qs.filter(**{kunci: filt[kunci]})
    return qs.order_by("batch", "dibuat_pada", "id")


def _url_soal(soal_id, filt):
    url = reverse("cpns:kelola_tinjau_soal", args=[soal_id])
    query = _query_filter(filt)
    return f"{url}?{query}" if query else url


def _url_antrean(filt):
    url = reverse("cpns:kelola_tinjau")
    query = _query_filter(filt)
    return f"{url}?{query}" if query else url


@wajib_superuser
def kelola_beranda(request):
    return redirect("cpns:kelola_tinjau")


@wajib_superuser
def kelola_tinjau(request):
    filt = _filter_dari(request.GET)
    pertama = _antrean(filt).values_list("id", flat=True).first()
    if pertama is not None:
        return redirect(_url_soal(pertama, filt))
    return _render_tinjau(request, None, filt)


@wajib_superuser
def kelola_tinjau_soal(request, soal_id):
    soal = get_object_or_404(Soal, pk=soal_id)
    return _render_tinjau(request, soal, _filter_dari(request.GET))


@wajib_superuser
def kelola_ubah(request, soal_id):
    soal = get_object_or_404(Soal, pk=soal_id)
    filt = _filter_dari(request.GET)
    if request.method == "POST":
        form = SoalForm(request.POST, instance=soal, user=request.user)
        if form.is_valid():
            with transaction.atomic():
                form.save()
            messages.success(request, "Perubahan disimpan.")
            return redirect(_url_soal(soal.id, filt))
    else:
        form = SoalForm(instance=soal, user=request.user)
    subtes_form = form["subtes"].value()
    return render(
        request,
        "cpns/kelola/ubah_soal.html",
        {
            **konteks_kelola(request, "tinjau"),
            "soal": soal,
            "form": form,
            "filt": filt,
            "query_filter": _query_filter(filt),
            "url_kembali": _url_soal(soal.id, filt),
            "subtes_awal": subtes_form if subtes_form in Soal.SUBTES else soal.subtes,
        },
    )


def _pemeriksaan(soal):
    data = {f.name: getattr(soal, f.name) for f in soal._meta.concrete_fields}
    data["ditinjau_oleh"] = soal.ditinjau_oleh_id
    pesan = validasi_soal(data, untuk_tayang=False)

    opsi = [p for p in pesan if p.startswith(("Isi opsi", "Ada opsi"))]
    kunci = [p for p in pesan if p.startswith(("Pilih kunci", "Isi bobot"))]
    bahas = [p for p in pesan if p.startswith("Isi pembahasan")]
    sisa = [p for p in pesan if p not in opsi + kunci + bahas]

    mirip = list(
        Soal.objects.filter(sidik_teks=soal.sidik_teks)
        .exclude(pk=soal.pk)
        .values_list("id", flat=True)[:5]
    )
    hasil = [
        {"label": "5 opsi terisi dan berbeda", "masalah": opsi},
        {
            "label": "Bobot TKP valid" if soal.subtes == "TKP" else "Kunci valid",
            "masalah": kunci,
        },
        {"label": "Pembahasan 3 bagian lengkap", "masalah": bahas},
        {"label": "Jenis ujian dan subtes cocok", "masalah": sisa},
        {
            "label": "Tidak mirip soal lain di bank",
            "masalah": [f"Teksnya sama dengan soal nomor {', '.join(map(str, mirip))}."]
            if mirip
            else [],
        },
    ]
    if soal.perlu_cek:
        hasil.append(
            {
                "label": "Fakta sudah dicek",
                "masalah": ["Periksa rujukannya, lalu hapus tanda perlu cek lewat Edit."],
            }
        )
    return hasil


def _opsi(soal):
    bobot = soal.bobot or {}
    tkp = soal.subtes == "TKP"
    return [
        {
            "huruf": h,
            "teks": getattr(soal, f"opsi_{h.lower()}"),
            "kunci": not tkp and soal.kunci == h,
            "bobot": bobot.get(h) if tkp else None,
        }
        for h in HURUF
    ]


def _nilai_berbeda(kolom):
    return list(
        Soal.objects.exclude(**{kolom: ""})
        .order_by(kolom)
        .values_list(kolom, flat=True)
        .distinct()
    )


def _render_tinjau(request, soal, filt):
    konteks = {
        **konteks_kelola(request, "tinjau"),
        "filt": filt,
        "query_filter": _query_filter(filt),
        "soal": soal,
        "ditinjau_hari_ini": Soal.objects.filter(
            ditinjau_oleh=request.user, ditinjau_pada__date=timezone.localdate()
        ).count(),
        "draf_tersisa": Soal.objects.filter(status="draf").count(),
        "pilihan_status_label": Soal._meta.get_field("status").choices,
        "pilihan_subtes": Soal.SUBTES,
        "pilihan_subtopik": _nilai_berbeda("subtopik"),
        "pilihan_batch": _nilai_berbeda("batch"),
    }
    if soal is not None:
        ids = list(
            Soal.objects.filter(batch=soal.batch)
            .order_by("dibuat_pada", "id")
            .values_list("id", flat=True)
        )
        konteks.update(
            {
                "opsi": _opsi(soal),
                "pemeriksaan": _pemeriksaan(soal),
                "nomor_di_batch": ids.index(soal.id) + 1,
                "jumlah_di_batch": len(ids),
            }
        )
    return render(request, "cpns/kelola/tinjau.html", konteks)


def _berikutnya(ids, soal_id, *, putar):
    if soal_id in ids:
        i = ids.index(soal_id)
        if i + 1 < len(ids):
            return ids[i + 1]
        lain = [x for x in ids if x != soal_id]
        return lain[0] if putar and lain else None
    return ids[0] if ids else None


@wajib_superuser
@require_POST
def kelola_aksi(request, soal_id):
    filt = _filter_dari(request.POST)
    aksi = request.POST.get("aksi", "")
    status_awal = request.POST.get("status_awal", "")
    alasan = request.POST.get("alasan", "").strip()
    ids = list(_antrean(filt).values_list("id", flat=True))
    kembali = _url_soal(soal_id, filt)
    get_object_or_404(Soal, pk=soal_id)

    if aksi not in ("setujui", "tolak", "lewati"):
        messages.error(request, "Aksi tidak dikenal.")
        return redirect(kembali)

    if aksi == "lewati":
        tujuan = _berikutnya(ids, soal_id, putar=True)
        return redirect(_url_soal(tujuan, filt) if tujuan else _url_antrean(filt))

    if aksi == "tolak" and not alasan:
        messages.error(request, PESAN_ALASAN)
        return redirect(kembali)

    with transaction.atomic():
        soal = Soal.objects.select_for_update().get(pk=soal_id)
        if soal.status != status_awal:
            messages.error(request, PESAN_KONFLIK)
            return redirect(kembali)
        if aksi == "setujui" and soal.status == "tayang":
            messages.error(request, "Soal ini sudah tayang.")
            return redirect(kembali)
        if aksi == "setujui" and soal.perlu_cek:
            messages.error(request, PESAN_PERLU_CEK)
            return redirect(kembali)
        soal.ditinjau_oleh = request.user
        soal.ditinjau_pada = timezone.now()
        if aksi == "setujui":
            soal.status = "tayang"
            soal.catatan_tinjau = ""
            try:
                soal.full_clean()
            except ValidationError as galat:
                for pesan in galat.messages:
                    messages.error(request, pesan)
                return redirect(kembali)
        else:
            soal.status = "ditolak"
            soal.catatan_tinjau = alasan
        soal.save()

    messages.success(request, "Soal ditayangkan." if aksi == "setujui" else "Soal ditolak.")
    tujuan = _berikutnya(ids, soal_id, putar=False)
    return redirect(_url_soal(tujuan, filt) if tujuan else _url_antrean(filt))


@wajib_superuser
def kelola_cakupan(request):
    hasil = hitung_cakupan()
    kelompok = {}
    for b in hasil["baris"]:
        query = urlencode({"status": "tayang", "subtes": b["subtes"], "subtopik": b["subtopik"]})
        b["url"] = f"{reverse('cpns:kelola_tinjau')}?{query}"
        kelompok.setdefault(b["subtes"], []).append(b)
    return render(
        request,
        "cpns/kelola/cakupan.html",
        {
            **konteks_kelola(request, "cakupan"),
            "skema": hasil["skema"],
            "kelompok": list(kelompok.items()),
        },
    )


STATUS_LAPORAN_BAWAAN = "baru"


def _status_laporan(data):
    status = data.get("status") or STATUS_LAPORAN_BAWAAN
    return status if status in ("baru", "selesai", "semua") else STATUS_LAPORAN_BAWAAN


@wajib_superuser
def kelola_laporan(request):
    status = _status_laporan(request.GET)
    qs = LaporanSoal.objects.select_related("soal", "user").order_by("-dibuat_pada", "-id")
    if status != "semua":
        qs = qs.filter(status=status)
    kelompok = {}
    for lap in qs:
        k = kelompok.setdefault(lap.soal_id, {"soal": lap.soal, "laporan": []})
        k["laporan"].append(lap)
    daftar = [{**k, "jumlah": len(k["laporan"])} for k in kelompok.values()]
    return render(
        request,
        "cpns/kelola/laporan.html",
        {
            **konteks_kelola(request, "laporan"),
            "status": status,
            "pilihan_status": [("baru", "Baru"), ("selesai", "Selesai"), ("semua", "Semua")],
            "kelompok": daftar,
        },
    )


@wajib_superuser
@require_POST
def kelola_laporan_selesai(request, laporan_id):
    laporan = get_object_or_404(LaporanSoal, pk=laporan_id)
    if laporan.status != "selesai":
        laporan.status = "selesai"
        laporan.save(update_fields=["status"])
        messages.success(request, "Laporan ditandai selesai.")
    status = _status_laporan(request.POST)
    url = reverse("cpns:kelola_laporan")
    if status != STATUS_LAPORAN_BAWAAN:
        url = f"{url}?{urlencode({'status': status})}"
    return redirect(url)
