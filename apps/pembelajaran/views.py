import json
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.utils import timezone
from django.http import HttpResponse, JsonResponse

from .models import Modul, UserSubmission, UserProgress
from .forms import LkpdSubmissionForm, ReflectionSubmissionForm
from .checkpoints import get_gamified_quest_for_module
from .lkpd_guides import get_lkpd_guide_for_module
from apps.gamification.models import XPHistory


def modul_list_view(request):
    """
    Daftar 16 Modul Orientasi PPLG / Konsentrasi Keahlian RPL.
    Menampilkan status progres penyelesaian, gating sekuensial, dan akumulasi XP per modul.
    """
    modul_list = Modul.objects.filter(is_published=True).order_by('urutan')
    
    completed_modul_ids = set()
    submitted_lkpd_ids = set()
    unlocked_modul_ids = set()

    is_teacher = request.user.is_authenticated and (request.user.is_staff or getattr(request.user, 'is_guru', False))

    if request.user.is_authenticated:
        completed_modul_ids = set(
            UserProgress.objects.filter(user=request.user).values_list('modul_id', flat=True)
        )
        submitted_lkpd_ids = set(
            UserSubmission.objects.filter(user=request.user, submission_type='lkpd').values_list('modul_id', flat=True)
        )

    # Gating Sekuensial: Modul 1 selalu terbuka, Modul N+1 terbuka jika Modul N selesai
    for m in modul_list:
        if is_teacher or m.urutan == 1:
            unlocked_modul_ids.add(m.id)
        else:
            prev_m = next((pm for pm in modul_list if pm.urutan == m.urutan - 1), None)
            if prev_m and prev_m.id in completed_modul_ids:
                unlocked_modul_ids.add(m.id)

    context = {
        'modul_list': modul_list,
        'completed_modul_ids': completed_modul_ids,
        'submitted_lkpd_ids': submitted_lkpd_ids,
        'unlocked_modul_ids': unlocked_modul_ids,
        'is_teacher': is_teacher,
        'active_nav': 'pembelajaran',
    }
    return render(request, 'pembelajaran/modul_list.html', context)


def modul_detail_view(request, slug):
    """
    4-Tab Reader Modul Pembelajaran dengan Sequential Gating & Anti Copy-Paste Protection:
    Tab 1: Materi & Konsep Interaktif
    Tab 2: Form LKPD Interaktif & Bukti Google Drive (+25 XP)
    Tab 3: Jurnal Refleksi Pembelajaran Mandiri (+15 XP) [Lokasi Tombol Selesai Modul]
    Tab 4: Panduan KKTP & Hasil Penilaian Guru (Level 0 - Level 4)
    """
    modul = get_object_or_404(Modul, slug=slug, is_published=True)
    all_modules = Modul.objects.filter(is_published=True).order_by('urutan')

    is_teacher = request.user.is_authenticated and (request.user.is_staff or getattr(request.user, 'is_guru', False))
    is_completed = False
    lkpd_submission = None
    reflection_submission = None

    if request.user.is_authenticated:
        is_completed = UserProgress.objects.filter(user=request.user, modul=modul).exists()
        lkpd_submission = UserSubmission.objects.filter(user=request.user, modul=modul, submission_type='lkpd').first()
        reflection_submission = UserSubmission.objects.filter(user=request.user, modul=modul, submission_type='reflection').first()

    # Gating Sekuensial: Siswa non-guru harus menyelesaikan modul prasyarat
    if not is_teacher and modul.urutan > 1:
        prev_m = Modul.objects.filter(urutan=modul.urutan - 1, is_published=True).first()
        if prev_m:
            prereq_completed = request.user.is_authenticated and UserProgress.objects.filter(user=request.user, modul=prev_m).exists()
            if not prereq_completed:
                return render(request, 'pembelajaran/modul_locked.html', {
                    'modul': modul,
                    'prereq_modul': prev_m,
                    'active_nav': 'pembelajaran',
                })

    # Inisialisasi Form
    initial_lkpd = {}
    if lkpd_submission:
        initial_lkpd = {
            'drive_url': lkpd_submission.drive_url,
            'work_summary': lkpd_submission.form_data.get('work_summary', ''),
            'additional_notes': lkpd_submission.form_data.get('additional_notes', ''),
        }
    lkpd_form = LkpdSubmissionForm(initial=initial_lkpd)

    initial_reflection = {}
    if reflection_submission:
        initial_reflection = {
            'understanding': reflection_submission.form_data.get('understanding', ''),
            'obstacle': reflection_submission.form_data.get('obstacle', ''),
            'action_plan': reflection_submission.form_data.get('action_plan', ''),
        }
    reflection_form = ReflectionSubmissionForm(initial=initial_reflection)

    # Navigasi Modul Sebelum & Sesudah
    prev_modul = Modul.objects.filter(urutan__lt=modul.urutan, is_published=True).order_by('-urutan').first()
    next_modul = Modul.objects.filter(urutan__gt=modul.urutan, is_published=True).order_by('urutan').first()

    # Checkpoint Gamifikasi State
    has_passed_checkpoint = False
    if is_teacher or is_completed or (lkpd_submission is not None):
        has_passed_checkpoint = True
    elif request.user.is_authenticated:
        has_passed_checkpoint = UserSubmission.objects.filter(
            user=request.user, modul=modul, submission_type='checkpoint'
        ).exists()

    quest = get_gamified_quest_for_module(modul.slug, modul.judul)
    quest_json = json.dumps(quest)
    lkpd_guide = get_lkpd_guide_for_module(modul.slug, modul.judul)

    is_modul_1 = (modul.urutan == 1 or modul.slug == 'orientasi-pplg-01-pengantar-skill-passport')
    lkpd_audit_rows = []
    if lkpd_submission and isinstance(lkpd_submission.form_data, dict):
        lkpd_audit_rows = lkpd_submission.form_data.get('audit_table', [])
    lkpd_audit_rows_json = json.dumps(lkpd_audit_rows)

    context = {
        'modul': modul,
        'all_modules': all_modules,
        'prev_modul': prev_modul,
        'next_modul': next_modul,
        'is_completed': is_completed,
        'has_passed_checkpoint': has_passed_checkpoint,
        'quest': quest,
        'quest_json': quest_json,
        'lkpd_guide': lkpd_guide,
        'is_modul_1': is_modul_1,
        'lkpd_audit_rows_json': lkpd_audit_rows_json,
        'lkpd_submission': lkpd_submission,
        'reflection_submission': reflection_submission,
        'lkpd_form': lkpd_form,
        'reflection_form': reflection_form,
        'is_teacher': is_teacher,
        'active_nav': 'pembelajaran',
    }
    return render(request, 'pembelajaran/modul_detail.html', context)


@login_required
@require_POST
def mark_material_read_view(request, slug):
    """
    HTMX Endpoint: Siswa menandai telah membaca materi dan klaim +10 XP.
    """
    modul = get_object_or_404(Modul, slug=slug, is_published=True)
    progress, created = UserProgress.objects.get_or_create(user=request.user, modul=modul)

    if created:
        request.user.xp += modul.xp_materi
        request.user.recalculate_level()
        request.user.save(update_fields=['xp', 'level'])

        XPHistory.objects.create(
            user=request.user,
            amount=modul.xp_materi,
            category='modul',
            description=f'Membaca Materi Modul {modul.kode}: {modul.judul}'
        )

    context = {
        'modul': modul,
        'is_completed': True,
        'just_claimed': created,
    }
    return render(request, 'pembelajaran/partials/progress_status.html', context)


@login_required
@require_POST
def claim_checkpoint_view(request, slug):
    """
    Endpoint saat siswa menyelesaikan Mini-Game Checkpoint 3 Ronde (+15 XP).
    Membuka gerbang akses ke Form LKPD.
    """
    modul = get_object_or_404(Modul, slug=slug, is_published=True)
    quest = get_gamified_quest_for_module(modul.slug, modul.judul)
    xp_reward = quest.get('xpReward', 15)

    sub, created = UserSubmission.objects.get_or_create(
        user=request.user,
        modul=modul,
        submission_type='checkpoint',
        defaults={
            'score': 100,
            'status': 'submitted',
            'form_data': {
                'completed_at': timezone.now().isoformat(),
                'quest_id': quest.get('id', '')
            }
        }
    )

    if created:
        request.user.xp += xp_reward
        request.user.recalculate_level()
        request.user.save(update_fields=['xp', 'level'])

        XPHistory.objects.create(
            user=request.user,
            amount=xp_reward,
            category='modul',
            description=f'Menyelesaikan Mini-Game Checkpoint {modul.kode}: {modul.judul}'
        )

    return JsonResponse({
        'success': True,
        'just_claimed': created,
        'xp_earned': xp_reward if created else 0,
        'total_xp': request.user.xp,
        'message': f'Gerbang Checkpoint {modul.kode} berhasil ditaklukkan! Tab LKPD telah terbuka.'
    })


@login_required
@require_POST
def submit_lkpd_view(request, slug):
    """
    HTMX Endpoint: Submisi LKPD & Google Drive Link evidence oleh siswa (+25 XP).
    Mendukung formulir LKPD Dinamis (Modul 01 Tabel Audit) dan Standar (Modul 02-16).
    KKM Guard (73): Jika sudah dinilai dan tuntas (>= 73), terkunci dari resubmission.
    """
    modul = get_object_or_404(Modul, slug=slug, is_published=True)

    # Cek apakah sudah dinilai tuntas KKM 73
    existing = UserSubmission.objects.filter(user=request.user, modul=modul, submission_type='lkpd').first()
    if existing and existing.status == 'graded' and existing.teacher_score is not None and existing.teacher_score >= 73:
        context = {
            'modul': modul,
            'lkpd_submission': existing,
            'success': False,
            'message': 'LKPD Anda telah dinilai TUNTAS oleh Guru (KKM >= 73) dan telah terkunci.',
        }
        return render(request, 'pembelajaran/partials/lkpd_status.html', context)

    drive_url = request.POST.get('drive_url', '').strip()
    work_summary = request.POST.get('work_summary', '').strip()
    additional_notes = request.POST.get('additional_notes', '').strip()

    if not drive_url:
        return render(request, 'pembelajaran/partials/lkpd_status.html', {
            'modul': modul,
            'success': False,
            'message': 'Link folder Google Drive Evidence wajib diisi.',
        })

    is_modul_1 = (modul.urutan == 1 or modul.slug == 'orientasi-pplg-01-pengantar-skill-passport')
    form_payload = {
        'work_summary': work_summary,
        'additional_notes': additional_notes,
    }

    if is_modul_1:
        # Ekstrak baris tabel audit dinamis
        audit_table = []
        for key in sorted(request.POST.keys()):
            if key.startswith('app_name_'):
                idx = key.split('_')[-1]
                aname = request.POST.get(f'app_name_{idx}', '').strip()
                afeat = request.POST.get(f'app_feature_{idx}', '').strip()
                aroles = request.POST.get(f'app_roles_{idx}', '').strip()
                if aname:
                    audit_table.append({
                        'app_name': aname,
                        'feature': afeat,
                        'roles': aroles
                    })

        form_payload['student_name'] = request.POST.get('student_name', request.user.display_name)
        form_payload['student_nis'] = request.POST.get('student_nis', getattr(request.user, 'nis', '') or '')
        form_payload['student_class'] = request.POST.get('student_class', getattr(request.user, 'kelas', '') or '')
        form_payload['submission_date'] = request.POST.get('submission_date', timezone.now().strftime('%Y-%m-%d'))
        form_payload['audit_table'] = audit_table

    submission, created = UserSubmission.objects.update_or_create(
        user=request.user,
        modul=modul,
        submission_type='lkpd',
        defaults={
            'drive_url': drive_url,
            'form_data': form_payload,
            'status': 'submitted',
        }
    )

    if created:
        request.user.xp += modul.xp_lkpd
        request.user.recalculate_level()
        request.user.save(update_fields=['xp', 'level'])

        XPHistory.objects.create(
            user=request.user,
            amount=modul.xp_lkpd,
            category='lkpd',
            description=f'Submisi LKPD Modul {modul.kode}: {modul.judul}'
        )

    context = {
        'modul': modul,
        'lkpd_submission': submission,
        'success': True,
        'message': f'LKPD {modul.kode} & Link Google Drive Evidence berhasil dikirim!',
        'just_claimed': created,
    }
    return render(request, 'pembelajaran/partials/lkpd_status.html', context)


@login_required
@require_POST
def submit_reflection_view(request, slug):
    """
    HTMX Endpoint: Submisi Jurnal Refleksi oleh siswa (+15 XP) dan Menandai Selesai Modul.
    """
    modul = get_object_or_404(Modul, slug=slug, is_published=True)
    form = ReflectionSubmissionForm(request.POST)

    if form.is_valid():
        understanding = form.cleaned_data['understanding']
        obstacle = form.cleaned_data['obstacle']
        action_plan = form.cleaned_data['action_plan']

        submission, created = UserSubmission.objects.update_or_create(
            user=request.user,
            modul=modul,
            submission_type='reflection',
            defaults={
                'form_data': {
                    'understanding': understanding,
                    'obstacle': obstacle,
                    'action_plan': action_plan,
                },
                'status': 'submitted',
            }
        )

        # Tandai modul selesai pada UserProgress
        progress, prog_created = UserProgress.objects.get_or_create(user=request.user, modul=modul)

        if created:
            request.user.xp += modul.xp_reflection
            request.user.recalculate_level()
            request.user.save(update_fields=['xp', 'level'])

            XPHistory.objects.create(
                user=request.user,
                amount=modul.xp_reflection,
                category='modul',
                description=f'Jurnal Refleksi Modul {modul.kode}: {modul.judul}'
            )

        context = {
            'modul': modul,
            'reflection_submission': submission,
            'is_completed': True,
            'success': True,
            'message': 'Jurnal Refleksi berhasil disimpan! Modul ini telah tuntas ditandai selesai.',
            'just_claimed': created,
        }
    else:
        context = {
            'modul': modul,
            'reflection_form': form,
            'success': False,
            'message': 'Harap lengkapi seluruh pertanyaan refleksi.',
        }

    return render(request, 'pembelajaran/partials/reflection_status.html', context)
