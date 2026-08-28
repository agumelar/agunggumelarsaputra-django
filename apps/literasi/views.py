from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.utils import timezone
from django.http import HttpResponse

from .models import LiterasiReport, LiterasiPeerReview
from .forms import LiterasiReportForm, PeerReviewForm
from apps.gamification.models import XPHistory


def literasi_hub_view(request):
    """
    Hub Utama Rabu Literasi (RESIK):
    Tab 1: Form Tulis Laporan Baru (+ Live Word Counter)
    Tab 2: Riwayat Laporan Saya
    Tab 3: Feed & Peer Review Teman Sekelas
    """
    user_reports = []
    peer_feed = []

    if request.user.is_authenticated:
        user_reports = LiterasiReport.objects.filter(user=request.user).prefetch_related('peer_reviews').order_by('-report_date', '-created_at')

    # Feed publik seluruh siswa (20 laporan terbaru)
    peer_feed = LiterasiReport.objects.select_related('user').prefetch_related('peer_reviews', 'peer_reviews__reviewer').order_by('-report_date', '-created_at')[:25]

    report_form = LiterasiReportForm(initial={'report_date': timezone.now().date(), 'week_number': 1})
    peer_form = PeerReviewForm()

    context = {
        'user_reports': user_reports,
        'peer_feed': peer_feed,
        'report_form': report_form,
        'peer_form': peer_form,
        'active_nav': 'literasi',
    }
    return render(request, 'literasi/literasi_hub.html', context)


@login_required
@require_POST
def submit_literasi_view(request):
    """
    HTMX Endpoint: Submisi Laporan Literasi RESIK (+35 XP).
    Memvalidasi jumlah kata (minimal 100 kata).
    """
    form = LiterasiReportForm(request.POST)

    if form.is_valid():
        report = form.save(commit=False)
        report.user = request.user
        words = report.summary.strip().split()
        report.word_count = len(words)
        report.status = 'submitted'
        report.save()

        # Award +35 XP
        xp_reward = 35
        request.user.xp += xp_reward
        request.user.recalculate_level()
        request.user.save(update_fields=['xp', 'level'])

        XPHistory.objects.create(
            user=request.user,
            amount=xp_reward,
            category='literasi',
            description=f'Setoran Rabu Literasi Minggu Ke-{report.week_number}: {report.book_title}'
        )

        context = {
            'report': report,
            'success': True,
            'message': f'Laporan Literasi Minggu Ke-{report.week_number} ({report.word_count} kata) berhasil dikirim!',
            'xp_reward': xp_reward,
        }
    else:
        context = {
            'form': form,
            'success': False,
            'message': form.errors.get('summary', ['Terjadi kesalahan pada form isian laporan.'])[0],
        }

    return render(request, 'literasi/partials/report_status.html', context)


@login_required
@require_POST
def submit_peer_review_view(request, report_id):
    """
    HTMX Endpoint: Submisi Peer Review & Rating Antarsiswa (+5 XP untuk Reviewer).
    """
    report = get_object_or_404(LiterasiReport, id=report_id)

    if report.user == request.user:
        return render(request, 'literasi/partials/peer_review_status.html', {
            'success': False,
            'message': 'Anda tidak dapat mereview laporan Anda sendiri.',
        })

    form = PeerReviewForm(request.POST)
    if form.is_valid():
        rating = int(form.cleaned_data['rating'])
        comment = form.cleaned_data['comment']

        review, created = LiterasiPeerReview.objects.update_or_create(
            report=report,
            reviewer=request.user,
            defaults={
                'rating': rating,
                'comment': comment,
            }
        )

        if created:
            # Award +5 XP for Reviewer
            request.user.xp += 5
            request.user.recalculate_level()
            request.user.save(update_fields=['xp', 'level'])

            XPHistory.objects.create(
                user=request.user,
                amount=5,
                category='peer_review',
                description=f'Memberikan Peer Review untuk {report.user.display_name} ({report.book_title})'
            )

        context = {
            'report': report,
            'review': review,
            'success': True,
            'message': f'Terima kasih! Ulasan & rating ★{rating} berhasil dikirim.',
            'just_created': created,
        }
    else:
        context = {
            'success': False,
            'message': 'Harap isi ulasan tanggapan Anda dengan lengkap.',
        }

    return render(request, 'literasi/partials/peer_review_status.html', context)


def literasi_detail_view(request, report_id):
    """
    Detail Laporan Literasi RESIK, ulasan guru, dan daftar peer review siswa.
    """
    report = get_object_or_404(LiterasiReport.objects.select_related('user', 'graded_by').prefetch_related('peer_reviews', 'peer_reviews__reviewer'), id=report_id)
    peer_form = PeerReviewForm()

    user_has_reviewed = False
    if request.user.is_authenticated:
        user_has_reviewed = report.peer_reviews.filter(reviewer=request.user).exists()

    context = {
        'report': report,
        'peer_form': peer_form,
        'user_has_reviewed': user_has_reviewed,
        'active_nav': 'literasi',
    }
    return render(request, 'literasi/literasi_detail.html', context)
