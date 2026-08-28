from django.urls import path
from . import views

app_name = 'admin_panel'

urlpatterns = [
    path('', views.dashboard_view, name='dashboard'),
    path('tokens/', views.token_list_view, name='token_list'),
    path('tokens/create/', views.token_create_view, name='token_create'),
    path('tokens/<int:token_id>/toggle/', views.token_toggle_view, name='token_toggle'),
    path('tokens/<int:token_id>/', views.token_detail_view, name='token_detail'),
]
