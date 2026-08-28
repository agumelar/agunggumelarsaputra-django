from django.urls import path
from . import views

app_name = 'pembelajaran'

urlpatterns = [
    path('', views.modul_list_view, name='modul_list'),
    path('<slug:slug>/', views.modul_detail_view, name='modul_detail'),
]
