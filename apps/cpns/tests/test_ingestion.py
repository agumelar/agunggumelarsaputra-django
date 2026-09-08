import json
import tempfile
import os
from django.test import TestCase
from django.core.management import call_command
from django.core.management.base import CommandError
from apps.cpns.models import CpnsPackage, CpnsQuestion


class CpnsIngestionTest(TestCase):
    def setUp(self):
        self.pkg = CpnsPackage.objects.create(
            kode='IMPORT-TEST-01',
            judul='Paket Uji Impor',
            slug='paket-uji-impor',
            tipe_ujian='SKD',
            kategori='SIMULASI_LENGKAP'
        )

    def test_import_cpns_json_success(self):
        """Memverifikasi command import_cpns dapat mem-parse berkas JSON dengan penjelasan 3 tingkat."""
        sample_data = [
            {
                "subtes": "TWK",
                "subtopik": "Integritas Nasional",
                "urutan": 1,
                "pertanyaan": "Nilai dasar integritas yang tercermin dalam keberanian menolak gratifikasi adalah...",
                "opsi": {
                    "A": "Jujur dan berani",
                    "B": "Peduli dan santun",
                    "C": "Disiplin semata",
                    "D": "Kerja keras saja",
                    "E": "Tanggung jawab normatif"
                },
                "kunci_jawaban": "A",
                "bobot_tkp": None,
                "bedah_konsep": "9 Nilai Integritas KPK mencakup Jujur, Peduli, Mandiri, Disiplin, Tanggung Jawab, Kerja Keras, Sederhana, Berani, Adil.",
                "alasan_pengecoh": "Opsi B tidak menyentuh aspek keberanian melawan tindakan koruptif.",
                "tips_cepat": "Kata kunci 'menolak suap/gratifikasi' selalu berpasangan dengan 'jujur' dan 'berani'."
            },
            {
                "subtes": "TKP",
                "subtopik": "Sosial Budaya",
                "urutan": 2,
                "pertanyaan": "Ketika ditugaskan ke wilayah terpencil dengan adat istiadat yang sangat berbeda...",
                "opsi": {
                    "A": "Membatasi pergaulan",
                    "B": "Menghormati dan proaktif beradaptasi dengan tokoh adat setempat",
                    "C": "Menuntut warga mengikuti kebiasaan asal Anda",
                    "D": "Mengajukan mutasi kembali segera",
                    "E": "Menjalankan tugas seadanya tanpa sosialisasi"
                },
                "kunci_jawaban": "B",
                "bobot_tkp": {"A": 2, "B": 5, "C": 1, "D": 1, "E": 3},
                "bedah_konsep": "Kompetensi Sosial Budaya menuntut ASN mampu beradaptasi dan menjadi perekat bangsa dalam kemajemukan.",
                "alasan_pengecoh": "Opsi C melanggar etika kemajemukan dengan memaksakan budaya.",
                "tips_cepat": "Pilih sikap yang proaktif membangun relasi harmonis dan toleransi aktif."
            }
        ]

        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False, encoding='utf-8') as f:
            json.dump(sample_data, f, ensure_ascii=False)
            temp_path = f.name

        try:
            call_command('import_cpns', file=temp_path, package='IMPORT-TEST-01')
            
            # Verifikasi data tersimpan
            questions = CpnsQuestion.objects.filter(package=self.pkg).order_by('urutan')
            self.assertEqual(questions.count(), 2)

            q1 = questions.first()
            self.assertEqual(q1.subtes, 'TWK')
            self.assertEqual(q1.kunci_jawaban, 'A')
            self.assertTrue('9 Nilai Integritas' in q1.bedah_konsep)
            self.assertTrue('Opsi B tidak menyentuh' in q1.alasan_pengecoh)
            self.assertTrue('Kata kunci' in q1.tips_cepat)

            q2 = questions.last()
            self.assertEqual(q2.subtes, 'TKP')
            self.assertEqual(q2.bobot_tkp.get('B'), 5)
        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)
