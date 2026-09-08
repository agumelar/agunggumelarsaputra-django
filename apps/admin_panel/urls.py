from django.urls import path
from . import views

app_name = 'admin_panel'

urlpatterns = [
    path('', views.dashboard_view, name='dashboard'),
    path('tokens/', views.token_list_view, name='token_list'),
    path('tokens/create/', views.token_create_view, name='token_create'),
    path('tokens/<int:token_id>/toggle/', views.token_toggle_view, name='token_toggle'),
    path('tokens/<int:token_id>/', views.token_detail_view, name='token_detail'),
    path('submissions/', views.submission_list_view, name='submission_list'),
    path('submissions/grade-api/', views.grade_submission_api_view, name='grade_submission_api'),
    path('submissions/review-api/', views.review_reflection_api_view, name='review_reflection_api'),
    path('submissions/export-lkpd/', views.export_lkpd_excel_view, name='export_lkpd_excel'),
    path('submissions/export-reflections/', views.export_reflections_excel_view, name='export_reflections_excel'),
    path('submissions/<int:submission_id>/grade/', views.grade_submission_view, name='grade_submission'),
    path('tka-results/', views.tka_results_view, name='tka_results'),
    path('literasi/', views.literasi_list_view, name='literasi_list'),
    path('literasi/<int:report_id>/grade/', views.literasi_grade_view, name='literasi_grade'),
]
