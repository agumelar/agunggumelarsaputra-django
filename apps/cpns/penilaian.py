from apps.cpns.models import SesiSoal, SkemaBagian, Soal
from apps.cpns.validasi import POIN_MAKS_BOBOT  # noqa: F401  (diekspor ulang)


def poin_soal(soal: Soal, jawaban: str, bagian: SkemaBagian) -> int:
    if not jawaban:
        return 0
    if bagian.cara_nilai == "bobot_opsi":
        return int((soal.bobot or {}).get(jawaban, 0))
    return bagian.poin_benar if jawaban == soal.kunci else bagian.poin_salah


def bagian_implisit(soal: Soal) -> SkemaBagian:
    """Bagian sementara (tidak disimpan) untuk sesi belajar yang tanpa skema."""
    return SkemaBagian(
        subtes=soal.subtes,
        cara_nilai="bobot_opsi" if soal.bobot else "benar_salah",
        poin_benar=5,
        poin_salah=0,
        ambang_batas=0,
        jumlah_soal=0,
        urutan=0,
    )


def adalah_benar(soal: Soal, jawaban: str) -> bool:
    if not jawaban:
        return False
    if soal.bobot:
        return soal.bobot.get(jawaban) == POIN_MAKS_BOBOT
    return jawaban == soal.kunci


def _nilai_cat(sesi, butir_semua):
    skor_bagian = []
    for bagian in sesi.skema.bagian.all():
        skor = 0
        for butir in butir_semua:
            if butir.soal.subtes != bagian.subtes:
                continue
            butir.poin = poin_soal(butir.soal, butir.jawaban, bagian)
            skor += butir.poin
        faktor = POIN_MAKS_BOBOT if bagian.cara_nilai == "bobot_opsi" else bagian.poin_benar
        skor_bagian.append(
            {
                "subtes": bagian.subtes,
                "skor": skor,
                "maks": bagian.jumlah_soal * faktor,
                "ambang": bagian.ambang_batas,
                "lulus": skor >= bagian.ambang_batas,
            }
        )
    return skor_bagian


def _nilai_belajar(butir_semua):
    per_subtes = {}
    for butir in butir_semua:
        butir.poin = poin_soal(butir.soal, butir.jawaban, bagian_implisit(butir.soal))
        ringkas = per_subtes.setdefault(
            butir.soal.subtes,
            {"subtes": butir.soal.subtes, "skor": 0, "maks": 0, "ambang": 0, "lulus": True},
        )
        ringkas["skor"] += butir.poin
        ringkas["maks"] += 5
    return list(per_subtes.values())


def butir_benar(butir) -> bool:
    """Hasil beku saat dinilai; butir lama yang belum punya snapshot memakai kunci terkini."""
    if butir.benar is not None:
        return butir.benar
    return adalah_benar(butir.soal, butir.jawaban)


def nilai_sesi(sesi) -> None:
    butir_semua = list(sesi.butir.select_related("soal"))
    if sesi.mode == "cat":
        skor_bagian = _nilai_cat(sesi, butir_semua)
    else:
        skor_bagian = _nilai_belajar(butir_semua)
    for butir in butir_semua:
        if butir.poin is None:
            butir.poin = 0
        # Butir belajar dibekukan saat dijawab; penilaian akhir tidak menimpanya.
        if butir.benar is None or sesi.mode == "cat":
            butir.benar = adalah_benar(butir.soal, butir.jawaban)
    SesiSoal.objects.bulk_update(butir_semua, ["poin", "benar"])
    sesi.skor_bagian = skor_bagian
    sesi.total = sum(b["skor"] for b in skor_bagian)
    sesi.lulus = all(b["lulus"] for b in skor_bagian)
    sesi.save(update_fields=["skor_bagian", "total", "lulus"])
