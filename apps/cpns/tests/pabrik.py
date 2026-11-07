import itertools

from apps.cpns.models import Sesi, SesiSoal, Soal

_hitung = itertools.count(1)
_TKP_BOBOT = {"A": 1, "B": 2, "C": 3, "D": 4, "E": 5}


def buat_soal(
    subtes,
    *,
    kunci="A",
    bobot=None,
    status="tayang",
    jenis_ujian=None,
    subtopik="Umum",
    teks=None,
):
    if jenis_ujian is None:
        jenis_ujian = "SKB_GURU" if subtes in ("PEDAGOGIK", "MATERI_RPL") else "SKD"
    if subtes == "TKP" and bobot is None:
        bobot = dict(_TKP_BOBOT)
        kunci = ""
    n = next(_hitung)
    return Soal.objects.create(
        jenis_ujian=jenis_ujian,
        subtes=subtes,
        subtopik=subtopik,
        teks=teks or f"Soal pabrik nomor {n} untuk {subtes}",
        opsi_a=f"Opsi A soal {n}",
        opsi_b=f"Opsi B soal {n}",
        opsi_c=f"Opsi C soal {n}",
        opsi_d=f"Opsi D soal {n}",
        opsi_e=f"Opsi E soal {n}",
        kunci=kunci,
        bobot=bobot,
        pembahasan_konsep="Konsep soal.",
        pembahasan_pengecoh="Pengecoh soal.",
        pembahasan_cepat="Cara cepat soal.",
        status=status,
    )


def buat_sesi_cat(user, skema, soal_list, jawaban_list):
    sesi = Sesi.objects.create(user=user, mode="cat", skema=skema)
    for nomor, (soal, jawaban) in enumerate(zip(soal_list, jawaban_list), start=1):
        SesiSoal.objects.create(
            sesi=sesi,
            soal=soal,
            nomor=nomor,
            urutan_opsi="ABCDE",
            jawaban=jawaban,
        )
    return sesi


def isi_bank_skd(twk=30, tiu=35, tkp=45):
    return {
        "TWK": [buat_soal("TWK") for _ in range(twk)],
        "TIU": [buat_soal("TIU") for _ in range(tiu)],
        "TKP": [buat_soal("TKP") for _ in range(tkp)],
    }
