from django.contrib import messages
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils import timezone
from django.utils.dateformat import format as format_tanggal
from django.views.decorators.http import require_GET, require_POST

from apps.cpns.akses import akses_untuk
from apps.cpns.models import PengaturanCPNS
from apps.cpns.views._bantu import wajib_masuk
from apps.cpns.voucher import BATAS_GAGAL_PER_JAM, VoucherDitolak, pakai_voucher

PANJANG_KODE_MAKS = 20
PESAN_KODE_CACAT = "Masukkan kode voucher, paling banyak 20 karakter."


def _tanggal(nilai):
    return format_tanggal(timezone.localtime(nilai), "d M Y")


@require_GET
def premium(request):
    pengaturan = PengaturanCPNS.ambil()
    email = request.user.email if request.user.is_authenticated else ""
    harga = []
    for durasi, teks in pengaturan.daftar_harga():
        harga.append({"durasi": durasi, "teks": teks, "wa": pengaturan.tautan_wa(durasi, email)})
    premium_sampai = None
    if request.user.is_authenticated:
        sampai = akses_untuk(request.user).premium_sampai
        if sampai is not None and sampai > timezone.now():
            premium_sampai = sampai
    return render(request, "cpns/premium/halaman.html", {
        "harga": harga,
        "wa_umum": None if harga else pengaturan.tautan_wa(30, email),
        "ada_kontak": bool(pengaturan.tautan_wa(1, "")),
        "premium_sampai": premium_sampai,
        "superuser": request.user.is_authenticated and request.user.is_superuser,
    })


def _balas(request, sukses, teks, status=200):
    if request.headers.get("HX-Request") == "true":
        return render(request, "cpns/premium/_hasil_voucher.html", {"sukses": sukses, "teks": teks}, status=status)
    (messages.success if sukses else messages.error)(request, teks)
    return redirect(reverse("cpns:premium"))


def _tukar(request):
    kode = request.POST.get("kode", "").strip()
    if not kode or len(kode) > PANJANG_KODE_MAKS:
        return _balas(request, False, PESAN_KODE_CACAT, status=400)
    try:
        akses = pakai_voucher(request.user, kode)
    except VoucherDitolak as e:
        if e.alasan == "terlalu_sering":
            return _balas(request, False, "Terlalu banyak percobaan. Coba lagi dalam satu jam.")
        return _balas(
            request,
            False,
            "Kode tidak ditemukan atau sudah dipakai. Periksa lagi huruf dan angkanya. "
            f"Sisa percobaan: {e.sisa} dari {BATAS_GAGAL_PER_JAM} per jam.",
        )
    return _balas(request, True, f"Premium aktif sampai {_tanggal(akses.premium_sampai)}.")


tukar_voucher = wajib_masuk(require_POST(_tukar))
