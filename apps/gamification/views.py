from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Sum
from .services import get_leaderboard_data
from .models import XPHistory
from apps.admin_panel.views import teacher_check


def leaderboard_view(request):
    """
    Papan Peringkat (Live Leaderboard) Siswa RPL SMKN 1 Rongga.
    Mendukung filter Topik/Subject, Rombel/Kelas, Sesi Token, dan HTMX partial swap.
    """
    subject = request.GET.get('subject', 'all')
    target_class = request.GET.get('class', 'all')
    token_id = request.GET.get('tokenId', '')
    limit = int(request.GET.get('limit', 50))

    data = get_leaderboard_data(
        subject=subject,
        target_class=target_class,
        token_id=token_id,
        current_user=request.user,
        limit=limit
    )

    context = {
        'leaderboard': data['ranked_list'],
        'top3': data['top3'],
        'current_user_rank': data['current_user_rank'],
        'points_to_next': data['points_to_next'],
        'total_students': data['total_students'],
        'tokens_list': data['tokens_list'],
        'selected_subject': subject,
        'selected_class': target_class,
        'selected_token': token_id,
        'active_nav': 'leaderboard',
    }

    if request.htmx:
        return render(request, 'gamification/partials/leaderboard_table.html', context)

    return render(request, 'gamification/leaderboard.html', context)


@login_required
def xp_history_view(request):
    """
    Riwayat Perolehan XP & Level Progression Siswa.
    """
    history_logs = XPHistory.objects.filter(user=request.user).order_by('-created_at')
    
    # Category Breakdown with defaults
    breakdown = {
        'modul_lkpd': 0,
        'tka': 0,
        'literasi': 0,
        'peer_review': 0,
    }
    for item in XPHistory.objects.filter(user=request.user).values('category').annotate(total=Sum('amount')):
        cat = item['category']
        if cat in ['modul', 'lkpd']:
            breakdown['modul_lkpd'] += item['total']
        elif cat in breakdown:
            breakdown[cat] = item['total']

    # Level tiers definition
    level_tiers = [
        {'level': 1, 'title': 'Novice Coder', 'min_xp': 0, 'max_xp': 99, 'badge': '🌱'},
        {'level': 2, 'title': 'Junior Developer', 'min_xp': 100, 'max_xp': 249, 'badge': '⚡'},
        {'level': 3, 'title': 'Frontend Crafter', 'min_xp': 250, 'max_xp': 499, 'badge': '🎨'},
        {'level': 4, 'title': 'Backend Artisan', 'min_xp': 500, 'max_xp': 849, 'badge': '⚙️'},
        {'level': 5, 'title': 'Fullstack Engineer', 'min_xp': 850, 'max_xp': 1299, 'badge': '🚀'},
        {'level': 6, 'title': 'DevOps Specialist', 'min_xp': 1300, 'max_xp': 1849, 'badge': '🛡️'},
        {'level': 7, 'title': 'Software Architect', 'min_xp': 1850, 'max_xp': 2499, 'badge': '🏛️'},
        {'level': 8, 'title': 'Tech Lead', 'min_xp': 2500, 'max_xp': 3499, 'badge': '👑'},
        {'level': 9, 'title': 'Staff Engineer', 'min_xp': 3500, 'max_xp': 4999, 'badge': '💎'},
        {'level': 10, 'title': 'Principal Architect', 'min_xp': 5000, 'max_xp': 99999, 'badge': '🌌'},
    ]

    current_tier = next((t for t in level_tiers if t['level'] == request.user.level), level_tiers[0])
    next_tier = next((t for t in level_tiers if t['level'] == request.user.level + 1), None)

    xp_in_tier = max(0, request.user.xp - current_tier['min_xp'])
    tier_range = (next_tier['min_xp'] - current_tier['min_xp']) if next_tier else 1000
    tier_progress_percent = min(100, round((xp_in_tier / tier_range) * 100)) if next_tier else 100

    context = {
        'history_logs': history_logs,
        'breakdown': breakdown,
        'level_tiers': level_tiers,
        'current_tier': current_tier,
        'next_tier': next_tier,
        'tier_progress_percent': tier_progress_percent,
        'active_nav': 'xp_history',
    }
    return render(request, 'gamification/xp_history.html', context)


@user_passes_test(teacher_check, login_url='accounts:login')
def projector_leaderboard_view(request):
    """
    Layar Proyektor Kelas Fullscreen (Realtime Classroom Scoreboard).
    Dirancang khusus untuk proyektor lab dengan visual kontras tinggi dan auto-refresh polling 10s.
    """
    subject = request.GET.get('subject', 'all')
    target_class = request.GET.get('class', 'all')
    token_id = request.GET.get('tokenId', '')

    data = get_leaderboard_data(
        subject=subject,
        target_class=target_class,
        token_id=token_id,
        limit=30
    )

    context = {
        'leaderboard': data['ranked_list'],
        'top3': data['top3'],
        'total_students': data['total_students'],
        'tokens_list': data['tokens_list'],
        'selected_subject': subject,
        'selected_class': target_class,
        'selected_token': token_id,
    }

    if request.htmx:
        return render(request, 'gamification/partials/projector_table.html', context)

    return render(request, 'gamification/projector_scoreboard.html', context)
