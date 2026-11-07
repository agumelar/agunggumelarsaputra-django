# CPNS Hub Rencana 2: Catatan Keputusan dan Temuan Tertunda

Dokumen ini menyimpan isi ledger kerja Rencana 2. Ledger itu dihapus setelah rencana selesai, jadi catatan ini yang dipakai untuk Rencana 3 dan 4.

Branch: `feat/cpns-hub-2`, dibuat dari master `8877260`. Belum di-push dan belum di-deploy.

## Keputusan pelaksana (rulings) dan risikonya

| No | Keputusan | Risiko kalau keliru |
|---|---|---|
| R2-1 | Route `''` tetap bernama `beranda` dan dipetakan ke view `beranda_publik` | Hanya perlu ganti nama |
| R2-2 | Penolakan voucher (kode salah, terlalu sering) dibalas 200 berisi partial HTMX. Respons 400 berteks hanya untuk permintaan cacat (kode kosong atau terlalu panjang) | Hanya kode status yang berubah |
| R2-3 | Admin memvalidasi `pesan_wa` saat disimpan. `tautan_wa` kembali ke pesan bawaan bila template rusak | Sedikit kode berlebih |
| R2-4 | Mencegah pengambilalihan akun lewat `/daftar/`: email guru ditolak; promosi ke guru lewat Google membuat sandi tidak bisa dipakai; login Google pertama ke akun hasil `/daftar/` membuat sandi tidak bisa dipakai | Peserta yang mendaftar dengan sandi lalu masuk lewat Google harus terus memakai Google |
| R2-5 | Tes leaderboard dan panel guru yang tidak bisa gagal dinaikkan ke Important lalu diperbaiki | Sedikit kerja tambahan |
| R2-6 | Pengolahan harga dipusatkan di `PengaturanCPNS.daftar_harga()` dan dipakai beranda, premium, dan admin | Refaktor kecil |
| R2-7 | Teks Premium yang saling bertentangan saat harga dan kontak sama-sama kosong diperbaiki (Review Focus 5) | Sedikit kerja tambahan |
| R2-8 | Tautan nav "Akun" disembunyikan untuk peserta. Halaman akun khusus CPNS ditunda | Peserta belum punya halaman akun |

## Temuan tinjauan akhir yang sudah diperbaiki
- **C1:** isolasi peserta di host cpns. Rute sekolah sekarang dialihkan ke dasbor.
- **I1:** login Google dari `/cpns/` di domain utama sekarang membuat peserta.
- **I2:** ada pesan "Akun ini sekarang masuk lewat Google" dan petunjuk di halaman Masuk.
- **I3:** voucher tidak bisa dipakai ulang setelah pemakainya dihapus.
- **M1:** `CPNS_URL` yang kosong tidak lagi menjadi `/`.
- **M2:** error callback Google di jalur cpns diarahkan ke `cpns:masuk`.
- **M3:** nilai `next` tetap ada setelah login gagal.
- **M4:** teks beranda jujur saat kontak belum diatur.

## Wajib sebelum deploy (Rencana 4)
- **Pemilik:**
  - Meninjau isi Syarat Layanan dan Kebijakan Privasi, lalu mengisi `[KEBIJAKAN PENGEMBALIAN DANA]` dan `[NAMA DAN KONTAK PENGELOLA]`.
  - Mengisi harga dan nomor WA di admin produksi.
- **Alamat balik Google:** yang benar adalah `https://cpns.agunggumelarsaputra.com/accounts/oauth/google/callback/`. Spesifikasi §11 menulis `/accounts/google/callback/`, dan itu keliru.
- **Batas percobaan login** di `/masuk/`. Saat ini kata sandi bisa ditebak berulang tanpa batas.
- **Logout lewat POST** dengan CSRF. Saat ini logout masih lewat GET.
- **Pemeriksaan data produksi:**
  - Pengguna dengan email `GURU_EMAILS` yang masih punya kata sandi.
  - Email ganda yang hanya beda huruf besar dan kecil (`_cari_user` belum memakai `order_by`).
- **Uji konkurensi voucher di Postgres** (`TransactionTestCase`). Termasuk bukti bahwa percobaan gagal tetap tercatat.
- **`CPNS_URL` di development:** set di `development.py` atau `.env` lokal. Defaultnya sekarang mengarah ke produksi.
- **Admin `buat-banyak`:** pakai izin tambah eksplisit sebelum ada akun staf selain pemilik.

## Rencana 3 (konten)
- Pindahkan `SUBTES_PER_JENIS` dari admin ke `validasi.py`. Beri konstanta untuk bobot 5.
- Teks trial "1 paket, 30 soal, 1 simulasi" masih ditulis langsung. Ambil dari data setelah paket trial nyata ada.
- Kalimat beranda menggantung bila skema SKD tidak ada. Seed 0004 selalu membuatnya.

## Boleh menunggu
- **Akun dan login:**
  - Petunjuk "Akun ini memakai Google" belum muncul untuk peserta yang dibuat langsung lewat Google (sandi acaknya masih bisa dipakai).
  - `IntegrityError` saat dua orang mendaftar bersamaan dengan email yang sama.
  - Username dari email belum dinormalisasi.
- **Voucher dan Premium:**
  - Lencana status di halaman Premium belum diperbarui setelah tukar kode lewat HTMX. Pesan berhasil sudah menyebut tanggal baru.
  - Sesi kedaluwarsa saat menukar kode lewat HTMX: halaman masuk ikut tampil di dalam wadah hasil.
  - Pesan WA bawaan menyebut 30 hari saat harga belum diisi.
- **Ruang CAT:**
  - Jawaban yang ditolak (400) tetap terlihat terpilih.
  - Status "gagal" menutupi "ditolak" dalam satu batch kiriman.
  - Fokus tetap terjebak setelah layar diperlebar ke ukuran lg.
  - Pengumuman dengan teks yang sama tidak dibacakan ulang.
- **Kerapian dan tes:**
  - Gaya aktif nav mobile Premium berbeda dari nav lain.
  - Warna teks harga memakai sky.
  - Input belum berbingkai merah saat error.
  - Beberapa tes masih hanya memeriksa teks.
- **Performa:**
  - `PengaturanCPNS.ambil()` bisa bentrok saat dua permintaan pertama datang bersamaan. Seed barisnya lewat migrasi.
  - Analitik subtopik memuat semua butir ke Python.
- **Tes cepat:** commit `config/settings/test.py` dengan hasher MD5. Saat ini suite penuh dengan PBKDF2 sangat lambat di mesin lokal.
