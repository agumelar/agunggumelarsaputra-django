from django.urls import path
from . import views

app_name = 'gamification'

urlpatterns = [
    path('leaderboard/', views.leaderboard_view, name='leaderboard'),
    path('history/', views.xp_history_view, name='xp_history'),
    path('projector/', views.projector_leaderboard_view, name='projector_leaderboard'),
]
