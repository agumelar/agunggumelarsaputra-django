from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages


def login_view(request):
    """Placeholder view untuk autentikasi login pengguna."""
    if request.user.is_authenticated:
        return redirect('core:home')
    return render(request, 'accounts/login.html')


def logout_view(request):
    """View untuk logout pengguna."""
    logout(request)
    messages.info(request, 'Anda telah berhasil keluar dari sistem.')
    return redirect('core:home')


@login_required
def profile_view(request):
    """View profil pengguna."""
    return render(request, 'accounts/profile.html', {'user': request.user})
