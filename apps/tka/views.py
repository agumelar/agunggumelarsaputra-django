import json
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.utils import timezone
from django.db.models import Max

from .models import TkaPackage, TkaQuestion, TkaAttempt
from apps.gamification.models import XPHistory


def tka_list_view(request):
    """
    Daftar 10 Paket Drilling & Simulator CBT TKA PPLG.
    Menampilkan status pengerjaan, skor tertinggi, dan kelulusan siswa.
    """
    packages = TkaPackage.objects.filter(is_published=True).order_by('urutan')

    user_best_attempts = {}
    if request.user.is_authenticated:
        attempts = TkaAttempt.objects.filter(user=request.user)
        for att in attempts:
            pkg_id = att.package_id
            if pkg_id not in user_best_attempts or att.score > user_best_attempts[pkg_id].score:
                user_best_attempts[pkg_id] = att

    context = {
        'packages': packages,
        'user_best_attempts': user_best_attempts,
        'active_nav': 'tka',
    }
    return render(request, 'tka/tka_list.html', context)


def tka_detail_view(request, slug):
    """
    Halaman Pengantar Paket TKA: Bedah Materi, Tips Guru, Petunjuk Pengerjaan, dan Riwayat Attempt.
    """
    package = get_object_or_404(TkaPackage, slug=slug, is_published=True)
    all_packages = TkaPackage.objects.filter(is_published=True).order_by('urutan')

    attempts = []
    best_attempt = None
    if request.user.is_authenticated:
        attempts = TkaAttempt.objects.filter(user=request.user, package=package).order_by('-completed_at')
        best_attempt = attempts.order_by('-score').first()

    context = {
        'package': package,
        'all_packages': all_packages,
        'attempts': attempts,
        'best_attempt': best_attempt,
        'active_nav': 'tka',
    }
    return render(request, 'tka/tka_detail.html', context)


@login_required
def tka_exam_view(request, slug):
    """
    Antarmuka Ujian CBT Interaktif (60 Soal, Timer Mundur, Navigasi Nomor Soal, Keyboard Shortcut).
    """
    package = get_object_or_404(TkaPackage, slug=slug, is_published=True)
    questions = package.questions.all().order_by('urutan')

    if not questions.exists():
        messages.error(request, "Paket soal ini belum memiliki butir soal.")
        return redirect('tka:tka_detail', slug=slug)

    # Format JSON payload untuk Alpine.js CBT engine
    questions_data = []
    for q in questions:
        questions_data.append({
            'id': q.id,
            'number': q.urutan,
            'category': q.category,
            'text': q.question_text,
            'options': [
                {'key': 'A', 'text': q.option_a},
                {'key': 'B', 'text': q.option_b},
                {'key': 'C', 'text': q.option_c},
                {'key': 'D', 'text': q.option_d},
                {'key': 'E', 'text': q.option_e},
            ]
        })

    context = {
        'package': package,
        'questions_json': json.dumps(questions_data),
        'total_questions': len(questions_data),
        'duration_seconds': package.durasi_menit * 60,
        'active_nav': 'tka',
    }
    return render(request, 'tka/tka_exam.html', context)


@login_required
@require_POST
def tka_submit_view(request, slug):
    """
    Auto-Scoring Engine: Memproses seluruh jawaban siswa, menghitung skor 0-100, award XP, dan menyimpan attempt.
    """
    package = get_object_or_404(TkaPackage, slug=slug, is_published=True)
    questions = package.questions.all().order_by('urutan')

    total_questions = questions.count()
    if total_questions == 0:
        messages.error(request, "Terjadi kesalahan: Bank soal kosong.")
        return redirect('tka:tka_detail', slug=slug)

    # Ambil raw payload dari request POST
    raw_answers = request.POST.get('answers_payload', '{}')
    time_spent = int(request.POST.get('time_spent_seconds', 0))

    try:
        user_answers = json.loads(raw_answers)
    except json.JSONDecodeError:
        user_answers = {}

    correct_count = 0
    for q in questions:
        q_id_str = str(q.id)
        selected = user_answers.get(q_id_str, '').upper()
        if selected == q.correct_answer:
            correct_count += 1

    score = round((correct_count / total_questions) * 100, 1)
    wrong_count = total_questions - correct_count
    is_passed = score >= package.passing_grade

    # Bonus XP formula: 10 + round((score / 100) * 50)
    bonus_xp = package.xp_base + round((score / 100) * 50)

    # Hitung nomor attempt
    previous_attempts_count = TkaAttempt.objects.filter(user=request.user, package=package).count()
    attempt_number = previous_attempts_count + 1

    attempt = TkaAttempt.objects.create(
        user=request.user,
        package=package,
        attempt_number=attempt_number,
        score=score,
        total_questions=total_questions,
        correct_answers=correct_count,
        wrong_answers=wrong_count,
        user_answers=user_answers,
        xp_earned=bonus_xp,
        is_passed=is_passed,
        time_spent_seconds=time_spent
    )

    # Award XP to Student
    request.user.xp += bonus_xp
    request.user.recalculate_level()
    request.user.save(update_fields=['xp', 'level'])

    XPHistory.objects.create(
        user=request.user,
        amount=bonus_xp,
        category='tka',
        description=f'Simulasi CBT {package.kode} (Skor: {score}%)'
    )

    return redirect('tka:tka_result', slug=package.slug, attempt_id=attempt.id)


@login_required
def tka_result_view(request, slug, attempt_id):
    """
    Halaman Hasil & Pembahasan: Skor, Passing Grade, Perolehan XP, dan Review Butir Soal Lengkap.
    """
    package = get_object_or_404(TkaPackage, slug=slug, is_published=True)
    attempt = get_object_or_404(TkaAttempt, id=attempt_id, user=request.user, package=package)
    questions = package.questions.all().order_by('urutan')

    # Buat review data per soal
    question_reviews = []
    for q in questions:
        q_id_str = str(q.id)
        user_choice = attempt.user_answers.get(q_id_str, '-')
        is_correct = (user_choice == q.correct_answer)

        options_map = {
            'A': q.option_a,
            'B': q.option_b,
            'C': q.option_c,
            'D': q.option_d,
            'E': q.option_e,
        }

        question_reviews.append({
            'question': q,
            'user_choice': user_choice,
            'user_choice_text': options_map.get(user_choice, 'Tidak Dijawab'),
            'correct_answer': q.correct_answer,
            'correct_answer_text': options_map.get(q.correct_answer, ''),
            'is_correct': is_correct,
            'explanation': q.explanation,
        })

    context = {
        'package': package,
        'attempt': attempt,
        'question_reviews': question_reviews,
        'active_nav': 'tka',
    }
    return render(request, 'tka/tka_result.html', context)
