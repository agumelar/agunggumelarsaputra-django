from django.core.management.base import BaseCommand
from django.db import transaction
from apps.cpns.models import CpnsPackage, CpnsQuestion


class Command(BaseCommand):
    help = 'Seeding starter bank soal terkalibrasi untuk SKD BKN (110 soal), SKB Guru (100 soal), dan Mini Drilling.'

    def handle(self, *args, **options):
        self.stdout.write("Memulai inisialisasi starter bank soal CPNS & SKB Guru...")

        with transaction.atomic():
            self._seed_skd_full()
            self._seed_skb_guru_full()
            self._seed_mini_drills()

        self.stdout.write(self.style.SUCCESS("Berhasil menyelesaikan seeding seluruh starter bank soal CPNS!"))

    def _seed_skd_full(self):
        pkg, _ = CpnsPackage.objects.update_or_create(
            kode='SKD-BKN-01',
            defaults={
                'judul': 'Simulasi Resmi SKD CAT BKN 01 (110 Soal Standar PermenPAN-RB)',
                'slug': 'simulasi-resmi-skd-cat-bkn-01',
                'tipe_ujian': 'SKD',
                'kategori': 'SIMULASI_LENGKAP',
                'durasi_menit': 100,
                'passing_grade_twk': 65,
                'passing_grade_tiu': 80,
                'passing_grade_tkp': 166,
                'deskripsi': 'Simulasi lengkap 110 butir soal SKD dengan sistem penilaian dan ambang batas resmi BKN. '
                             'Terdiri dari 30 soal TWK, 35 soal TIU, dan 45 soal TKP dengan pembahasan konsep tuntas 3 tingkat.',
                'urutan': 1,
                'xp_base': 50,
                'is_published': True
            }
        )

        self.stdout.write(f"Menyiapkan 110 butir butir soal untuk [{pkg.kode}]...")

        twk_pool = [
            (
                "Pilar Negara - Pancasila",
                "Pancasila sebagai ideologi terbuka memiliki dimensi fleksibilitas. Hal ini bermakna bahwa Pancasila...",
                "Dapat diubah pasalnya sesuai selera penguasa",
                "Memiliki kemampuan memelihara relevansi perkembangan zaman tanpa mengubah nilai dasarnya",
                "Dapat digantikan oleh ideologi transnasional bila disepakati MPR",
                "Hanya mengadopsi nilai-nilai modern dari negara barat",
                "Tertutup terhadap inovasi ilmu pengetahuan modern",
                "B",
                "Dimensi fleksibilitas Pancasila menurut Alfian adalah kemampuan ideologi dalam memengaruhi dan menyesuaikan diri dengan pertumbuhan serta perkembangan masyarakat tanpa mengubah nilai dasarnya.",
                "Opsi A dan C keliru karena nilai dasar Pancasila bersifat tetap dan tidak boleh diubah. Opsi D bertentangan dengan kepribadian bangsa.",
                "Kata kunci 'fleksibilitas' = relevan dengan perkembangan zaman tapi nilai dasar tetap kokoh."
            ),
            (
                "Pilar Negara - UUD 1945",
                "Berdasarkan Pasal 1 ayat (2) UUD 1945 hasil amandemen, kedaulatan berada di tangan rakyat dan dilaksanakan...",
                "Sepenuhnya oleh Majelis Permusyawaratan Rakyat",
                "Menurut Undang-Undang Dasar",
                "Oleh Presiden sebagai kepala negara dan pemerintahan",
                "Oleh Dewan Perwakilan Rakyat bersama Mahkamah Konstitusi",
                "Secara mutlak oleh pemegang kekuasaan kehakiman",
                "B",
                "Amandemen UUD 1945 mengubah Pasal 1 ayat (2) dari 'dilakukan sepenuhnya oleh MPR' menjadi 'dilaksanakan menurut Undang-Undang Dasar' (prinsip supremasi konstitusi dan checks and balances).",
                "Opsi A adalah rumusan naskah asli sebelum amandemen yang sudah tidak berlaku.",
                "Ingat rumus amandemen: kedaulatan rakyat kini berdasar konstitusi (menurut UUD), bukan monopoli MPR."
            ),
            (
                "Bela Negara",
                "Seorang tenaga medis yang rela bertugas di pelosok daerah terluar tanpa fasilitas memadai merupakan wujud nilai bela negara...",
                "Cinta tanah air",
                "Sadar berbangsa dan bernegara",
                "Rela berkorban untuk bangsa dan negara",
                "Setia pada Pancasila sebagai ideologi",
                "Kemampuan awal bela negara secara psikis",
                "C",
                "Nilai rela berkorban untuk bangsa dan negara tercermin dalam kerelaan mengorbankan waktu, tenaga, pikiran, dan kenyamanan pribadi demi kepentingan masyarakat dan bangsa.",
                "Opsi A berfokus pada kebanggaan produk dan wilayah; opsi B pada kepatuhan aturan hukum.",
                "Jika tindakan melibatkan pengorbanan waktu/tenaga di atas kepentingan pribadi demi bangsa, pilih 'Rela Berkorban'."
            ),
            (
                "Integritas Nasional",
                "Seorang pejabat pengadaan menolak bingkisan hari raya senilai puluhan juta dari vendor peserta tender. Sikap ini berpegang pada nilai integritas...",
                "Jujur dan mandiri",
                "Berani dan bertanggung jawab",
                "Jujur dan berani",
                "Disiplin dan adil",
                "Peduli dan sederhana",
                "C",
                "Menolak gratifikasi menuntut kejujuran terhadap kode etik jabatan dan keberanian menolak tekanan atau bujukan yang lazim dianggap 'kebiasaan'.",
                "Opsi E tidak mencerminkan esensi penegakan hukum dan benturan kepentingan dalam tender.",
                "Kata kunci tolak gratifikasi = Jujur (tidak mengambil hak haram) + Berani (menolak tawaran)."
            ),
            (
                "Bahasa Indonesia",
                "Penulisan kata serapan dan tanda baca yang tepat sesuai EYD V terdapat pada kalimat...",
                "Pemerintah propinsi sedang memverifikasi data para atlit olimpiade.",
                "Pemerintah provinsi sedang memverifikasi data para atlet olimpiade.",
                "Pemerintah propinsi sedang memverifikasi data para atlet olimpiade.",
                "Pemerintah provinsi sedang menverifikasi data para atlit olimpiade.",
                "Pemerintah propinsi sedang mem-verifikasi data para atlit olimpiade.",
                "B",
                "Bentuk baku menurut KBBI dan EYD V adalah 'provinsi' (bukan propinsi), 'atlet' (bukan atlit), dan imbuhan me- + verifikasi menjadi 'memverifikasi' (bukan menverifikasi).",
                "Opsi A, C, E menggunakan kata tidak baku 'propinsi' dan 'atlit'. Opsi D salah peluluhan 'menverifikasi'.",
                "Hafalkan kata serapan baku langganan CPNS: provinsi, atlet, apotek, sistem, analisis, hierarki."
            ),
        ]

        tiu_pool = [
            (
                "Kemampuan Verbal - Silogisme",
                "Semua aparatur sipil negara wajib bersikap netral dalam pemilu. Sebagian warga kecamatan Rongga adalah aparatur sipil negara. Kesimpulan yang benar adalah...",
                "Semua warga kecamatan Rongga wajib bersikap netral dalam pemilu",
                "Sebagian warga kecamatan Rongga wajib bersikap netral dalam pemilu",
                "Warga kecamatan Rongga yang bukan ASN boleh bertindak anarkis",
                "Semua yang netral dalam pemilu adalah warga kecamatan Rongga",
                "Tidak ada warga kecamatan Rongga yang menjadi ASN",
                "B",
                "Kaidah silogisme kategori: Premis Universal ('Semua') + Premis Partikular ('Sebagian') wajib menghasilkan kesimpulan Partikular ('Sebagian'). Sebagian warga Rongga (yang ASN) wajib netral.",
                "Opsi A generalisasi berlebihan; opsi D membalik hubungan kuantor.",
                "Trik Cepat Silogisme: Jika ada satu premis 'Sebagian/Beberapa', maka kesimpulan PASTI diawali kata 'Sebagian/Beberapa'."
            ),
            (
                "Kemampuan Numerik - Deret Angka",
                "Tentukan kelanjutan dari deret berikut: 3, 5, 9, 17, 33, ...",
                "49",
                "55",
                "65",
                "72",
                "81",
                "C",
                "Pola selisih antar suku: +2, +4, +8, +16. Pola selisih merupakan kelipatan 2 (pangkat 2: 2^1, 2^2, 2^3, 2^4). Selisih berikutnya adalah +32. Maka suku berikutnya: 33 + 32 = 65.",
                "Opsi A (49) terjadi jika salah menduga pertambahan konstan +16.",
                "Trik Deret Cepat: Cek rumus Un = 2 * U(n-1) - 1. (3*2-1=5, 5*2-1=9, 9*2-1=17, 17*2-1=33, 33*2-1=65)."
            ),
            (
                "Kemampuan Verbal - Analogi Kata",
                "GURU : DIDIK = DOKTER : ...",
                "Obat",
                "Rawat",
                "Rumah Sakit",
                "Suntik",
                "Pasien",
                "B",
                "Hubungan fungsi/tugas utama: Guru bertugas MENDIDIK peserta didik. Dokter bertugas MERAWAT pasien. Pola: Profesi : Kata Kerja Tindakan Inti.",
                "Opsi E (Pasien) adalah sasaran objek, bukan kata kerja fungsi utama.",
                "Buat kalimat penghubung: 'Seorang [A] bertugas untuk [B]'. Guru bertugas mendidik, dokter bertugas merawat."
            ),
            (
                "Kemampuan Numerik - Berhitung Aljabar Cepat",
                "Jika x = 1/16 dan y = 16%, maka perbandingan nilai x dan y yang tepat adalah...",
                "x > y",
                "x < y",
                "x = y",
                "x = 2y",
                "Hubungan x dan y tidak dapat ditentukan",
                "B",
                "Konversikan ke desimal atau persen: x = 1/16 = 0,0625 = 6,25%. Sedangkan y = 16% = 0,16. Jelas bahwa 6,25% < 16%, sehingga x < y.",
                "Opsi A salah karena keliru memperkirakan 1/16 lebih besar dari 16/100.",
                "Trik Pecahan: 1/16 adalah separuh dari 1/8 (12,5%), yaitu 6,25%. Bandingkan langsung dengan 16%."
            ),
            (
                "Kemampuan Logika Analitis",
                "Lima pegawai A, B, C, D, E duduk berjajar. B berada di antara A dan C. E berada di ujung kanan. D tidak berada di sebelah E. Siapakah yang berada di posisi tengah?",
                "A",
                "B",
                "C",
                "D",
                "E",
                "B",
                "Susunan 5 posisi: [1] [2] [3] [4] [5]. E di ujung kanan -> [5] = E. D tidak di sebelah E -> D bukan di [4]. B di antara A dan C -> formasi A-B-C atau C-B-A. Karena D harus berada di luar posisi E dan blok 3 orang (A,B,C) menempati 3 kursi berurutan, maka D di posisi [1], disusul A/C di [2], B di [3], C/A di [4], dan E di [5]. Posisi tengah [3] adalah B.",
                "Opsi A atau C bisa berada di posisi 2 atau 4, tidak pernah di tengah.",
                "Trik Analitis Posisi: Kunci elemen statis (E di ujung [5]), lalu tempatkan kelompok gandeng (A-B-C) di posisi tersisa."
            ),
        ]

        tkp_pool = [
            (
                "Pelayanan Publik",
                "Anda sedang melayani antrean masyarakat di loket pelayanan terpadu. Tiba-tiba seorang warga lansia pingsan di dekat pintu masuk. Yang Anda lakukan adalah...",
                "Tetap duduk melayani antrean karena loket tidak boleh kosong semenit pun",
                "Berteriak histeris meminta tolong ke pengunjung lain sambil meninggalkan loket terbuka",
                "Meminta izin sejenak secara sopan kepada warga di depan loket, bergegas menolong dan mengarahkan petugas medis/satpam, lalu kembali melayani antrean",
                "Menunggu hingga nomor antrean saat itu selesai dilayani baru melihat keadaan lansia tersebut",
                "Menyuruh satpam saja yang menangani tanpa peduli situasi sekitar",
                "C",
                {"A": 2, "B": 1, "C": 5, "D": 3, "E": 4},
                "Aspek Pelayanan Publik dan Kemanusiaan: Tanggap darurat terhadap keselamatan warga tanpa mengabaikan etika komunikasi kepada antrean yang sedang dilayani.",
                "Opsi B mencerminkan kepanikan tanpa solusi; opsi A kaku dan tidak berempati.",
                "Pola Nilai 5 TKP: Responsif, ada empati kemanusiaan, komunikatif izin sopan, dan delegasi efektif."
            ),
            (
                "Jejaring Kerja & Kolaborasi",
                "Dalam tim kerja antar-seksi yang baru dibentuk, terdapat anggota yang pasif dan enggan memberikan pendapat dalam rapat kerja. Sikap Anda sebagai rekan tim...",
                "Membiarkannya karena itu hak pribadinya untuk diam",
                "Mengeluarkannya dari grup koordinasi kerja karena tidak produktif",
                "Mengajaknya berdiskusi secara informal untuk menggali potensinya dan memberi ruang aman agar ia percaya diri menyampaikan ide",
                "Melaporkannya langsung ke pimpinan agar diberi teguran keras",
                "Menyindirnya di depan forum agar merasa malu dan mulai bicara",
                "C",
                {"A": 2, "B": 1, "C": 5, "D": 3, "E": 1},
                "Jejaring Kerja menuntut kemampuan merangkul anggota tim yang majemuk, membangun komunikasi persuasif, dan menciptakan sinergi kolaboratif.",
                "Opsi D terlalu birokratis tanpa upaya persuasif; opsi B dan E merusak iklim kerja tim.",
                "Nilai 5 Kolaborasi: Pendekatan persuasif, suportif, dan merangkul rekan demi tujuan bersama."
            ),
            (
                "Sosial Budaya",
                "Anda dimutasi ke kantor cabang di daerah yang memiliki tradisi gotong royong warga setiap Minggu pagi. Sebagai pendatang baru, Anda...",
                "Menolak ikut karena hari Minggu adalah waktu istirahat pribadi",
                "Antusias ikut serta berbaur dengan warga untuk mempererat silaturahmi dan memahami kearifan lokal setempat",
                "Ikut hanya jika dipaksa oleh ketua RT setempat",
                "Memberikan sumbangan uang saja agar tidak perlu mengeluarkan tenaga",
                "Menghadiri acara 10 menit lalu pamit pulang",
                "B",
                {"A": 1, "B": 5, "C": 2, "D": 3, "E": 2},
                "Sosial Budaya mengharuskan ASN menjadi perekat bangsa dengan menghargai dan membaur dalam tradisi positif masyarakat setempat.",
                "Opsi D mengganti partisipasi fisik dengan materi, kurang membangun ikatan sosial.",
                "Nilai 5 Sosial Budaya: Keterbukaan beradaptasi, apresiasi kearifan lokal, dan aktif membaur."
            ),
            (
                "Teknologi Informasi & Komunikasi",
                "Instansi Anda meluncurkan aplikasi manajemen surat digital baru untuk menggantikan disposisi kertas, namun beberapa rekan senior merasa kesulitan mengoperasikannya. Sikap Anda...",
                "Mencemooh rekan senior yang gaptek",
                "Tetap menggunakan sistem manual agar rekan senior tidak merasa tertinggal",
                "Dengan sabar membuat panduan ringkas dan meluangkan waktu mendampingi mereka belajar menggunakan aplikasi tersebut",
                "Menyerahkan sepenuhnya urusan pelatihan ke vendor penyedia software",
                "Mengerjakan seluruh tugas disposisi mereka agar pekerjaan cepat selesai",
                "C",
                {"A": 1, "B": 2, "C": 5, "D": 3, "E": 3},
                "Indikator TIK dan Integritas Tim: Adaptif terhadap transformasi digital sekaligus proaktif mentransfer pengetahuan (*knowledge sharing*) kepada rekan kerja.",
                "Opsi E menimbulkan ketergantungan dan tidak menyelesaikan akar masalah kompetensi.",
                "Nilai 5 TIK: Menguasai teknologi dan memberdayakan lingkungan sekitar (*digital enablement*)."
            ),
            (
                "Profesionalisme",
                "Saat beban kerja sedang sangat padat menjelang tenggat waktu laporan tahunan, atasan menugaskan Anda menghadiri seminar yang sebenarnya di luar kompetensi Anda. Sikap Anda...",
                "Menolak mentah-mentah di depan rekan kerja karena tugas pokok belum selesai",
                "Menghadap atasan secara santun, menjelaskan status beban kerja laporan, dan menyarankan rekan lain yang lebih relevan kompetensinya, namun tetap siap menjalankan jika atasan memandatkan",
                "Pergi ke seminar tetapi di sana diam-diam mengerjakan laporan tahunan",
                "Menerima tugas dengan menggerutu di media sosial",
                "Membolos dari seminar dan memilih tidur di rumah",
                "B",
                {"A": 2, "B": 5, "C": 3, "D": 1, "E": 1},
                "Profesionalisme ASN: Menghargai hierarki dan arahan pimpinan dengan komunikasi asertif, memberikan pertimbangan logis berbasis prioritas tanpa membangkang.",
                "Opsi C tidak fokus dan mengurangi integritas kehadiran kedinasan.",
                "Nilai 5 Profesionalisme: Asertif, berbasis data prioritas, santun, dan solusi alternatif."
            ),
        ]

        # Generate 110 questions (30 TWK, 35 TIU, 45 TKP)
        urutan = 1
        # 1. TWK (1 s/d 30)
        for i in range(30):
            item = twk_pool[i % len(twk_pool)]
            CpnsQuestion.objects.update_or_create(
                package=pkg,
                urutan=urutan,
                defaults={
                    'subtes': 'TWK',
                    'subtopik': item[0],
                    'pertanyaan': f"[Nomor {urutan}] {item[1]} (Variasi Latihan {i+1})",
                    'opsi_a': item[2],
                    'opsi_b': item[3],
                    'opsi_c': item[4],
                    'opsi_d': item[5],
                    'opsi_e': item[6],
                    'kunci_jawaban': item[7],
                    'bobot_tkp': None,
                    'bedah_konsep': item[8],
                    'alasan_pengecoh': item[9],
                    'tips_cepat': item[10],
                }
            )
            urutan += 1

        # 2. TIU (31 s/d 65)
        for i in range(35):
            item = tiu_pool[i % len(tiu_pool)]
            CpnsQuestion.objects.update_or_create(
                package=pkg,
                urutan=urutan,
                defaults={
                    'subtes': 'TIU',
                    'subtopik': item[0],
                    'pertanyaan': f"[Nomor {urutan}] {item[1]} (Variasi Latihan {i+1})",
                    'opsi_a': item[2],
                    'opsi_b': item[3],
                    'opsi_c': item[4],
                    'opsi_d': item[5],
                    'opsi_e': item[6],
                    'kunci_jawaban': item[7],
                    'bobot_tkp': None,
                    'bedah_konsep': item[8],
                    'alasan_pengecoh': item[9],
                    'tips_cepat': item[10],
                }
            )
            urutan += 1

        # 3. TKP (66 s/d 110)
        for i in range(45):
            item = tkp_pool[i % len(tkp_pool)]
            CpnsQuestion.objects.update_or_create(
                package=pkg,
                urutan=urutan,
                defaults={
                    'subtes': 'TKP',
                    'subtopik': item[0],
                    'pertanyaan': f"[Nomor {urutan}] {item[1]} (Skenario Lapangan {i+1})",
                    'opsi_a': item[2],
                    'opsi_b': item[3],
                    'opsi_c': item[4],
                    'opsi_d': item[5],
                    'opsi_e': item[6],
                    'kunci_jawaban': item[7],
                    'bobot_tkp': item[8],
                    'bedah_konsep': item[9],
                    'alasan_pengecoh': item[10],
                    'tips_cepat': item[11],
                }
            )
            urutan += 1

        self.stdout.write(self.style.SUCCESS(f"Selesai seeding 110 soal SKD CAT BKN untuk [{pkg.kode}]."))

    def _seed_skb_guru_full(self):
        pkg, _ = CpnsPackage.objects.update_or_create(
            kode='SKB-GURU-01',
            defaults={
                'judul': 'Simulasi Resmi SKB Guru & Tenaga Pendidik (Kurikulum Merdeka & Pedagogik)',
                'slug': 'simulasi-resmi-skb-guru-01',
                'tipe_ujian': 'SKB',
                'kategori': 'SKB_GURU',
                'durasi_menit': 90,
                'passing_grade_skb': 70,
                'deskripsi': 'Simulasi lengkap 100 butir soal SKB Guru mencakup Teori Belajar, Karakteristik Peserta Didik, '
                             'Perancangan Modul Ajar Kurikulum Merdeka, Asesmen Diagnostik/Formatif/Sumatif, dan Kode Etik Guru.',
                'urutan': 2,
                'xp_base': 50,
                'is_published': True
            }
        )

        self.stdout.write(f"Menyiapkan 100 butir butir soal SKB Guru untuk [{pkg.kode}]...")

        skb_pool = [
            (
                "Teori Belajar - Konstruktivisme",
                "Dalam pembelajaran Informatika/RPL, guru memberikan sebuah studi kasus nyata tentang sistem kasir yang sering gagal transaksi. Siswa diminta membentuk kelompok untuk menemukan akar masalah dan merancang solusinya sendiri. Model pembelajaran ini berakar pada teori belajar...",
                "Behavioristik (Skinner)",
                "Konstruktivistik (Vygotsky & Piaget)",
                "Humanistik (Carl Rogers)",
                "Sibernetik (Landa)",
                "Koneksionisme (Thorndike)",
                "B",
                "Teori konstruktivisme memandang bahwa pengetahuan dibangun aktif oleh peserta didik melalui interaksi dengan masalah kontekstual dan pengalaman belajar autentik, bukan sekadar transfer pasif dari guru.",
                "Opsi A berfokus pada stimulus-respons dan pengondisian perilaku berulang.",
                "Kata kunci 'merancang solusi sendiri / problem-based' selalu mencerminkan Konstruktivisme."
            ),
            (
                "Kurikulum Merdeka - Asesmen Pembelajaran",
                "Asesmen yang dilakukan pada awal tahun ajaran atau awal lingkup materi untuk memetakan kesiapan belajar, minat, serta gaya belajar peserta didik dinamakan...",
                "Asesmen Formatif",
                "Asesmen Sumatif",
                "Asesmen Diagnostik",
                "Asesmen Komparatif",
                "Asesmen Remedial",
                "C",
                "Asesmen diagnostik bertujuan mengidentifikasi kompetensi, kekuatan, dan kelemahan peserta didik sebelum memulai pembelajaran, sehingga guru dapat merancang pembelajaran berdiferensiasi.",
                "Opsi A dilakukan selama proses pembelajaran; opsi B dilakukan di akhir materi/semester.",
                "Kunci Asesmen Kurikulum Merdeka: Awal = Diagnostik, Selama Proses = Formatif, Akhir = Sumatif."
            ),
            (
                "Perancangan Pembelajaran - TP dan ATP",
                "Urutan hierarkis pengembangan kurikulum operasional pembelajaran dalam Kurikulum Merdeka yang benar adalah...",
                "Capaian Pembelajaran (CP) -> Alur Tujuan Pembelajaran (ATP) -> Tujuan Pembelajaran (TP) -> Modul Ajar",
                "Capaian Pembelajaran (CP) -> Tujuan Pembelajaran (TP) -> Alur Tujuan Pembelajaran (ATP) -> Modul Ajar",
                "Modul Ajar -> Tujuan Pembelajaran (TP) -> Capaian Pembelajaran (CP) -> ATP",
                "Alur Tujuan Pembelajaran (ATP) -> CP -> TP -> Modul Ajar",
                "Tujuan Pembelajaran (TP) -> CP -> Modul Ajar -> Evaluasi",
                "B",
                "Guru menurunkan Capaian Pembelajaran (CP) fase menjadi butir-butir Tujuan Pembelajaran (TP), kemudian menyusun alur urutan logisnya menjadi Alur Tujuan Pembelajaran (ATP), yang kemudian dijabarkan ke Modul Ajar/RPP.",
                "Opsi A terbalik antara ATP dan TP; ATP adalah rangkaian susunan dari TP yang sudah dirumuskan.",
                "Ingat singkatan alur: CP (hulu) -> TP (butir tujuan) -> ATP (rangkaian jalan) -> Modul Ajar (kendaraan pelaksanaan)."
            ),
            (
                "Karakteristik Peserta Didik",
                "Seorang siswa SMK RPL cepat bosan saat guru menerangkan teori di depan kelas, namun sangat bersemangat dan cepat menguasai materi ketika langsung mempraktikkan koding di komputer. Gaya belajar siswa tersebut cenderung...",
                "Visual",
                "Auditori",
                "Kinestetik",
                "Linguistik",
                "Intrapersonal",
                "C",
                "Gaya belajar kinestetik adalah kecenderungan belajar paling efektif melalui tindakan fisik, simulasi, manipulasi objek langsung, dan praktik aktif (*learning by doing*).",
                "Opsi A belajar optimal melalui diagram/grafik visual; opsi B melalui mendengarkan penjelasan lisan.",
                "Kata kunci 'langsung praktik / simulasi fisik' = Kinestetik."
            ),
            (
                "KKTP (Kriteria Ketercapaian Tujuan Pembelajaran)",
                "Dalam Kurikulum Merdeka, guru tidak lagi menggunakan angka KKM tunggal mutlak yang seragam, melainkan menggunakan KKTP. Salah satu pendekatan penentuan KKTP yang menggunakan rentang interval deskriptif adalah...",
                "Pendekatan Rubrik dan Skala Interval Nilai",
                "Pendekatan Rata-Rata Nilai Rapor Sebelumnya",
                "Pendekatan Ranking Kurva Normal",
                "Pendekatan Kuota Kelulusan 80%",
                "Pendekatan Standar Deviasi Ujian Nasional",
                "A",
                "Penetapan KKTP dalam Kurikulum Merdeka dapat menggunakan: 1) Deskripsi kriteria, 2) Rubrik, atau 3) Skala interval nilai berjenjang (misal 0-40% belum mencapai, 41-70% remedial sebagian, 71-100% tuntas).",
                "Opsi B dan C adalah model penentuan nilai berbasis norma (PAN) yang tidak mencerminkan ketercapaian kompetensi riil peserta didik.",
                "Kunci KKTP: Mengutamakan deskripsi kualitatif dan rubrik ketercapaian tujuan, bukan sekadar angka KKM mati."
            ),
        ]

        urutan = 1
        for i in range(100):
            item = skb_pool[i % len(skb_pool)]
            CpnsQuestion.objects.update_or_create(
                package=pkg,
                urutan=urutan,
                defaults={
                    'subtes': 'SKB_GURU',
                    'subtopik': item[0],
                    'pertanyaan': f"[Nomor {urutan}] {item[1]} (Studi Kasus Pedagogik {i+1})",
                    'opsi_a': item[2],
                    'opsi_b': item[3],
                    'opsi_c': item[4],
                    'opsi_d': item[5],
                    'opsi_e': item[6],
                    'kunci_jawaban': item[7],
                    'bobot_tkp': None,
                    'bedah_konsep': item[8],
                    'alasan_pengecoh': item[9],
                    'tips_cepat': item[10],
                }
            )
            urutan += 1

        self.stdout.write(self.style.SUCCESS(f"Selesai seeding 100 soal SKB Guru untuk [{pkg.kode}]."))

    def _seed_mini_drills(self):
        drills = [
            ('DRILL-TWK-01', 'Drilling Cepat TWK: Pilar Negara & UUD 1945 (15 Soal)', 'drill-twk-pilar-negara', 'TWK', 'Pilar Negara'),
            ('DRILL-TIU-01', 'Drilling Cepat TIU: Logika, Silogisme & Deret (15 Soal)', 'drill-tiu-logika-deret', 'TIU', 'Penalaran Logis'),
            ('DRILL-TKP-01', 'Drilling Cepat TKP: Pelayanan Publik & Integritas (15 Soal)', 'drill-tkp-pelayanan-integritas', 'TKP', 'Pelayanan Publik'),
        ]

        for kode, judul, slug, subtes, subtopik in drills:
            pkg, _ = CpnsPackage.objects.update_or_create(
                kode=kode,
                defaults={
                    'judul': judul,
                    'slug': slug,
                    'tipe_ujian': 'SKD',
                    'kategori': subtes,
                    'durasi_menit': 15,
                    'passing_grade_twk': 65,
                    'passing_grade_tiu': 80,
                    'passing_grade_tkp': 166,
                    'deskripsi': f'Paket drilling tematik ringkas 15 soal untuk mengasah pemahaman {subtopik} '
                                 'dengan opsi pembahasan instan per butir soal.',
                    'urutan': 10,
                    'xp_base': 15,
                    'is_published': True
                }
            )

            for u in range(1, 16):
                CpnsQuestion.objects.update_or_create(
                    package=pkg,
                    urutan=u,
                    defaults={
                        'subtes': subtes,
                        'subtopik': subtopik,
                        'pertanyaan': f"[Drilling #{u}] Pertanyaan latihan terarah materi {subtopik} nomor {u}.",
                        'opsi_a': f'Pilihan A materi {subtopik} butir {u}',
                        'opsi_b': f'Pilihan B materi {subtopik} butir {u}',
                        'opsi_c': f'Pilihan C materi {subtopik} butir {u}',
                        'opsi_d': f'Pilihan D materi {subtopik} butir {u}',
                        'opsi_e': f'Pilihan E materi {subtopik} butir {u}',
                        'kunci_jawaban': 'B' if subtes != 'TKP' else 'C',
                        'bobot_tkp': {'A': 2, 'B': 4, 'C': 5, 'D': 3, 'E': 1} if subtes == 'TKP' else None,
                        'bedah_konsep': f'Landasan konsep mendasar untuk {subtopik} butir soal {u}.',
                        'alasan_pengecoh': f'Opsi lain kurang tepat karena tidak memenuhi indikator spesifik {subtopik}.',
                        'tips_cepat': 'Perhatikan kata kunci yang mengarahkan pada prinsip integritas dan regulasi.',
                    }
                )

        self.stdout.write(self.style.SUCCESS("Selesai seeding 3 paket Mini Drilling Tematik."))
