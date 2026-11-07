# Spesifikasi Desain: CPNS Hub (cpns.agunggumelarsaputra.com)

- **Tanggal:** 2026-11-07
- **Status:** menunggu tinjauan pemilik
- **Pemilik:** Agung Gumelar Saputra, S.Tr.T.
- **Mockup:** `design/cpns-hub-mockup.figcraft` (gambar di `design/png/`)
- **Latar belakang:** `docs/audit-cpns-2026-11-07.md` dan `anti-slop/audit-002-2026-11-07.md`

## 1. Tujuan

CPNS Hub adalah tempat latihan mandiri untuk seleksi CPNS. Penggunanya pemilik sendiri dan masyarakat umum. Ada dua jenis ujian: **SKD** dan **SKB Guru RPL/PPLG**. Setiap jenis ujian bisa dikerjakan dalam dua mode:

- **Mode Belajar:** satu soal per layar, dan pembahasan langsung muncul setelah menjawab.
- **Mode Ujian CAT:** kondisinya seperti ujian sungguhan, dan penilaiannya mengikuti aturan BKN.

Bank soal dibangun bertahap supaya simulasi bisa diulang tanpa banyak soal berulang. Akses dibagi menjadi **trial** dan **premium**. Premium dibuka dengan kode voucher yang dibeli lewat WhatsApp.

**Kriteria berhasil:**
1. Peserta bisa mengikuti simulasi SKD 110 soal dalam 100 menit. Skornya sama dengan hitungan manual aturan BKN, dan jawaban tidak hilang walaupun halaman di-refresh.
2. Setiap percobaan CAT mendapat soal dan urutan opsi yang berbeda, dirakit dari bank soal.
3. Kunci dan pembahasan tidak bisa diintip dari browser sebelum waktunya.
4. Pemilik bisa meninjau draf soal dengan cepat (satu soal per layar, pakai pintasan keyboard) dan membuat kode voucher sendiri.
5. Peserta umum tidak pernah muncul di halaman sekolah: daftar siswa, leaderboard, maupun XP.

## 2. Keputusan yang sudah disepakati

| Topik | Keputusan |
|---|---|
| Pengguna | Pemilik dan masyarakat umum |
| SKB Guru | Format latihan materi bidang (Pedagogik + Materi RPL/PPLG). Penilaian sementara benar 5 / salah 0. Skema diganti setelah ada kisi-kisi resmi |
| Sumber soal | Draf dibuat AI di sesi Claude Code, lalu **setiap soal ditinjau dan disetujui pemilik** sebelum tayang |
| Trial | 1 paket belajar (30 soal) + 1 simulasi CAT SKD. Skor tampil, pembahasan hasil simulasi dikunci |
| Premium | Akses penuh selama masa aktif. Durasi dipilih saat membuat kode (contoh 30 / 90 hari). Kode baru menambah masa aktif yang sedang berjalan |
| Pembayaran | Manual lewat WhatsApp. Pemilik mengirim kode voucher |
| Login | Google + email/kata sandi. Simulasi CAT trial hanya untuk akun Google sampai server bisa mengirim email |
| Arsitektur | Dikembangkan di dalam projek Django yang sama, dengan peran baru `peserta` |
| XP sekolah | CPNS tidak memberi XP gamifikasi |
| Admin | Tinjau Soal, Cakupan, dan Laporan dibuat khusus. Voucher, Pengaturan, Skema, dan Paket Belajar lewat Django Admin |
| Tampilan | Mengikuti `DESIGN.md`: aksen sky `#38BDF8`, latar `#090D16`, font Outfit / Inter / JetBrains Mono. Dial ENERGY 1 / RHYTHM 1 / MOTION 1 |

## 3. Model data (app `apps/cpns`, dibangun ulang)

Tabel lama (`CpnsPackage`, `CpnsQuestion`, `CpnsAttempt`) dibiarkan apa adanya di rilis pertama dan tidak dipakai lagi (lihat bagian 10).

### 3.1 `Soal`
- `jenis_ujian`: `SKD` | `SKB_GURU`
- `subtes`: `TWK` | `TIU` | `TKP` | `PEDAGOGIK` | `MATERI_RPL`
- `subtopik` (teks, sesuai kisi-kisi) dan `tingkat`: `mudah` | `sedang` | `sulit`
- `teks`, `opsi_a` sampai `opsi_e`
- `kunci` (`A`–`E`, untuk soal benar/salah) **atau** `bobot` (JSON `{"A":1..5}`, untuk TKP)
- `pembahasan_konsep`, `pembahasan_pengecoh`, `pembahasan_cepat`
- `rujukan` (teks, boleh kosong) dan `perlu_cek` (bool)
- `status`: `draf` | `tayang` | `ditolak`; `catatan_tinjau`, `ditinjau_oleh`, `ditinjau_pada`
- `sumber`: `draf_ai` | `tulisan_sendiri` | `lama`; `batch` (teks)
- `sidik_teks`: teks soal yang sudah dinormalisasi, untuk mendeteksi duplikat
- `dibuat_pada`, `diubah_pada`

**Validasi** (dipakai di model, form admin, dan impor):
- kelima opsi terisi dan tidak ada yang sama persis
- soal benar/salah wajib punya `kunci` yang valid
- soal TKP wajib punya `bobot` berisi nilai 1, 2, 3, 4, 5 yang semuanya berbeda
- ketiga bagian pembahasan tidak boleh kosong
- `status=tayang` hanya boleh kalau semua syarat di atas terpenuhi dan `ditinjau_oleh` terisi

### 3.2 `SkemaUjian` dan `SkemaBagian`
- **`SkemaUjian`:** `kode`, `nama`, `jenis_ujian`, `durasi_menit`, `aktif`, `keterangan`.
- **`SkemaBagian`:** `skema`, `urutan`, `subtes`, `jumlah_soal`, `cara_nilai` (`benar_salah` | `bobot_opsi`), `poin_benar`, `poin_salah`, `ambang_batas`.
- **Aturan lulus:** setiap bagian harus mencapai `ambang_batas`. Total adalah jumlah semua bagian.

Data awal:
- **SKD-CAT:** 100 menit. TWK 30 (5/0, ambang 65), TIU 35 (5/0, ambang 80), TKP 45 (bobot, ambang 166).
- **SKB-GURU-LATIHAN:** dibuat dalam keadaan `aktif=False` dengan nilai awal: 90 menit, Pedagogik 50 soal (5/0), Materi RPL/PPLG 50 soal (5/0), ambang 0 (0 berarti tanpa ambang). Pemilik mengubah komposisi dan ambangnya di admin, lalu mengaktifkannya. Selama belum aktif, kartu SKB di dasbor bertuliskan "Segera tersedia".

### 3.3 `PaketBelajar`
- `nama`, `jenis_ujian`, `untuk_trial` (bool), `aktif`.
- Daftar soal berurutan lewat tabel `PaketSoal` (`paket`, `soal`, `urutan`).
- Hanya boleh ada satu paket `untuk_trial` yang aktif per jenis ujian.

### 3.4 `Sesi` dan `SesiSoal`
- **`Sesi`:**
  - `user`, `mode` (`cat` | `belajar`), `skema` (CAT), `paket` (belajar dari paket), `filter_subtopik` (belajar per subtopik, JSON)
  - `status` (`berjalan` | `selesai`), `dimulai_pada`, `batas_waktu` (CAT), `selesai_pada`
  - `skor_bagian` (JSON per bagian: skor, ambang, lulus), `total`, `lulus`
- **`SesiSoal`:**
  - `sesi`, `soal`, `nomor`, `urutan_opsi` (string seperti `"CAEBD"`, artinya posisi tampil ke-1 adalah opsi asli C, dan seterusnya)
  - `jawaban` (kunci opsi **asli**, boleh kosong), `ragu`, `dijawab_pada`, `poin`
- **Batasan:** satu `Sesi` CAT berstatus `berjalan` per user (dicek di view dan dengan constraint parsial).

### 3.5 Akses, voucher, laporan, pengaturan
- **`AksesPeserta`** (satu per user): `premium_sampai` (datetime, boleh kosong) dan `via_google` (bool, diisi saat login atau daftar lewat Google).
- **`Voucher`:** `kode` (unik), `durasi_hari`, `catatan`, `dibuat_oleh`, `dibuat_pada`, `dipakai_oleh`, `dipakai_pada`, `dibatalkan`.
- **`PercobaanVoucher`:** `user`, `waktu`, `berhasil`. Dipakai untuk batas 5 kali gagal per jam.
- **`LaporanSoal`:** `soal`, `user`, `alasan` (`kunci_salah` | `ambigu` | `typo` | `lainnya`), `catatan`, `status` (`baru` | `selesai`), `dibuat_pada`.
- **`PengaturanCPNS`** (satu baris): `nomor_wa`, `teks_harga` (per durasi, JSON), `pesan_wa` (template).

### 3.6 Peran user
- Tambah `User.ROLE_PESERTA = 'peserta'`.
- Pendaftaran dan login Google pertama kali **lewat host cpns** membuat user `peserta`.
- User lama (guru/siswa) tetap bisa memakai CPNS. `AksesPeserta` mereka dibuat otomatis saat pertama kali dipakai.

## 4. Aturan akses

| Fitur | Trial | Premium | Superuser |
|---|---|---|---|
| Paket belajar trial | ya (bisa diulang) | ya | ya |
| Belajar paket lain / per subtopik | tidak | ya | ya |
| Simulasi CAT SKD | 1 kali, hanya kalau `via_google` | tanpa batas | tanpa batas |
| Simulasi CAT SKB Guru | tidak | tanpa batas | tanpa batas |
| Pembahasan hasil simulasi | tidak (skor saja) | ya | ya |

- **Premium aktif** artinya `premium_sampai > sekarang` atau user adalah superuser.
- **Kuota trial CAT dianggap terpakai** kalau user pernah punya `Sesi` CAT dengan status apa pun.
- **Semua pemeriksaan dilakukan di server** pada setiap view dan endpoint. Menyembunyikan tombol saja tidak cukup.

## 5. Alur Mode CAT

1. **Mulai** (`POST /simulasi/<kode-skema>/mulai/`):
   - Server memeriksa akses dan memastikan tidak ada sesi CAT lain yang berjalan.
   - Server merakit soal. Untuk setiap bagian, soal `tayang` sesuai subtes diambil acak, dengan prioritas soal yang belum pernah muncul di `SesiSoal` milik user ini. Kalau soal yang belum pernah muncul tidak cukup, kekurangannya diambil dari soal yang sudah pernah muncul.
   - Kalau total soal tayang lebih sedikit dari `jumlah_soal`, sesi **tidak dibuat** dan muncul pesan "Bank soal untuk bagian X belum cukup".
   - Urutan bagian mengikuti `SkemaBagian.urutan`, dan urutan opsi setiap soal diacak.
   - `batas_waktu = dimulai_pada + durasi`.
2. **Ruang ujian** (`GET /ujian/<id>/`):
   - Server hanya mengirim teks soal, opsi sesuai urutan tampil, jawaban dan tanda ragu yang tersimpan, serta sisa detik yang dihitung server.
   - **Tidak ada kunci, bobot, atau pembahasan di HTML.**
   - Kalau batas waktu sudah lewat, sesi dinilai lalu peserta diarahkan ke halaman hasil.
3. **Simpan otomatis** (`POST /ujian/<id>/simpan/`, JSON `{nomor, jawaban_tampil, ragu}`):
   - Server menerjemahkan jawaban dari posisi tampil ke opsi asli.
   - Penyimpanan bersifat idempoten (dikirim dua kali hasilnya sama).
   - Kiriman setelah `batas_waktu + 30 detik` ditolak dengan status 409.
   - Di browser: indikator "Tersimpan / Menyimpan… / Gagal, mencoba lagi". Jawaban yang gagal terkirim ditahan di `localStorage` dan dikirim ulang begitu tersambung.
4. **Kumpulkan** (`POST /ujian/<id>/kumpulkan/`), atau otomatis saat sesi dibuka setelah waktunya habis:
   - Skor dihitung per bagian sesuai `cara_nilai`, termasuk total dan status lulus.
   - Status sesi menjadi `selesai`. Proses ini idempoten.
5. **Hasil** (`GET /hasil/<id>/`):
   - Skor per bagian ditampilkan sebagai bar dengan garis ambang batas, ditambah total dan waktu pengerjaan dalam menit dan detik.
   - Pembahasan per soal hanya untuk premium. Trial melihat kartu ajakan Premium.

## 6. Alur Mode Belajar

1. Peserta memilih paket (trial) atau subtes/subtopik dan jumlah soal 10, 20, atau 30 (premium). Sistem membuat `Sesi` belajar. Kalau soal tayang di subtopik itu lebih sedikit dari yang diminta, sistem memakai semua yang ada dan memberi tahu jumlahnya.
2. Soal tampil satu per satu tanpa timer.
3. `POST /belajar/<id>/jawab/` menyimpan jawaban, lalu membalas dengan potongan HTML (HTMX): benar/salah, kunci, jawaban peserta, dan pembahasan 3 bagian.
4. Progres tersimpan dan bisa dilanjutkan. Ringkasan akhirnya berupa persentase benar per subtopik.
5. Tombol "Laporkan soal" ada di setiap pembahasan.

## 7. Akun, trial, premium, voucher

**Daftar dan masuk**
- Halaman `/daftar/` dan `/masuk/` khusus cpns (nama, email, kata sandi) ditambah tombol "Masuk dengan Google".
- Tanpa token rombel dan tanpa onboarding foto/kelas siswa.

**Perbaikan wajib di login Google** (`apps/accounts/views.py`):
- Hapus penentuan guru lewat `'agung' in email`. Peran guru hanya diberikan untuk daftar email eksplisit yang disimpan di pengaturan.
- Login Google dari host cpns membuat `peserta` dan mengisi `AksesPeserta.via_google=True`.

**Kode voucher**
- Format `XXXX-XXXX` dari alfabet tanpa huruf atau angka yang mirip (tanpa 0, O, 1, I, L), dibuat dengan `secrets`.

**Memakai kode** (`POST /premium/voucher/`)
- Diproses dalam `transaction.atomic()` dengan `select_for_update` pada baris voucher.
- Kode ditolak kalau dibatalkan atau sudah dipakai.
- Masa aktif baru dihitung dari `max(sekarang, premium_sampai) + durasi_hari`.
- Setiap percobaan dicatat. Setelah 5 kali gagal dalam 1 jam, permintaan ditolak tanpa memeriksa kodenya.

**Django Admin untuk Voucher**
- Aksi "Buat N kode", diisi jumlah, durasi, dan catatan. Hasilnya daftar kode yang tinggal disalin.
- Kode yang belum dipakai bisa dibatalkan.
- Daftar bisa disaring per status.

**Halaman Premium**
- Menampilkan harga dari `PengaturanCPNS` dan tombol WhatsApp ke `https://wa.me/<nomor>?text=<pesan berisi email akun>`.
- Ada kolom kode voucher.

**Halaman Syarat Layanan dan Kebijakan Privasi**
- Isinya draf dari pengembang, dan **wajib ditinjau pemilik sebelum tayang**.

## 8. Konten: kisi-kisi, draf AI, tinjau, laporan

1. **Kisi-kisi:** `docs/cpns/kisi-kisi.md` berisi subtopik per subtes dan target jumlah soal. Disetujui pemilik sebelum draf pertama dibuat.
2. **Draf batch:** file JSON di `data/cpns/batch/<nama-batch>.json` (misalnya 30 soal satu subtopik). Rujukan wajib ada untuk soal TWK yang memuat fakta. Kalau tidak yakin, soal diberi `perlu_cek=true` dan rujukan tidak boleh dikarang.
3. **Impor:** `python manage.py cpns_impor_soal <file>`.
   - Validator di 3.1 dijalankan, ditambah pemeriksaan duplikat berdasarkan `sidik_teks`.
   - Soal yang lolos masuk sebagai `draf`. Soal yang gagal dilaporkan per baris beserta alasannya, dan tidak ada data setengah jadi yang tersimpan.
4. **Tinjau Soal** (`/kelola/tinjau/`, superuser):
   - Satu soal per layar, tampil seperti yang dilihat peserta, ditambah kunci atau bobot, pembahasan, rujukan, dan hasil pemeriksaan otomatis.
   - Aksi Setujui (S), Edit (E), Tolak + alasan (T), dan Lewati (→).
   - Bisa disaring per status, subtes, subtopik, dan batch. Ada penghitung "ditinjau hari ini".
5. **Cakupan** (`/kelola/cakupan/`):
   - Per subtopik ditampilkan target, jumlah tayang, dan jumlah draf.
   - Ada perkiraan "cukup untuk N simulasi tanpa soal berulang", yaitu nilai terkecil dari `tayang // jumlah_soal` di antara semua bagian skema.
6. **Laporan** (`/kelola/laporan/`): antrean laporan soal dengan tautan ke halaman Tinjau untuk soal tersebut.

## 9. Halaman dan tampilan

**Halaman:** sesuai mockup `design/cpns-hub-mockup.figcraft`, yaitu 01 Beranda, 02 Masuk, 03 Dasbor, 04 Mode Belajar, 05 Ruang CAT, 05b Daftar Soal, 06 Hasil, 07 Premium, dan 08 Admin Tinjau Soal. Ditambah halaman Daftar, Riwayat, Syarat Layanan, Kebijakan Privasi, Cakupan, dan Laporan dengan gaya yang sama.

**Tampilan umum:**
- Navigasi peserta: Beranda · Belajar · Simulasi · Riwayat · Premium · Akun. Tombol "Menu" muncul di bawah lebar 1024 px.
- Halaman cpns dibuat full-width, tidak lagi dibungkus `max-w-7xl` milik `base.html`. Judul tab berakhiran "CPNS Hub".
- Tanpa emoji, gradien, titik berkedip, klaim "resmi", atau "soal asli BKN". Di beranda tertulis "Latihan mandiri. Tidak berafiliasi dengan BKN."

**Pola dari perbaikan audit #002 yang dipertahankan:**
- target sentuh minimal 44 px
- opsi berupa `<button aria-pressed>`
- Escape menutup panel dan dialog
- pintasan huruf diabaikan saat Ctrl, Cmd, atau Alt ditekan

**Setiap tampilan data punya keadaan kosong, memuat, dan error**, misalnya: belum ada simulasi, bank soal belum cukup, gagal menyimpan, dan kode voucher salah.

## 10. Data lama dan migrasi

- **Soal lama:** `python manage.py cpns_impor_soal_lama` menyalin soal lama yang teksnya unik ke `Soal` dengan `sumber=lama` dan `status=draf`. Soal yang melanggar validator, misalnya bobot TKP ganda, tetap diimpor sebagai draf, diberi `perlu_cek=true` dan catatannya.
- **Tabel lama** tidak dihapus di rilis ini. Penghapusannya menjadi rilis terpisah setelah pemilik setuju.
- **Alamat lama** dialihkan permanen (301): `/packages/...` ke `/`, `/exam/...` ke `/dasbor/`, dan `/result/...` ke `/riwayat/`.

## 11. Keamanan produksi

- Variabel lingkungan di VPS:
  - `SESSION_COOKIE_SECURE=True`, `CSRF_COOKIE_SECURE=True`
  - `SECURE_HSTS_SECONDS`, dimulai dari 3600 lalu dinaikkan
  - `ALLOWED_HOSTS` berisi daftar domain eksplisit
  - `docker-compose.yml` tidak lagi memaksa `ALLOWED_HOSTS=*`
- Login Google untuk cpns butuh alamat balik `https://cpns.agunggumelarsaputra.com/accounts/google/callback/` terdaftar di Google Cloud Console. **Ini dilakukan pemilik.**
- Data peserta yang disimpan hanya nama dan email. Tidak ada data pembayaran.

## 12. Pengujian

**Tes otomatis** (`apps/cpns/tests/`):
- **Penilaian:** benar/salah, bobot TKP, kosong, ambang per bagian, dan total.
- **Perakitan:** komposisi tepat per bagian, prioritas soal yang belum pernah dikerjakan, bank kurang (sesi tidak dibuat), dan acakan opsi yang dinilai benar setelah diterjemahkan.
- **Timer:** jawaban ditolak setelah batas + 30 detik, dan sesi yang ditinggal dinilai otomatis.
- **Simpan otomatis:** idempoten, dan menolak nomor atau sesi milik orang lain.
- **Voucher:** sekali pakai, menambah masa premium, kode dibatalkan, batas 5 gagal per jam, dan pemakaian bersamaan.
- **Akses:** trial CAT hanya untuk `via_google`, kuota 1 kali, pembahasan khusus premium, dan superuser.
- **Isolasi peserta:** tidak muncul di panel guru, leaderboard, maupun XP.
- **Kebocoran kunci:** HTML ruang ujian tidak memuat kunci, bobot, atau teks pembahasan.
- **Validator dan impor:** bobot TKP salah, opsi ganda, pembahasan kosong, duplikat, dan impor gagal tanpa menyimpan setengah data.
- **Login Google:** email berisi "agung" tidak lagi menjadi guru.

**Cek di browser** (HP 375 px, tablet 768 px, desktop 1280 px):
- alur mockup klik demi klik
- navigasi dengan keyboard
- tidak ada overflow
- konsol bersih

**Delivery Gate antislop** dijalankan sebelum diserahkan.

## 13. Di luar cakupan

- Payment gateway otomatis, verifikasi email (menunggu SMTP), dan lupa kata sandi otomatis.
- AI di server, ranking nasional atau leaderboard peserta, dan aplikasi HP native.
- Skema PPPK Guru (bisa ditambahkan sebagai skema baru setelah ada dokumen resmi).
- Penghapusan tabel lama.

## 14. Urutan pengerjaan (untuk rencana implementasi)

1. **Fondasi:** model, validator, skema awal, peran `peserta`, dan perbaikan login Google.
2. **Mesin sesi:** perakitan, penilaian, timer, simpan otomatis, Mode CAT dan Mode Belajar, termasuk UI ruang ujian dan hasil.
3. **Akses:** halaman daftar dan masuk, trial, premium, voucher, Django Admin, dan halaman Premium.
4. **Konten:** impor, Tinjau Soal, Cakupan, Laporan, dan dokumen kisi-kisi.
5. **Rilis:** impor soal lama, pengalihan alamat lama, pengaturan keamanan produksi, deploy, dan verifikasi live.

Batch draf soal pertama dibuat setelah kisi-kisi disetujui dan halaman Tinjau Soal sudah berjalan.

## 15. Yang masih menunggu pemilik

- Harga per durasi dan nomor WhatsApp, diisi di admin.
- Nomor KepmenPAN-RB untuk sumber ambang batas SKD.
- Kisi-kisi resmi SKB Guru, kalau tersedia.
- Pendaftaran alamat balik Google untuk cpns.
- Tinjauan isi Syarat Layanan dan Kebijakan Privasi.
