import json
from django.shortcuts import render, get_object_or_404, redirect
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.db.models import Count

from .models import CpnsPackage, CpnsQuestion, CpnsAttempt

try:
    from apps.gamification.models import XPHistory
except ImportError:
    XPHistory = None


def cpns_landing_view(request):
    """
    Beranda Portal Subdomain cpns.agunggumelarsaputra.com.
    Menampilkan fitur unggulan, statistik latihan, dan daftar paket populer.
    """
    packages = CpnsPackage.objects.filter(is_published=True).order_by('urutan')
    total_questions = CpnsQuestion.objects.count()
    total_attempts = CpnsAttempt.objects.count()

    context = {
        'packages': packages,
        'total_questions': total_questions,
        'total_attempts': total_attempts,
        'active_nav': 'cpns',
    }
    return render(request, 'cpns/landing.html', context)


def cpns_package_list_view(request):
    """
    Katalog Paket Drilling CPNS: Memisahkan SKD BKN dan SKB Guru secara rapi.
    """
    skd_packages = CpnsPackage.objects.filter(is_published=True, tipe_ujian='SKD').order_by('urutan')
    skb_packages = CpnsPackage.objects.filter(is_published=True, tipe_ujian='SKB').order_by('urutan')

    user_best_attempts = {}
    if request.user.is_authenticated:
        attempts = CpnsAttempt.objects.filter(user=request.user)
        for att in attempts:
            pkg_id = att.package_id
            if pkg_id not in user_best_attempts or att.total_skor > user_best_attempts[pkg_id].total_skor:
                user_best_attempts[pkg_id] = att

    context = {
        'skd_packages': skd_packages,
        'skb_packages': skb_packages,
        'user_best_attempts': user_best_attempts,
        'active_nav': 'cpns',
    }
    return render(request, 'cpns/package_list.html', context)


def cpns_package_detail_view(request, slug):
    """
    Halaman Pengantar & Tata Tertib Paket Ujian: Kisi-kisi, Passing Grade, dan Riwayat Percobaan.
    """
    package = get_object_or_404(CpnsPackage, slug=slug, is_published=True)
    all_packages = CpnsPackage.objects.filter(is_published=True).exclude(id=package.id)[:4]

    attempts = []
    best_attempt = None
    if request.user.is_authenticated:
        attempts = CpnsAttempt.objects.filter(user=request.user, package=package).order_by('-completed_at')
        best_attempt = attempts.order_by('-total_skor').first()

    context = {
        'package': package,
        'all_packages': all_packages,
        'attempts': attempts,
        'best_attempt': best_attempt,
        'active_nav': 'cpns',
    }
    return render(request, 'cpns/package_detail.html', context)


def cpns_cbt_exam_view(request, slug):
    """
    Ruang Simulasi CBT CAT BKN Interaktif (Alpine.js State Engine, Timer, dan Navigasi 110 Soal).
    Mendukung mode 'SIMULASI_CAT' (ujian ketat) dan 'DRILLING_BEBAS' (latihan fleksibel).
    """
    package = get_object_or_404(CpnsPackage, slug=slug, is_published=True)
    questions = package.questions.all().order_by('urutan')

    if not questions.exists():
        messages.error(request, "Paket soal ini belum memiliki butir pertanyaan.")
        return redirect('cpns:package_detail', slug=slug)

    mode = request.GET.get('mode', 'SIMULASI_CAT')

    # Format JSON payload untuk Alpine.js CBT engine
    questions_data = []
    for q in questions:
        explanation_payload = None
        if mode == 'DRILLING_BEBAS':
            explanation_payload = {
                'concept': q.bedah_konsep,
                'distractor': q.alasan_pengecoh,
                'fast_tip': q.tips_cepat,
                'correct_answer': q.kunci_jawaban,
                'tkp_weights': q.bobot_tkp,
            }

        questions_data.append({
            'id': q.id,
            'number': q.urutan,
            'subtest': q.subtes,
            'topic': q.subtopik,
            'text': q.pertanyaan,
            'options': [
                {'key': 'A', 'text': q.opsi_a},
                {'key': 'B', 'text': q.opsi_b},
                {'key': 'C', 'text': q.opsi_c},
                {'key': 'D', 'text': q.opsi_d},
                {'key': 'E', 'text': q.opsi_e},
            ],
            'explanation': explanation_payload
        })

    duration_seconds = package.durasi_menit * 60 if mode == 'SIMULASI_CAT' else 0

    context = {
        'package': package,
        'questions_json': json.dumps(questions_data),
        'total_questions': len(questions_data),
        'mode': mode,
        'duration_seconds': duration_seconds,
        'active_nav': 'cpns',
    }
    return render(request, 'cpns/cbt_room.html', context)


@require_POST
def cpns_cbt_submit_view(request, slug):
    """
    Endpoint Auto-Scoring CAT BKN: Memproses seluruh jawaban peserta, mengevaluasi bobot TKP & TWK/TIU,
    menghitung status kelulusan passing grade simultan, dan menyimpan attempt.
    """
    package = get_object_or_404(CpnsPackage, slug=slug, is_published=True)
    raw_answers = request.POST.get('answers_payload', '{}')
    time_spent = int(request.POST.get('time_spent_seconds', 0))
    mode = request.POST.get('mode', 'SIMULASI_CAT')

    try:
        answers = json.loads(raw_answers)
    except json.JSONDecodeError:
        answers = {}

    session_key = ''
    if not request.user.is_authenticated:
        if not request.session.session_key:
            request.session.create()
        session_key = request.session.session_key

    attempt = CpnsAttempt.evaluate_and_create(
        user=request.user,
        package=package,
        mode=mode,
        answers=answers,
        time_spent_seconds=time_spent,
        session_key=session_key
    )

    # Gamification XP award jika user login
    if request.user.is_authenticated and XPHistory:
        bonus_xp = package.xp_base + (20 if attempt.status_lulus else 5)
        request.user.xp += bonus_xp
        if hasattr(request.user, 'recalculate_level'):
            request.user.recalculate_level()
        request.user.save(update_fields=['xp', 'level'])

        XPHistory.objects.create(
            user=request.user,
            amount=bonus_xp,
            category='cpns',
            description=f'Simulasi CPNS {package.kode} (Total Skor: {attempt.total_skor})'
        )

    return redirect('cpns:cbt_result', slug=package.slug, attempt_id=attempt.id)


def cpns_result_view(request, slug, attempt_id):
    """
    Halaman Hasil & Review Konsep Tuntas: Skor per pilar, Passing Grade, dan Review 3 Tingkat Pembahasan.
    Mendukung filter interaktif HTMX (Semua, Salah, Per Subtes).
    """
    package = get_object_or_404(CpnsPackage, slug=slug, is_published=True)
    
    if request.user.is_authenticated:
        attempt = get_object_or_404(CpnsAttempt, id=attempt_id, package=package, user=request.user)
    else:
        session_key = request.session.session_key or ''
        attempt = get_object_or_404(CpnsAttempt, id=attempt_id, package=package, session_key=session_key)

    filter_type = request.GET.get('filter', 'all')
    questions = package.questions.all().order_by('urutan')

    reviews = []
    for q in questions:
        user_choice = attempt.jawaban_peserta.get(str(q.id), '')
        is_answered = bool(user_choice)
        
        earned_points = 0
        is_correct = False
        if q.subtes == 'TKP':
            earned_points = (q.bobot_tkp or {}).get(user_choice, 0) if user_choice else 0
            is_correct = earned_points == 5
        else:
            is_correct = (user_choice == q.kunci_jawaban)
            earned_points = 5 if is_correct else 0

        # Filter logika
        if filter_type == 'salah' and is_correct:
            continue
        elif filter_type in ['TWK', 'TIU', 'TKP', 'SKB_GURU'] and q.subtes != filter_type:
            continue

        reviews.append({
            'question': q,
            'user_choice': user_choice,
            'is_answered': is_answered,
            'is_correct': is_correct,
            'earned_points': earned_points,
        })

    context = {
        'package': package,
        'attempt': attempt,
        'reviews': reviews,
        'filter_type': filter_type,
        'active_nav': 'cpns',
    }

    if request.headers.get('HX-Request') == 'true':
        return render(request, 'cpns/partials/review_list.html', context)

    return render(request, 'cpns/result_review.html', context)
