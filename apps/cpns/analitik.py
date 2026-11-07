from collections import defaultdict

from apps.cpns.models import SesiSoal
from apps.cpns.penilaian import adalah_benar


def kelemahan_subtopik(user, minimal_dijawab: int = 3, batas: int = 3) -> list[dict]:
    """Subtopik dengan persen benar terendah, dihitung dari butir sesi belajar yang sudah dijawab."""
    butir = (
        SesiSoal.objects.filter(sesi__user=user, sesi__mode="belajar")
        .exclude(jawaban="")
        .exclude(soal__subtopik="")
        .select_related("soal")
    )
    hitung = defaultdict(lambda: [0, 0])
    for b in butir:
        kunci = (b.soal.subtes, b.soal.subtopik)
        hitung[kunci][1] += 1
        if adalah_benar(b.soal, b.jawaban):
            hitung[kunci][0] += 1
    hasil = [
        {
            "subtes": subtes,
            "subtopik": subtopik,
            "benar": benar,
            "dijawab": dijawab,
            "persen": round(benar * 100 / dijawab),
        }
        for (subtes, subtopik), (benar, dijawab) in hitung.items()
        if dijawab >= minimal_dijawab
    ]
    hasil.sort(key=lambda h: (h["persen"], -h["dijawab"], h["subtes"], h["subtopik"]))
    return hasil[:batas]
