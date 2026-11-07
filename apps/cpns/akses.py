from django.utils import timezone

from apps.cpns.models import AksesPeserta, Sesi


def akses_untuk(user):
    return AksesPeserta.objects.get_or_create(user=user)[0]


def is_premium(user, now=None):
    if user.is_superuser:
        return True
    sampai = akses_untuk(user).premium_sampai
    return sampai is not None and sampai > (now or timezone.now())


def boleh_mulai_cat(user, skema):
    premium = is_premium(user)
    sesi_cat = Sesi.objects.filter(user=user, mode="cat")
    if not skema.aktif and not user.is_superuser:
        return False, "Skema ini belum tersedia."
    if sesi_cat.filter(status="berjalan").exists():
        return False, "Selesaikan dulu simulasi yang sedang berjalan."
    if skema.jenis_ujian == "SKB_GURU" and not premium:
        return False, "Simulasi SKB Guru khusus Premium."
    if premium:
        return True, ""
    if not akses_untuk(user).via_google:
        return False, "Simulasi gratis hanya untuk akun Google."
    if sesi_cat.exists():
        return False, "Kuota simulasi gratis sudah terpakai."
    return True, ""


def boleh_belajar_paket(user, paket):
    return paket.untuk_trial or is_premium(user)


def boleh_belajar_subtopik(user):
    return is_premium(user)


def boleh_lihat_pembahasan(user, sesi):
    return sesi.user_id == user.id and (sesi.mode == "belajar" or is_premium(user))
