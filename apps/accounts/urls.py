from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile_view, name='profile'),
    path('claim-token/', views.claim_token_view, name='claim_token'),
    path('api/check-token/', views.check_token_view, name='check_token'),
]
