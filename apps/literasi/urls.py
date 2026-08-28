from django.urls import path
from . import views

app_name = 'literasi'

urlpatterns = [
    path('', views.literasi_home_view, name='literasi_home'),
]
