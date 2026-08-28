from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.utils import timezone
from django.http import HttpResponse

from .models import Modul, UserSubmission, UserProgress
from .forms import LkpdSubmissionForm, ReflectionSubmissionForm
from apps.gamification.models import XPHistory


def modul_list_view(request):
    """
    Daftar 16 Modul Orientasi PPLG / Konsentrasi Keahlian RPL.
    Menampilkan status progres penyelesaian dan akumulasi XP per modul.
    """
    modul_list = Modul.objects.filter(is_published=True).order_by('urutan')
    
    completed_modul_ids = set()
    submitted_lkpd_ids = set()

    if request.user.is_authenticated:
        completed_modul_ids = set(
            UserProgress.objects.filter(user=request.user).values_list('modul_id', flat=True)
        )
        submitted_lkpd_ids = set(
            UserSubmission.objects.filter(user=request.user, submission_type='lkpd').values_list('modul_id', flat=True)
        )

    context = {
        'modul_list': modul_list,
        'completed_modul_ids': completed_modul_ids,
        'submitted_lkpd_ids': submitted_lkpd_ids,
        'active_nav': 'pembelajaran',
    }
    return render(request, 'pembelajaran/modul_list.html', context)


def modul_detail_view(request, slug):
    """
    4-Tab Reader Modul Pembelajaran:
    Tab 1: Materi & Konsep Interaktif
    Tab 2: Form LKPD Interaktif & Bukti Google Drive
    Tab 3: Jurnal Refleksi Pembelajaran Mandiri
    Tab 4: Panduan KKTP & Hasil Penilaian Guru
    """
    modul = get_object_or_404(Modul, slug=slug, is_published=True)
    all_modules = Modul.objects.filter(is_published=True).order_by('urutan')

    is_completed = False
    lkpd_submission = None
    reflection_submission = None

    if request.user.is_authenticated:
        is_completed = UserProgress.objects.filter(user=request.user, modul=modul).exists()
        lkpd_submission = UserSubmission.objects.filter(user=request.user, modul=modul, submission_type='lkpd').first()
        reflection_submission = UserSubmission.objects.filter(user=request.user, modul=modul, submission_type='reflection').first()

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

    context = {
        'modul': modul,
        'all_modules': all_modules,
        'prev_modul': prev_modul,
        'next_modul': next_modul,
        'is_completed': is_completed,
        'lkpd_submission': lkpd_submission,
        'reflection_submission': reflection_submission,
        'lkpd_form': lkpd_form,
        'reflection_form': reflection_form,
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
def submit_lkpd_view(request, slug):
    """
    HTMX Endpoint: Submisi LKPD & Google Drive Link evidence oleh siswa (+25 XP).
    """
    modul = get_object_or_404(Modul, slug=slug, is_published=True)
    form = LkpdSubmissionForm(request.POST)

    if form.is_valid():
        drive_url = form.cleaned_data['drive_url']
        work_summary = form.cleaned_data['work_summary']
        additional_notes = form.cleaned_data['additional_notes']

        submission, created = UserSubmission.objects.update_or_create(
            user=request.user,
            modul=modul,
            submission_type='lkpd',
            defaults={
                'drive_url': drive_url,
                'form_data': {
                    'work_summary': work_summary,
                    'additional_notes': additional_notes,
                },
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
            'message': 'LKPD & Link Google Drive Evidence berhasil dikirim!',
            'just_claimed': created,
        }
    else:
        context = {
            'modul': modul,
            'lkpd_form': form,
            'success': False,
            'message': 'Harap periksa isian form LKPD Anda.',
        }

    return render(request, 'pembelajaran/partials/lkpd_status.html', context)


@login_required
@require_POST
def submit_reflection_view(request, slug):
    """
    HTMX Endpoint: Submisi Jurnal Refleksi oleh siswa (+15 XP).
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
            'success': True,
            'message': 'Jurnal Refleksi berhasil disimpan!',
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
