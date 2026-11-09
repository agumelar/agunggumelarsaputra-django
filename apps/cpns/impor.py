from dataclasses import dataclass, field

from django.db import DatabaseError, transaction

from .kisi_kisi import baca_kisi_kisi
from .models import Soal
from .validasi import SUMBER, TINGKAT, validasi_soal

OPSI = tuple(f"opsi_{h}" for h in "abcde")
WAJIB_TEKS = ("jenis_ujian", "subtes", "subtopik", "teks")
FIELD_DIKENAL = {
    *WAJIB_TEKS,
    *OPSI,
    "kunci",
    "bobot",
    "pembahasan_konsep",
    "pembahasan_pengecoh",
    "pembahasan_cepat",
    "tingkat",
    "rujukan",
    "perlu_cek",
    "sumber",
}


class ImporGagal(Exception):
    """Impor berhenti karena kesalahan di luar isi baris (nama batch, kisi-kisi, database)."""


CHAR_FIELD = ("jenis_ujian", "subtes", "subtopik", "tingkat", "kunci", "sumber")
STRIP_FIELD = CHAR_FIELD


@dataclass
class HasilImpor:
    masuk: list[int] = field(default_factory=list)
    gagal: list[tuple[int, list[str]]] = field(default_factory=list)


def _cek_tipe(baris):
    if not isinstance(baris, dict):
        return ["Baris ini bukan objek soal."]
    pesan = [f"Field {n} harus berupa teks." for n in WAJIB_TEKS if not isinstance(baris.get(n), str)]
    if "bobot" in baris and baris["bobot"] is not None and not isinstance(baris["bobot"], dict):
        pesan.append("Field bobot harus berupa objek.")
    if "perlu_cek" in baris and not isinstance(baris["perlu_cek"], bool):
        pesan.append("Field perlu_cek harus berupa benar atau salah (true/false).")
    for n in ("rujukan", "kunci", "tingkat", "sumber"):
        if n in baris and not isinstance(baris[n], str):
            pesan.append(f"Field {n} harus berupa teks.")
    return pesan


def _cek_baris(baris, kisi, sidik_file, nomor):
    pesan = _cek_tipe(baris)
    if pesan:
        return pesan, None
    data = dict(baris)
    for n in STRIP_FIELD:
        if isinstance(data.get(n), str):
            data[n] = data[n].strip()
    tak_dikenal = sorted(set(baris) - FIELD_DIKENAL)
    if tak_dikenal:
        pesan.append(f"Field tidak dikenal: {', '.join(tak_dikenal)}.")
    for n, nilai in data.items():
        if isinstance(nilai, str) and "\x00" in nilai:
            pesan.append(f"Field {n} berisi karakter yang tidak diizinkan.")
    for n in CHAR_FIELD:
        batas = Soal._meta.get_field(n).max_length
        if isinstance(data.get(n), str) and len(data[n]) > batas:
            pesan.append(f"Field {n} terlalu panjang (maksimal {batas} karakter).")
    if data.get("tingkat", "sedang") not in TINGKAT:
        pesan.append(f"Tingkat {data['tingkat']} tidak dikenal.")
    if data.get("sumber", "draf_ai") not in SUMBER:
        pesan.append(f"Sumber {data['sumber']} tidak dikenal.")

    for n in OPSI:
        if isinstance(data.get(n), (int, float)) and not isinstance(data.get(n), bool):
            data[n] = str(data[n])
    pesan += validasi_soal(data)
    if data["subtes"] == "TKP":
        if data.get("kunci"):
            pesan.append("Soal TKP memakai bobot, kosongkan kunci.")
    elif data.get("bobot"):
        pesan.append("Soal selain TKP memakai kunci, hapus bobot.")

    if kisi and (data["subtes"], data["subtopik"].strip()) not in kisi:
        pesan.append(
            f"Subtopik {data['subtopik']} tidak terdaftar di kisi-kisi untuk subtes {data['subtes']}."
        )
    if data["subtes"] == "TWK" and not data.get("rujukan", "").strip() and data.get("perlu_cek") is not True:
        pesan.append("Soal TWK tanpa rujukan harus diberi perlu_cek=true. Jangan mengarang rujukan.")

    sidik = Soal(teks=data["teks"]).hitung_sidik()
    if sidik in sidik_file:
        pesan.append(f"Soal ini sama dengan baris {sidik_file[sidik]} di file ini.")
    else:
        ada = Soal.objects.filter(sidik_teks=sidik).values_list("id", flat=True).first()
        if ada is not None:
            pesan.append(f"Soal ini sama dengan soal yang sudah ada di bank (nomor {ada}).")
    return pesan, (data, sidik)


def _buat(data, batch):
    nilai = {n: data[n] for n in WAJIB_TEKS + OPSI}
    for n in ("pembahasan_konsep", "pembahasan_pengecoh", "pembahasan_cepat"):
        nilai[n] = data[n]
    for n in ("kunci", "bobot", "tingkat", "rujukan", "perlu_cek", "sumber"):
        if n in data and data[n] is not None:
            nilai[n] = data[n]
    return Soal(**nilai, status="draf", batch=batch)


def impor_batch(data: list, batch: str, coba: bool = False) -> HasilImpor:
    batas = Soal._meta.get_field("batch").max_length
    if len(batch) > batas:
        raise ImporGagal(f"Nama batch terlalu panjang (maksimal {batas} karakter).")
    hasil = HasilImpor()
    try:
        kisi = {(s.subtes, s.nama) for s in baca_kisi_kisi()}
    except ValueError as e:
        raise ImporGagal(f"Kisi-kisi tidak bisa dibaca: {e}") from e
    sidik_file = {}
    siap = []
    for nomor, baris in enumerate(data, 1):
        pesan, ok = _cek_baris(baris, kisi, sidik_file, nomor)
        if pesan:
            hasil.gagal.append((nomor, pesan))
            continue
        isi, sidik = ok
        sidik_file[sidik] = nomor
        siap.append((nomor, isi))
    if coba:
        hasil.masuk = [n for n, _ in siap]
        return hasil
    try:
        with transaction.atomic():
            for nomor, isi in siap:
                _buat(isi, batch).save()
                hasil.masuk.append(nomor)
    except DatabaseError as e:
        raise ImporGagal(f"Database menolak data, tidak ada soal yang disimpan: {e}") from e
    return hasil
