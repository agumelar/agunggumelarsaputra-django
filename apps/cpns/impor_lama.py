from dataclasses import dataclass, field

from django.db import transaction

from .models import CpnsQuestion, Soal
from .validasi import validasi_soal

JENIS_LAMA = {"SKD": "SKD", "SKB": "SKB_GURU"}
CATATAN_SKB = "Subtes asli SKB_GURU. Pilih PEDAGOGIK atau MATERI_RPL."


@dataclass
class HasilSalin:
    masuk: int = 0
    dilewati_sama: int = 0
    perlu_cek: int = 0
    paket: dict[str, int] = field(default_factory=dict)


def _bobot(mentah):
    """Ubah nilai teks seperti "5" jadi angka. Bentuk lain dibiarkan agar validasi menandainya."""
    if not isinstance(mentah, dict):
        return mentah
    hasil = {}
    for k, v in mentah.items():
        if isinstance(v, str) and v.strip().isdigit():
            v = int(v.strip())
        hasil[str(k).strip().upper()] = v
    return hasil


def _potong(nilai, nama, catatan):
    batas = Soal._meta.get_field(nama).max_length
    if len(nilai) > batas:
        catatan.append(f"Field {nama} dipotong dari {len(nilai)} jadi {batas} karakter.")
        return nilai[:batas]
    return nilai


def _bentuk(q: CpnsQuestion) -> Soal:
    catatan = []
    subtes = q.subtes
    if subtes == "SKB_GURU":
        subtes = "PEDAGOGIK"
        catatan.append(CATATAN_SKB)
    tkp = subtes == "TKP"
    soal = Soal(
        jenis_ujian=JENIS_LAMA.get(q.package.tipe_ujian, q.package.tipe_ujian),
        subtes=subtes,
        subtopik=_potong((q.subtopik or "").strip() or "Umum", "subtopik", catatan),
        teks=q.pertanyaan,
        opsi_a=q.opsi_a,
        opsi_b=q.opsi_b,
        opsi_c=q.opsi_c,
        opsi_d=q.opsi_d,
        opsi_e=q.opsi_e,
        kunci="" if tkp else _potong((q.kunci_jawaban or "").strip(), "kunci", catatan),
        bobot=_bobot(q.bobot_tkp) if tkp else None,
        pembahasan_konsep=q.bedah_konsep,
        pembahasan_pengecoh=q.alasan_pengecoh,
        pembahasan_cepat=q.tips_cepat,
        sumber="lama",
        status="draf",
        batch=_potong(f"lama-{q.package.kode}", "batch", catatan),
    )
    data = {f.name: getattr(soal, f.name) for f in Soal._meta.concrete_fields}
    pesan = validasi_soal(data)
    if pesan:
        catatan.append("Pemeriksaan otomatis: " + "; ".join(pesan))
    if catatan:
        soal.perlu_cek = True
        soal.catatan_tinjau = " ".join(catatan)
    return soal


def salin_soal_lama(coba: bool = False) -> HasilSalin:
    hasil = HasilSalin()
    ada = set(Soal.objects.values_list("sidik_teks", flat=True))
    siap = []
    lama = CpnsQuestion.objects.select_related("package").order_by("package__kode", "urutan", "id")
    for q in lama:
        soal = _bentuk(q)
        sidik = soal.hitung_sidik()
        if sidik in ada:
            hasil.dilewati_sama += 1
            continue
        ada.add(sidik)
        siap.append(soal)
        hasil.masuk += 1
        hasil.perlu_cek += int(soal.perlu_cek)
        hasil.paket[q.package.kode] = hasil.paket.get(q.package.kode, 0) + 1
    if not coba:
        with transaction.atomic():
            for soal in siap:
                soal.save()
    return hasil
