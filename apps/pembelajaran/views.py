from django.shortcuts import render, get_object_or_404
from .models import Modul


def modul_list_view(request):
    """Menampilkan daftar 16 Modul Pembelajaran RPL."""
    modul_list = Modul.objects.filter(is_published=True)
    return render(request, 'pembelajaran/modul_list.html', {'modul_list': modul_list})


def modul_detail_view(request, slug):
    """Menampilkan konten modul pembelajaran dengan 4-Tab Reader."""
    modul = get_object_or_404(Modul, slug=slug, is_published=True)
    return render(request, 'pembelajaran/modul_detail.html', {'modul': modul})
