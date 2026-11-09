from django.urls import path
from django.views.generic import RedirectView

from . import views

app_name = 'cpns'

class _AlihTanpaParameter(RedirectView):
    """RedirectView meneruskan slug dan id alamat lama ke reverse tujuan; di sini dibuang."""

    def get_redirect_url(self, *args, **kwargs):
        return super().get_redirect_url()


def _alih(tujuan):
    return _AlihTanpaParameter.as_view(pattern_name=tujuan, permanent=True, query_string=False)


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
    path('kelola/cakupan/', views.kelola_cakupan, name='kelola_cakupan'),
    path('kelola/laporan/', views.kelola_laporan, name='kelola_laporan'),
    path('kelola/laporan/<int:laporan_id>/selesai/', views.kelola_laporan_selesai, name='kelola_laporan_selesai'),
    path('kelola/soal/<int:soal_id>/ubah/', views.kelola_ubah, name='kelola_ubah'),
    # Alamat lama yang sudah dibagikan: dialihkan permanen ke halaman baru.
    path('packages/', _alih('cpns:beranda')),
    path('packages/<slug:slug>/', _alih('cpns:beranda')),
    path('exam/<slug:slug>/', _alih('cpns:dasbor')),
    path('exam/<slug:slug>/submit/', _alih('cpns:dasbor')),
    path('result/<slug:slug>/<int:attempt_id>/', _alih('cpns:riwayat')),
]
