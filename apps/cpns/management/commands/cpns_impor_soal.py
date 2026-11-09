import json
import sys
from pathlib import Path

from django.core.management.base import BaseCommand, CommandError

from apps.cpns.impor import ImporGagal, impor_batch


class Command(BaseCommand):
    help = "Impor batch soal dari file JSON sebagai draf."

    def add_arguments(self, parser):
        parser.add_argument("file")
        parser.add_argument("--coba", action="store_true", help="Periksa saja, tidak menyimpan.")

    def handle(self, *args, **opsi):
        path = Path(opsi["file"])
        if not path.is_file():
            raise CommandError(f"File {path} tidak ditemukan.")
        try:
            data = json.loads(path.read_text(encoding="utf-8-sig"))
        except (ValueError, UnicodeDecodeError) as e:
            raise CommandError(f"File {path.name} bukan JSON yang benar: {e}")
        if not isinstance(data, list):
            raise CommandError("Isi file harus berupa daftar soal (list JSON).")
        try:
            hasil = impor_batch(data, path.stem, coba=opsi["coba"])
        except ImporGagal as e:
            raise CommandError(str(e))
        self.stdout.write(f"Masuk: {len(hasil.masuk)} soal (draf). Gagal: {len(hasil.gagal)} baris.")
        for nomor, pesan in hasil.gagal:
            self.stdout.write(f"Baris {nomor}: {'; '.join(pesan)}")
        if hasil.gagal:
            sys.exit(1)
