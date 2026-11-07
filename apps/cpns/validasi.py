import hashlib
import re

JENIS = ("SKD", "SKB_GURU")
SUBTES = ("TWK", "TIU", "TKP", "PEDAGOGIK", "MATERI_RPL")
TINGKAT = ("mudah", "sedang", "sulit")
STATUS = ("draf", "tayang", "ditolak")
SUMBER = ("draf_ai", "tulisan_sendiri", "lama")

HURUF = ("A", "B", "C", "D", "E")


def sidik_teks(teks):
    bersih = re.sub(r"[^\w\s]|_", " ", (teks or "").lower())
    bersih = re.sub(r"\s+", " ", bersih).strip()
    return hashlib.sha256(bersih.encode("utf-8")).hexdigest()


def _bobot_valid(bobot):
    if not isinstance(bobot, dict) or set(bobot) != set(HURUF):
        return False
    nilai = list(bobot.values())
    if any(isinstance(n, bool) or not isinstance(n, int) for n in nilai):
        return False
    return sorted(nilai) == [1, 2, 3, 4, 5]


def validasi_soal(data, untuk_tayang=False):
    pesan = []

    opsi = {}
    for h in HURUF:
        isi = (data.get("opsi_" + h.lower()) or "").strip()
        opsi[h] = isi
        if not isi:
            pesan.append(f"Isi opsi {h}.")
    terisi = [v for v in opsi.values() if v]
    if len(set(terisi)) != len(terisi):
        pesan.append("Ada opsi yang isinya sama persis.")

    if data.get("subtes") == "TKP":
        if not _bobot_valid(data.get("bobot")):
            pesan.append(
                "Isi bobot TKP: kunci A sampai E, nilainya 1, 2, 3, 4, 5 dan tidak boleh ada yang sama."
            )
    elif (data.get("kunci") or "") not in HURUF:
        pesan.append("Pilih kunci jawaban (A sampai E).")

    for nama, label in (
        ("pembahasan_konsep", "konsep"),
        ("pembahasan_pengecoh", "pengecoh"),
        ("pembahasan_cepat", "cepat"),
    ):
        if not (data.get(nama) or "").strip():
            pesan.append(f"Isi pembahasan {label}.")

    if untuk_tayang and not data.get("ditinjau_oleh"):
        pesan.append("Soal tayang harus sudah ditinjau oleh seorang peninjau.")

    return pesan
