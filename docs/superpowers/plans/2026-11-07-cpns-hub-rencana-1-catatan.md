# CPNS Hub Rencana 1: Catatan Keputusan dan Temuan Tertunda

Rencana: `2026-11-07-cpns-hub-rencana-1-fondasi-mesin-sesi.md`
Branch: `feat/cpns-hub`. Status: selesai, 269 tes lolos, tinjauan akhir bersih setelah satu putaran perbaikan.

Dokumen ini memindahkan isi ledger kerja (yang dihapus setelah rencana selesai) supaya bisa dipakai untuk Rencana 2 sampai 4.

## Keputusan pelaksana (rulings) dan risikonya

| No | Keputusan | Risiko kalau keliru |
|---|---|---|
| R1 | Sesi belajar dinilai dengan bagian implisit: TKP memakai bobot, selain itu 5/0. "Benar" berarti jawaban sama dengan kunci, atau bobot 5 untuk TKP. | Hanya angka ringkasan belajar yang berubah. |
| R2 | Tautan navigasi sempat literal di T9, lalu diganti `{% url %}` di T12. | Sudah selesai. |
| R3 | Tes larangan kata "resmi" dipindah ke T12. | Sudah selesai. |
| R4 | T10 membuat dasbor sementara dan rute `''`; T12 menggantinya dengan dasbor penuh. | Sudah selesai. |
| R5 | Branch dibuat di checkout yang sama, bukan git worktree. | Sesi lain yang berbagi checkout bisa terganggu. |
| R6 | Urutan cek mulai CAT: skema nonaktif, CAT berjalan, SKB non-premium, trial non-Google, lalu kuota trial. | Hanya teks pesan untuk kombinasi kondisi tertentu. |
| R7 | Sesi CAT ditutup otomatis setelah batas waktu + 30 detik (sama dengan toleransi simpan). | Sesi tertutup 30 detik lebih lambat. |
| R8 | Judul ganda "CPNS Hub \| CPNS Hub" diterima karena setiap halaman mengisi judulnya sendiri. | Tab berlabel ganda di halaman tanpa judul. |
| R9 | Form "Laporkan soal" dipasang di T12 lewat slot kosong dari T11. | Sudah selesai. |
| R10 | Halaman ringkasan belajar menutup sesi saat dibuka (GET). | Prefetch tautan bisa menutup sesi lebih awal, tanpa kehilangan jawaban. |
| R11 | Dasbor tanpa persen per subtopik. Bagian #premium berisi teks "Info pembelian Premium segera tersedia." | Fitur ringkasan kelemahan ditambah di Rencana 2. |
| R12 | Modal onboarding SMK dikosongkan di halaman cpns, tapi tetap ada di halaman Akun untuk role siswa. | Siswa yang memakai CPNS tetap melihat modal di halaman profil. |
| R13 | Laporkan juga diizinkan dari sesi belajar yang sudah selesai, walau butirnya tidak dijawab (kuncinya tampil di ringkasan). | Sedikit lebih banyak laporan. |
| R14 | Verifikasi browser (T13) dijalankan langsung oleh pengendali. | Laporan verifikasi tidak melewati peninjau per-task; tetap dilihat peninjau akhir. |

## Temuan tertunda (hasil pilah tinjauan akhir)

### Sebelum deploy (Rencana 2)
- Tautan footer Syarat Layanan dan Kebijakan Privasi masih 404 (R-24, **memblokir deploy**). Tamu belum punya tautan Masuk.
- Dialog di ruang ujian belum punya focus trap.
- HTMX 400/403/409 belum menampilkan pesan apa pun (form laporkan, jawab belajar).
- `role="status"` pada hasil laporkan muncul sudah berisi, dan fokus tidak dipindah.
- Ruang CAT: 409 `sudah_selesai` ditampilkan sebagai "Waktu habis"; status tidak berubah saat timer 0; respons 400 masih tampil "Tersimpan".
- Riwayat menampilkan CAT yang sudah lewat waktu sebagai "Berjalan".
- Kartu skema SKB tampil sebelum SKD; urutkan berdasarkan `jenis_ujian` atau beri field urutan.
- `bar_skor` bisa melebihi 100% kalau admin mengisi ambang lebih besar dari nilai maksimal.
- `SkemaBagian.subtes` belum divalidasi terhadap `jenis_ujian`, padahal admin skema akan bisa diedit.
- Tes login: email None, kosong, atau berspasi, dan parsing env `GURU_EMAILS`.

### Rencana 3 (konten)
- Validator `.strip()` mengasumsikan semua opsi berupa string; impor JSON bisa berisi angka.
- `save(update_fields=...)`, `bulk_create`, dan `update` melewati pengisian `sidik_teks`.
- Pesan bobot TKP memuat kata "kunci".
- Laporan ganda bisa lolos saat dikirim bersamaan; perlu `UniqueConstraint(soal, user)` parsial untuk status `baru`.
- **Kebijakan snapshot:** label Benar/Salah di halaman hasil dihitung dari kunci terkini, sedangkan skor memakai `poin` yang tersimpan. Putuskan dulu sebelum fitur edit soal: kunci dan bobot dibekukan saat perakitan, atau penilaian ulang diterima.
- Command lama (`seed_cpns_starter`, `import_cpns`, `scrape_cpns`) masih menulis ke tabel lama dan memuat kata "Resmi". Hapus atau arahkan ke model baru.

### Rencana 4 (rilis)
- Tes yang memaksa CSRF (`enforce_csrf_checks`).
- Pindahkan JavaScript inline `ruang.html` ke file statis sebelum memasang Content Security Policy.
- Hapus tabel lama (rilis terpisah, setelah pemilik setuju).

### Boleh menunggu
- Antrean `localStorage` yang lama menimpa jawaban server tanpa membandingkan waktu.
- Sesi belajar menumpuk setiap kali "Mulai belajar" diklik; riwayat tanpa paginasi; `is_premium` dipanggil per paket.
- Queryset perakitan tanpa `order_by('id')`, sehingga acakan bertambal seed tidak sama di PostgreSQL. Hanya berdampak pada tes.
- Sejumlah tes tambahan untuk batas dan kasus tepi: model, skema, akses, `sisa_detik`, dan cabang laporkan.

### Di luar branch ini (master)
- `scripts/consolidate_and_import_neon.py:131` masih memakai aturan `'agung' in email`. **Perbaiki sebelum migrasi Neon tanggal 1.**
- Audit akun produksi yang sudah terlanjur menjadi guru atau staff lewat aturan lama (butuh izin pemilik).
