from django import forms
from .models import UserSubmission


class LkpdSubmissionForm(forms.Form):
    """
    Form Submisi LKPD Praktikum & Link Google Drive Evidence.
    """
    drive_url = forms.URLField(
        required=True,
        max_length=500,
        widget=forms.URLInput(attrs={
            'class': 'm3-input font-mono text-xs',
            'placeholder': 'https://drive.google.com/drive/folders/...',
            'autocomplete': 'off',
        }),
        help_text='Pastikan akses folder Google Drive disetel ke "Anyone with the link can view".'
    )
    work_summary = forms.CharField(
        required=True,
        widget=forms.Textarea(attrs={
            'class': 'm3-input text-xs',
            'rows': 4,
            'placeholder': 'Tuliskan ringkasan hasil audit / pekerjaan praktikum yang telah kalian selesaikan...',
        }),
        help_text='Jelaskan secara singkat poin-poin utama bukti karya praktikum kalian.'
    )
    additional_notes = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'm3-input text-xs',
            'rows': 2,
            'placeholder': 'Catatan tambahan untuk Pak Agung (opsional)...',
        })
    )


class ReflectionSubmissionForm(forms.Form):
    """
    Form Jurnal Refleksi Pembelajaran Mandiri Siswa.
    """
    understanding = forms.CharField(
        label='1. Konsep Utama yang Dipahami',
        required=True,
        widget=forms.Textarea(attrs={
            'class': 'm3-input text-xs',
            'rows': 3,
            'placeholder': 'Apa konsep terpenting yang kalian pelajari dan pahami pada materi modul ini?...',
        })
    )
    obstacle = forms.CharField(
        label='2. Kendala / Tantangan yang Dihadapi',
        required=True,
        widget=forms.Textarea(attrs={
            'class': 'm3-input text-xs',
            'rows': 3,
            'placeholder': 'Kendala atau tantangan apa yang kalian temui saat mempraktikkan materi ini?...',
        })
    )
    action_plan = forms.CharField(
        label='3. Rencana Tindak Lanjut / Perbaikan',
        required=True,
        widget=forms.Textarea(attrs={
            'class': 'm3-input text-xs',
            'rows': 3,
            'placeholder': 'Langkah konkret apa yang akan kalian lakukan untuk meningkatkan pemahaman kalian?...',
        })
    )
