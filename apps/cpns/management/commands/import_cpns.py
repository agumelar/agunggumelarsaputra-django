import json
import os
from django.core.management.base import BaseCommand, CommandError
from apps.cpns.models import CpnsPackage, CpnsQuestion


class Command(BaseCommand):
    help = 'Import butir soal CPNS format JSON ke dalam paket ujian dengan penjelasan 3 tingkat.'

    def add_arguments(self, parser):
        parser.add_argument('--file', type=str, required=True, help='Path file JSON bank soal')
        parser.add_argument('--package', type=str, required=True, help='Kode Paket (e.g. SKD-BKN-01) atau slug paket')

    def handle(self, *args, **options):
        file_path = options['file']
        package_identifier = options['package']

        if not os.path.exists(file_path):
            raise CommandError(f"Berkas tidak ditemukan: {file_path}")

        try:
            package = CpnsPackage.objects.filter(kode=package_identifier).first() or \
                      CpnsPackage.objects.filter(slug=package_identifier).first()
            if not package:
                raise CommandError(f"Paket soal dengan identifier '{package_identifier}' tidak ditemukan.")

            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            if not isinstance(data, list):
                raise CommandError("Format JSON tidak valid: Data harus berupa array of question objects.")

            created_count = 0
            updated_count = 0

            for index, item in enumerate(data, start=1):
                subtes = item.get('subtes', 'TWK').upper()
                subtopik = item.get('subtopik', '')
                urutan = item.get('urutan', index)
                pertanyaan = item.get('pertanyaan', '').strip()
                opsi = item.get('opsi', {})
                kunci = item.get('kunci_jawaban', 'A').upper()
                bobot_tkp = item.get('bobot_tkp')
                bedah_konsep = item.get('bedah_konsep', '').strip()
                alasan_pengecoh = item.get('alasan_pengecoh', '').strip()
                tips_cepat = item.get('tips_cepat', '').strip()

                if not pertanyaan or not opsi:
                    self.stdout.write(self.style.WARNING(f"Melewati nomor {urutan}: Pertanyaan atau opsi kosong."))
                    continue

                question, created = CpnsQuestion.objects.update_or_create(
                    package=package,
                    urutan=urutan,
                    defaults={
                        'subtes': subtes,
                        'subtopik': subtopik,
                        'pertanyaan': pertanyaan,
                        'opsi_a': opsi.get('A', ''),
                        'opsi_b': opsi.get('B', ''),
                        'opsi_c': opsi.get('C', ''),
                        'opsi_d': opsi.get('D', ''),
                        'opsi_e': opsi.get('E', ''),
                        'kunci_jawaban': kunci,
                        'bobot_tkp': bobot_tkp,
                        'bedah_konsep': bedah_konsep,
                        'alasan_pengecoh': alasan_pengecoh,
                        'tips_cepat': tips_cepat,
                    }
                )

                if created:
                    created_count += 1
                else:
                    updated_count += 1

            self.stdout.write(self.style.SUCCESS(
                f"Selesai mengimpor ke [{package.kode}]. {created_count} soal dibuat, {updated_count} diperbarui."
            ))

        except Exception as e:
            raise CommandError(f"Terjadi kesalahan saat impor: {str(e)}")
