from .akun import daftar, masuk
from .belajar import (
    jawab_belajar,
    mulai_belajar,
    pilih_belajar,
    ringkasan_belajar,
    soal_belajar,
)
from .cat import hasil_cat, kumpulkan_cat, mulai_cat, ruang_cat, simpan_cat
from .dasbor import dasbor, laporkan_soal, riwayat
from .publik import beranda_publik, privasi, syarat

__all__ = [
    "masuk",
    "daftar",
    "beranda_publik",
    "syarat",
    "privasi",
    "dasbor",
    "riwayat",
    "laporkan_soal",
    "mulai_cat",
    "ruang_cat",
    "simpan_cat",
    "kumpulkan_cat",
    "hasil_cat",
    "pilih_belajar",
    "mulai_belajar",
    "soal_belajar",
    "jawab_belajar",
    "ringkasan_belajar",
]
