from django.test import TestCase
from django.contrib.auth import get_user_model
from apps.cpns.models import CpnsPackage, CpnsQuestion, CpnsAttempt

User = get_user_model()


class CpnsScoringModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='calon_cpns',
            email='calon_cpns@example.com',
            password='Password123!',
            role='student'
        )

        self.pkg = CpnsPackage.objects.create(
            kode='SKD-BKN-TEST',
            judul='Simulasi Uji Coba SKD CAT BKN',
            slug='simulasi-uji-coba-skd-cat-bkn',
            tipe_ujian='SKD',
            kategori='SIMULASI_LENGKAP',
            durasi_menit=100,
            passing_grade_twk=65,
            passing_grade_tiu=80,
            passing_grade_tkp=166,
            passing_grade_skb=70,
            deskripsi='Paket uji coba kalkulasi skor CAT BKN.',
            urutan=1,
            is_published=True
        )

        # 1. Buat Soal TWK
        self.q_twk = CpnsQuestion.objects.create(
            package=self.pkg,
            subtes='TWK',
            subtopik='Pilar Negara',
            urutan=1,
            pertanyaan='Lambang negara Garuda Pancasila dengan semboyan Bhinneka Tunggal Ika diatur dalam UUD 1945 pasal...',
            opsi_a='Pasal 36A',
            opsi_b='Pasal 36B',
            opsi_c='Pasal 36C',
            opsi_d='Pasal 35',
            opsi_e='Pasal 34',
            kunci_jawaban='A',
            bedah_konsep='Pasal 36A UUD 1945 menyatakan lambang negara ialah Garuda Pancasila dengan semboyan Bhinneka Tunggal Ika.',
            alasan_pengecoh='Pasal 35 mengatur bendera, Pasal 36B lagu kebangsaan, Pasal 36C ketentuan lebih lanjut.',
            tips_cepat='Ingat urutan Bab XV: Pasal 35 (Bendera), 36 (Bahasa), 36A (Lambang), 36B (Lagu).'
        )

        # 2. Buat Soal TIU
        self.q_tiu = CpnsQuestion.objects.create(
            package=self.pkg,
            subtes='TIU',
            subtopik='Silogisme',
            urutan=2,
            pertanyaan='Semua guru adalah pendidik. Sebagian guru adalah penulis. Maka...',
            opsi_a='Semua pendidik adalah penulis',
            opsi_b='Sebagian pendidik adalah penulis',
            opsi_c='Semua guru bukan penulis',
            opsi_d='Tidak ada pendidik yang penulis',
            opsi_e='Semua penulis adalah guru',
            kunci_jawaban='B',
            bedah_konsep='Silogisme kategori sebagian (partikular): Jika semua A adalah B dan sebagian A adalah C, maka sebagian B adalah C.',
            alasan_pengecoh='Opsi A generalisasi berlebih, opsi E membalik premis.',
            tips_cepat='Premis Universal + Partikular menghasilkan kesimpulan Partikular ("Sebagian").'
        )

        # 3. Buat Soal TKP (Gradasi Skor 1-5)
        self.q_tkp = CpnsQuestion.objects.create(
            package=self.pkg,
            subtes='TKP',
            subtopik='Pelayanan Publik',
            urutan=3,
            pertanyaan='Ketika melayani warga lansia yang kesulitan mengisi formulir digital, sikap Anda...',
            opsi_a='Menyuruh pulang menunggu anaknya',
            opsi_b='Meminta satpam membantunya',
            opsi_c='Menyediakan waktu membimbing pengisian hingga selesai dengan ramah',
            opsi_d='Memberikan contoh berkas kertas saja',
            opsi_e='Menjelaskan secara lisan lalu meninggalkannya',
            kunci_jawaban='C',
            bobot_tkp={'A': 1, 'B': 3, 'C': 5, 'D': 2, 'E': 4},
            bedah_konsep='Kompetensi Pelayanan Publik menuntut empati, kesabaran, dan tuntas melayani kelompok rentan.',
            alasan_pengecoh='Opsi E ramah tapi tidak tuntas, opsi B melempar tanggung jawab ke satpam.',
            tips_cepat='Pilih opsi yang berorientasi tindakan tuntas langsung dari diri sendiri dengan integritas tinggi.'
        )

    def test_pedagogical_explanation_fields_exist(self):
        """Pastikan setiap butir soal memiliki penjelasan 3 tingkat konsep."""
        q = self.q_twk
        self.assertTrue(len(q.bedah_konsep) > 0)
        self.assertTrue(len(q.alasan_pengecoh) > 0)
        self.assertTrue(len(q.tips_cepat) > 0)

    def test_tkp_weights_scoring_and_passing_grade_evaluation(self):
        """Uji perhitungan skor TWK, TIU, dan bobot TKP serta status ambang batas kelulusan."""
        answers = {
            str(self.q_twk.id): 'A',  # TWK Benar = 5
            str(self.q_tiu.id): 'B',  # TIU Benar = 5
            str(self.q_tkp.id): 'C',  # TKP Opsi C bobot = 5
        }

        attempt = CpnsAttempt.evaluate_and_create(
            user=self.user,
            package=self.pkg,
            mode='SIMULASI_CAT',
            answers=answers,
            time_spent_seconds=1200
        )

        self.assertEqual(attempt.skor_twk, 5)
        self.assertEqual(attempt.skor_tiu, 5)
        self.assertEqual(attempt.skor_tkp, 5)
        self.assertEqual(attempt.total_skor, 15)

        # Karena passing grade belum tercapai (TWK 5 < 65, TIU 5 < 80, TKP 5 < 166)
        self.assertFalse(attempt.lulus_twk)
        self.assertFalse(attempt.lulus_tiu)
        self.assertFalse(attempt.lulus_tkp)
        self.assertFalse(attempt.status_lulus)

    def test_tkp_graduated_weight_selection(self):
        """Memilih opsi B pada TKP harus memberikan bobot 3 sesuai dictionary bobot."""
        answers = {
            str(self.q_tkp.id): 'B'  # Bobot opsi B adalah 3
        }
        attempt = CpnsAttempt.evaluate_and_create(
            user=self.user,
            package=self.pkg,
            mode='DRILLING_BEBAS',
            answers=answers,
            time_spent_seconds=300
        )
        self.assertEqual(attempt.skor_tkp, 3)
