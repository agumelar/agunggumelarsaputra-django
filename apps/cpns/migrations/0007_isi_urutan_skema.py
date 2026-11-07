from django.db import migrations

URUTAN = {"SKD-CAT": 1, "SKB-GURU-LATIHAN": 2}


def isi_urutan(apps, schema_editor):
    SkemaUjian = apps.get_model("cpns", "SkemaUjian")
    for kode, urutan in URUTAN.items():
        SkemaUjian.objects.filter(kode=kode).update(urutan=urutan)


def kosongkan_urutan(apps, schema_editor):
    SkemaUjian = apps.get_model("cpns", "SkemaUjian")
    SkemaUjian.objects.filter(kode__in=URUTAN).update(urutan=0)


class Migration(migrations.Migration):

    dependencies = [
        ("cpns", "0006_premium_urutan_skema"),
    ]

    operations = [
        migrations.RunPython(isi_urutan, kosongkan_urutan),
    ]
