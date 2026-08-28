from django.shortcuts import render
from .models import LaporanLiterasi


def literasi_home_view(request):
    """Beranda Rabu Literasi (RESIK) & feed bacaan siswa."""
    laporan_list = LaporanLiterasi.objects.select_related('user').filter(is_verified=True)[:20]
    return render(request, 'literasi/literasi_home.html', {'laporan_list': laporan_list})
