"""Form login /admin/ yang ikut batas percobaan login (batas_masuk)."""
from django.contrib.admin.forms import AdminAuthenticationForm
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError

from . import batas_masuk


def _cari_user(username):
    User = get_user_model()
    field = User.USERNAME_FIELD
    return (
        User.objects.filter(**{field: username}).first()
        or User.objects.filter(**{f"{field}__iexact": username}).order_by("pk").first()
    )


class FormMasukAdmin(AdminAuthenticationForm):
    """Akun yang ditemukan dikunci per pk, jadi hitungan dibagi dengan login CPNS
    dan login sekolah. Saat terkunci, authenticate tidak dipanggil sama sekali."""

    def clean(self):
        username = (self.cleaned_data.get("username") or "").strip()
        password = self.cleaned_data.get("password")
        if not username or password is None:
            return super().clean()

        kunci = batas_masuk.kunci_untuk(_cari_user(username), username)
        if batas_masuk.terkunci(kunci):
            raise ValidationError(batas_masuk.PESAN_TERKUNCI, code="terkunci")
        try:
            hasil = super().clean()
        except ValidationError:
            batas_masuk.catat_gagal(kunci)
            raise
        batas_masuk.bersihkan(kunci)
        return hasil
