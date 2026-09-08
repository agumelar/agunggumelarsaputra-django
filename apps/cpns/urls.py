from django.urls import path
from . import views

app_name = 'cpns'

urlpatterns = [
    path('', views.cpns_landing_view, name='landing'),
    path('packages/', views.cpns_package_list_view, name='package_list'),
    path('packages/<slug:slug>/', views.cpns_package_detail_view, name='package_detail'),
    path('exam/<slug:slug>/', views.cpns_cbt_exam_view, name='cbt_exam'),
    path('exam/<slug:slug>/submit/', views.cpns_cbt_submit_view, name='cbt_submit'),
    path('result/<slug:slug>/<int:attempt_id>/', views.cpns_result_view, name='cbt_result'),
]
