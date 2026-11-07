from django.urls import path

from . import views

app_name = 'cpns'

urlpatterns = [
    path('', views.beranda, name='beranda'),
    path('dasbor/', views.dasbor_sementara, name='dasbor'),
    path('simulasi/<slug:kode>/mulai/', views.mulai_cat, name='cat_mulai'),
    path('ujian/<int:sesi_id>/', views.ruang_cat, name='cat_ruang'),
    path('ujian/<int:sesi_id>/simpan/', views.simpan_cat, name='cat_simpan'),
    path('ujian/<int:sesi_id>/kumpulkan/', views.kumpulkan_cat, name='cat_kumpulkan'),
    path('hasil/<int:sesi_id>/', views.hasil_cat, name='cat_hasil'),
]
