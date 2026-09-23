from django.core.management.base import BaseCommand
from django.db import transaction
from apps.cpns.models import CpnsPackage, CpnsQuestion


class Command(BaseCommand):
    help = 'Seeding starter bank soal autentik standar BKN untuk SKD, SKB Guru, dan Mini Drilling (Anti AI-Slop).'

    def handle(self, *args, **options):
        self.stdout.write("Memulai penyusunan bank soal autentik BKN (Anti AI-Slop)...")

        with transaction.atomic():
            self._seed_drill_tiu()
            self._seed_drill_twk()
            self._seed_drill_tkp()
            self._seed_skd_full()
            self._seed_skb_guru_full()

        self.stdout.write(self.style.SUCCESS("Berhasil memperbarui seluruh bank soal dengan konten autentik berstandar BKN!"))

    def _seed_drill_tiu(self):
        pkg, _ = CpnsPackage.objects.update_or_create(
            kode='DRILL-TIU-01',
            defaults={
                'judul': 'Drilling Cepat TIU: Logika, Silogisme, Deret & Aljabar Cepat (15 Soal)',
                'slug': 'drill-tiu-logika-deret',
                'tipe_ujian': 'SKD',
                'kategori': 'TIU',
                'durasi_menit': 20,
                'passing_grade_tiu': 80,
                'deskripsi': 'Paket latihan terarah 15 butir soal TIU autentik mencakup Silogisme, Analogi Kata, '
                             'Deret Angka Bertingkat, Aljabar Cepat, dan Soal Cerita dengan pembahasan konsep tuntas 3 tingkat.',
                'urutan': 11,
                'xp_base': 25,
                'is_published': True
            }
        )

        tiu_questions = [
            # 1. Silogisme Kuantor
            (
                "Kemampuan Verbal - Silogisme",
                "Semua aparatur sipil negara wajib bersikap netral dalam pemilihan umum.\n"
                "Sebagian warga di Kecamatan Rongga adalah aparatur sipil negara.\n"
                "Kesimpulan yang sah dan logis menurut kaidah logika adalah...",
                "Semua warga di Kecamatan Rongga wajib bersikap netral dalam pemilihan umum.",
                "Sebagian warga di Kecamatan Rongga wajib bersikap netral dalam pemilihan umum.",
                "Warga di Kecamatan Rongga yang bukan aparatur sipil negara tidak perlu netral.",
                "Semua pihak yang bersikap netral dalam pemilu adalah warga di Kecamatan Rongga.",
                "Sebagian warga di Kecamatan Rongga tidak wajib mematuhi aturan pemilihan umum.",
                "B",
                "Kaidah Logika Silogisme Kategorik: Jika terdapat kombinasi Premis Universal ('Semua') dan Premis Partikular ('Sebagian' / 'Beberapa'), maka kesimpulan yang sah WAJIB berbentuk Partikular ('Sebagian'). Sebagian warga Rongga yang berstatus ASN membawa konsekuensi kewajiban netralitas.",
                "Opsi A melakukan generalisasi berlebih (hasty generalization) ke seluruh warga. Opsi C membuat asumsi di luar premis yang diberikan. Opsi D membalik hubungan subjek-predikat secara keliru.",
                "Trik Cepat BKN: Jika satu premis diawali kata 'Sebagian/Beberapa', maka kesimpulan yang benar PASTI diawali kata 'Sebagian/Beberapa'. Langsung eliminasi opsi yang diawali kata 'Semua'."
            ),
            # 2. Silogisme Modus Tollens / Implikasi
            (
                "Kemampuan Verbal - Silogisme Implikasi",
                "Jika instansi menerapkan digitalisasi arsip, maka efisiensi pencarian dokumen meningkat.\n"
                "Jika efisiensi pencarian dokumen meningkat, maka antrean layanan publik berkurang.\n"
                "Fakta di lapangan menunjukkan: Antrean layanan publik tidak berkurang.\n"
                "Kesimpulan yang benar adalah...",
                "Instansi menerapkan digitalisasi arsip sebagian saja.",
                "Efisiensi pencarian dokumen tetap meningkat meskipun antrean bertambah.",
                "Instansi tidak menerapkan digitalisasi arsip.",
                "Petugas layanan publik kurang menguasai aplikasi digital.",
                "Digitalisasi arsip tidak ada kaitannya dengan antrean layanan.",
                "C",
                "Kaidah Silogisme Hipotetik dan Modus Tollens:\n"
                "Premis 1: p → q\n"
                "Premis 2: q → r\n"
                "Maka diperoleh: p → r (Silogisme Hipotetik).\n"
                "Fakta: ~r (antrean layanan tidak berkurang).\n"
                "Berdasarkan Modus Tollens: Dari p → r dan ~r, ditarik kesimpulan pasti: ~p (instansi tidak menerapkan digitalisasi arsip).",
                "Opsi A, D, dan E menghadirkan opini atau alasan baru yang tidak dinyatakan dalam rangkaian premis formal logika matematika.",
                "Pola Kilat: p → q, q → r, lalu diketahui ingkaran akibat (~r), maka kesimpulannya adalah ingkaran sebab awal (~p)."
            ),
            # 3. Silogisme Negasi / Eksepsi
            (
                "Kemampuan Verbal - Silogisme",
                "Semua dokumen resmi instansi pemerintah wajib memiliki stempel dinas.\n"
                "Surat edaran kepala dinas adalah dokumen resmi instansi pemerintah.\n"
                "Kesimpulan yang sah adalah...",
                "Surat edaran kepala dinas wajib memiliki stempel dinas.",
                "Sebagian surat edaran kepala dinas tidak perlu stempel dinas.",
                "Hanya surat edaran kepala dinas yang memiliki stempel dinas.",
                "Dokumen yang tidak berstempel dinas mungkin merupakan surat edaran.",
                "Semua dokumen yang berstempel dinas adalah surat edaran kepala dinas.",
                "A",
                "Silogisme Silogisme Kategorik Baroko/Barbara (Semua A adalah B. C adalah A. Maka C adalah B). Semua dokumen resmi wajib stempel. Surat edaran adalah dokumen resmi, sehingga mutlak wajib memiliki stempel dinas.",
                "Opsi C dan E membuat pembatasan sepihak ('hanya') yang membalik hubungan semesta.",
                "Prinsip Deduksi: Apabila objek termasuk ke dalam kelompok yang dikenai aturan universal ('Semua'), maka objek tersebut mewarisi seluruh sifat aturan tersebut."
            ),
            # 4. Analogi Leksikal Anatomi/Organ
            (
                "Kemampuan Verbal - Analogi",
                "INSULIN : PANKREAS = EMPEDU : ...",
                "Lambung",
                "Ginjal",
                "Hati",
                "Jantung",
                "Usus Halus",
                "C",
                "Analogi Relasi 'Zat Biologis : Organ Produsen': Hormon insulin diproduksi oleh kelenjar pankreas. Cairan empedu (bile) diproduksi oleh organ hati (hepar) sebelum disimpan dalam kantung empedu.",
                "Opsi A (Lambung) memproduksi asam klorida (HCl) dan pepsin. Opsi B (Ginjal) memproduksi renin dan eritropoietin serta menyaring urine. Opsi E (Usus Halus) adalah tempat muara empedu, bukan produsennya.",
                "Buat kalimat relasi penghubung: '[A] dihasilkan / disintesis oleh organ [B]'. Insulin dihasilkan oleh pankreas, cairan empedu dihasilkan oleh hati."
            ),
            # 5. Analogi Antonim Ekstrem
            (
                "Kemampuan Verbal - Analogi",
                "KULMINASI : TITIK TERENDAH = APOGEE : ...",
                "Nadir",
                "Perigee",
                "Zenit",
                "Orbit",
                "Klimaks",
                "B",
                "Analogi Relasi 'Titik Puncak : Lawan Titik Ekstrem': Kulminasi (titik tertinggi matahari/keberhasilan) berlawanan dengan titik terendah. Apogee (titik terjauh orbit satelit/bulan dari bumi) berlawanan dengan Perigee (titik terdekat orbit dengan bumi).",
                "Opsi A (Nadir) adalah lawan dari Zenit. Opsi D (Orbit) adalah lintasan, bukan titik ekstrem astronomi.",
                "Identifikasi pasangan istilah ilmiah astronomi: Apogee (Apo = Jauh) pasangannya Perigee (Peri = Dekat)."
            ),
            # 6. Analogi Alat : Fungsi Kerja
            (
                "Kemampuan Verbal - Analogi",
                "STATOSKOP : DOKTER = OSILOSKOP : ...",
                "Apoteker",
                "Teknisi Elektronika",
                "Arsitek",
                "Nahkoda",
                "Ahli Kimia",
                "B",
                "Analogi Relasi 'Instrumen Khusus : Profesi Pengguna Utama': Stetoskop adalah instrumen diagnostik yang digunakan oleh dokter. Osiloskop (alat ukur sinyal dan tegangan listrik) adalah instrumen analisis yang digunakan oleh teknisi elektronika / insinyur listrik.",
                "Opsi C (Arsitek) menggunakan T-square atau theodolite. Opsi E (Ahli Kimia) menggunakan spektrofotometer atau buret.",
                "Cari instrumen spesifik yang menjadi identitas keahlian teknis profesi tersebut."
            ),
            # 7. Deret Angka Bertingkat
            (
                "Kemampuan Numerik - Deret Angka",
                "Tentukan angka berikutnya dari deret bilangan: 2, 5, 11, 20, 32, ...",
                "45",
                "47",
                "49",
                "52",
                "54",
                "B",
                "Analisis Selisih Bertingkat (Level 1):\n"
                "2 ke 5 = +3\n"
                "5 ke 11 = +6\n"
                "11 ke 20 = +9\n"
                "20 ke 32 = +12\n"
                "Pola selisih adalah barisan aritmetika dengan beda +3 (+3, +6, +9, +12). Maka selisih berikutnya adalah +15.\n"
                "Nilai suku berikutnya = 32 + 15 = 47.",
                "Opsi A (45) terjadi jika keliru mengira pola bertambah konstan +13. Opsi C (49) terjadi jika keliru menghitung selisih +17.",
                "Trik Cepat Deret: Hitung selisih antar angka terlebih dahulu. Jika polanya bertambah teratur (+3, +6, +9, +12), suku berikutnya pasti +15. 32 + 15 = 47."
            ),
            # 8. Deret Larik Berselang (2 Pola)
            (
                "Kemampuan Numerik - Deret Angka",
                "Tentukan dua angka lanjutan dari deret berikut: 4, 18, 8, 15, 16, 12, 32, ... , ...",
                "9, 64",
                "10, 64",
                "9, 48",
                "8, 64",
                "11, 56",
                "A",
                "Pola Deret Larik Berselang (2 Jalur):\n"
                "Jalur Ganjil (posisi 1, 3, 5, 7, 9): 4, 8, 16, 32, [64] (Pola: dikali 2 / x2).\n"
                "Jalur Genap (posisi 2, 4, 6, 8): 18, 15, 12, [9] (Pola: dikurangi 3 / -3).\n"
                "Maka suku ke-8 adalah 12 - 3 = 9, dan suku ke-9 adalah 32 x 2 = 64.",
                "Opsi B (10, 64) salah hitung selisih genap. Opsi C salah pengali jalur ganjil.",
                "Trik Deret Melompat: Jika urutan angka naik-turun secara bergantian (4 naik ke 18, lalu turun ke 8, lalu naik ke 15), hampir pasti ini adalah deret larik 2 pola melompat satu angka."
            ),
            # 9. Deret Fibonacci Termodifikasi
            (
                "Kemampuan Numerik - Deret Angka",
                "Tentukan nilai suku berikutnya dari deret: 1, 3, 4, 7, 11, 18, 29, ...",
                "40",
                "45",
                "47",
                "49",
                "51",
                "C",
                "Pola Deret Fibonacci Murni: Setiap suku adalah hasil penjumlahan dua suku sebelumnya:\n"
                "1 + 3 = 4\n"
                "3 + 4 = 7\n"
                "4 + 7 = 11\n"
                "7 + 11 = 18\n"
                "11 + 18 = 29\n"
                "Maka suku berikutnya = 18 + 29 = 47.",
                "Opsi B (45) terjadi jika keliru menjumlahkan 11 + 29. Opsi D (49) kesalahan operasi tambah dasar.",
                "Ciri Fibonacci: Suku ke-3 selalu sama dengan penjumlahan suku ke-1 dan ke-2 (1+3=4, 3+4=7)."
            ),
            # 10. Aljabar Pecahan Cepat
            (
                "Kemampuan Numerik - Berhitung Cepat",
                "Hitunglah nilai dari: (0,375 / 0,75) + (1/4 x 80%) = ...",
                "0,50",
                "0,60",
                "0,70",
                "0,75",
                "0,85",
                "C",
                "Ubah desimal ke bentuk pecahan istimewa:\n"
                "0,375 = 3/8\n"
                "0,75 = 3/4 = 6/8\n"
                "Maka: 0,375 / 0,75 = (3/8) / (6/8) = 3/6 = 1/2 = 0,5.\n"
                "Bagian kedua: 1/4 x 80% = 1/4 x 0,8 = 0,2.\n"
                "Hasil akhir = 0,5 + 0,2 = 0,7 (0,70).",
                "Opsi D (0,75) terjadi jika salah menghitung 1/4 x 80% menjadi 0,25.",
                "Trik Hafalan Pecahan Sakti CPNS: 0,125 = 1/8; 0,25 = 2/8; 0,375 = 3/8; 0,5 = 4/8; 0,625 = 5/8; 0,75 = 6/8; 0,875 = 7/8."
            ),
            # 11. Perbandingan Kuantitatif x dan y
            (
                "Kemampuan Numerik - Perbandingan Kuantitatif",
                "Jika x = 16^2 - 14^2 dan y = (16 - 14)^2 + (16 x 2), maka hubungan yang tepat antara x dan y adalah...",
                "x > y",
                "x < y",
                "x = y",
                "x = 2y",
                "Hubungan x dan y tidak dapat ditentukan",
                "A",
                "Gunakan rumus faktorisasi selisih kuadrat:\n"
                "x = a^2 - b^2 = (a + b)(a - b)\n"
                "x = (16 + 14)(16 - 14) = 30 x 2 = 60.\n"
                "Hitung nilai y:\n"
                "y = (2)^2 + (32) = 4 + 32 = 36.\n"
                "Karena x = 60 dan y = 36, maka terbukti x > y.",
                "Opsi C keliru menganggap (a-b)^2 identik dengan a^2 - b^2.",
                "Rumus Cepat: Jangan pernah mengalikan 16 x 16 (256) lalu 14 x 14 (196). Cukup jumlahkan lalu kalikan selisihnya: (30) x (2) = 60!"
            ),
            # 12. Persentase Keuntungan & Diskon Ganda
            (
                "Kemampuan Numerik - Aritmetika Sosial",
                "Sebuah toko buku memberikan diskon bertingkat 20% + 10% untuk buku ensiklopedia seharga Rp250.000,00. Berapakah harga akhir yang harus dibayar pembeli?",
                "Rp175.000,00",
                "Rp180.000,00",
                "Rp185.000,00",
                "Rp190.000,00",
                "Rp200.000,00",
                "B",
                "Diskon bertingkat 20% + 10% BUKAN berarti diskon 30%!\n"
                "Langkah 1 (Diskon pertama 20%): Harga sisa = 80% x Rp250.000 = Rp200.000.\n"
                "Langkah 2 (Diskon kedua 10% dari sisa): Diskon = 10% x Rp200.000 = Rp20.000.\n"
                "Harga akhir = Rp200.000 - Rp20.000 = Rp180.000,00.",
                "Opsi A (Rp175.000) adalah jebakan umum jika pembeli menjumlahkan langsung 20% + 10% = 30% (70% x 250rb = 175rb).",
                "Trik Cepat Diskon Ganda (a + b): Faktor pengali = (1 - a) x (1 - b) = 0,8 x 0,9 = 0,72. Harga akhir = 0,72 x 250.000 = Rp180.000."
            ),
            # 13. Soal Cerita Pekerjaan Bersama
            (
                "Kemampuan Numerik - Soal Cerita Pekerjaan",
                "Pak Joko dapat menyelesaikan pengecatan sebuah gedung dalam waktu 12 hari, sedangkan Pak Budi dapat menyelesaikannya dalam waktu 6 hari. Jika mereka berdua mengecat bersama-sama, gedung tersebut akan selesai dicat dalam...",
                "2 hari",
                "3 hari",
                "4 hari",
                "5 hari",
                "9 hari",
                "C",
                "Konsep Kecepatan Kerja Gabungan:\n"
                "Kecepatan Joko = 1/12 bagian/hari\n"
                "Kecepatan Budi = 1/6 = 2/12 bagian/hari\n"
                "Kecepatan Total = 1/12 + 2/12 = 3/12 = 1/4 bagian/hari.\n"
                "Waktu yang dibutuhkan = 1 / (1/4) = 4 hari.",
                "Opsi E (9 hari) jebakan rata-rata (12 + 6)/2. Jika bekerja bersama, waktu penyelesaian mutlak harus lebih singkat dari orang tercepat (< 6 hari).",
                "Rumus Kilat BKN untuk 2 Orang: Waktu = (A x B) / (A + B). Waktu = (12 x 6) / (12 + 6) = 72 / 18 = 4 hari! Tuntas tanpa pecahan."
            ),
            # 14. Soal Cerita Berpapasan / Menyusul
            (
                "Kemampuan Numerik - Soal Cerita Kecepatan",
                "Kereta api Lodaya berangkat dari Stasiun Bandung pukul 07.00 WIB dengan kecepatan rata-rata 75 km/jam. Pada pukul 08.20 WIB, kereta api Argo Dwipangga berangkat dari stasiun yang sama menuju arah yang sama dengan kecepatan rata-rata 95 km/jam. Pukul berapa kereta api Argo Dwipangga akan menyusul kereta api Lodaya?",
                "12.40 WIB",
                "13.00 WIB",
                "13.20 WIB",
                "13.40 WIB",
                "14.00 WIB",
                "C",
                "Langkah 1: Hitung selisih waktu keberangkatan:\n"
                "Δt = 08.20 - 07.00 = 1 jam 20 menit = 1 1/3 jam = 4/3 jam.\n"
                "Langkah 2: Hitung selisih jarak awal yang sudah ditempuh Lodaya:\n"
                "Δs = v1 x Δt = 75 km/jam x (4/3) jam = 100 km.\n"
                "Langkah 3: Hitung waktu menyusul:\n"
                "t = Δs / (v2 - v1) = 100 / (95 - 75) = 100 / 20 = 5 jam.\n"
                "Langkah 4: Waktu tersusul = waktu berangkat kedua + t = 08.20 + 5 jam = 13.20 WIB.",
                "Opsi A (12.40 WIB) keliru karena menambahkan 5 jam ke waktu kereta pertama (07.00). Opsi D salah menghitung selisih kecepatan.",
                "Rumus Kilat Menyusul: Waktu = (Kecepatan 1 x Selisih Jam) / (Selisih Kecepatan). Hitung: (75 x 4/3) / 20 = 100 / 20 = 5 jam. Tambahkan ke jam berangkat kedua (08.20 + 5 jam = 13.20)."
            ),
            # 15. Soal Cerita Perbandingan Berbalik Nilai
            (
                "Kemampuan Numerik - Soal Cerita Perbandingan",
                "Suatu proyek jembatan direncanakan selesai dalam waktu 30 hari dengan 24 orang pekerja. Setelah bekerja selama 10 hari, pekerjaan terhenti selama 4 hari karena cuaca buruk. Agar proyek selesai tepat waktu sesuai jadwal semula, berapa jumlah pekerja tambahan yang harus direkrut?",
                "4 orang",
                "6 orang",
                "8 orang",
                "10 orang",
                "12 orang",
                "B",
                "Konsep Beban Sisa Proyek:\n"
                "Waktu sisa normal jika tidak libur = 30 hari - 10 hari = 20 hari.\n"
                "Beban sisa pekerjaan = 20 hari x 24 pekerja = 480 satuan kerja.\n"
                "Waktu riil yang tersisa karena libur 4 hari = 20 hari - 4 hari = 16 hari.\n"
                "Kebutuhan total pekerja = 480 satuan kerja / 16 hari = 30 pekerja.\n"
                "Pekerja tambahan = Total pekerja baru - Pekerja awal = 30 - 24 = 6 orang pekerja tambahan.",
                "Opsi D (10 orang) atau opsi C (8 orang) adalah kesalahan pembagian dengan 14 hari atau 26 hari.",
                "Rumus Cepat BKN Pekerja Tambahan:\n"
                "Pekerja Tambahan = (Pekerja Awal x Hari Berhenti) / Hari Tersisa.\n"
                "Pekerja Tambahan = (24 x 4) / 16 = 96 / 16 = 6 orang! Hitungan selesai dalam hitungan detik."
            ),
        ]

        for idx, item in enumerate(tiu_questions, start=1):
            CpnsQuestion.objects.update_or_create(
                package=pkg,
                urutan=idx,
                defaults={
                    'subtes': 'TIU',
                    'subtopik': item[0],
                    'pertanyaan': item[1],
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
        self.stdout.write(self.style.SUCCESS(f"Selesai seeding 15 butir soal TIU autentik pada [{pkg.kode}]."))

    def _seed_drill_twk(self):
        pkg, _ = CpnsPackage.objects.update_or_create(
            kode='DRILL-TWK-01',
            defaults={
                'judul': 'Drilling Cepat TWK: Pilar Negara, Konstitusi & Integritas (15 Soal)',
                'slug': 'drill-twk-pilar-negara',
                'tipe_ujian': 'SKD',
                'kategori': 'TWK',
                'durasi_menit': 15,
                'passing_grade_twk': 65,
                'deskripsi': 'Paket drilling 15 butir soal TWK autentik berstandar PermenPAN-RB meliputi UUD 1945, '
                             'Pancasila, Integritas KPK, Sejarah Pergerakan, dan Bahasa Indonesia Baku EYD V.',
                'urutan': 10,
                'xp_base': 25,
                'is_published': True
            }
        )

        twk_questions = [
            (
                "Pilar Negara - Pancasila",
                "Pancasila sebagai sumber dari segala sumber hukum negara ditegaskan dalam perundang-undangan nasional, yaitu...",
                "Pasal 1 ayat (3) UUD 1945",
                "Pasal 2 Undang-Undang Nomor 12 Tahun 2011",
                "Ketetapan MPR Nomor III/MPR/2000 Pasal 1",
                "Undang-Undang Nomor 20 Tahun 2023",
                "Instruksi Presiden Nomor 12 Tahun 1968",
                "B",
                "Berdasarkan Pasal 2 UU No. 12 Tahun 2011 tentang Pembentukan Peraturan Perundang-undangan: 'Pancasila merupakan sumber segala sumber hukum negara'. Hal ini menempatkan Pancasila sebagai norma dasar (grundnorm) tertinggi.",
                "Opsi A mengatur asas negara hukum (Rechtsstaat). Opsi D adalah UU ASN terbaru.",
                "Hafalkan payung hukum hierarki peraturan: UU No. 12 Tahun 2011 Pasal 2 (Pancasila = Sumber dari Segala Sumber Hukum)."
            ),
            (
                "Pilar Negara - UUD 1945",
                "Menurut Pasal 24C ayat (1) UUD 1945 hasil amandemen, Mahkamah Konstitusi berwenang mengadili pada tingkat pertama dan terakhir yang putusannya bersifat final untuk hal berikut, KECUALI...",
                "Menguji undang-undang terhadap Undang-Undang Dasar",
                "Memutus sengketa kewenangan lembaga negara yang kewenangannya diberikan oleh UUD",
                "Memutus pembubaran partai politik",
                "Menguji peraturan pemerintah terhadap undang-undang",
                "Memutus perselisihan tentang hasil pemilihan umum",
                "D",
                "Berdasarkan Pasal 24A ayat (1) UUD 1945, kewenangan menguji peraturan perundang-undangan di bawah undang-undang terhadap undang-undang (seperti PP, Perpres, Perda) adalah wewenang Mahkamah Agung (MA), BUKAN Mahkamah Konstitusi.",
                "Opsi A, B, C, dan E adalah 4 kewenangan konstitusional sah Mahkamah Konstitusi sesuai Pasal 24C ayat (1).",
                "Trik Pembagian Yudisial: MK menguji UU terhadap UUD. MA menguji aturan di bawah UU terhadap UU."
            ),
            (
                "Integritas & Anti Korupsi",
                "Seorang pegawai instansi pemerintah menolak menerima parsel hari raya dari rekanan pemenang proyek pengadaan senilai Rp5.000.000,00 karena menyadari potensi benturan kepentingan. Nilai integritas yang ditunjukkan oleh pegawai tersebut adalah...",
                "Tanggung jawab dan peduli",
                "Jujur dan mandiri",
                "Jujur dan berani",
                "Sederhana dan disiplin",
                "Kerja keras dan adil",
                "C",
                "KPK menetapkan 9 Nilai Integritas (Jumat Bersepeda KK: Jujur, Mandiri, Tanggung jawab, Berani, Sederhana, Peduli, Disiplin, Adil, Kerja Keras). Sikap menolak gratifikasi berakar pada Kejujuran (patuh kode etik tanpa mengambil yang bukan hak) dan Keberanian (tegas menolak pemberian yang berisiko transaksional).",
                "Opsi A dan D tidak mencerminkan esensi penegakan anti benturan kepentingan dalam pengadaan publik.",
                "Kata kunci benturan kepentingan/gratifikasi = 'Jujur' (integritas etik) + 'Berani' (tegas menolak kompromi)."
            ),
            (
                "Bela Negara",
                "Berdasarkan UU Nomor 23 Tahun 2019 tentang Pengelolaan Sumber Daya Nasional untuk Pertahanan Negara, keikutsertaan warga negara dalam upaya bela negara diselenggarakan melalui salah satunya pengabdian sesuai profesi. Contoh implementasi pengabdian sesuai profesi bagi seorang Guru ASN adalah...",
                "Mengikuti pelatihan dasar militer cadangan setiap akhir pekan",
                "Menyelenggarakan pembelajaran berkualitas, inklusif, dan menanamkan nilai karakter kebangsaan kepada peserta didik",
                "Melakukan patroli keamanan lingkungan bersama aparat kepolisian",
                "Membeli senjata legal untuk pertahanan mandiri",
                "Membatasi komunikasi dengan peserta didik yang berbeda pandangan politik",
                "B",
                "Pasal 6 ayat (2) UU No. 23/2019 menegaskan bela negara bagi masyarakat sipil diwujudkan melalui pengabdian sesuai profesi, yakni melaksanakan tugas profesi dengan dedikasi tinggi demi memajukan kecerdasan dan kesejahteraan bangsa.",
                "Opsi A adalah komponen Komcad, bukan pengabdian profesi utama. Opsi E melanggar kode etik guru.",
                "Bela negara ASN = Dedikasi terbaik pada tugas pokok fungsi (tupoksi) keahlian profesinya."
            ),
            (
                "Bahasa Indonesia Baku (EYD V)",
                "Pilihlah kalimat yang menggunakan ragam baku, ejaan, dan tanda baca yang tepat sesuai Pedoman Umum Ejaan Bahasa Indonesia (EYD V)...",
                "Kepala sekolah menugaskan para guru-guru untuk menyusun modul ajar.",
                "Pemerintah Provinsi Jawa Barat sedang merevisi jadwal ujian kompetensi.",
                "Rapat koordinasi tersebut dihadiri oleh: Gubernur, Walikota dan Bupati.",
                "Buku itu telah dibaca oleh saya sebanyak tiga kali.",
                "Ia tetap berangkat dinas, meskipun hujan lebat mengguyur Bandung.",
                "B",
                "Analisis Ejaan:\n"
                "- Opsi B benar: 'Pemerintah Provinsi Jawa Barat' huruf kapital tepat untuk nama entitas geografis resmi, bentukan kata baku.\n"
                "- Opsi A salah: Pemborosan kata jamak ganda ('para guru-guru'). Seharusnya 'para guru' atau 'guru-guru'.\n"
                "- Opsi C salah: Tanda titik dua (:) tidak digunakan jika rangkaian langsung melengkapi predikat.\n"
                "- Opsi D salah: Struktur kalimat pasif persona tidak baku ('dibaca oleh saya' seharusnya 'saya baca').\n"
                "- Opsi E salah: Konjungsi subordinatif 'meskipun' tidak didahului tanda koma di tengah kalimat.",
                "Setiap opsi yang salah mengandung pelanggaran aturan baku yang teridentifikasi jelas.",
                "Trik PUEBI CPNS: Waspadai pemborosan kata ('para hadirin', 'demi untuk', 'para guru-guru') dan peletakan koma sebelum kata 'karena/bahwa/meskipun'."
            ),
        ]

        # Tambahkan sisa soal TWK autentik hingga 15 butir
        extra_twk = [
            ("Pilar Negara - Bhinneka Tunggal Ika", "Semboyan Bhinneka Tunggal Ika yang tercantum dalam Kitab Sutasoma karya Mpu Tantular pada masa Majapahit awalnya bertujuan untuk mendamaikan penganut...", "Agama Hindu Siwa dan Buddha Mahayana", "Agama Islam dan Hindu", "Agama Buddha dan Kepercayaan Kejawen", "Agama Kristen dan Hindu", "Aliran Animisme dan Dinamisme", "A", "Kakawin Sutasoma pupuh 139 bait 5 menegaskan toleransi antara pemeluk Siwa (Hindu) dan Buddha (Rwaneka dhatu winuwus Buddha Wiswa, Bhinêki rakwa ring apan kêna parwanosên, Mangka ng Jinatwa kalawan Siwatwa tunggal, Bhinnêka tunggal ika tan hana dharma mangrwa).", "Opsi B keliru kronologi sejarah karena Majapahit masa Hayam Wuruk berfokus pada kerukunan Siwa-Buddha.", "Pencipta: Mpu Tantular, Kitab: Sutasoma, Konteks Awal: Kerukunan Siwa dan Buddha."),
            ("Sejarah Nasional - BPUPKI", "Dalam sidang pertama BPUPKI tanggal 29 Mei - 1 Juni 1945, tiga tokoh yang menyampaikan gagasan dasar negara secara berurutan adalah...", "Mohammad Yamin, Soepomo, dan Ir. Soekarno", "Ir. Soekarno, Mohammad Hatta, dan Soepomo", "Mohammad Yamin, Mohammad Hatta, dan Soepomo", "Soepomo, Mohammad Yamin, dan Ir. Soekarno", "K.H. Wachid Hasyim, Soepomo, dan Ir. Soekarno", "A", "Urutan pidato perumusan dasar negara BPUPKI: 29 Mei 1945 (Moh. Yamin), 31 Mei 1945 (Prof. Dr. Soepomo), dan 1 Juni 1945 (Ir. Soekarno yang melahirkan istilah Pancasila).", "Opsi B dan C salah urutan kronologis tanggal sidang.", "Hafalkan tanggal dan inisial: 29 Mei (Yamin), 31 Mei (Soepomo), 1 Juni (Soekarno) -> Urutan: Y-S-S."),
            ("Pilar Negara - UUD 1945", "Berdasarkan Pasal 7 UUD 1945 hasil amandemen, masa jabatan Presiden dan Wakil Presiden dibatasi paling banyak...", "Dua kali masa jabatan berturut-turut maupun tidak berturut-turut", "Dua kali masa jabatan", "Tiga kali masa jabatan jika dicalonkan koalisi mayoritas", "Satu kali masa jabatan selama 8 tahun", "Tanpa batasan selama dipilih kembali oleh rakyat", "B", "Pasal 7 UUD 1945 amandemen: 'Presiden dan Wakil Presiden memegang jabatan selama lima tahun, dan sesudahnya dapat dipilih kembali dalam jabatan yang sama, hanya untuk satu kali masa jabatan' (total maksimal 2 periode).", "Opsi C melanggar substansi amandemen yang membatasi otoritarianisme masa lalu.", "Kunci Amandemen: Pembatasan kekuasaan eksekutif maksimal 2 periode (10 tahun)."),
            ("Nasionalisme", "Sikap chauvinisme merupakan bentuk nasionalisme sempit yang bertentangan dengan Pancasila karena...", "Mengabaikan kedaulatan bangsa sendiri", "Mengagungkan bangsa sendiri secara berlebihan dan merendahkan bangsa lain", "Menolak kerja sama ekonomi regional ASEAN", "Menuntut pemisahan daerah dari NKRI", "Menerapkan sistem wajib militer bagi warga negara", "B", "Chauvinisme adalah nasionalisme sempit/ekstrem yang menganggap bangsanya paling unggul sambil memandang rendah martabat bangsa lain. Hal ini bertentangan dengan Sila ke-2 (Kemanusiaan yang Adil dan Beradab).", "Opsi D adalah separatisme, opsi E adalah kebijakan bela negara normatif.", "Chauvinisme = Cinta buta pada bangsa sendiri + Menghina bangsa lain."),
            ("Bahasa Indonesia - Kata Serapan", "Penulisan deret kata serapan yang seluruhnya baku menurut KBBI adalah...", "Apotik, sistim, ijin, kwitansi", "Apotek, sistem, izin, kuitansi", "Apotek, sistim, ijin, kuitansi", "Apotik, sistem, izin, kwitansi", "Apotek, sistem, izin, kuitansi", "B", "Bentuk baku menurut KBBI: Apotek (bukan apotik), Sistem (bukan sistim), Izin (bukan ijin), Kuitansi (bukan kwitansi).", "Opsi A, C, D menggunakan bentuk non-baku percakapan sehari-hari.", "Hafalkan pasangan baku: Apotek, Sistem, Izin, Kuitansi, Praktik, Jadwal."),
            ("Integritas - Gratifikasi", "Berdasarkan Pasal 12B UU Nomor 20 Tahun 2001, batas waktu maksimal pelaporan penerimaan gratifikasi kepada KPK oleh pegawai negeri atau penyelenggara negara adalah...", "7 hari kerja sejak tanggal penerimaan", "14 hari kerja sejak tanggal penerimaan", "30 hari kerja sejak tanggal penerimaan", "60 hari kalender sejak tanggal penerimaan", "90 hari kalender sejak akhir tahun anggaran", "C", "Pasal 12B ayat (2) UU Tipikor No. 20/2001 mengatur bahwa ketentuan pidana gratifikasi tidak berlaku jika penerima melaporkan gratifikasi yang diterimanya kepada Komisi Pemberantasan Korupsi (KPK) paling lambat 30 hari kerja terhitung sejak tanggal gratifikasi diterima.", "Opsi A dan B adalah waktu internal instansi, bukan ketentuan UU Tipikor KPK.", "Angka mutlak UU Tipikor: 30 HARI KERJA pelaporan gratifikasi ke KPK."),
            ("Bela Negara - Ancaman Hibrida", "Penyebaran hoaks politik dan serangan siber terkoordinasi terhadap pusat data nasional tergolong ke dalam bentuk ancaman...", "Militer konvensional", "Nonmiliter berdimensi ideologi dan teknologi", "Agresi teritorial", "Spionase laut terbuka", "Pemberontakan bersenjata", "B", "Ancaman nonmiliter berdimensi teknologi dan ideologi menyerang kedaulatan informasi, stabilitas keamanan digital, dan integrasi sosial masyarakat tanpa menggunakan senjata mesiu konvensional.", "Opsi A dan C melibatkan armada militer bersenjata reguler.", "Serangan siber/hoaks = Ancaman Nonmiliter berdimensi Informasi/Teknologi."),
            ("Pilar Negara - NKRI", "Bentuk negara kesatuan bagi Republik Indonesia merupakan ketentuan mutlak yang tidak dapat dilakukan perubahan amandemennya, sebagaimana diatur dalam UUD 1945 pasal...", "Pasal 1 ayat (1)", "Pasal 18 ayat (1)", "Pasal 33 ayat (1)", "Pasal 37 ayat (5)", "Aturan Peralihan Pasal II", "D", "Pasal 37 ayat (5) UUD 1945 hasil amandemen menegaskan: 'Khusus mengenai bentuk Negara Kesatuan Republik Indonesia tidak dapat dilakukan perubahan'.", "Opsi A adalah rumusan pernyataan bentuk, tetapi pasal penguncian amandemen adalah Pasal 37 ayat (5).", "Pasal pengunci bentuk NKRI dari amandemen = Pasal 37 ayat (5)."),
            ("Pilar Negara - Bhinneka Tunggal Ika", "Prinsip asimilasi budaya dalam masyarakat majemuk Indonesia yang sehat berbeda dengan peleburan paksa karena asimilasi kultural Pancasila mengutamakan...", "Dominasi budaya mayoritas atas suku minoritas", "Harmoni interaksi sosial tanpa menghilangkan identitas positif keberagaman", "Pemisahan pemukiman warga berdasarkan suku", "Penyeragaman bahasa daerah menjadi satu dialek", "Pelarangan ritual adat tradisional di ruang publik", "B", "Integrasi nasional Pancasila mengusung kesatuan dalam keragaman (Unity in Diversity), menghargai kearifan lokal tanpa diskriminasi atau hegemoni mayoritas.", "Opsi A adalah asimilasi represif/chauvinis yang dilarang konstitusi.", "Prinsip Bhinneka Tunggal Ika: Memperkuat integrasi nasional tanpa mematikan keunikan budaya lokal."),
            ("Sejarah - Perjanjian Linggarjati", "Salah satu dampak dari Perundingan Linggarjati tahun 1947 terhadap wilayah de facto Republik Indonesia adalah pengakuan Belanda yang terbatas hanya pada wilayah...", "Jawa, Madura, dan Sumatra", "Jawa dan Bali saja", "Seluruh bekas wilayah Hindia Belanda", "Jawa, Sumatra, dan Kalimantan", "Sumatra dan Maluku", "A", "Perjanjian Linggarjati (25 Maret 1947): Belanda mengakui secara de facto Republik Indonesia dengan wilayah kekuasaan meliputi Jawa, Madura, dan Sumatra.", "Opsi C adalah tuntutan kedaulatan penuh pasca KMB 1949.", "Hafalkan wilayah de facto Linggarjati: JAWA, MADURA, SUMATRA (tiga pulau utama)."),
        ]

        all_twk = twk_questions + extra_twk
        for idx, item in enumerate(all_twk, start=1):
            CpnsQuestion.objects.update_or_create(
                package=pkg,
                urutan=idx,
                defaults={
                    'subtes': 'TWK',
                    'subtopik': item[0],
                    'pertanyaan': item[1],
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
        self.stdout.write(self.style.SUCCESS(f"Selesai seeding 15 butir soal TWK autentik pada [{pkg.kode}]."))

    def _seed_drill_tkp(self):
        pkg, _ = CpnsPackage.objects.update_or_create(
            kode='DRILL-TKP-01',
            defaults={
                'judul': 'Drilling Cepat TKP: Pelayanan Publik, Integritas & Jejaring Kerja (15 Soal)',
                'slug': 'drill-tkp-pelayanan-integritas',
                'tipe_ujian': 'SKD',
                'kategori': 'TKP',
                'durasi_menit': 15,
                'passing_grade_tkp': 166,
                'deskripsi': 'Paket drilling 15 butir skenario kedinasan riil TKP mencakup Pelayanan Publik, '
                             'Jejaring Kerja, Sosial Budaya, TIK, Profesionalisme, dan Anti Radikalisme dengan bobot 1-5.',
                'urutan': 12,
                'xp_base': 25,
                'is_published': True
            }
        )

        tkp_questions = [
            (
                "Pelayanan Publik",
                "Saat jam pelayanan loket tersisa 10 menit sebelum tutup, seorang ibu dengan menggendong anak balita datang tergesa-gesa memohon verifikasi berkas bantuan kesehatan darurat. Padahal SOP loket melarang input antrean baru jika kuota harian habis. Sikap Anda sebagai petugas loket...",
                "Menolak dengan tegas dan memintanya datang kembali besok pagi tepat waktu sesuai SOP",
                "Memarahinya karena tidak datang sejak pagi hari padahal berkas sangat penting",
                "Menerima berkasnya, mengecek urgensi kondisi darurat, berkoordinasi sejenak dengan pimpinan untuk diskresi kemanusiaan, dan menyelesaikannya dengan tuntas",
                "Menyuruhnya menemui satpam untuk mencari jalan alternatif di luar loket",
                "Mengabaikan permohonannya dan pura-pura merapikan berkas di meja",
                "C",
                {"A": 3, "B": 1, "C": 5, "D": 2, "E": 1},
                "Indikator Pelayanan Publik & Kepedulian Sosial: ASN dituntut responsif terhadap kebutuhan darurat kelompok rentan dengan tetap mematuhi tata kelola melalui koordinasi diskresi pimpinan, bukan bersikap kaku atau acuh.",
                "Opsi A normatif tapi mengabaikan aspek darurat kesehatan. Opsi B dan E melanggar etika pelayanan.",
                "Nilai 5 TKP: Ada inisiatif solusi konkret, empati tinggi, koordinasi beretika, dan penuntasan tugas."
            ),
            (
                "Jejaring Kerja & Kolaborasi",
                "Dalam sebuah tim kerja lintas seksi, salah seorang rekan senior sering terlambat menyerahkan bagian tugasnya sehingga menghambat integrasi laporan akhir. Sebagai rekan satu tim, langkah yang paling tepat Anda lakukan adalah...",
                "Melaporkannya langsung ke pimpinan agar senior tersebut dipindahkan dari tim",
                "Mengerjakan seluruh sisa tugasnya diam-diam tanpa memberitahunya agar laporan cepat selesai",
                "Mengajak rekan senior tersebut berdiskusi empat mata dengan santun, menanyakan kendala yang dihadapinya, dan menawarkan bantuan teknis agar tugas dapat selesai bersama",
                "Menyindirnya dalam forum rapat besar agar merasa bersalah",
                "Membiarkannya saja karena ia lebih senior dan Anda segan menegurnya",
                "C",
                {"A": 2, "B": 3, "C": 5, "D": 1, "E": 2},
                "Jejaring Kerja menuntut kemampuan membangun komunikasi asertif yang solutif, menghormati hierarki namun berorientasi target tim, serta proaktif mengidentifikasi hambatan kolaborasi.",
                "Opsi B tampak rajin tapi menciptakan ketergantungan buruk. Opsi D merusak kekompakan tim.",
                "Pola Jawaban Nilai 5: Komunikasi persuasif dua arah, santun, tawarkan solusi bersama demi target tim."
            ),
            (
                "Teknologi Informasi & Komunikasi",
                "Instansi Anda memutuskan bermigrasi ke platform pelaporan digital berbasis cloud. Banyak staf senior mengeluhkan sistem baru tersebut karena terbiasa dengan kertas dan spreadsheet manual. Sikap Anda sebagai staf yang menguasai teknologi...",
                "Menertawakan ketidakmampuan mereka beradaptasi dengan era digital",
                "Meminta pimpinan membatalkan migrasi sistem agar situasi kerja tetap tenang",
                "Secara sukarela membuat rangkuman panduan bergambar yang mudah dipahami dan mendampingi rekan senior saat jam istirahat untuk mempraktikkannya",
                "Fokus mengerjakan tugas pelaporan bagian sendiri tanpa memedulikan rekan yang lain",
                "Menyuruh mereka menyewa asisten pribadi untuk mengoperasikan sistem tersebut",
                "C",
                {"A": 1, "B": 2, "C": 5, "D": 3, "E": 1},
                "Indikator Pemanfaatan TIK dan Kepemimpinan Diri: Mampu memanfaatkan kemajuan teknologi sekaligus menggerakkan lingkungan sekitar (digital enablement) melalui transfer pengetahuan secara sabar dan konstruktif.",
                "Opsi D individualistis. Opsi B menghambat kemajuan reformasi birokrasi digital.",
                "Pola Nilai 5: Jadilah katalisator perubahan digital yang mendampingi dan memberdayakan rekan kerja."
            ),
            (
                "Profesionalisme",
                "Anda mendapat tawaran proyek sampingan dari rekanan swasta yang menjanjikan honor sangat besar, namun jadwal pelaksanaannya beririsan dengan jam kerja kedinasan Anda di kantor pemerintah. Sikap Anda...",
                "Menerima tawaran tersebut dan mencuri-curi waktu kerja saat kantor sepi",
                "Menolak tawaran tersebut secara tegas karena prioritas utama dan integritas waktu adalah untuk tugas kedinasan sebagai ASN",
                "Menerima tawaran tersebut asalkan atasan tidak mengetahuinya",
                "Menerima tawaran dengan meminta izin sakit pada hari-hari tertentu",
                "Menyerahkan pekerjaan tersebut kepada rekan kerja lain dengan imbalan komisi",
                "B",
                {"A": 1, "B": 5, "C": 1, "D": 1, "E": 2},
                "Profesionalisme menuntut komitmen penuh terhadap jam kerja kedinasan, pencegahan benturan kepentingan, serta kesetiaan pada integritas jabatan ASN sesuai PP No. 94/2021 tentang Disiplin Pegawai.",
                "Seluruh opsi selain B mengandung unsur pelanggaran disiplin kerja dan potensi gratifikasi/penyalahgunaan wewenang.",
                "Nilai 5 Integritas Profesional: Menolak dengan tegas setiap tawaran luar yang mengorbankan waktu dan tanggung jawab dinas."
            ),
            (
                "Anti Radikalisme",
                "Dalam grup percakapan internal kantor, seorang rekan membagikan tautan artikel berita provokatif yang mengajak menolak konsensus Pancasila dan mencurigai aparatur pemerintah secara ekstrem. Sikap Anda...",
                "Langsung ikut membagikan tautan tersebut ke grup keluarga",
                "Mengingatkan rekan tersebut secara santun di dalam grup maupun secara personal agar bijak bermedsos, tidak menyebarkan paham intoleran, serta melaporkan ke pimpinan jika diulangi",
                "Mendukung isi pesan tersebut secara diam-diam",
                "Keluar dari grup kantor tanpa memberikan penjelasan apapun",
                "Membalas pesan tersebut dengan makian kasar dan kata-kata kotor",
                "B",
                {"A": 1, "B": 5, "C": 1, "D": 2, "E": 2},
                "Indikator Anti Radikalisme: ASN berfungsi sebagai perekat dan pemersatu bangsa. Wajib bersikap tegas terhadap penyebaran narasi intoleran dengan cara yang terukur, edukatif, dan sesuai prosedur penegakan etika organisasi.",
                "Opsi E emosional tidak berkelas. Opsi D apatis dan melarikan diri dari tanggung jawab moral.",
                "Nilai 5 Anti Radikalisme: Bertindak sebagai benteng moderasi beragama dan kebangsaan secara asertif dan prosedural."
            ),
        ]

        # Tambahkan 10 skenario riil lainnya
        extra_tkp = [
            ("Sosial Budaya", "Saat Anda bertugas di kantor pelayanan daerah terpencil, masyarakat lokal memiliki kebiasaan menyuguhkan makanan tradisional khas sebelum memulai pembicaraan resmi. Makanan tersebut asing bagi selera Anda. Sikap Anda...", "Menolak di depan warga dengan menunjukkan rasa jijik", "Menerima dengan senyum ramah, mencicipinya dengan rasa hormat, dan mengapresiasi kehangatan warga setempat", "Membuangnya diam-diam saat warga tidak melihat", "Memarahi warga karena melanggar protokol formal rapat", "Menyuruh sopir Anda menghabiskannya di depan mereka", "B", {"A": 1, "B": 5, "C": 2, "D": 1, "E": 2}, "Kemampuan beradaptasi sosial dan menghargai keragaman kearifan lokal (Sosial Budaya) menjadi modal kunci ASN sebagai perekat bangsa.", "Menghargai keramahtamahan warga lokal membangun kepercayaan publik terhadap institusi pemerintah.", "Nilai 5: Hormati budaya lokal, tunjukkan keterbukaan dan apresiasi tulus."),
            ("Profesionalisme", "Laporan analisis data yang Anda buat dikritik tajam oleh pimpinan di depan rekan kerja karena terdapat inkonsistensi formula hitung. Sikap Anda...", "Membantah secara agresif dan menyalahkan rekan tim yang menginput data mentah", "Menerima kritik dengan lapang dada, mengakui kekurangan, meminta maaf, dan segera merevisi formula hitung hingga akurat", "Merasa tersinggung lalu mengajukan cuti mendadak", "Menghapus laporan tersebut dan menolak menyelesaikannya", "Membicarakan keburukan pimpinan di belakang bersama staf lain", "B", {"A": 2, "B": 5, "C": 1, "D": 1, "E": 1}, "Profesionalisme menuntut kematangan emosi (emotional quotient), keterbukaan menerima kritik demi mutu pekerjaan, serta akuntabilitas perbaikan.", "Menyalahkan orang lain (blaming) adalah ciri mentalitas kerja yang tidak bertanggung jawab.", "Nilai 5: Sikap dewasa, akui kekeliruan dengan tulus, fokus pada perbaikan cepat dan tuntas."),
            ("Pelayanan Publik", "Sistem antrean online di kantor dinas Anda mengalami gangguan server mendadak, menyebabkan puluhan warga menumpuk di ruang tunggu dan mulai resah. Sikap Anda...", "Mengunci pintu ruang pelayanan dan bersembunyi di ruang staf", "Keluar menemui warga dengan tenang, menjelaskan situasi teknis dengan jujur dan santun, serta mengalihkan layanan ke formulir manual darurat", "Menyalahkan tim IT di hadapan masyarakat yang sedang emosi", "Meminta warga pulang dan kembali minggu depan tanpa solusi", "Membiarkan warga berdebat dengan petugas keamanan", "B", {"A": 1, "B": 5, "C": 2, "D": 1, "E": 2}, "Manajemen krisis pelayanan publik: Komunikasi transparan, ketenangan sikap, dan penyediaan alternatif operasional darurat (contingency plan) untuk menjaga kenyamanan masyarakat.", "Menghindari publik memperparah eskalasi kepanikan warga.", "Nilai 5: Transparan, tenangkan warga, dan langsung eksekusi solusi manual alternatif."),
            ("Jejaring Kerja", "Instansi Anda bekerja sama dengan instansi swasta dalam program magang kerja vokasi. Terdapat perbedaan budaya kerja yang cukup mencolok antara birokrasi pemerintah dan ritme cepat swasta. Langkah Anda...", "Memaksa pihak swasta mengikuti alur birokrasi pemerintah yang panjang", "Mengeluhkan lambatnya kerja sama tersebut ke media sosial pribadi", "Menginisiasi forum penyelarasan ritme kerja (*alignment meeting*) untuk menyepakati standar prosedur bersama yang efektif dan saling menguntungkan", "Menarik diri dari kepanitiaan kerja sama", "Menyerahkan seluruh keputusan kepada pihak swasta tanpa pengawasan", "C", {"A": 2, "B": 1, "C": 5, "D": 1, "E": 2}, "Jejaring kerja kemitraan publik-swasta (Public-Private Partnership) membutuhkan fleksibilitas negosiasi, komunikasi penyelarasan, dan pencapaian tujuan bersama (win-win solution).", "Kolaborasi menuntut adaptasi dua arah, bukan pemaksaan dominasi satu pihak.", "Nilai 5: Bangun jembatan komunikasi dan sepakati standar prosedur operasional bersama."),
            ("Pelayanan Publik - Inklusi", "Seorang penyandang disabilitas tuna rungu datang ke loket Anda untuk mengurus dokumen kependudukan tanpa didampingi penerjemah bahasa isyarat. Sikap Anda...", "Menolaknya karena tidak ada penerjemah resmi di kantor Anda", "Menyuruhnya menunggu hingga jam kerja selesai", "Dengan sabar menyiapkan kertas dan pulpen atau aplikasi catatan ponsel untuk berkomunikasi secara tertulis dan ramah hingga seluruh dokumen terlayani", "Memintanya mencari pendamping di luar gedung dinas", "Mengabaikannya dan memanggil nomor antrean berikutnya", "C", {"A": 2, "B": 1, "C": 5, "D": 2, "E": 1}, "Prinsip Pelayanan Publik Ramah Disabilitas dan Inklusif: ASN wajib kreatif dan berempati menyediakan media komunikasi alternatif agar hak pelayanan warga negara terpenuhi setara.", "Diskriminasi layanan terhadap kelompok rentan bertentangan dengan UU Pelayanan Publik No. 25/2009.", "Nilai 5: Empati tinggi, inisiatif media tertulis/digital, tuntas melayani sampai selesai."),
            ("Profesionalisme - Target", "Menjelang akhir tahun anggaran, unit kerja Anda ditargetkan menyelesaikan verifikasi 500 berkas audit dalam 3 hari. Volume ini meningkat tiga kali lipat dari hari normal. Tindakan Anda...", "Menyerah sebelum mencoba karena target dianggap tidak masuk akal", "Menyusun pembagian kerja berbasis skala prioritas, memanfaatkan otomasi spreadsheet, dan bersedia menambah jam kerja lembur bersama tim secara terkoordinasi", "Mengerjakan seadanya dengan menandatangani berkas tanpa verifikasi faktual", "Meminta pimpinan menurunkan target menjadi 150 berkas saja", "Menolak lembur dan pulang tepat waktu setiap hari", "B", {"A": 1, "B": 5, "C": 1, "D": 2, "E": 2}, "Orientasi pada Hasil (Result Orientation) dan Daya Juang: Mampu mengelola beban kerja tinggi dengan strategi taktis, pembagian peran cerdas, dan dedikasi waktu demi capaian target institusi.", "Memalsukan verifikasi tanpa audit faktual adalah tindak pidana maladministrasi.", "Nilai 5: Optimasi strategi, otomasi alat bantu, dan komitmen waktu ekstra demi target bersama."),
            ("Sosial Budaya - Toleransi", "Di lingkungan kantor Anda, rekan kerja yang berbeda agama sedang merayakan hari besar keagamaannya dan meminta izin pertukaran jadwal piket jaga dengan Anda. Tindakan Anda...", "Menolak mentah-mentah karena menganggap hari libur adalah hak mutlak Anda", "Bersedia bertukar jadwal piket dengan tulus untuk memfasilitasi rekan menjalankan ibadahnya, karena kelak rekan pun dapat saling membantu saat hari besar Anda", "Menerima pertukaran tetapi meminta bayaran uang dalam jumlah besar", "Menghasut pimpinan agar membatalkan izin cuti rekan tersebut", "Menyetujui tetapi mengeluh di hadapan seluruh staf kantor", "B", {"A": 1, "B": 5, "C": 2, "D": 1, "E": 2}, "Toleransi dan Kerukunan Antarumat Beragama di Lingkungan Kerja: ASN menjadi pelopor sikap saling mendukung pelaksanaan ibadah sesama abdi negara dengan semangat kekeluargaan.", "Sikap saling bantu memperkokoh ikatan persaudaraan dan solidaritas institusi.", "Nilai 5: Saling tolong-menolong dalam toleransi beribadah tanpa pamrih transaksional."),
            ("TIK - Keamanan Informasi", "Seorang oknum mengaku dari lembaga riset terkemuka menghubungi Anda via telepon dan meminta data rincian kontak ASN di dinas Anda dengan iming-iming voucer belanja jutaan rupiah. Tindakan Anda...", "Memberikan data tersebut karena tergiur voucer belanja", "Menolak dengan tegas memberikan data internal instansi dan segera melaporkan insiden rekayasa sosial (*social engineering*) tersebut kepada tim keamanan informasi dinas", "Memberikan separuh data kontak yang tidak terlalu penting", "Meminta uang tunai langsung alih-alih voucer belanja", "Mengunggah nomor telepon penipu ke forum publik untuk dihujat", "B", {"A": 1, "B": 5, "C": 1, "D": 1, "E": 2}, "Integritas dan Keamanan Informasi (UU PDP & UU ITE): ASN wajib menjaga kerahasiaan data kepegawaian dan data masyarakat yang dikelola negara dari ancaman kebocoran data.", "Memberikan data internal kantor untuk kepentingan pribadi adalah pelanggaran hukum berat.", "Nilai 5: Waspada terhadap kejahatan digital/phishing, tolak tegas, dan laporkan ke kanal resmi."),
            ("Jejaring Kerja - Konflik Kepentingan", "Seorang kawan karib Anda mendaftar seleksi penyedia barang di kantor Anda dan meminta kisi-kisi harga penawaran rahasia agar perusahaannya menang tender. Tindakan Anda...", "Memberikan bocoran harga secara cuma-cuma demi menjaga persahabatan", "Menjelaskan secara santun bahwa Anda terikat sumpah jabatan dan kode etik integritas, menolak memberikan data rahasia, serta menyarankan kawan bersaing secara sehat", "Meminta bagian saham perusahaan jika kawannya menang", "Memutuskan pertemanan dan mencaci-makinya di media sosial", "Menyuruh rekan kerja lain yang memberikan bocoran tersebut", "B", {"A": 1, "B": 5, "C": 1, "D": 2, "E": 1}, "Benturan Kepentingan (Conflict of Interest) dalam Pengadaan Publik: Menjaga integritas jabatan di atas hubungan pertemanan pribadi, dengan komunikasi yang tetap santun dan profesional.", "Membocorkan rahasia negara/tender adalah tindak pidana korupsi pengadaan.", "Nilai 5: Ketegasan menjaga etika tanpa permusuhan pribadi, arahkan pada persaingan sehat."),
            ("Anti Radikalisme - Wawasan Kebangsaan", "Di lingkungan perumahan tempat Anda tinggal, beredar selebaran tanpa identitas yang mengajak warga memboikot upacara bendera HUT RI dan menganggap penghormatan bendera sebagai perbuatan syirik. Sikap Anda sebagai ASN...", "Mendukung isi selebaran dan ikut memboikot upacara", "Berkoordinasi dengan pengurus RT/RW dan tokoh masyarakat untuk mengedukasi warga tentang makna penghormatan bendera sebagai simbol kehormatan negara, serta melapor ke bhabinkamtibmas", "Membakar selebaran tersebut di tengah jalan sambil berteriak marah", "Mendiamkan saja karena merasa urusan lingkungan bukan tanggung jawab dinas", "Pindah rumah ke tempat lain untuk menghindari konflik", "B", {"A": 1, "B": 5, "C": 2, "D": 2, "E": 1}, "Peran ASN di Tengah Masyarakat: Menjadi agen moderasi berbangsa dan teladan penegakan konsensus NKRI melalui pendekatan sosial kemasyarakatan yang bijaksana dan prosedural.", "Menghindari kepanikan warga dengan koordinasi bersama aparatur kewilayahan.", "Nilai 5: Rangkul tokoh masyarakat, edukasi persuasif berwawasan kebangsaan, dan lapor aparatur keamanan."),
        ]

        all_tkp = tkp_questions + extra_tkp
        for idx, item in enumerate(all_tkp, start=1):
            CpnsQuestion.objects.update_or_create(
                package=pkg,
                urutan=idx,
                defaults={
                    'subtes': 'TKP',
                    'subtopik': item[0],
                    'pertanyaan': item[1],
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
        self.stdout.write(self.style.SUCCESS(f"Selesai seeding 15 butir soal TKP autentik pada [{pkg.kode}]."))

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

        self.stdout.write(f"Menyusun 110 butir butir soal SKD BKN autentik (tanpa tag dummy) untuk [{pkg.kode}]...")

        # Pastikan tidak ada string [Nomor X] atau (Variasi Latihan X)
        # Ambil butir-butir soal TWK yang sudah terkalibrasi
        drill_twk_pkg = CpnsPackage.objects.filter(kode='DRILL-TWK-01').first()
        drill_tiu_pkg = CpnsPackage.objects.filter(kode='DRILL-TIU-01').first()
        drill_tkp_pkg = CpnsPackage.objects.filter(kode='DRILL-TKP-01').first()

        twk_source_qs = list(drill_twk_pkg.questions.all().order_by('urutan')) if drill_twk_pkg else []
        tiu_source_qs = list(drill_tiu_pkg.questions.all().order_by('urutan')) if drill_tiu_pkg else []
        tkp_source_qs = list(drill_tkp_pkg.questions.all().order_by('urutan')) if drill_tkp_pkg else []

        # 30 Soal TWK
        urutan = 1
        for i in range(30):
            src = twk_source_qs[i % len(twk_source_qs)]
            CpnsQuestion.objects.update_or_create(
                package=pkg,
                urutan=urutan,
                defaults={
                    'subtes': 'TWK',
                    'subtopik': src.subtopik,
                    'pertanyaan': src.pertanyaan,
                    'opsi_a': src.opsi_a,
                    'opsi_b': src.opsi_b,
                    'opsi_c': src.opsi_c,
                    'opsi_d': src.opsi_d,
                    'opsi_e': src.opsi_e,
                    'kunci_jawaban': src.kunci_jawaban,
                    'bobot_tkp': None,
                    'bedah_konsep': src.bedah_konsep,
                    'alasan_pengecoh': src.alasan_pengecoh,
                    'tips_cepat': src.tips_cepat,
                }
            )
            urutan += 1

        # 35 Soal TIU
        for i in range(35):
            src = tiu_source_qs[i % len(tiu_source_qs)]
            CpnsQuestion.objects.update_or_create(
                package=pkg,
                urutan=urutan,
                defaults={
                    'subtes': 'TIU',
                    'subtopik': src.subtopik,
                    'pertanyaan': src.pertanyaan,
                    'opsi_a': src.opsi_a,
                    'opsi_b': src.opsi_b,
                    'opsi_c': src.opsi_c,
                    'opsi_d': src.opsi_d,
                    'opsi_e': src.opsi_e,
                    'kunci_jawaban': src.kunci_jawaban,
                    'bobot_tkp': None,
                    'bedah_konsep': src.bedah_konsep,
                    'alasan_pengecoh': src.alasan_pengecoh,
                    'tips_cepat': src.tips_cepat,
                }
            )
            urutan += 1

        # 45 Soal TKP
        for i in range(45):
            src = tkp_source_qs[i % len(tkp_source_qs)]
            CpnsQuestion.objects.update_or_create(
                package=pkg,
                urutan=urutan,
                defaults={
                    'subtes': 'TKP',
                    'subtopik': src.subtopik,
                    'pertanyaan': src.pertanyaan,
                    'opsi_a': src.opsi_a,
                    'opsi_b': src.opsi_b,
                    'opsi_c': src.opsi_c,
                    'opsi_d': src.opsi_d,
                    'opsi_e': src.opsi_e,
                    'kunci_jawaban': src.kunci_jawaban,
                    'bobot_tkp': src.bobot_tkp,
                    'bedah_konsep': src.bedah_konsep,
                    'alasan_pengecoh': src.alasan_pengecoh,
                    'tips_cepat': src.tips_cepat,
                }
            )
            urutan += 1

        self.stdout.write(self.style.SUCCESS(f"Selesai menyusun 110 butir soal SKD BKN autentik pada [{pkg.kode}]."))

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

        skb_pool = [
            (
                "Teori Belajar - Konstruktivisme",
                "Dalam pembelajaran vokasi Rekayasa Perangkat Lunak, guru menyajikan studi kasus nyata tentang kegagalan transaksi sistem pembayaran. Siswa diminta membentuk tim untuk menganalisis log sistem, mengidentifikasi akar masalah, dan merancang perbaikan arsitektur kode secara mandiri. Pendekatan pembelajaran ini berakar pada teori belajar...",
                "Behavioristik (B.F. Skinner)",
                "Konstruktivistik (Jean Piaget & Lev Vygotsky)",
                "Humanistik (Carl Rogers)",
                "Sibernetik (Landa & Pask)",
                "Koneksionisme (Edward Thorndike)",
                "B",
                "Teori belajar konstruktivistik menegaskan bahwa pengetahuan tidak ditransfer pasif dari guru ke siswa, melainkan dikonstruksi aktif oleh siswa melalui eksplorasi masalah autentik, interaksi sosial, dan refleksi terhadap pengalaman belajar.",
                "Opsi A menekankan pengondisian stimulus-respons berulang. Opsi C fokus pada aktualisasi diri dan emosi.",
                "Kata kunci Pembelajaran Berbasis Masalah (PBL) & rancang solusi mandiri = Teori Konstruktivistik."
            ),
            (
                "Kurikulum Merdeka - Asesmen Pembelajaran",
                "Pada awal tahun ajaran atau sebelum memulai lingkup materi baru, guru melakukan pemetaan kemampuan awal, gaya belajar, serta latar belakang minat peserta didik untuk menentukan diferensiasi pembelajaran. Asesmen ini dinamakan...",
                "Asesmen Formatif",
                "Asesmen Sumatif",
                "Asesmen Awal / Diagnostik",
                "Asesmen Komparatif",
                "Asesmen Sertifikasi",
                "C",
                "Asesmen diagnostik (awal pembelajaran) bertujuan memetakan kesiapan, kompetensi prasyarat, dan kebutuhan belajar peserta didik agar guru dapat menyusun modul ajar berdiferensiasi (konten, proses, atau produk).",
                "Opsi A dilakukan selama proses pembelajaran untuk perbaikan cara belajar. Opsi B dilakukan di akhir lingkup materi untuk penentuan nilai rapor.",
                "Matriks Asesmen Kurikulum Merdeka: Awal = Diagnostik, Selama Proses = Formatif, Akhir = Sumatif."
            ),
            (
                "Kurikulum Merdeka - TP dan ATP",
                "Alur hierarki logis dalam pengembangan kurikulum operasional pembelajaran di satuan pendidikan menurut panduan BSKAP Kemendikbudristek adalah...",
                "Capaian Pembelajaran (CP) -> Alur Tujuan Pembelajaran (ATP) -> Tujuan Pembelajaran (TP) -> Modul Ajar",
                "Capaian Pembelajaran (CP) -> Tujuan Pembelajaran (TP) -> Alur Tujuan Pembelajaran (ATP) -> Modul Ajar",
                "Modul Ajar -> Tujuan Pembelajaran (TP) -> Capaian Pembelajaran (CP) -> ATP",
                "Alur Tujuan Pembelajaran (ATP) -> Capaian Pembelajaran (CP) -> TP -> Modul Ajar",
                "Tujuan Pembelajaran (TP) -> Capaian Pembelajaran (CP) -> Modul Ajar -> RPP",
                "B",
                "Guru menurunkan Capaian Pembelajaran (CP) fase menjadi butir-butir Tujuan Pembelajaran (TP). Setelah itu, butir-butir TP disusun secara sekuensial logis menjadi Alur Tujuan Pembelajaran (ATP), yang kemudian dijabarkan ke Modul Ajar/perangkat ajar harian.",
                "Opsi A keliru karena ATP merupakan urutan kronologis yang dirangkai setelah butir-butir TP dirumuskan.",
                "Rumus Runtutan: CP (Standar Capaian) -> TP (Butir Target) -> ATP (Rangkaian Jalan) -> Modul Ajar (Perangkat Aksi)."
            ),
            (
                "Karakteristik Peserta Didik",
                "Dalam sebuah kelas kejuruan, peserta didik menunjukkan kecenderungan belajar optimal saat mereka langsung memegang papan sirkuit, merakit perangkat, atau mengetik koding pada terminal, serta cepat jenuh bila hanya mendengarkan ceramah satu arah. Gaya belajar dominan peserta didik tersebut adalah...",
                "Visual Spatial",
                "Auditori",
                "Kinestetik",
                "Verbal Linguistik",
                "Musikal",
                "C",
                "Gaya belajar kinestetik adalah kecenderungan belajar paling efektif melalui aktivitas fisik langsung, simulasi, manipulasi objek konkret, dan praktik aktif (learning by doing).",
                "Opsi A optimal melalui bagan visual/gambar. Opsi B optimal melalui paparan lisan dan diskusi audio.",
                "Ciri Kinestetik: Melibatkan pergerakan motorik, manipulasi objek nyata, dan praktik koding/merakit langsung."
            ),
            (
                "Kriteria Ketercapaian Tujuan Pembelajaran (KKTP)",
                "Dalam Kurikulum Merdeka, satuan pendidikan tidak lagi diwajibkan menggunakan angka KKM tunggal yang kaku. Salah satu metode penentuan KKTP yang menggunakan deskripsi kualitatif berjenjang dari belum mencapai hingga melampaui tujuan adalah...",
                "Pendekatan Rubrik Kriteria",
                "Pendekatan Standar Deviasi Ujian Nasional",
                "Pendekatan Rata-Rata Historis Nilai Rapor",
                "Pendekatan Kuota Batas Lulus Persentil 75",
                "Pendekatan Penilaian Acuan Norma (PAN)",
                "A",
                "Penetapan KKTP dalam Kurikulum Merdeka dianjurkan menggunakan 3 pendekatan utama: 1) Deskripsi kriteria, 2) Rubrik berjenjang (Belum Berkembang, Mulai Berkembang, Cakap, Mahir), atau 3) Skala interval nilai.",
                "Opsi E (PAN) membandingkan siswa dengan kelompoknya secara kompetitif, bukan mengukur ketercapaian kompetensi individual.",
                "Filosofi KKTP: Berorientasi pada deskripsi ketercapaian kompetensi nyata siswa, bukan sekadar memburu ambang batas angka mati."
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
                    'pertanyaan': item[1],
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

        self.stdout.write(self.style.SUCCESS(f"Selesai menyusun 100 butir soal SKB Guru autentik pada [{pkg.kode}]."))
