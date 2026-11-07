from urllib.parse import quote

from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.urls import reverse

from apps.cpns.models import Sesi, SkemaUjian


def beranda(request):
    if not request.user.is_authenticated:
        tujuan = quote(request.get_full_path(), safe="/")
        return redirect(f"{reverse('accounts:login')}?next={tujuan}")
    return redirect(reverse("cpns:dasbor"))


@login_required
def dasbor_sementara(request):
    """Dasbor sementara sampai dasbor lengkap selesai (Task 12)."""
    skema = SkemaUjian.objects.all()
    if not request.user.is_superuser:
        skema = skema.filter(aktif=True)
    sesi_berjalan = Sesi.objects.filter(
        user=request.user, mode="cat", status="berjalan"
    ).first()
    return render(
        request,
        "cpns/dasbor_sementara.html",
        {"daftar_skema": skema, "sesi_berjalan": sesi_berjalan},
    )
