from django.core.management.base import BaseCommand

from apps.cpns.impor_lama import salin_soal_lama


class Command(BaseCommand):
    help = "Salin soal CPNS lama ke bank soal baru sebagai draf."

    def add_arguments(self, parser):
        parser.add_argument("--coba", action="store_true", help="Hitung saja, tidak menyimpan.")

    def handle(self, *args, **opsi):
        hasil = salin_soal_lama(coba=opsi["coba"])
        self.stdout.write(
            f"Disalin: {hasil.masuk} soal (draf, sumber lama). "
            f"Dilewati karena sama: {hasil.dilewati_sama}. "
            f"Ditandai perlu cek: {hasil.perlu_cek}."
        )
        for kode, jumlah in sorted(hasil.paket.items()):
            self.stdout.write(f"{kode}: {jumlah}")
        if opsi["coba"]:
            self.stdout.write("Percobaan saja, tidak ada yang disimpan.")
