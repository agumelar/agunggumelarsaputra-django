import csv
import json
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.utils import timezone
from django.http import HttpResponse, JsonResponse

from .models import LiterasiReport, LiterasiPeerReview
from .forms import LiterasiReportForm, PeerReviewForm
from apps.gamification.models import XPHistory


def literasi_hub_view(request):
    """
    Hub Utama Rabu Literasi (RESIK):
    Tab 1: Form Tulis Laporan Baru (+ Live Word Counter & Anti Copy-Paste)
    Tab 2: Riwayat & Cetak PDF Resensi Saya (Kop Surat Resmi SMKN 1 Rongga)
    Tab 3: Galeri Literasi & Peer Review Teman Sekelas
    Tab 4: Panel Evaluasi & Rubrik 9 Aspek Guru (Khusus Guru Pengampu)
    """
    user_reports = []
    peer_feed = []
    total_reports = 0
    graded_reports = 0
    avg_score = None
    next_week_number = 1

    if request.user.is_authenticated:
        user_reports = LiterasiReport.objects.filter(user=request.user).prefetch_related('peer_reviews').order_by('-report_date', '-created_at')
        total_reports = user_reports.count()
        graded_qs = user_reports.filter(status='graded', final_score__isnull=False)
        graded_reports = graded_qs.count()
        if graded_reports > 0:
            scores = [r.final_score for r in graded_qs]
            avg_score = round(sum(scores) / len(scores), 1)
        first_rep = user_reports.first()
        if first_rep:
            next_week_number = first_rep.week_number + 1

    # Feed publik seluruh siswa (30 laporan terbaru)
    peer_feed = LiterasiReport.objects.select_related('user').prefetch_related('peer_reviews', 'peer_reviews__reviewer').order_by('-report_date', '-created_at')[:30]

    # Hak Akses Guru Pengampu
    is_teacher = request.user.is_authenticated and (
        getattr(request.user, 'is_guru', False) or request.user.is_staff or request.user.is_superuser
    )

    all_submissions = []
    if is_teacher:
        all_submissions = LiterasiReport.objects.select_related('user', 'graded_by').prefetch_related('peer_reviews').order_by('-report_date', '-created_at')

    report_form = LiterasiReportForm(initial={
        'report_date': timezone.now().date(),
        'week_number': next_week_number
    })
    peer_form = PeerReviewForm()

    context = {
        'user_reports': user_reports,
        'peer_feed': peer_feed,
        'report_form': report_form,
        'peer_form': peer_form,
        'active_nav': 'literasi',
        'total_reports': total_reports,
        'graded_reports': graded_reports,
        'avg_score': avg_score,
        'next_week_number': next_week_number,
        'is_teacher': is_teacher,
        'all_submissions': all_submissions,
    }
    return render(request, 'literasi/literasi_hub.html', context)


@login_required
@require_POST
def submit_literasi_view(request):
    """
    HTMX Endpoint: Submisi Laporan Literasi RESIK (+35 XP).
    Memvalidasi jumlah kata (minimal 100 kata ringkasan, minimal 30 kata amanat).
    """
    form = LiterasiReportForm(request.POST)

    if form.is_valid():
        report = form.save(commit=False)
        report.user = request.user
        words = report.summary.strip().split()
        report.word_count = len(words)
        report.status = 'submitted'

        # Simpan status checklist mandatori
        checklist_data = {
            'tata_bahasa': request.POST.get('check_tata_bahasa') == 'on',
            'tanda_baca': request.POST.get('check_tanda_baca') == 'on',
            'kalimat_efektif': request.POST.get('check_kalimat_efektif') == 'on',
            'bahasa_baku': request.POST.get('check_bahasa_baku') == 'on',
        }
        report.self_checklist = checklist_data
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
        error_msg = 'Terjadi kesalahan pada form isian laporan.'
        if form.errors.get('summary'):
            error_msg = form.errors['summary'][0]
        elif form.errors.get('moral_message'):
            error_msg = form.errors['moral_message'][0]
        elif form.errors:
            error_msg = list(form.errors.values())[0][0]

        context = {
            'form': form,
            'success': False,
            'message': error_msg,
        }

    return render(request, 'literasi/partials/report_status.html', context)


@login_required
@require_POST
def submit_peer_review_view(request, report_id):
    """
    HTMX / JSON Endpoint: Submisi Peer Review & Rating Antarsiswa (+5 XP untuk Reviewer).
    """
    report = get_object_or_404(LiterasiReport, id=report_id)

    is_json = request.content_type == 'application/json'
    if is_json:
        try:
            data = json.loads(request.body)
            rating = int(data.get('rating', 5))
            comment = str(data.get('comment', '')).strip()
        except Exception:
            return JsonResponse({'success': False, 'error': 'Format data tidak valid.'}, status=400)
    else:
        form = PeerReviewForm(request.POST)
        if form.is_valid():
            rating = int(form.cleaned_data['rating'])
            comment = form.cleaned_data['comment']
        else:
            rating = None
            comment = ''

    if report.user == request.user:
        msg = 'Anda tidak dapat mereview laporan Anda sendiri.'
        if is_json:
            return JsonResponse({'success': False, 'error': msg}, status=400)
        return render(request, 'literasi/partials/peer_review_status.html', {
            'success': False,
            'message': msg,
        })

    if not rating or not comment:
        msg = 'Harap isi ulasan tanggapan dan rating Anda dengan lengkap.'
        if is_json:
            return JsonResponse({'success': False, 'error': msg}, status=400)
        return render(request, 'literasi/partials/peer_review_status.html', {
            'success': False,
            'message': msg,
        })

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

    success_msg = f'Terima kasih! Ulasan & rating ★{rating} berhasil dikirim.'
    if is_json:
        return JsonResponse({
            'success': True,
            'message': success_msg,
            'just_created': created,
            'rating': rating,
        })

    context = {
        'report': report,
        'review': review,
        'success': True,
        'message': success_msg,
        'just_created': created,
    }
    return render(request, 'literasi/partials/peer_review_status.html', context)


@login_required
@require_POST
def grade_literasi_view(request):
    """
    Endpoint Evaluasi Guru: Rubrik 9 Aspek RESIK (4 Menulis + 5 Presentasi).
    Rumus Resmi: ((Total Menulis + Total Presentasi) / 36) * 100
    """
    is_teacher = getattr(request.user, 'is_guru', False) or request.user.is_staff or request.user.is_superuser
    if not is_teacher:
        return HttpResponse("Akses ditolak. Khusus guru pengampu.", status=403)

    if request.content_type == 'application/json':
        try:
            data = json.loads(request.body)
        except Exception:
            return JsonResponse({'success': False, 'error': 'JSON tidak valid.'}, status=400)
    else:
        data = request.POST

    report_id = data.get('reportId') or data.get('report_id')
    report = get_object_or_404(LiterasiReport, id=report_id)

    try:
        w1 = int(data.get('w1', 4))
        w2 = int(data.get('w2', 4))
        w3 = int(data.get('w3', 4))
        w4 = int(data.get('w4', 4))

        p1 = int(data.get('p1', 4))
        p2 = int(data.get('p2', 4))
        p3 = int(data.get('p3', 4))
        p4 = int(data.get('p4', 4))
        p5 = int(data.get('p5', 4))
    except (ValueError, TypeError):
        return JsonResponse({'success': False, 'error': 'Format skor kriteria tidak valid.'}, status=400)

    total_writing = max(4, min(16, w1 + w2 + w3 + w4))
    total_presentation = max(5, min(20, p1 + p2 + p3 + p4 + p5))
    final_score = round(((total_writing + total_presentation) / 36.0) * 100)

    teacher_feedback = str(data.get('teacherFeedback') or data.get('teacher_feedback', '')).strip()

    report.writing_score = total_writing
    report.presentation_score = total_presentation
    report.final_score = final_score
    report.teacher_feedback = teacher_feedback
    report.graded_by = request.user
    report.graded_at = timezone.now()
    report.status = 'graded'
    report.save()

    return JsonResponse({
        'success': True,
        'message': f'Penilaian untuk {report.user.display_name} berhasil disimpan! Nilai Akhir: {final_score}/100.',
        'report_id': report.id,
        'writing_score': total_writing,
        'presentation_score': total_presentation,
        'final_score': final_score,
        'teacher_feedback': teacher_feedback,
    })


@login_required
def export_rekap_literasi_view(request):
    """
    Ekspor Rekapitulasi Penilaian Rabu Literasi (RESIK) ke format CSV (Excel Compatible UTF-8 BOM).
    """
    is_teacher = getattr(request.user, 'is_guru', False) or request.user.is_staff or request.user.is_superuser
    if not is_teacher:
        return HttpResponse("Akses ditolak. Khusus guru pengampu.", status=403)

    reports = LiterasiReport.objects.select_related('user', 'graded_by').order_by('week_number', 'user__first_name')

    response = HttpResponse(content_type='text/csv; charset=utf-8-sig')
    response['Content-Disposition'] = 'attachment; filename="Rekap_Rabu_Literasi_RESIK_SMKN1Rongga.csv"'

    writer = csv.writer(response)
    writer.writerow([
        'No',
        'Nama Peserta Didik',
        'NISN',
        'Kelas / Rombel',
        'Minggu Ke-',
        'Tanggal Baca',
        'Judul Buku / Sumber',
        'Penulis',
        'Penerbit & Tahun',
        'Jumlah Kata Ringkasan',
        'Skor Menulis (Max 16)',
        'Skor Presentasi (Max 20)',
        'Nilai Akhir (0-100)',
        'Status Ketercapaian',
        'Catatan Feedback Guru',
        'Guru Penilai'
    ])

    for idx, rep in enumerate(reports, start=1):
        status_ketercapaian = 'MENUNGGU PENILAIAN'
        if rep.final_score is not None:
            status_ketercapaian = 'TUNTAS (SANGAT BAIK)' if rep.final_score >= 75 else 'PERLU PEMBINAAN'

        writer.writerow([
            idx,
            rep.user.display_name,
            rep.user.nisn or '-',
            rep.user.kelas or '10 RPL',
            f"Minggu {rep.week_number}",
            rep.report_date.strftime('%d/%m/%Y'),
            rep.book_title,
            rep.author,
            f"{rep.publisher} ({rep.year})" if rep.publisher or rep.year else '-',
            rep.word_count,
            rep.writing_score if rep.writing_score is not None else '-',
            rep.presentation_score if rep.presentation_score is not None else '-',
            rep.final_score if rep.final_score is not None else '-',
            status_ketercapaian,
            rep.teacher_feedback or '-',
            rep.graded_by.display_name if rep.graded_by else '-'
        ])

    return response


def literasi_detail_view(request, report_id):
    """
    Detail Laporan Literasi RESIK, ulasan guru, dan daftar peer review siswa.
    """
    report = get_object_or_404(
        LiterasiReport.objects.select_related('user', 'graded_by').prefetch_related('peer_reviews', 'peer_reviews__reviewer'),
        id=report_id
    )
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
