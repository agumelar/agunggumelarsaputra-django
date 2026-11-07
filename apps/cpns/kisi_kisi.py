from dataclasses import dataclass
from pathlib import Path

from django.conf import settings

from .validasi import SUBTES, SUBTES_PER_JENIS


@dataclass(frozen=True)
class Subtopik:
    jenis_ujian: str
    subtes: str
    nama: str
    target: int


def _sel(baris):
    return [bagian.strip() for bagian in baris.strip().strip("|").split("|")]


def _ke_subtopik(sel, nomor):
    if len(sel) != 4:
        raise ValueError(f"Kisi-kisi baris {nomor}: harus ada 4 kolom.")
    jenis, subtes, nama, target = sel
    if subtes not in SUBTES:
        raise ValueError(f"Kisi-kisi baris {nomor}: subtes {subtes} tidak dikenal.")
    if subtes not in SUBTES_PER_JENIS.get(jenis, ()):
        raise ValueError(
            f"Kisi-kisi baris {nomor}: subtes {subtes} tidak cocok dengan jenis {jenis}."
        )
    if not nama:
        raise ValueError(f"Kisi-kisi baris {nomor}: nama subtopik kosong.")
    if not (target.isascii() and target.isdigit()) or int(target) < 1:
        raise ValueError(
            f"Kisi-kisi baris {nomor}: target {target} harus angka positif."
        )
    return Subtopik(jenis, subtes, nama, int(target))


def baca_kisi_kisi(path: Path | None = None) -> list[Subtopik]:
    path = path or Path(settings.BASE_DIR) / "docs/cpns/kisi-kisi.md"
    if not path.exists():
        return []
    hasil = []
    ada = set()
    kepala_terlihat = False
    for nomor, baris in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not baris.strip().startswith("|"):
            if kepala_terlihat:
                break
            continue
        sel = _sel(baris)
        if not kepala_terlihat:
            kepala_terlihat = True
            continue
        if all(set(s) <= set("-: ") for s in sel):
            continue
        subtopik = _ke_subtopik(sel, nomor)
        kunci = (subtopik.jenis_ujian, subtopik.subtes, subtopik.nama)
        if kunci in ada:
            raise ValueError(
                f"Kisi-kisi baris {nomor}: subtopik {subtopik.nama} untuk {subtopik.subtes} sudah ada."
            )
        ada.add(kunci)
        hasil.append(subtopik)
    return hasil
