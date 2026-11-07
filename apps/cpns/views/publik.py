from django.shortcuts import redirect, render
from django.urls import reverse
from django.views.decorators.http import require_GET

from apps.cpns.models import PengaturanCPNS, SkemaUjian


def _bagian_skd():
    skema = SkemaUjian.objects.filter(kode="SKD-CAT").first()
    if skema is None:
        return None, []
    baris = []
    for b in skema.bagian.all():
        if b.cara_nilai == "bobot_opsi":
            aturan = "1 sampai 5 per soal"
        else:
            aturan = f"benar {b.poin_benar}, salah 0"
        baris.append({"subtes": b.subtes, "jumlah": b.jumlah_soal, "aturan": aturan, "ambang": b.ambang_batas})
    return skema, baris


@require_GET
def beranda_publik(request):
    if request.user.is_authenticated:
        return redirect(reverse("cpns:dasbor"))
    skema, bagian = _bagian_skd()
    pengaturan = PengaturanCPNS.ambil()
    return render(request, "cpns/publik/beranda.html", {
        "skema": skema,
        "bagian_skd": bagian,
        "harga": [{"durasi": d, "teks": t} for d, t in pengaturan.daftar_harga()],
        "ada_kontak": bool(pengaturan.tautan_wa(1, "")),
        "total_soal": sum(b["jumlah"] for b in bagian),
    })


@require_GET
def syarat(request):
    return render(request, "cpns/publik/syarat.html")


@require_GET
def privasi(request):
    return render(request, "cpns/publik/privasi.html")
