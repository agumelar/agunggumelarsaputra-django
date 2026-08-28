from django.urls import path
from . import views

app_name = 'tka'

urlpatterns = [
    path('', views.tka_list_view, name='tka_list'),
    path('<slug:slug>/', views.tka_detail_view, name='tka_detail'),
]
