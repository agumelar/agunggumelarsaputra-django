from django.urls import path
from . import views

app_name = 'pembelajaran'

urlpatterns = [
    path('', views.modul_list_view, name='modul_list'),
    path('<slug:slug>/', views.modul_detail_view, name='modul_detail'),
    path('<slug:slug>/mark-read/', views.mark_material_read_view, name='mark_read'),
    path('<slug:slug>/checkpoint/', views.claim_checkpoint_view, name='claim_checkpoint'),
    path('<slug:slug>/submit-lkpd/', views.submit_lkpd_view, name='submit_lkpd'),
    path('<slug:slug>/submit-refleksi/', views.submit_reflection_view, name='submit_refleksi'),
    path('<slug:slug>/complete/', views.complete_modul_view, name='complete_modul'),
]
