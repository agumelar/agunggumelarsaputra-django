from django.urls import path
from . import views

app_name = 'literasi'

urlpatterns = [
    path('', views.literasi_hub_view, name='literasi_home'),
    path('hub/', views.literasi_hub_view, name='literasi_hub'),
    path('submit/', views.submit_literasi_view, name='submit_literasi'),
    path('<int:report_id>/', views.literasi_detail_view, name='literasi_detail'),
    path('<int:report_id>/peer-review/', views.submit_peer_review_view, name='submit_peer_review'),
]
