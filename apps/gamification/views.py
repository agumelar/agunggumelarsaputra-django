from django.shortcuts import render
from django.contrib.auth import get_user_model

User = get_user_model()


def leaderboard_view(request):
    """Papan peringkat (Leaderboard) live siswa RPL SMKN 1 Rongga."""
    top_students = User.objects.filter(role=User.ROLE_SISWA).order_by('-xp')[:50]
    return render(request, 'gamification/leaderboard.html', {'top_students': top_students})
