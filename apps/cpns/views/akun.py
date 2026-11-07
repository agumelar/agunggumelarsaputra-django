from django.contrib import messages
from django.contrib.auth import authenticate, get_user_model, login
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.db import transaction
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils.http import url_has_allowed_host_and_scheme

from apps.cpns.models import AksesPeserta, PengaturanCPNS

User = get_user_model()

PESAN_EMAIL_ADA = "Email ini sudah terdaftar. Silakan masuk."
PESAN_MASUK_GAGAL = "Email atau kata sandi salah."
PESAN_SANDI_BEDA = "Kata sandi dan ulangannya tidak sama."
PESAN_SETUJU = "Centang persetujuan untuk melanjutkan."
PESAN_NAMA = "Nama wajib diisi."
PESAN_EMAIL_TIDAK_VALID = "Alamat email tidak valid."


def _tujuan_aman(request):
    tujuan = request.POST.get("next") or request.GET.get("next") or ""
    if tujuan and url_has_allowed_host_and_scheme(
        tujuan,
        allowed_hosts={request.get_host()},
        require_https=request.is_secure(),
    ):
        return tujuan
    return ""


def _username_unik(email):
    dasar = email.split("@")[0] or "peserta"
    username = dasar
    angka = 1
    while User.objects.filter(username__iexact=username).exists():
        username = f"{dasar}{angka}"
        angka += 1
    return username


def _cari_user(identitas):
    if "@" in identitas:
        return User.objects.filter(email__iexact=identitas).first()
    return User.objects.filter(username__iexact=identitas).first()


def masuk(request):
    if request.user.is_authenticated:
        return redirect("cpns:dasbor")

    galat = ""
    identitas = ""
    if request.method == "POST":
        identitas = request.POST.get("identitas", "").strip()
        kata_sandi = request.POST.get("kata_sandi", "")
        cocok = _cari_user(identitas) if identitas else None
        user = (
            authenticate(request, username=cocok.username, password=kata_sandi)
            if cocok
            else None
        )
        if user is not None:
            login(request, user)
            return redirect(_tujuan_aman(request) or reverse("cpns:dasbor"))
        galat = PESAN_MASUK_GAGAL

    nomor_wa = "".join(c for c in PengaturanCPNS.ambil().nomor_wa if c.isdigit())
    return render(
        request,
        "cpns/akun/masuk.html",
        {
            "galat": galat,
            "identitas": identitas,
            "next": request.GET.get("next", ""),
            "tautan_wa": f"https://wa.me/{nomor_wa}" if nomor_wa else "",
        },
    )


def daftar(request):
    if request.user.is_authenticated:
        return redirect("cpns:dasbor")

    galat = {}
    isian = {"nama": "", "email": ""}
    if request.method == "POST":
        nama = request.POST.get("nama", "").strip()
        email = request.POST.get("email", "").strip()
        kata_sandi = request.POST.get("kata_sandi", "")
        ulang = request.POST.get("ulang_kata_sandi", "")
        isian = {"nama": nama, "email": email}

        if not nama:
            galat["nama"] = PESAN_NAMA
        try:
            validate_email(email)
        except ValidationError:
            galat["email"] = PESAN_EMAIL_TIDAK_VALID
        else:
            if User.objects.filter(email__iexact=email).exists():
                galat["email"] = PESAN_EMAIL_ADA
        if kata_sandi != ulang:
            galat["ulang_kata_sandi"] = PESAN_SANDI_BEDA
        else:
            try:
                validate_password(kata_sandi, User(username=email.split("@")[0], email=email, first_name=nama))
            except ValidationError as e:
                galat["kata_sandi"] = " ".join(e.messages)
        if not request.POST.get("setuju"):
            galat["setuju"] = PESAN_SETUJU

        if not galat:
            with transaction.atomic():
                user = User.objects.create_user(
                    username=_username_unik(email),
                    email=email,
                    password=kata_sandi,
                    first_name=nama,
                    role=User.ROLE_PESERTA,
                )
                AksesPeserta.objects.create(user=user, via_google=False)
            login(request, user, backend="django.contrib.auth.backends.ModelBackend")
            messages.success(request, "Akun dibuat. Selamat berlatih.")
            return redirect("cpns:dasbor")

    return render(request, "cpns/akun/daftar.html", {"galat": galat, "isian": isian})
