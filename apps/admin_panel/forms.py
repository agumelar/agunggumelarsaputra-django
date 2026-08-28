from django import forms
from .models import EnrollmentToken, generate_random_token


class EnrollmentTokenForm(forms.ModelForm):
    """
    Form Pembuatan / Edit Token Sesi oleh Guru Pengampu.
    """
    CLASS_CHOICES = [
        ('Semua Kelas', 'Semua Kelas (Umum)'),
        ('10 RPL 1', '10 RPL 1 (Fase E)'),
        ('10 RPL 2', '10 RPL 2 (Fase E)'),
        ('11 RPL 1', '11 RPL 1 (Fase F)'),
        ('11 RPL 2', '11 RPL 2 (Fase F)'),
        ('12 RPL 1', '12 RPL 1 (Fase F Lanjut)'),
        ('12 RPL 2', '12 RPL 2 (Fase F Lanjut)'),
    ]

    target_class = forms.ChoiceField(
        choices=CLASS_CHOICES,
        initial='Semua Kelas',
        widget=forms.Select(attrs={'class': 'm3-input'})
    )
    custom_token = forms.CharField(
        max_length=32,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'm3-input font-mono uppercase',
            'placeholder': 'Kosongkan untuk generate otomatis (misal: RPL-8F3A)'
        }),
        help_text='Biarkan kosong jika ingin token di-generate secara otomatis.'
    )

    class Meta:
        model = EnrollmentToken
        fields = ['title', 'description', 'target_class', 'target_type', 'target_slug', 'max_uses', 'expires_at']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'm3-input', 'placeholder': 'Contoh: KBM Praktikum Orientasi PPLG Gasal'}),
            'description': forms.Textarea(attrs={'class': 'm3-input', 'rows': 3, 'placeholder': 'Petunjuk atau catatan sesi untuk siswa...'}),
            'target_type': forms.Select(attrs={'class': 'm3-input'}),
            'target_slug': forms.TextInput(attrs={'class': 'm3-input font-mono', 'placeholder': 'Slug modul (opsional)'}),
            'max_uses': forms.NumberInput(attrs={'class': 'm3-input font-mono', 'min': 1, 'max': 100}),
            'expires_at': forms.DateTimeInput(attrs={'class': 'm3-input', 'type': 'datetime-local'}),
        }

    def save(self, commit=True, user=None):
        instance = super().save(commit=False)
        custom = self.cleaned_data.get('custom_token')
        if custom and custom.strip():
            instance.token = custom.strip().upper().replace(' ', '-')
        else:
            # Generate prefix based on target class
            cls = self.cleaned_data.get('target_class', 'RPL')
            prefix = 'RPL' if cls == 'Semua Kelas' else cls.replace(' ', '')
            instance.token = generate_random_token(prefix=prefix)

        if user:
            instance.created_by = user

        if commit:
            instance.save()
        return instance
