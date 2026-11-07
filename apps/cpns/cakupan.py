from django.db.models import Count

from apps.cpns.kisi_kisi import baca_kisi_kisi
from apps.cpns.models import Soal, SkemaUjian


def hitung_cakupan():
    """Cakupan bank soal per subtopik (kisi-kisi + data) dan kecukupan tiap skema."""
    jumlah = {}
    for r in Soal.objects.values("jenis_ujian", "subtes", "subtopik", "status").annotate(n=Count("id")):
        kunci = (r["jenis_ujian"], r["subtes"], r["subtopik"])
        jumlah.setdefault(kunci, {})[r["status"]] = r["n"]

    target = {(s.jenis_ujian, s.subtes, s.nama): s.target for s in baca_kisi_kisi()}
    baris = []
    for kunci in sorted(set(target) | set(jumlah)):
        jenis, subtes, subtopik = kunci
        tayang = jumlah.get(kunci, {}).get("tayang", 0)
        tgt = target.get(kunci)
        baris.append(
            {
                "jenis_ujian": jenis,
                "subtes": subtes,
                "subtopik": subtopik,
                "target": tgt,
                "tayang": tayang,
                "draf": jumlah.get(kunci, {}).get("draf", 0),
                "kurang": max(tgt - tayang, 0) if tgt is not None else 0,
            }
        )

    tayang_subtes = {}
    for (jenis, subtes, _), per_status in jumlah.items():
        tayang_subtes[(jenis, subtes)] = tayang_subtes.get((jenis, subtes), 0) + per_status.get("tayang", 0)

    skema = []
    for s in SkemaUjian.objects.prefetch_related("bagian"):
        pembagi = [
            tayang_subtes.get((s.jenis_ujian, b.subtes), 0) // b.jumlah_soal
            for b in s.bagian.all()
            if b.jumlah_soal > 0
        ]
        skema.append(
            {
                "kode": s.kode,
                "nama": s.nama,
                "aktif": s.aktif,
                "cukup_untuk": min(pembagi) if pembagi else 0,
            }
        )
    return {"baris": baris, "skema": skema}
