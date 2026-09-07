from django import forms
from .models import LiterasiReport, LiterasiPeerReview


class LiterasiReportForm(forms.ModelForm):
    """
    Form Pengumpulan Laporan Rabu Literasi (RESIK) dengan Validasi Kata (Min. 100 Kata).
    """
    class Meta:
        model = LiterasiReport
        fields = [
            'week_number', 'report_date', 'book_title', 'author', 
            'publisher', 'city', 'year', 'page_count', 'edition', 
            'source_type', 'summary', 'moral_message'
        ]
        widgets = {
            'week_number': forms.NumberInput(attrs={'class': 'm3-input font-mono', 'min': 1, 'max': 20}),
            'report_date': forms.DateInput(attrs={'class': 'm3-input', 'type': 'date'}),
            'book_title': forms.TextInput(attrs={'class': 'm3-input', 'placeholder': 'Contoh: Clean Code / Filosofi Teras / Dokumentasi Django'}),
            'author': forms.TextInput(attrs={'class': 'm3-input', 'placeholder': 'Nama penulis atau pengarang buku'}),
            'publisher': forms.TextInput(attrs={'class': 'm3-input', 'placeholder': 'Penerbit (opsional)'}),
            'city': forms.TextInput(attrs={'class': 'm3-input', 'placeholder': 'Kota terbit (opsional)'}),
            'year': forms.TextInput(attrs={'class': 'm3-input font-mono', 'placeholder': '2024'}),
            'page_count': forms.TextInput(attrs={'class': 'm3-input font-mono', 'placeholder': 'Hal. 1 - 45'}),
            'edition': forms.TextInput(attrs={'class': 'm3-input', 'placeholder': 'Cetakan ke-1 (opsional)'}),
            'source_type': forms.Select(attrs={'class': 'm3-input'}),
            'summary': forms.Textarea(attrs={
                'class': 'm3-input text-xs leading-relaxed',
                'rows': 8,
                'placeholder': 'Paragraf 1 (Awal): Kenalkan tokoh utama, latar tempat/waktu, dan situasi pembuka...\n\nParagraf 2 (Tengah): Uraikan inti konflik, alur peristiwa penting, atau gagasan utama...\n\nParagraf 3 (Akhir): Jelaskan penyelesaian masalah, klimaks cerita, dan simpulan akhir...',
                'x-model': 'summaryText',
                'onpaste': 'return false;',
                'ondrop': 'return false;',
                'oncontextmenu': 'return false;',
                'data-no-paste': 'true',
            }),
            'moral_message': forms.Textarea(attrs={
                'class': 'm3-input text-xs leading-relaxed',
                'rows': 4,
                'placeholder': 'Tuliskan amanat, nilai moral, atau relevansi materi bacaan ini dengan pembentukan etika dan keterampilan di Rekayasa Perangkat Lunak (Minimal 30 kata)...',
                'x-model': 'moralText',
                'onpaste': 'return false;',
                'ondrop': 'return false;',
                'oncontextmenu': 'return false;',
                'data-no-paste': 'true',
            }),
        }

    def clean_summary(self):
        summary = self.cleaned_data.get('summary', '').strip()
        words = summary.split()
        word_count = len(words)
        if word_count < 100:
            raise forms.ValidationError(f"Rangkuman Anda baru berisi {word_count} kata. Syarat minimal laporan RESIK adalah 100 kata.")
        return summary

    def clean_moral_message(self):
        moral = self.cleaned_data.get('moral_message', '').strip()
        words = moral.split()
        word_count = len(words)
        if word_count < 30:
            raise forms.ValidationError(f"Amanat/pesan moral Anda baru berisi {word_count} kata. Syarat minimal adalah 30 kata.")
        return moral


class PeerReviewForm(forms.ModelForm):
    """
    Form Peer Review & Rating Antarsiswa.
    """
    RATING_CHOICES = [
        (5, '★★★★★ (5 - Sangat Menginspirasi & Rapi)'),
        (4, '★★★★☆ (4 - Bagus & Informatif)'),
        (3, '★★★☆☆ (3 - Cukup Baik)'),
        (2, '★★☆☆☆ (2 - Kurang Lengkap)'),
        (1, '★☆☆☆☆ (1 - Perlu Diperbaiki)'),
    ]

    rating = forms.ChoiceField(
        choices=RATING_CHOICES,
        initial=5,
        widget=forms.Select(attrs={'class': 'm3-input font-mono'})
    )

    class Meta:
        model = LiterasiPeerReview
        fields = ['rating', 'comment']
        widgets = {
            'comment': forms.Textarea(attrs={
                'class': 'm3-input text-xs',
                'rows': 3,
                'placeholder': 'Tuliskan tanggapan, apresiasi, atau masukan untuk laporan literasi teman Anda...',
            })
        }
