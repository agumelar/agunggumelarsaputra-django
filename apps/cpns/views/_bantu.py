from functools import wraps

from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import redirect_to_login
from django.core.exceptions import PermissionDenied
from django.urls import reverse

from apps.cpns.penilaian import adalah_benar

wajib_masuk = login_required(login_url="cpns:masuk")

HURUF = "ABCDE"
LABEL_JENIS = {"SKD": "SKD", "SKB_GURU": "SKB Guru"}


def teks_opsi(soal, huruf_asli):
    return getattr(soal, f"opsi_{huruf_asli.lower()}")


def ke_posisi_tampil(urutan_opsi, jawaban_asli):
    if not jawaban_asli or jawaban_asli not in urutan_opsi:
        return ""
    return HURUF[urutan_opsi.index(jawaban_asli)]


def opsi_ulasan(butir):
    """Opsi dalam urutan tampil, lengkap dengan tanda jawaban, kunci, dan bobot."""
    soal = butir.soal
    return [
        {
            "huruf": HURUF[i],
            "teks": teks_opsi(soal, asli),
            "dipilih": butir.jawaban == asli,
            "kunci": adalah_benar(soal, asli),
            "bobot": (soal.bobot or {}).get(asli, 0),
        }
        for i, asli in enumerate(butir.urutan_opsi)
    ]


def wajib_superuser(view):
    """Hanya superuser. Tamu ke halaman masuk CPNS, user lain mendapat 403."""

    @wraps(view)
    def dibungkus(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect_to_login(request.get_full_path(), reverse("cpns:masuk"))
        if not request.user.is_superuser:
            raise PermissionDenied
        return view(request, *args, **kwargs)

    return dibungkus
