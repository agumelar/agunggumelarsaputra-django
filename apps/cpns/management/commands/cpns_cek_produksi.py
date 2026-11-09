from pathlib import Path

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.db.models import Count, Q
from django.db.models.functions import Lower

from apps.cpns.impor_lama import salin_soal_lama
from apps.cpns.kisi_kisi import baca_kisi_kisi
from apps.cpns.models import CpnsQuestion, PengaturanCPNS, SkemaUjian, Soal

PLACEHOLDER = ("[KEBIJAKAN PENGEMBALIAN DANA]", "[NAMA DAN KONTAK PENGELOLA]")
TANDA_DRAF_TEMPLAT = "Draf, menunggu tinjauan pengelola."
TANDA_DRAF_KISI = "Draf, menunggu persetujuan pemilik."
TEMPLAT = ("syarat.html", "privasi.html")
BARIS_AWAL_KISI = 10
PANDUAN_GURU = (
    "Pastikan akun ini milik Anda atau guru yang sah dan kata sandinya dibuat sendiri "
    "oleh pemiliknya. Kalau tidak, nonaktifkan kata sandinya lewat admin."
)


def _teks_templat(nama):
    return (Path(settings.BASE_DIR) / "templates/cpns/publik" / nama).read_text(encoding="utf-8")


def _awal_kisi():
    path = Path(settings.BASE_DIR) / "docs/cpns/kisi-kisi.md"
    return "\n".join(path.read_text(encoding="utf-8").splitlines()[:BARIS_AWAL_KISI])


class Command(BaseCommand):
    help = "Periksa data produksi sebelum rilis. Hanya membaca, tidak menulis apa pun."

    def handle(self, *args, **opsi):
        perlu = 0
        for judul, periksa in (
            ("Akun guru", self.guru_sandi),
            ("Email ganda", self.email_ganda),
            ("Pengaturan CPNS", self.pengaturan),
            ("Halaman syarat dan privasi", self.templat_hukum),
            ("Kisi-kisi", self.kisi),
            ("Soal tayang untuk SKD-CAT", self.cukup_soal),
            ("Soal lama", self.soal_lama),
        ):
            try:
                ok, teks, rincian = periksa()
            except Exception as e:
                ok, teks, rincian = False, None, []
                self.stdout.write(
                    f"[PERLU TINDAKAN] {judul}: gagal diperiksa ({type(e).__name__})."
                )
            if teks is not None:
                self.stdout.write(f"[{'OK' if ok else 'PERLU TINDAKAN'}] {teks}")
            for baris in rincian:
                self.stdout.write(f"    {baris}")
            perlu += 0 if ok else 1
        self.stdout.write(f"Ringkasan: {perlu} butir perlu tindakan.")

    def guru_sandi(self):
        User = get_user_model()
        daftar = [e.strip().lower() for e in settings.GURU_EMAILS if e.strip()]
        kena = []
        if daftar:
            cocok = Q()
            for email in daftar:
                cocok |= Q(email__iexact=email)
            kena = [
                u.get_username()
                for u in User.objects.filter(cocok).order_by("pk")
                if u.has_usable_password()
            ]
        if not kena:
            return True, "Tidak ada akun guru yang punya kata sandi aktif.", []
        return (
            False,
            f"{len(kena)} akun guru masih punya kata sandi yang bisa dipakai.",
            [f"username: {nama}" for nama in kena] + [PANDUAN_GURU],
        )

    def email_ganda(self):
        User = get_user_model()
        grup = (
            User.objects.exclude(email="")
            .annotate(email_kecil=Lower("email"))
            .values("email_kecil")
            .annotate(n=Count("pk"))
            .filter(n__gt=1)
            .order_by("email_kecil")
        )
        kunci = [g["email_kecil"] for g in grup]
        if not kunci:
            return True, "Tidak ada email ganda yang hanya beda huruf besar-kecil.", []
        pengguna = (
            User.objects.annotate(email_kecil=Lower("email"))
            .filter(email_kecil__in=kunci)
            .order_by("pk")
        )
        return (
            False,
            f"{len(kunci)} email ganda ditemukan.",
            [f"username: {u.get_username()}" for u in pengguna],
        )

    def pengaturan(self):
        obj = PengaturanCPNS.objects.filter(pk=1).first()
        if obj is None:
            return False, "Pengaturan CPNS belum dibuat. Nomor WA dan harga belum diisi.", []
        masalah = []
        if not obj.nomor_wa.strip():
            masalah.append("Nomor WA masih kosong.")
        if not obj.daftar_harga():
            masalah.append("Daftar harga masih kosong.")
        if masalah:
            return False, "Pengaturan CPNS belum lengkap.", masalah
        return True, "Nomor WA dan daftar harga sudah diisi.", []

    def templat_hukum(self):
        masalah = []
        for nama in TEMPLAT:
            try:
                teks = _teks_templat(nama)
            except OSError:
                masalah.append(f"{nama}: file tidak terbaca.")
                continue
            for tanda in PLACEHOLDER:
                if tanda in teks:
                    masalah.append(f"{nama}: masih ada {tanda}")
            if TANDA_DRAF_TEMPLAT in teks:
                masalah.append(f"{nama}: masih ada baris \"{TANDA_DRAF_TEMPLAT}\"")
        if masalah:
            return False, "Halaman syarat dan privasi belum final.", masalah
        return True, "Halaman syarat dan privasi sudah bebas placeholder dan tanda draf.", []

    def kisi(self):
        try:
            baris = baca_kisi_kisi()
        except ValueError as e:
            return False, "Dokumen kisi-kisi tidak terbaca.", [str(e)]
        if not baris:
            return False, "Dokumen kisi-kisi kosong atau tidak ditemukan.", []
        try:
            awal = _awal_kisi()
        except OSError:
            return False, "Dokumen kisi-kisi tidak terbaca.", []
        if TANDA_DRAF_KISI in awal:
            return False, f"Kisi-kisi terbaca ({len(baris)} subtopik) tetapi belum disetujui pemilik.", []
        return True, f"Kisi-kisi terbaca ({len(baris)} subtopik) dan sudah disetujui.", []

    def cukup_soal(self):
        skema = SkemaUjian.objects.filter(kode="SKD-CAT").prefetch_related("bagian").first()
        if skema is None:
            return False, "Skema SKD-CAT tidak ditemukan.", []
        tayang = {
            r["subtes"]: r["n"]
            for r in Soal.objects.filter(status="tayang", jenis_ujian=skema.jenis_ujian)
            .values("subtes")
            .annotate(n=Count("pk"))
        }
        rincian = []
        pembagi = []
        for b in skema.bagian.all():
            ada = tayang.get(b.subtes, 0)
            rincian.append(f"{b.subtes}: {ada} tayang, butuh {b.jumlah_soal} per simulasi")
            if b.jumlah_soal > 0:
                pembagi.append(ada // b.jumlah_soal)
        cukup = min(pembagi) if pembagi else 0
        rincian.append(f"Cukup untuk {cukup} simulasi")
        if cukup < 1:
            return False, "Soal tayang belum cukup untuk satu simulasi SKD-CAT.", rincian
        return True, f"Soal tayang cukup untuk {cukup} simulasi SKD-CAT.", rincian

    def soal_lama(self):
        jumlah = CpnsQuestion.objects.count()
        hasil = salin_soal_lama(coba=True)
        rincian = [
            f"Soal lama: {jumlah}",
            f"Perkiraan masuk: {hasil.masuk}, dilewati karena sama: {hasil.dilewati_sama}, "
            f"perlu cek: {hasil.perlu_cek}",
        ]
        if hasil.masuk:
            return False, f"{hasil.masuk} soal lama belum disalin ke bank soal.", rincian
        return True, "Tidak ada soal lama yang masih perlu disalin.", rincian
