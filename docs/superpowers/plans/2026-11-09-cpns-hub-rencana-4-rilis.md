# CPNS Hub Rencana 4: Data Lama, Keamanan Produksi, dan Rilis

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** CPNS Hub siap tayang di `cpns.agunggumelarsaputra.com`:
- soal lama disalin sebagai draf,
- alamat lama dialihkan permanen,
- pengaturan produksi aman secara bawaan,
- login dibatasi percobaannya dan logout aman,
- data produksi diperiksa,
- uji di Postgres,
- deploy dilakukan bertahap dengan persetujuan pemilik di setiap langkah yang menyentuh server.

**Architecture:**
- **Perintah manajemen baru:**
  - `cpns_impor_soal_lama` menulis ke database.
  - `cpns_cek_produksi` hanya membaca.
- **Pengalihan 301:** ditaruh di `apps/cpns/urls.py`.
- **Batas percobaan login:** model `PercobaanMasuk` di app `accounts`, dipakai bersama oleh login CPNS dan login sekolah.
- **Pengaturan produksi gagal-tertutup:** tanpa `DJANGO_SECRET_KEY` atau kata sandi database, server tidak mau jalan.

**Tech Stack:** Python 3.12, Django 5.1, PostgreSQL 17 (produksi, Docker), HTMX 2.0.4, Alpine.js 3.14.8, Tailwind CSS 3.4.

**Spec:** `docs/superpowers/specs/2026-11-07-cpns-hub-design.md` (bagian 10, 11, 12, 15).

**Catatan bawaan:**
- `docs/superpowers/plans/2026-11-07-cpns-hub-rencana-1-catatan.md` bagian "Rencana 4 (rilis)"
- `docs/superpowers/plans/2026-11-07-cpns-hub-rencana-2-catatan.md` bagian "Wajib sebelum deploy (Rencana 4)"
- `docs/superpowers/plans/2026-11-07-cpns-hub-rencana-3-catatan.md` bagian "Wajib sebelum deploy (Rencana 4)"

**Di luar rencana ini:**
- **Content Security Policy** dan pemindahan JavaScript inline ruang ujian. Spesifikasi §11 tidak mewajibkannya, jadi ini rilis keamanan berikutnya.
- **Penghapusan tabel lama.** Ini rilis terpisah setelah pemilik setuju (spesifikasi §10).
- **Rotasi kata sandi database produksi.** Lihat Task 3: nilainya dipindah ke `.env` tetapi tidak diganti.
- **Penulisan batch soal sungguhan.** Dikerjakan di sesi konten terpisah.

## Global Constraints

- **Branch:** `feat/cpns-hub-4` dari `master` lokal. Stage dengan path eksplisit. Jangan `git add -A`.
- **Task 1 sampai 8 hanya mengubah repo lokal.** Server tidak disentuh.
- **Task 9 (deploy):** setiap langkah yang menulis ke VPS atau GitHub (backup, push, ubah `.env`, restart container, perintah impor di produksi) baru dijalankan setelah pemilik menulis persetujuan untuk langkah itu di chat. Tidak ada langkah produksi berdasarkan persetujuan umum.
- **Tes:** suite penuh harus lolos di akhir setiap task. Untuk kecepatan, pakai settings hasher MD5 di luar repo.
- **Teks UI:** bahasa Indonesia sederhana. Tanpa em dash, emoji, kata "resmi", atau "soal asli BKN".
- **Tampilan:** warna mengikuti `DESIGN.md`. Target sentuh minimal 44 px. Status tidak hanya ditandai warna.
- **Alamat:** pakai `reverse` atau `{% url %}`. Prefiks `/cpns/` di domain utama harus tetap jalan.
- **Rahasia:** jangan menulis kata sandi, kunci, atau token ke file yang di-commit, ke chat, atau ke laporan. Tulis nama variabelnya saja.

## Review Focus

1. **Impor soal lama dijalankan dua kali, atau soal lama sama dengan soal yang sudah ada di bank.** Tidak boleh ada soal ganda. Laporan menyebut berapa yang dilewati. Diuji di Task 1.
2. **Server produksi dinyalakan tanpa `DJANGO_SECRET_KEY` atau tanpa kata sandi database.** Server harus gagal dengan pesan jelas, tidak boleh diam-diam memakai nilai bawaan. Diuji di Task 3.
3. **Tautan lama yang sudah dibagikan.** Contoh: `/exam/skd-bkn-01/` di subdomain cpns, atau `/cpns/packages/` di domain utama. Keduanya harus mengarah ke halaman baru yang benar dengan status 301, tanpa redirect berulang. Diuji di Task 2.
4. **Batas percobaan login.**
   - Percobaan salah berulang dengan huruf besar-kecil atau spasi berbeda (`Budi@x.id` dan ` budi@x.id`) tetap dihitung untuk akun yang sama.
   - Login yang benar sesudah batas tetap ditolak sampai jeda habis.
   - Diuji di Task 4.
5. **Logout.** Tautan logout di halaman lain, atau GET dari situs lain, tidak boleh mengeluarkan pengguna. Diuji di Task 5.

---

## Peta file

```
apps/cpns/management/commands/cpns_impor_soal_lama.py   (baru)
apps/cpns/impor_lama.py                                 (baru)  salin_soal_lama()
apps/cpns/urls.py                                       (ubah)  pengalihan 301
config/settings/production.py, base.py, development.py  (ubah)
docker-compose.yml, scripts/entrypoint.sh, .env.example (ubah/baru)
apps/accounts/models.py (+migrasi), apps/accounts/batas_masuk.py (baru)
apps/accounts/views.py, apps/cpns/views/akun.py         (ubah)  batas login, logout POST
templates/components/navbar.html, templates/cpns/base_cpns.html, templates/accounts/keluar.html  (ubah/baru)
apps/cpns/admin.py, templates/cpns/kelola/tinjau.html   (ubah)  perapian kecil
apps/cpns/management/commands/cpns_cek_produksi.py      (baru)
apps/cpns/tests/test_postgres.py                        (baru)  khusus Postgres
docs/cpns/rilis.md                                      (baru)  daftar periksa rilis untuk pemilik
docs/cpns/kisi-kisi.md                                  (ubah)  tandai disetujui
```

---

### Task 1: Impor soal lama

**Files:**
- Create: `apps/cpns/impor_lama.py`, `apps/cpns/management/commands/cpns_impor_soal_lama.py`
- Test: `apps/cpns/tests/test_impor_lama.py`

**Interfaces:**
- `salin_soal_lama(coba: bool = False) -> HasilSalin`
  - `HasilSalin` adalah dataclass dengan field `masuk: int`, `dilewati_sama: int`, `perlu_cek: int`, `paket: dict[str, int]`.
- **Pemetaan per `CpnsQuestion`:**
  - `jenis_ujian`: dari `package.tipe_ujian` (SKD menjadi SKD, SKB menjadi SKB_GURU).
  - `subtes`:
    - TWK, TIU, TKP tetap.
    - `SKB_GURU` menjadi `PEDAGOGIK`, dengan `perlu_cek=True` dan catatan "Subtes asli SKB_GURU. Pilih PEDAGOGIK atau MATERI_RPL."
  - `subtopik`: diambil apa adanya. Kalau kosong, menjadi "Umum".
  - `teks` dari `pertanyaan`. `opsi_a` sampai `opsi_e` disalin.
  - `kunci` dari `kunci_jawaban`, kecuali untuk TKP.
  - `bobot` dari `bobot_tkp` untuk TKP.
  - Pembahasan: `pembahasan_konsep` dari `bedah_konsep`, `pembahasan_pengecoh` dari `alasan_pengecoh`, `pembahasan_cepat` dari `tips_cepat`.
  - `sumber="lama"`, `status="draf"`, `batch="lama-<package.kode>"`.
- **Aturan:**
  - Lewati soal yang `sidik_teks`-nya sudah ada di bank (status apa pun), juga yang ganda di antara soal lama itu sendiri.
  - Soal yang gagal `validasi_soal` tetap disalin, dengan `perlu_cek=True` dan `catatan_tinjau="Pemeriksaan otomatis: " + "; ".join(pesan)`.
  - Tidak pernah membuat soal `tayang`.
  - Semua penulisan berada dalam satu `transaction.atomic()`.
  - Tabel lama tidak diubah.
- **Command:**
  - `cpns_impor_soal_lama [--coba]` mencetak "Disalin: N soal (draf, sumber lama). Dilewati karena sama: M. Ditandai perlu cek: K.", lalu satu baris per paket.
  - Dengan `--coba`, tidak ada yang disimpan.

- [ ] **Step 1:** Buat branch: `git switch -c feat/cpns-hub-4`.
- [ ] **Step 2: Tulis tes yang gagal.**
  - `test_salin_pemetaan_lengkap`
  - `test_tkp_pakai_bobot`
  - `test_skb_guru_jadi_pedagogik_perlu_cek`
  - `test_subtopik_kosong_jadi_umum`
  - `test_tidak_valid_tetap_disalin_perlu_cek_dengan_catatan`
  - `test_jalan_dua_kali_tidak_ganda` (Review Focus 1)
  - `test_sama_dengan_bank_dilewati` (Review Focus 1)
  - `test_coba_tidak_menyimpan`
  - `test_tidak_pernah_tayang`
  - `test_tabel_lama_tidak_berubah`
  - `test_command_ringkasan`
- [ ] **Step 3:** Jalankan tes dan pastikan FAIL. Implementasikan. Jalankan lagi dan pastikan PASS, termasuk seluruh suite.
- [ ] **Step 4:** Commit `feat(cpns): salin soal lama sebagai draf`.

---

### Task 2: Pengalihan permanen alamat lama

**Files:**
- Modify: `apps/cpns/urls.py`
- Test: `apps/cpns/tests/test_alamat_lama.py`

**Interfaces:**
Tambahkan tiga route memakai `RedirectView(pattern_name=..., permanent=True, query_string=False)`:
- `packages/` dan `packages/<slug:slug>/` ke `cpns:beranda`
- `exam/<slug:slug>/` dan `exam/<slug:slug>/submit/` ke `cpns:dasbor`
- `result/<slug:slug>/<int:attempt_id>/` ke `cpns:riwayat`

Pengalihan berlaku di subdomain cpns (akar) dan di domain utama (`/cpns/...`) karena urls yang sama dipasang di keduanya.

- [ ] **Step 1: Tulis tes yang gagal.**
  - Untuk setiap alamat lama di kedua host: status 301 dan `Location` sama dengan `reverse` tujuan dengan urlconf host itu.
  - `test_tujuan_tidak_mengalihkan_lagi` (Review Focus 3): mengikuti redirect sekali menghasilkan 200 untuk tamu atau 302 ke masuk, bukan 301 lagi.
- [ ] **Step 2:** Jalankan tes dan pastikan FAIL. Implementasikan. Jalankan lagi dan pastikan PASS.
- [ ] **Step 3:** Commit `feat(cpns): alihkan alamat lama secara permanen`.

---

### Task 3: Pengaturan produksi gagal-tertutup

**Files:**
- Modify:
  - `config/settings/production.py`
  - `config/settings/base.py` (fallback SECRET_KEY hanya untuk development)
  - `config/settings/development.py` (`CPNS_URL = "http://cpns.localhost:8010/"`)
  - `docker-compose.yml`
  - `scripts/entrypoint.sh`
- Create: `.env.example`
- Test: `apps/core/tests/test_settings_produksi.py` (atau lokasi tes core yang sudah ada)

**Interfaces:**
- **`production.py`:**
  - `SECRET_KEY` wajib dari env `DJANGO_SECRET_KEY`. Kalau kosong, raise `ImproperlyConfigured("DJANGO_SECRET_KEY wajib diisi di .env produksi.")`.
  - Kata sandi database wajib. Sumbernya `DATABASE_URL` atau `DB_PASSWORD`, tanpa nilai bawaan di kode. Kalau kosong, pesannya "DB_PASSWORD atau DATABASE_URL wajib diisi."
  - `ALLOWED_HOSTS` bawaan berupa daftar eksplisit: `agunggumelarsaputra.com`, `www.agunggumelarsaputra.com`, `cpns.agunggumelarsaputra.com`. Bisa diganti lewat env. Nilai `*` ditolak dengan `ImproperlyConfigured`.
  - Bawaan `SESSION_COOKIE_SECURE=True`, `CSRF_COOKIE_SECURE=True`, `SECURE_HSTS_SECONDS=int(env, bawaan 3600)`, `SECURE_HSTS_INCLUDE_SUBDOMAINS=False`, `SECURE_HSTS_PRELOAD=False`.
  - `CSRF_TRUSTED_ORIGINS` bawaan hanya `https://` untuk ketiga domain.
- **`base.py`:** fallback SECRET_KEY tidak dipakai di produksi. Fallback itu tetap boleh di development.
- **`docker-compose.yml`:**
  - Hapus semua nilai rahasia dan `ALLOWED_HOSTS=*`.
  - Kredensial DB untuk `web` dan `db` diambil dari `.env` (`env_file` dan `${...}`).
  - Hapus juga override `SESSION_COOKIE_SECURE=False` dan `CSRF_COOKIE_SECURE=False`.
- **`entrypoint.sh`:** tanpa nilai bawaan kata sandi.
- **`.env.example`:** nama variabel wajib dengan nilai contoh `[ISI]`:
  - `DJANGO_SECRET_KEY`, `DB_NAME`, `DB_USER`, `DB_PASSWORD`
  - `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD`
  - `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET`
  - `GURU_EMAILS`, `CPNS_URL`, `SECURE_HSTS_SECONDS`

  Tambahkan komentar singkat bahwa kata sandi database harus sama dengan yang sudah dipakai volume Postgres.

- [ ] **Step 1: Tulis tes yang gagal.** Tes memuat modul settings produksi lewat subprocess `python -c` dengan env tertentu, tanpa `importlib.reload` di proses tes.
  - `test_tanpa_secret_key_gagal` (Review Focus 2)
  - `test_tanpa_password_db_gagal` (Review Focus 2)
  - `test_allowed_hosts_bintang_ditolak`
  - `test_bawaan_aman`: cookie secure, HSTS 3600, hosts eksplisit.
  - `test_compose_tanpa_rahasia`: `docker-compose.yml` tidak memuat `PASSWORD=` dengan nilai literal maupun `ALLOWED_HOSTS=*`.
  - `test_check_deploy_bersih`: `manage.py check --deploy` dengan settings produksi dan env contoh tidak menghasilkan error. Peringatan yang disengaja, seperti HSTS subdomain, dicatat di laporan.
- [ ] **Step 2:** Jalankan tes dan pastikan FAIL. Implementasikan. Jalankan lagi dan pastikan PASS.
- [ ] **Step 3:** Commit `fix(config): pengaturan produksi gagal-tertutup tanpa rahasia di repo`.

---

### Task 4: Batas percobaan login

**Files:**
- Create: `apps/accounts/batas_masuk.py`, model `PercobaanMasuk` di `apps/accounts/models.py` beserta migrasinya
- Modify: `apps/cpns/views/akun.py` (masuk), `apps/accounts/views.py` (`login_view`)
- Test: `apps/accounts/tests/test_batas_masuk.py`

**Interfaces:**
- `PercobaanMasuk`: field `kunci` (CharField 254, db_index), `waktu` (DateTimeField, default now, db_index).
- `BATAS_GAGAL = 5`, `JEDA = timedelta(minutes=15)`.
- `kunci_identitas(identitas: str) -> str` mengembalikan `identitas.strip().lower()`.
- `terkunci(identitas, now=None) -> bool` bernilai benar kalau jumlah percobaan gagal dalam 15 menit terakhir sudah 5 atau lebih.
- `catat_gagal(identitas, now=None)` dan `bersihkan(identitas)`. `bersihkan` dipanggil saat login berhasil.
- **Kedua view login:**
  - Kalau `terkunci`, jangan memanggil `authenticate`. Tampilkan "Terlalu banyak percobaan masuk. Coba lagi dalam 15 menit." dengan status 429.
  - Kalau gagal, panggil `catat_gagal`.
  - Pesan gagal biasa tidak berubah.
- Baris yang lebih lama dari 1 hari dihapus secara oportunistik saat `catat_gagal`.

- [ ] **Step 1: Tulis tes yang gagal.**
  - `test_lima_gagal_lalu_terkunci`
  - `test_variasi_huruf_dan_spasi_dihitung_sama` (Review Focus 4)
  - `test_benar_saat_terkunci_tetap_ditolak` (Review Focus 4)
  - `test_terbuka_setelah_15_menit`
  - `test_berhasil_membersihkan`
  - `test_login_sekolah_juga_dibatasi`
  - `test_status_429`
- [ ] **Step 2:** Jalankan tes dan pastikan FAIL. Implementasikan. Jalankan lagi dan pastikan PASS.
- [ ] **Step 3:** Commit `feat(accounts): batasi percobaan login`.

---

### Task 5: Logout lewat POST

**Files:**
- Modify:
  - `apps/accounts/views.py` (`logout_view`)
  - `templates/components/navbar.html`
  - `templates/cpns/base_cpns.html`
  - `templates/cpns/kelola/base_kelola.html` (kalau memuat tautan keluar)
- Create: `templates/accounts/keluar.html`
- Test: `apps/accounts/tests/test_logout.py`

**Interfaces:**
- **`logout_view`:**
  - GET menampilkan halaman konfirmasi "Keluar dari akun?" dengan tombol POST "Keluar". Pengguna tidak dikeluarkan. Di host cpns, halaman ini memakai `base_cpns.html`.
  - POST (dengan CSRF) mengeluarkan pengguna, lalu redirect seperti sekarang.
- **Semua tombol "Keluar"** di navbar, base_cpns (desktop dan mobile), dan kelola menjadi `<form method="post">` dengan `{% csrf_token %}`. Tampilannya tetap sama dan target sentuhnya tetap minimal 44 px.

- [ ] **Step 1: Tulis tes yang gagal.**
  - `test_get_tidak_mengeluarkan` (Review Focus 5)
  - `test_post_mengeluarkan`
  - `test_post_tanpa_csrf_ditolak` (`Client(enforce_csrf_checks=True)`)
  - `test_tombol_keluar_berupa_form_post`: untuk navbar dan base_cpns.
- [ ] **Step 2:** Jalankan tes dan pastikan FAIL. Implementasikan dan build CSS bila perlu. Jalankan lagi dan pastikan PASS.
- [ ] **Step 3:** Commit `fix(accounts): logout hanya lewat POST`.

---

### Task 6: Perapian rilis kecil dan tes CSRF

**Files:**
- Modify:
  - `apps/cpns/admin.py`: buat-banyak memeriksa `has_add_permission`. Ganti `has_add_permission` admin menjadi izin `cpns.add_voucher`, tapi tombol "Tambah" bawaan tetap disembunyikan.
  - `templates/cpns/kelola/tinjau.html` beserta view-nya: baris meta untuk batch kosong menjadi "Soal X dari Y tanpa batch".
- Create:
  - `apps/cpns/tests/test_csrf.py`
  - `apps/cpns/tests/test_postgres.py`

**Interfaces:**
- **`test_csrf.py`:** dengan `Client(enforce_csrf_checks=True)`, POST tanpa token mendapat 403 untuk endpoint berikut:
  - `cpns:masuk`, `cpns:daftar`, `cpns:tukar_voucher`, `cpns:cat_kumpulkan`, `cpns:laporkan`, `cpns:kelola_aksi`, `accounts:logout`
  - `cpns:cat_simpan`, sesuai cara template mengirim token
- **`test_postgres.py`:** `@skipUnless(connection.vendor == "postgresql")`, `TransactionTestCase`. Isinya:
  - Dua thread memakai voucher yang sama. Tepat satu berhasil, dan `premium_sampai` hanya bertambah sekali.
  - Dua thread memulai CAT untuk user yang sama. Tepat satu sesi berjalan.
  - Percobaan voucher gagal tetap tercatat walau penolakan terjadi.

- [ ] **Step 1: Tulis tes yang gagal** untuk admin dan teks batch. Tes CSRF yang langsung lolos dicatat sebagai pengunci perilaku.
- [ ] **Step 2:** Implementasikan. Jalankan tes sampai PASS. Di SQLite, `test_postgres.py` di-skip.
- [ ] **Step 3:** Commit `test(cpns): tes csrf, tes konkurensi postgres, perapian rilis`.

---

### Task 7: Pemeriksaan data produksi (hanya baca)

**Files:**
- Create: `apps/cpns/management/commands/cpns_cek_produksi.py`
- Test: `apps/cpns/tests/test_cek_produksi.py`

**Interfaces:**
Perintah ini **tidak menulis apa pun**. Ia mencetak daftar periksa berlabel `[OK]` atau `[PERLU TINDAKAN]`:
1. User dengan email `GURU_EMAILS` yang kata sandinya masih bisa dipakai. Cetak username saja, tanpa email.
2. Email ganda yang hanya berbeda huruf besar-kecil. Cetak jumlah dan username.
3. `PengaturanCPNS`: nomor WA dan harga sudah diisi atau belum.
4. Placeholder `[KEBIJAKAN PENGEMBALIAN DANA]` dan `[NAMA DAN KONTAK PENGELOLA]` masih ada atau tidak di template syarat dan privasi.
5. Kisi-kisi: dokumen terbaca dan sudah ditandai disetujui (tidak diawali "Draf").
6. Jumlah soal tayang per subtes dibanding kebutuhan skema SKD-CAT.
7. Jumlah soal lama dan perkiraan hasil `salin_soal_lama(coba=True)`.

- [ ] **Step 1: Tulis tes yang gagal.**
  - `test_tidak_menulis` memakai `assertNumQueries`, atau pemeriksaan bahwa tidak ada query yang menulis.
  - Satu tes untuk setiap butir 1 sampai 7.
  - `test_tanpa_email_di_keluaran`
- [ ] **Step 2:** Jalankan tes dan pastikan FAIL. Implementasikan. Jalankan lagi dan pastikan PASS.
- [ ] **Step 3:** Commit `feat(cpns): perintah pemeriksaan data produksi`.

---

### Task 8: Dokumen rilis, kisi-kisi disetujui, dan verifikasi lokal (pengendali)

**Files:**
- Create: `docs/cpns/rilis.md`, `anti-slop/audit-006-<tanggal>.md`
- Modify: `docs/cpns/kisi-kisi.md`. Baris "Draf, menunggu persetujuan pemilik." diganti menjadi "Disetujui pemilik pada 2026-11-09."

**Isi `docs/cpns/rilis.md`:** daftar periksa berurutan berbahasa sederhana.
- **Tugas pemilik:**
  - Tinjau Syarat Layanan dan Kebijakan Privasi, lalu isi placeholder.
  - Isi harga dan nomor WA di admin produksi.
  - Daftarkan `https://cpns.agunggumelarsaputra.com/accounts/oauth/google/callback/` di Google Cloud Console.
  - Pastikan `.env` VPS memuat semua variabel di `.env.example`.
  - Bila ada, berikan nomor KepmenPAN-RB sebagai sumber ambang batas SKD (spesifikasi §15). Tugas ini tidak memblokir rilis.
- **Urutan deploy:** sama dengan Task 9.
- **Cara mundur:**
  - `git reset --hard <commit sebelum deploy>` di VPS, lalu restart.
  - Pulihkan backup database bila migrasi bermasalah.

- [ ] **Step 1:** Ubah status kisi-kisi dan tulis `rilis.md`.
- [ ] **Step 2: Verifikasi browser lokal** di lebar 375, 768, dan 1280 px:
  - Logout: konfirmasi GET lalu POST.
  - Masuk salah 6 kali sampai muncul pesan batas.
  - Alamat lama `/exam/x/` menghasilkan 301 ke dasbor.
  - Tinjau batch "lama-..." setelah `cpns_impor_soal_lama` dijalankan lokal.
  - Hasil `cpns_cek_produksi` lokal.
- [ ] **Step 3:** Tulis laporan antislop audit-006, lalu commit `docs(cpns): daftar periksa rilis dan verifikasi rencana 4`.

---

### Task 9: Uji Postgres dan deploy (pengendali, setiap langkah atas persetujuan pemilik)

Setiap langkah di bawah dijalankan **hanya setelah** pemilik menulis persetujuan untuk langkah itu di chat. Sebelum meminta persetujuan, pengendali menjelaskan dengan bahasa sederhana apa yang akan dilakukan, dan bagaimana membatalkannya bila gagal.

- [ ] **Step 1: Uji suite di Postgres** (VPS, kontainer sementara, tidak menyentuh database produksi):
  - Jalankan `postgres:17-alpine` sementara dengan nama unik di jaringan Docker sendiri.
  - Bangun image dari commit branch.
  - Jalankan `manage.py test` dengan `DATABASE_URL` mengarah ke kontainer sementara itu, termasuk `test_postgres.py`.
  - Hapus kedua kontainer setelahnya.
  - Kalau gagal, perbaiki di lokal lewat alur task biasa sebelum lanjut.
- [ ] **Step 2: Pemeriksaan VPS hanya baca.**
  - Cabang dan commit repo di VPS.
  - Nama-nama variabel di `.env`, tanpa menampilkan nilainya.
  - Konfigurasi nginx untuk kedua domain: `proxy_pass` dan `X-Forwarded-Proto`.
  - Status container.
- [ ] **Step 3: Backup database produksi** dengan `pg_dump` ke file bertanggal di VPS, di luar folder repo.
- [ ] **Step 4: Gabung dan push.**
  - Merge branch ke `master` lokal (kalau pemilik memilih).
  - Push `master` ke GitHub.
- [ ] **Step 5: Lengkapi `.env` VPS.** Isi variabel yang belum ada, sesuai `.env.example`. Nilai kata sandi database sama dengan yang sedang dipakai.
- [ ] **Step 6: Perbarui kode dan kontainer di VPS.**
  - Di VPS, fast-forward kode, lalu `docker compose up -d --build web`.
  - Pantau log: migrasi, collectstatic, dan gunicorn harus jalan.
  - Kalau gagal, ikuti cara mundur di `rilis.md`.
- [ ] **Step 7: Periksa data produksi.**
  - Jalankan `cpns_cek_produksi` di VPS dan laporkan hasilnya ke pemilik.
  - Jalankan `cpns_impor_soal_lama --coba`. Setelah pemilik setuju, jalankan versi sungguhan.
- [ ] **Step 8: Uji asap di browser** pada `https://cpns.agunggumelarsaputra.com` dan `https://agunggumelarsaputra.com` tanpa login:
  - beranda, masuk, daftar, premium, syarat, privasi
  - alamat lama 301
  - situs sekolah tetap jalan
  - konsol bersih
  - Tulis hasilnya ke `docs/cpns/rilis.md` bagian "Catatan rilis".
- [ ] **Step 9:** Perbarui memori proyek. Status pembekuan deploy dicabut.
