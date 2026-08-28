from django.shortcuts import render
from django.contrib.auth.decorators import user_passes_test


def teacher_check(user):
    return user.is_authenticated and (user.is_guru or user.is_staff)


@user_passes_test(teacher_check, login_url='accounts:login')
def dashboard_view(request):
    """Dashboard Guru Pengampu RPL untuk monitoring dan evaluasi."""
    return render(request, 'admin_panel/dashboard.html')
