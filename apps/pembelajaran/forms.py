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
    Form Jurnal Refleksi Pembelajaran Mandiri Siswa (4 Pertanyaan Standar Kurikulum PPLG/RPL).
    """
    q1 = forms.CharField(
        label='1. Hal baru atau wawasan paling berkesan apa yang kalian pelajari hari ini?',
        required=False,
        widget=forms.Textarea(attrs={
            'id': 'refl_q1',
            'class': 'w-full px-3.5 py-2.5 rounded-xl bg-surface-low border border-outline-variant text-xs text-foreground focus:outline-none focus:border-primary leading-relaxed',
            'rows': 3,
            'placeholder': 'Contoh: Pada sesi ini saya baru memahami bahwa...',
        })
    )
    q2 = forms.CharField(
        label='2. Bagaimana konsep materi ini dapat diterapkan dalam proyek nyata software development atau persiapan karier kalian ke depan?',
        required=False,
        widget=forms.Textarea(attrs={
            'id': 'refl_q2',
            'class': 'w-full px-3.5 py-2.5 rounded-xl bg-surface-low border border-outline-variant text-xs text-foreground focus:outline-none focus:border-primary leading-relaxed',
            'rows': 3,
            'placeholder': 'Contoh: Konsep ini sangat berguna saat merancang arsitektur aplikasi dan bekerja sama dalam tim...',
        })
    )
    q3 = forms.CharField(
        label='3. Apa kendala, tantangan teknis, atau bagian materi yang masih perlu kalian perdalam dari pembelajaran hari ini?',
        required=False,
        widget=forms.Textarea(attrs={
            'id': 'refl_q3',
            'class': 'w-full px-3.5 py-2.5 rounded-xl bg-surface-low border border-outline-variant text-xs text-foreground focus:outline-none focus:border-primary leading-relaxed',
            'rows': 2,
            'placeholder': 'Contoh: Saya masih perlu berlatih lebih banyak pada bagian...',
        })
    )
    q4 = forms.CharField(
        label='4. Tuliskan satu komitmen belajar atau langkah konkrit kalian untuk sesi pertemuan berikutnya:',
        required=False,
        widget=forms.Textarea(attrs={
            'id': 'refl_q4',
            'class': 'w-full px-3.5 py-2.5 rounded-xl bg-surface-low border border-outline-variant text-xs text-foreground focus:outline-none focus:border-primary leading-relaxed',
            'rows': 2,
            'placeholder': 'Contoh: Saya akan membaca kembali referensi materi dan menyelesaikan kelengkapan portofolio sebelum kelas dimulai...',
        })
    )

    # Legacy fields fallback for compatibility
    understanding = forms.CharField(required=False, widget=forms.HiddenInput())
    obstacle = forms.CharField(required=False, widget=forms.HiddenInput())
    action_plan = forms.CharField(required=False, widget=forms.HiddenInput())

    def clean(self):
        cleaned_data = super().clean()
        q1 = cleaned_data.get('q1') or cleaned_data.get('understanding')
        q2 = cleaned_data.get('q2') or ''
        q3 = cleaned_data.get('q3') or cleaned_data.get('obstacle')
        q4 = cleaned_data.get('q4') or cleaned_data.get('action_plan')

        if not q1 or not q3 or not q4:
            raise forms.ValidationError('Harap lengkapi seluruh pertanyaan refleksi.')

        cleaned_data['q1'] = q1
        cleaned_data['q2'] = q2
        cleaned_data['q3'] = q3
        cleaned_data['q4'] = q4
        cleaned_data['understanding'] = q1
        cleaned_data['obstacle'] = q3
        cleaned_data['action_plan'] = q4
        return cleaned_data

