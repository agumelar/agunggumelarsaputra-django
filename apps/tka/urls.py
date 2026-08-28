from django.urls import path
from . import views

app_name = 'tka'

urlpatterns = [
    path('', views.tka_list_view, name='tka_list'),
    path('<slug:slug>/', views.tka_detail_view, name='tka_detail'),
    path('<slug:slug>/exam/', views.tka_exam_view, name='tka_exam'),
    path('<slug:slug>/submit/', views.tka_submit_view, name='tka_submit'),
    path('<slug:slug>/result/<int:attempt_id>/', views.tka_result_view, name='tka_result'),
]
