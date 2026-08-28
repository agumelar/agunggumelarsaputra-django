from django.shortcuts import render, get_object_or_404
from .models import PaketUjian


def tka_list_view(request):
    """Daftar simulasi ujian CBT TKA PPLG."""
    paket_list = PaketUjian.objects.filter(is_active=True)
    return render(request, 'tka/tka_list.html', {'paket_list': paket_list})


def tka_detail_view(request, slug):
    """Halaman petunjuk dan mulai ujian CBT."""
    paket = get_object_or_404(PaketUjian, slug=slug, is_active=True)
    return render(request, 'tka/tka_detail.html', {'paket': paket})
