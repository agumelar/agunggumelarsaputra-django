from django.db import migrations

SKEMA = [
    {
        "kode": "SKD-CAT",
        "nama": "Simulasi SKD CAT",
        "jenis_ujian": "SKD",
        "durasi_menit": 100,
        "aktif": True,
        "bagian": [
            ("TWK", 30, "benar_salah", 65),
            ("TIU", 35, "benar_salah", 80),
            ("TKP", 45, "bobot_opsi", 166),
        ],
    },
    {
        "kode": "SKB-GURU-LATIHAN",
        "nama": "Latihan SKB Guru RPL/PPLG",
        "jenis_ujian": "SKB_GURU",
        "durasi_menit": 90,
        "aktif": False,
        "bagian": [
            ("PEDAGOGIK", 50, "benar_salah", 0),
            ("MATERI_RPL", 50, "benar_salah", 0),
        ],
    },
]


def pasang(apps, schema_editor):
    SkemaUjian = apps.get_model("cpns", "SkemaUjian")
    SkemaBagian = apps.get_model("cpns", "SkemaBagian")
    for data in SKEMA:
        skema, _ = SkemaUjian.objects.update_or_create(
            kode=data["kode"],
            defaults={
                "nama": data["nama"],
                "jenis_ujian": data["jenis_ujian"],
                "durasi_menit": data["durasi_menit"],
                "aktif": data["aktif"],
            },
        )
        for urutan, (subtes, jumlah, cara, ambang) in enumerate(data["bagian"], start=1):
            SkemaBagian.objects.update_or_create(
                skema=skema,
                urutan=urutan,
                defaults={
                    "subtes": subtes,
                    "jumlah_soal": jumlah,
                    "cara_nilai": cara,
                    "poin_benar": 5,
                    "poin_salah": 0,
                    "ambang_batas": ambang,
                },
            )


class Migration(migrations.Migration):
    dependencies = [("cpns", "0003_skema_paket")]
    operations = [migrations.RunPython(pasang, migrations.RunPython.noop)]
