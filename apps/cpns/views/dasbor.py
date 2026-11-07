from urllib.parse import quote

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Min, Q
from django.http import HttpResponseBadRequest, HttpResponseForbidden
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils import timezone
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.http import require_GET, require_POST

from apps.cpns.akses import akses_untuk, boleh_mulai_cat, is_premium
from apps.cpns.models import LaporanSoal, PaketBelajar, Sesi, SesiSoal, SkemaUjian
from apps.cpns.sesi_layanan import selesaikan_jika_kedaluwarsa

from ._bantu import LABEL_JENIS

JUMLAH_SKOR_DASBOR = 5
CATATAN_MAKS = 1000
ALASAN_SAH = {kode for kode, _ in LaporanSoal.ALASAN_CHOICES}
PESAN_TERKIRIM = "Terima kasih, laporan terkirim."
PESAN_SUDAH_ADA = "Laporan untuk soal ini sudah kami terima."


def beranda(request):
    if not request.user.is_authenticated:
        tujuan = quote(request.get_full_path(), safe="/")
        return redirect(f"{reverse('accounts:login')}?next={tujuan}")
    return redirect(reverse("cpns:dasbor"))


def _dengan_progres(qs):
    return qs.annotate(
        jumlah_butir=Count("butir"),
        jumlah_dijawab=Count("butir", filter=~Q(butir__jawaban="")),
        nomor_belum=Min("butir__nomor", filter=Q(butir__jawaban="")),
    )


def _total_maks(sesi):
    return sum(b.get("maks", 0) for b in sesi.skor_bagian or [])


def _mm_ss(detik):
    return f"{detik // 60:02d}:{detik % 60:02d}"


def _lencana(user):
    if not is_premium(user):
        return "Akun Trial", None
    return "Premium", akses_untuk(user).premium_sampai


def _sesi_cat_berjalan(user):
    sesi = Sesi.objects.select_related("skema").filter(user=user, mode="cat", status="berjalan").first()
    if sesi is None or selesaikan_jika_kedaluwarsa(sesi):
        return None
    return sesi


def _kartu_skema(user, premium):
    kartu = []
    for skema in SkemaUjian.objects.prefetch_related("bagian"):
        boleh, alasan = boleh_mulai_cat(user, skema)
        kartu.append(
            {
                "skema": skema,
                "label": LABEL_JENIS.get(skema.jenis_ujian, skema.jenis_ujian),
                "boleh": boleh,
                "alasan": alasan,
                "segera": not skema.aktif and not user.is_superuser,
                "khusus_premium": skema.jenis_ujian == "SKB_GURU" and not premium,
            }
        )
    return kartu


def _kartu_paket_trial(user):
    kartu = []
    paket_trial = PaketBelajar.objects.filter(untuk_trial=True, aktif=True).annotate(
        jumlah_isi=Count("isi")
    )
    for paket in paket_trial.order_by("nama"):
        # GROUP BY dari annotate membuang Meta.ordering, jadi urutan harus eksplisit.
        terakhir = (
            _dengan_progres(Sesi.objects.filter(user=user, mode="belajar", paket=paket))
            .order_by("-dimulai_pada", "-pk")
            .first()
        )
        lanjut = (
            terakhir.nomor_belum
            if terakhir and terakhir.status == "berjalan" and terakhir.nomor_belum
            else None
        )
        kartu.append(
            {
                "paket": paket,
                "sesi": terakhir,
                "dijawab": terakhir.jumlah_dijawab if terakhir else 0,
                "jumlah": terakhir.jumlah_butir if terakhir else paket.jumlah_isi,
                "lanjut_nomor": lanjut,
            }
        )
    return kartu


def _skor_terakhir(user):
    daftar = list(
        Sesi.objects.select_related("skema")
        .filter(user=user, mode="cat", status="selesai")
        .order_by("-selesai_pada", "-pk")[:JUMLAH_SKOR_DASBOR]
    )
    for sesi in daftar:
        sesi.total_maks = _total_maks(sesi)
    return daftar


@login_required
@require_GET
def dasbor(request):
    user = request.user
    premium = is_premium(user)
    label_lencana, premium_sampai = _lencana(user)
    sesi_berjalan = _sesi_cat_berjalan(user)
    konteks = {
        "nama_sapaan": user.first_name or user.username,
        "label_lencana": label_lencana,
        "premium_sampai": premium_sampai,
        "sesi_berjalan": sesi_berjalan,
        "sisa_waktu": _mm_ss(sesi_berjalan.sisa_detik(timezone.now())) if sesi_berjalan else "",
        "kartu_skema": _kartu_skema(user, premium),
        "kartu_paket": _kartu_paket_trial(user),
        "skor_terakhir": _skor_terakhir(user),
    }
    return render(request, "cpns/dasbor.html", konteks)


def _judul_riwayat(sesi):
    if sesi.mode == "cat":
        label = LABEL_JENIS.get(sesi.skema.jenis_ujian, sesi.skema.jenis_ujian) if sesi.skema_id else ""
        return f"Simulasi CAT {label}".strip()
    if sesi.paket_id:
        return f"Belajar: {sesi.paket.nama}"
    saring = sesi.filter_subtopik or {}
    bagian = " ".join(b for b in (saring.get("subtes"), saring.get("subtopik")) if b)
    return f"Belajar: {bagian}" if bagian else "Belajar"


def _tautan_riwayat(sesi):
    if sesi.mode == "cat":
        nama = "cpns:cat_ruang" if sesi.status == "berjalan" else "cpns:cat_hasil"
        return reverse(nama, args=[sesi.pk]), "Lanjutkan" if sesi.status == "berjalan" else "Lihat hasil"
    if sesi.status == "berjalan" and sesi.nomor_belum:
        return reverse("cpns:belajar_soal", args=[sesi.pk, sesi.nomor_belum]), "Lanjutkan"
    return reverse("cpns:belajar_ringkasan", args=[sesi.pk]), "Lihat ringkasan"


def _ringkasan_skor(sesi):
    if sesi.mode == "cat":
        if sesi.status == "berjalan":
            return "Belum dinilai"
        hasil = "Lolos" if sesi.lulus else "Belum lolos"
        return f"{sesi.total} / {_total_maks(sesi)}, {hasil}"
    return f"{sesi.jumlah_dijawab}/{sesi.jumlah_butir} dijawab"


@login_required
@require_GET
def riwayat(request):
    daftar = []
    sesi_qs = _dengan_progres(
        Sesi.objects.select_related("skema", "paket").filter(user=request.user)
    ).order_by("-dimulai_pada", "-pk")
    for sesi in sesi_qs:
        url, label_tautan = _tautan_riwayat(sesi)
        daftar.append(
            {
                "sesi": sesi,
                "judul": _judul_riwayat(sesi),
                "status": "Berjalan" if sesi.status == "berjalan" else "Selesai",
                "skor": _ringkasan_skor(sesi),
                "url": url,
                "label_tautan": label_tautan,
            }
        )
    return render(request, "cpns/riwayat.html", {"daftar_riwayat": daftar})


def _soal_sudah_terbuka(user, soal_id):
    """Soal boleh dilaporkan hanya kalau kuncinya sudah pernah tampil ke user ini."""
    return SesiSoal.objects.filter(soal_id=soal_id, sesi__user=user).filter(
        Q(sesi__mode="belajar", sesi__status="selesai")
        | (Q(sesi__mode="belajar") & ~Q(jawaban=""))
        | Q(sesi__mode="cat", sesi__status="selesai")
    ).exists()


def _balas_laporan(request, pesan):
    if request.headers.get("HX-Request") == "true":
        return render(request, "cpns/komponen/_laporkan_hasil.html", {"pesan": pesan})
    messages.success(request, pesan)
    asal = request.META.get("HTTP_REFERER", "")
    if asal and url_has_allowed_host_and_scheme(
        asal, allowed_hosts={request.get_host()}, require_https=request.is_secure()
    ):
        return redirect(asal)
    return redirect("cpns:dasbor")


@login_required
@require_POST
def laporkan_soal(request, soal_id):
    if not _soal_sudah_terbuka(request.user, soal_id):
        return HttpResponseForbidden("Soal ini belum bisa kamu laporkan.")
    alasan = request.POST.get("alasan", "")
    catatan = request.POST.get("catatan", "").strip()
    if alasan not in ALASAN_SAH:
        return HttpResponseBadRequest("Pilih alasan laporan.")
    if len(catatan) > CATATAN_MAKS:
        return HttpResponseBadRequest(f"Catatan paling banyak {CATATAN_MAKS} karakter.")
    sudah_ada = LaporanSoal.objects.filter(
        soal_id=soal_id, user=request.user, status="baru"
    ).exists()
    if sudah_ada:
        return _balas_laporan(request, PESAN_SUDAH_ADA)
    LaporanSoal.objects.create(
        soal_id=soal_id, user=request.user, alasan=alasan, catatan=catatan
    )
    return _balas_laporan(request, PESAN_TERKIRIM)
