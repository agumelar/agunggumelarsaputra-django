from django import forms
from django.utils import timezone

from apps.cpns.models import Soal
from apps.cpns.validasi import HURUF


class SoalForm(forms.ModelForm):
    """Formulir edit soal. Jenis ujian tidak ikut diubah. Aturan isi dari validasi_soal lewat Soal.clean."""

    kembalikan_draf = forms.BooleanField(required=False, label="Kembalikan ke draf")
    bobot_a = forms.IntegerField(required=False, label="Bobot A")
    bobot_b = forms.IntegerField(required=False, label="Bobot B")
    bobot_c = forms.IntegerField(required=False, label="Bobot C")
    bobot_d = forms.IntegerField(required=False, label="Bobot D")
    bobot_e = forms.IntegerField(required=False, label="Bobot E")

    class Meta:
        model = Soal
        fields = [
            "subtes",
            "subtopik",
            "tingkat",
            "teks",
            "opsi_a",
            "opsi_b",
            "opsi_c",
            "opsi_d",
            "opsi_e",
            "kunci",
            "pembahasan_konsep",
            "pembahasan_pengecoh",
            "pembahasan_cepat",
            "rujukan",
            "perlu_cek",
        ]
        labels = {
            "subtes": "Subtes",
            "subtopik": "Subtopik",
            "tingkat": "Tingkat",
            "teks": "Teks soal",
            "kunci": "Kunci jawaban",
            "pembahasan_konsep": "Pembahasan: konsep",
            "pembahasan_pengecoh": "Pembahasan: kenapa opsi lain salah",
            "pembahasan_cepat": "Pembahasan: cara cepat",
            "rujukan": "Rujukan",
            "perlu_cek": "Perlu cek fakta",
        }

    def __init__(self, *args, user, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user
        self.status_awal = self.instance.status
        self.fields["kunci"] = forms.ChoiceField(
            required=False,
            label="Kunci jawaban",
            choices=[("", "Pilih kunci")] + [(h, h) for h in HURUF],
        )
        for h in HURUF:
            self.fields[f"opsi_{h.lower()}"].label = f"Opsi {h}"
        if self.instance.pk and not self.is_bound:
            for h in HURUF:
                self.initial[f"bobot_{h.lower()}"] = (self.instance.bobot or {}).get(h)

    def clean(self):
        data = super().clean()
        if data.get("subtes") == "TKP":
            nilai = {h: data.get(f"bobot_{h.lower()}") for h in HURUF}
            self.instance.bobot = nilai if all(v is not None for v in nilai.values()) else None
            data["kunci"] = ""
        else:
            self.instance.bobot = None

        if self.status_awal == "ditolak" and data.get("kembalikan_draf"):
            self.instance.status = "draf"
        if self.instance.status == "tayang":
            self.instance.ditinjau_oleh = self.user
        return data

    def save(self, commit=True):
        soal = super().save(commit=False)
        if soal.status == "tayang":
            soal.ditinjau_oleh = self.user
            soal.ditinjau_pada = timezone.now()
        if commit:
            soal.save()
        return soal
