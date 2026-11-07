"""
URL configuration khusus subdomain cpns.agunggumelarsaputra.com.

Rute CPNS dipasang di root. Rute situs utama ikut didaftarkan di belakangnya
karena halaman akun (login, daftar, profil) memakai navbar utama yang
memanggil {% url %} ke namespace pembelajaran, tka, literasi, dan lainnya.
Tanpa itu, halaman tersebut gagal dengan NoReverseMatch (500).
"""

from django.urls import include, path

from config.urls import urlpatterns as main_urlpatterns

urlpatterns = [
    path('', include('apps.cpns.urls', namespace='cpns')),
] + [
    pattern for pattern in main_urlpatterns
    if getattr(pattern, 'namespace', None) != 'cpns'
]
