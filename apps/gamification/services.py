from django.contrib.auth import get_user_model
from django.db.models import Count, Max, Sum, Q
from apps.admin_panel.models import EnrollmentToken, UserEnrollment
from apps.pembelajaran.models import UserProgress
from apps.tka.models import TkaAttempt
from apps.literasi.models import LiterasiReport

User = get_user_model()


def get_leaderboard_data(subject='all', target_class='all', token_id=None, current_user=None, limit=50):
    """
    Kalkulasi peringkat Live Leaderboard Siswa RPL.
    Mirroring logika get leaderboard dari Astro legacy.
    """
    # 1. Base query all students
    students_qs = User.objects.filter(role=User.ROLE_SISWA)

    # 2. Filter by Token or Class
    if token_id and str(token_id) not in ['all', '']:
        try:
            tid = int(token_id)
            enrolled_user_ids = UserEnrollment.objects.filter(token_id=tid).values_list('user_id', flat=True)
            students_qs = students_qs.filter(id__in=enrolled_user_ids)
        except (ValueError, TypeError):
            pass
    elif target_class and target_class not in ['all', 'Semua', 'Semua Kelas', 'Semua Siswa & Rombel (Global)']:
        clean_target = target_class.strip()
        # Direct class match or enrolled token class match
        enrolled_user_ids = UserEnrollment.objects.filter(
            Q(token__target_class__iexact=clean_target) | Q(token__token__iexact=clean_target)
        ).values_list('user_id', flat=True)
        students_qs = students_qs.filter(
            Q(kelas__iexact=clean_target) | Q(id__in=enrolled_user_ids)
        )

    student_list = list(students_qs)
    if not student_list:
        return {
            'ranked_list': [],
            'top3': [],
            'current_user_rank': None,
            'points_to_next': 0,
            'total_students': 0,
            'tokens_list': EnrollmentToken.objects.filter(is_active=True).order_by('-created_at'),
        }

    student_ids = [s.id for s in student_list]

    # 3. Aggregate metrics in bulk
    progress_counts = dict(
        UserProgress.objects.filter(user_id__in=student_ids)
        .values('user_id')
        .annotate(c=Count('id'))
        .values_list('user_id', 'c')
    )

    tka_stats = dict(
        TkaAttempt.objects.filter(user_id__in=student_ids)
        .values('user_id')
        .annotate(max_score=Max('score'), count=Count('id'))
        .values_list('user_id', 'max_score')
    )

    tka_counts = dict(
        TkaAttempt.objects.filter(user_id__in=student_ids)
        .values('user_id')
        .annotate(c=Count('id'))
        .values_list('user_id', 'c')
    )

    literasi_counts = dict(
        LiterasiReport.objects.filter(user_id__in=student_ids)
        .values('user_id')
        .annotate(c=Count('id'))
        .values_list('user_id', 'c')
    )

    # 4. Attach metrics to student objects
    for s in student_list:
        s.modules_count = progress_counts.get(s.id, 0)
        s.tka_top_score = tka_stats.get(s.id, 0) or 0
        s.tka_count = tka_counts.get(s.id, 0)
        s.literasi_count = literasi_counts.get(s.id, 0)

    # 5. Sorting by subject
    if subject in ['orientasi-pplg', 'modul']:
        student_list.sort(key=lambda s: (s.modules_count, s.xp), reverse=True)
    elif subject == 'tka':
        student_list.sort(key=lambda s: (s.tka_top_score, s.xp), reverse=True)
    elif subject == 'literasi':
        student_list.sort(key=lambda s: (s.literasi_count, s.xp), reverse=True)
    else:  # 'all'
        student_list.sort(key=lambda s: s.xp, reverse=True)

    # 6. Assign rank
    current_user_rank_obj = None
    points_to_next = 0

    for idx, s in enumerate(student_list):
        s.rank = idx + 1
        if current_user and current_user.is_authenticated and s.id == current_user.id:
            current_user_rank_obj = s
            if idx > 0:
                points_to_next = max(1, student_list[idx - 1].xp - s.xp)

    top3 = student_list[:3]
    top_limit = student_list[:limit]

    tokens_list = EnrollmentToken.objects.filter(is_active=True).order_by('-created_at')

    return {
        'ranked_list': top_limit,
        'top3': top3,
        'current_user_rank': current_user_rank_obj,
        'points_to_next': points_to_next,
        'total_students': len(student_list),
        'tokens_list': tokens_list,
    }
