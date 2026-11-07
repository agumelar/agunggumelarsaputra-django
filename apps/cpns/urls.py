from django.urls import path

from . import views

app_name = 'cpns'

urlpatterns = [
    path('', views.beranda_publik, name='beranda'),
    path('syarat-layanan/', views.syarat, name='syarat'),
    path('kebijakan-privasi/', views.privasi, name='privasi'),
    path('masuk/', views.masuk, name='masuk'),
    path('daftar/', views.daftar, name='daftar'),
    path('premium/', views.premium, name='premium'),
    path('premium/voucher/', views.tukar_voucher, name='tukar_voucher'),
    path('dasbor/', views.dasbor, name='dasbor'),
    path('riwayat/', views.riwayat, name='riwayat'),
    path('soal/<int:soal_id>/laporkan/', views.laporkan_soal, name='laporkan'),
    path('simulasi/<slug:kode>/mulai/', views.mulai_cat, name='cat_mulai'),
    path('ujian/<int:sesi_id>/', views.ruang_cat, name='cat_ruang'),
    path('ujian/<int:sesi_id>/simpan/', views.simpan_cat, name='cat_simpan'),
    path('ujian/<int:sesi_id>/kumpulkan/', views.kumpulkan_cat, name='cat_kumpulkan'),
    path('hasil/<int:sesi_id>/', views.hasil_cat, name='cat_hasil'),
    path('belajar/', views.pilih_belajar, name='belajar_pilih'),
    path('belajar/mulai/', views.mulai_belajar, name='belajar_mulai'),
    path('belajar/<int:sesi_id>/<int:nomor>/', views.soal_belajar, name='belajar_soal'),
    path('belajar/<int:sesi_id>/<int:nomor>/jawab/', views.jawab_belajar, name='belajar_jawab'),
    path('belajar/<int:sesi_id>/ringkasan/', views.ringkasan_belajar, name='belajar_ringkasan'),
    path('kelola/', views.kelola_beranda, name='kelola'),
    path('kelola/tinjau/', views.kelola_tinjau, name='kelola_tinjau'),
    path('kelola/tinjau/<int:soal_id>/', views.kelola_tinjau_soal, name='kelola_tinjau_soal'),
    path('kelola/tinjau/<int:soal_id>/aksi/', views.kelola_aksi, name='kelola_aksi'),
    path('kelola/soal/<int:soal_id>/ubah/', views.kelola_ubah, name='kelola_ubah'),
]
