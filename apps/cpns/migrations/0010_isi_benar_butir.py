from django.db import migrations
from django.db.models import Q

# Nilai bobot tertinggi; disalin agar migrasi tidak bergantung pada kode aplikasi.
BOBOT_MAKS = 5


def _benar(soal, jawaban):
    if not jawaban:
        return False
    if soal.bobot:
        return soal.bobot.get(jawaban) == BOBOT_MAKS
    return jawaban == soal.kunci


def isi_benar(apps, schema_editor):
    SesiSoal = apps.get_model("cpns", "SesiSoal")
    butir_lama = SesiSoal.objects.filter(benar__isnull=True).filter(
        Q(sesi__status="selesai") | (Q(sesi__mode="belajar") & ~Q(jawaban=""))
    )
    for butir in butir_lama.select_related("soal").iterator(chunk_size=500):
        butir.benar = _benar(butir.soal, butir.jawaban)
        butir.save(update_fields=["benar"])


def kosongkan(apps, schema_editor):
    """Reverse tidak melakukan apa-apa: kolom dihapus oleh migrasi 0009."""


class Migration(migrations.Migration):

    dependencies = [
        ("cpns", "0009_sesisoal_benar"),
    ]

    operations = [
        migrations.RunPython(isi_benar, kosongkan),
    ]
