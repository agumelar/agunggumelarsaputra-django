# CPNS Hub Rencana 3: Alat Konten (Kisi-kisi, Impor, Tinjau, Cakupan, Laporan)

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Pemilik bisa mengisi bank soal dengan aman, dengan alur berikut:
1. Draf AI disimpan sebagai file batch JSON.
2. File itu diimpor sebagai `draf` dengan pemeriksaan otomatis.
3. Draf ditinjau satu per satu di halaman Tinjau Soal, lalu disetujui, diedit, ditolak, atau dilewati.
4. Halaman Cakupan menunjukkan subtopik mana yang masih kurang.
5. Laporan soal dari peserta diselesaikan di satu antrean.

**Architecture:**
- **Layanan murni:**
  - `apps/cpns/kisi_kisi.py`: membaca tabel kisi-kisi dari markdown.
  - `apps/cpns/impor.py`: memvalidasi dan menyimpan batch.
  - `apps/cpns/cakupan.py`: menghitung angka cakupan.
- **Perintah:** `cpns_impor_soal` hanya membungkus `impor.py`.
- **Halaman kelola:** `apps/cpns/views/kelola.py`, rute `/kelola/...` di namespace `cpns`, khusus superuser, dengan tata letak sendiri sesuai mockup 08.
- **Snapshot hasil:** status Benar/Salah setiap butir disimpan saat dinilai, sehingga mengedit soal tidak mengubah hasil lama.

**Tech Stack:** Python 3.12, Django 5.1, HTMX 2.0.4, Alpine.js 3.14.8, Tailwind CSS 3.4 (`npm run build:css`, lalu `output.css` di-commit).

**Spec:** `docs/superpowers/specs/2026-11-07-cpns-hub-design.md` (bagian 3.1, 8, 9).

Catatan bawaan:
- `docs/superpowers/plans/2026-11-07-cpns-hub-rencana-1-catatan.md` bagian "Rencana 3 (konten)"
- `docs/superpowers/plans/2026-11-07-cpns-hub-rencana-2-catatan.md` bagian "Rencana 3 (konten)"

Mockup: `design/png/08-admin-tinjau-soal.png`.

**Di luar rencana ini:**
- **Menulis soal sungguhan.** Batch draf pertama dibuat dalam sesi terpisah setelah pemilik menyetujui kisi-kisi.
- **Rencana 4:**
  - impor soal lama (`cpns_impor_soal_lama`)
  - pengalihan 301
  - keamanan produksi
  - batas percobaan login
  - deploy

Server **tetap tidak di-deploy**.

## Global Constraints

- **Branch dan git:**
  - Branch `feat/cpns-hub-3` dari `master` lokal.
  - Stage dengan path eksplisit. Jangan pernah `git add -A`.
  - Jangan push. Jangan deploy.
- **Tes:**
  - Suite penuh lebih cepat dijalankan dengan settings hasher MD5 di luar repo (pengendali memberi perintahnya).
  - Seluruh suite harus lolos di akhir setiap task.
- **Teks UI:**
  - Bahasa Indonesia sederhana.
  - Dilarang em dash, emoji, kata "resmi", "soal asli BKN", dan angka atau testimoni karangan.
- **Tampilan:** warna dan font mengikuti `DESIGN.md`. Aksen tunggal sky `#38BDF8` dengan teks `#082F49`. Sukses `#34D399`, bahaya `#F87171`, premium/peringatan `#FBBF24`.
- **Aksesibilitas:**
  - Target sentuh minimal 44 px.
  - Fokus terlihat.
  - Status tidak hanya ditandai warna.
  - Setiap formulir berlabel.
- **Alamat:** gunakan `reverse`/`{% url %}`. Prefiks `/cpns/` di domain utama harus tetap jalan.
- **Akses kelola:** semua halaman `/kelola/...` hanya untuk superuser.
  - Tamu diarahkan ke `cpns:masuk`.
  - User login yang bukan superuser mendapat 403.
  - Pemeriksaan dilakukan di server untuk setiap view dan aksi POST.
- **Pintasan keyboard:**
  - Diabaikan saat Ctrl, Cmd, atau Alt ditekan.
  - Diabaikan saat fokus ada di `input`, `textarea`, atau `select`.
- **CSS:** task yang menambah kelas Tailwind menjalankan `npm run build:css` dan `collectstatic --noinput`, lalu meng-commit `static/css/output.css`.

## Review Focus

1. **Dua tab meninjau soal yang sama.** Contoh: tab A menolak, lalu tab B menekan Setujui. Aksi kedua ditolak dengan pesan "Soal ini sudah diubah di tab lain. Muat ulang untuk melihat keadaan terbaru.", dan status tidak tertimpa. Diuji di Task 5.
2. **Mengetik di kolom alasan tolak.** Huruf seperti "s", "e", dan "t" tidak memicu pintasan. Diuji di Task 5 (atribut markup) dan Task 9 (browser).
3. **File batch berisi masalah.** Tiga kasus:
   - opsi berupa angka JSON (`85`) diterima sebagai teks
   - soal ganda di dalam file yang sama ditolak
   - soal yang teksnya sama dengan soal yang sudah ada di bank (status apa pun) ditolak, dengan nomor baris disebut

   Diuji di Task 4.
4. **Mengedit soal tayang yang sudah pernah dipakai.**
   - Hasil simulasi dan belajar lama tetap menampilkan Benar/Salah dan skor seperti saat dinilai.
   - Edit yang tidak valid tidak menyimpan apa pun.

   Diuji di Task 2 dan Task 6.
5. **Bank kosong atau `jumlah_soal` bernilai 0.** Halaman Cakupan tetap tampil dengan angka 0 yang jujur, tanpa error pembagian. Diuji di Task 7.

---

## Peta file

```
apps/cpns/validasi.py                 (ubah)  SUBTES_PER_JENIS, POIN_MAKS_BOBOT, pesan bobot, opsi non-string
apps/cpns/models/soal.py              (ubah)  sidik_teks saat save(update_fields=...)
apps/cpns/models/akses.py             (ubah)  UniqueConstraint laporan baru
apps/cpns/models/sesi.py              (ubah)  SesiSoal.benar
apps/cpns/penilaian.py, sesi_layanan.py, views/belajar.py, views/cat.py, analitik.py  (ubah)  pakai snapshot
apps/cpns/admin.py                    (ubah)  impor konstanta dari validasi
apps/cpns/kisi_kisi.py                (baru)  baca_kisi_kisi()
apps/cpns/impor.py                    (baru)  impor_batch()
apps/cpns/cakupan.py                  (baru)  hitung_cakupan()
apps/cpns/management/commands/cpns_impor_soal.py   (baru)
apps/cpns/management/commands/{seed_cpns_starter,import_cpns,scrape_cpns}.py    (hapus)
apps/cpns/views/kelola.py             (baru)  tinjau, aksi, ubah, cakupan, laporan
templates/cpns/kelola/*               (baru)
docs/cpns/kisi-kisi.md                (baru)  draf kisi-kisi, menunggu persetujuan pemilik
docs/cpns/format-batch.md             (baru)  format file batch untuk sesi penulis draf
```

---

### Task 1: Perapian validasi dan model (catatan bawaan)

**Files:**
- Modify:
  - `apps/cpns/validasi.py`
  - `apps/cpns/models/soal.py`
  - `apps/cpns/models/akses.py` (beserta migrasinya)
  - `apps/cpns/admin.py`
  - `apps/cpns/penilaian.py`
- Test: `apps/cpns/tests/test_validasi.py`, `test_model_soal.py` (atau file tes model soal yang sudah ada), `test_dasbor.py`

**Interfaces:**
- Produces di `apps/cpns/validasi.py`:
  - `POIN_MAKS_BOBOT = 5`. `penilaian.py` mengimpornya dari sini, tidak lagi mendefinisikannya sendiri.
  - `SUBTES_PER_JENIS = {"SKD": ("TWK","TIU","TKP"), "SKB_GURU": ("PEDAGOGIK","MATERI_RPL")}`. `admin.py` mengimpornya dari sini, dan definisi di admin dihapus.
- `validasi_soal`:
  - Opsi, pembahasan, dan kunci yang bukan string (misalnya angka JSON) diubah ke `str` sebelum `.strip()`. `None` dianggap kosong.
  - Pesan bobot menjadi "Isi bobot TKP untuk opsi A sampai E dengan nilai 1, 2, 3, 4, 5 yang semuanya berbeda." (tanpa kata "kunci").
  - Validasi baru: `subtes` harus ada di `SUBTES_PER_JENIS[jenis_ujian]`. Kalau tidak, muncul pesan "Subtes {subtes} tidak cocok dengan jenis ujian {jenis}."
- `Soal.save()`: kalau `update_fields` diberikan dan memuat `"teks"`, tambahkan `"sidik_teks"` ke daftar itu.
- `Soal.hitung_sidik()`: method publik yang dipakai impor.
- `LaporanSoal`: `UniqueConstraint(fields=["soal","user"], condition=Q(status="baru"), name="satu_laporan_baru_per_user")`. View laporkan yang sudah ada menangkap `IntegrityError` lalu membalas pesan "sudah ada" yang sudah dipakai sekarang.

- [ ] **Step 1:** Buat branch dengan `git switch -c feat/cpns-hub-3`.
- [ ] **Step 2: Tulis tes yang gagal.**
  - `test_opsi_angka_diterima`: `opsi_a=85` dan seterusnya tidak menimbulkan error, kecuali kalau nilainya sama.
  - `test_pesan_bobot_tanpa_kata_kunci`
  - `test_subtes_tidak_cocok_jenis`: kombinasi SKD dan PEDAGOGIK menghasilkan pesan.
  - `test_update_fields_teks_ikut_sidik`: `s.teks="baru"; s.save(update_fields=["teks"])` lalu `refresh_from_db`, sehingga `sidik_teks == sidik_teks("baru")`.
  - `test_laporan_baru_ganda_ditolak_db`: dua `LaporanSoal(status="baru")` dengan soal dan user yang sama menghasilkan `IntegrityError`. Kalau yang pertama `selesai`, keduanya boleh ada.
  - `test_admin_dan_penilaian_pakai_konstanta_validasi`: `admin.SUBTES_PER_JENIS is validasi.SUBTES_PER_JENIS` dan `penilaian.POIN_MAKS_BOBOT is validasi.POIN_MAKS_BOBOT`.
- [ ] **Step 3:** Jalankan tes. Harus FAIL.
- [ ] **Step 4:** Implementasikan perubahan dan migrasinya.
- [ ] **Step 5:** Jalankan tes sampai PASS. Pastikan seluruh suite PASS dan `makemigrations --check` bersih.
- [ ] **Step 6:** Commit dengan pesan `refactor(cpns): rapikan validasi soal, sidik, dan laporan ganda`.

---

### Task 2: Snapshot Benar/Salah pada butir sesi

**Keputusan (diusulkan pengendali dan ditinjau pemilik bersama rencana ini):** hasil lama dibekukan.
- Status Benar/Salah dan poin setiap butir disimpan saat dinilai.
- Mengedit kunci, bobot, atau teks soal sesudahnya tidak mengubah hasil lama.
- Pembahasan di halaman hasil tetap menampilkan isi soal terkini.

**Files:**
- Modify:
  - `apps/cpns/models/sesi.py` (`SesiSoal.benar`), beserta migrasi skema dan migrasi data
  - `apps/cpns/penilaian.py`
  - `apps/cpns/views/belajar.py`
  - `apps/cpns/views/cat.py`
  - `apps/cpns/analitik.py`
- Test: `apps/cpns/tests/test_snapshot.py`

**Interfaces:**
- `SesiSoal.benar = models.BooleanField(null=True)`. Nilai `null` berarti belum dinilai.
- **Penilaian CAT:** `nilai_sesi(sesi)` mengisi `benar = adalah_benar(soal, jawaban)` untuk setiap butir. Butir kosong bernilai `False`. Nilai ini disimpan bersama `poin` dalam satu `bulk_update`.
- **Mode belajar:** `jawab_belajar` mengisi `benar` saat jawaban disimpan.
- **Halaman hasil:** label Benar/Salah memakai `butir.benar`. Kalau `None`, pakai `adalah_benar` sebagai cadangan.
- **Analitik:** `kelemahan_subtopik` juga memakai `butir.benar`, dengan cadangan yang sama.
- **Migrasi data:** mengisi `benar` untuk semua butir dari sesi `selesai` dan butir belajar yang sudah dijawab, memakai kunci saat migrasi dijalankan. Reverse-nya tidak melakukan apa-apa.

- [ ] **Step 1: Tulis tes yang gagal.**
  - `test_cat_benar_dibekukan`: kumpulkan CAT dengan jawaban benar, lalu ubah `kunci` soal. Halaman hasil tetap menampilkan "Benar" dan skor tidak berubah (Review Focus 4).
  - `test_belajar_benar_dibekukan`: jawab dengan benar, lalu ubah kunci. Ringkasan dan `kelemahan_subtopik` tetap menghitungnya benar.
  - `test_butir_kosong_benar_false`
  - `test_migrasi_isi_benar` memakai `MigrationExecutor`, atau langsung memanggil fungsi migrasi pada data buatan.
- [ ] **Step 2:** Jalankan tes. Harus FAIL.
- [ ] **Step 3:** Implementasikan.
- [ ] **Step 4:** Jalankan tes sampai PASS, lalu pastikan seluruh suite PASS.
- [ ] **Step 5:** Commit dengan pesan `feat(cpns): bekukan benar/salah butir saat dinilai`.

---

### Task 3: Kisi-kisi

**Files:**
- Create:
  - `docs/cpns/kisi-kisi.md`
  - `apps/cpns/kisi_kisi.py`
- Test: `apps/cpns/tests/test_kisi_kisi.py`

**Interfaces:**
- **Format `docs/cpns/kisi-kisi.md`:**
  - Baris pembuka "Draf, menunggu persetujuan pemilik."
  - Penjelasan singkat, lalu **satu tabel** berkolom `| Jenis | Subtes | Subtopik | Target |`, satu baris per subtopik.
  - Hanya tabel yang dibaca program.
- **Isi draf:**
  - **SKD:**
    - TWK: Pancasila, UUD 1945, Bhinneka Tunggal Ika, NKRI, Nasionalisme, Integritas, Bela Negara, Bahasa Negara
    - TIU: Analogi, Silogisme, Analitis, Deret Angka, Hitungan, Perbandingan Kuantitatif, Soal Cerita, Figural
    - TKP: Pelayanan Publik, Jejaring Kerja, Sosial Budaya, Teknologi Informasi dan Komunikasi, Profesionalisme, Anti Radikalisme
  - **SKB_GURU:**
    - PEDAGOGIK: Karakteristik Peserta Didik, Teori Belajar, Kurikulum Merdeka, Pembelajaran Berdiferensiasi, Asesmen, Pemanfaatan TIK
    - MATERI_RPL: Algoritma dan Pemrograman, Basis Data, Pemrograman Web, Pemrograman Berorientasi Objek, Jaringan Dasar, Rekayasa Perangkat Lunak
  - **Target awal per subtopik:** 60 untuk TWK dan TIU, 75 untuk TKP, dan 50 untuk SKB. Semua angka ditandai sebagai usulan yang bisa diubah pemilik.
  - **Catatan sumber:** subtopik SKD mengikuti pembagian umum materi SKD. Ambang dan komposisi resmi menunggu nomor KepmenPAN-RB dari pemilik (spesifikasi §15).
- **`apps/cpns/kisi_kisi.py`:**
  - `@dataclass(frozen=True) class Subtopik: jenis_ujian: str; subtes: str; nama: str; target: int`
  - `baca_kisi_kisi(path: Path | None = None) -> list[Subtopik]`. Bawaannya membaca `settings.BASE_DIR / "docs/cpns/kisi-kisi.md"`.
  - Baris tabel yang tidak valid (subtes tidak dikenal, target bukan angka positif, atau jenis dan subtes tidak cocok menurut `SUBTES_PER_JENIS`) melempar `ValueError` berisi nomor barisnya.
  - File yang tidak ada menghasilkan list kosong.

- [ ] **Step 1: Tulis tes yang gagal.**
  - `test_baca_kisi_kisi_repo`: file di repo terbaca, dan setiap subtes dari kelima subtes punya minimal 1 subtopik.
  - `test_baris_tidak_valid_menyebut_nomor` memakai file sementara.
  - `test_file_hilang_list_kosong`
- [ ] **Step 2:** Jalankan tes. Harus FAIL.
- [ ] **Step 3:** Implementasikan dan tulis dokumen kisi-kisi.
- [ ] **Step 4:** Jalankan tes sampai PASS.
- [ ] **Step 5:** Commit dengan pesan `feat(cpns): draf kisi-kisi dan pembacanya`.

---

### Task 4: Impor batch soal

**Files:**
- Create:
  - `apps/cpns/impor.py`
  - `apps/cpns/management/commands/cpns_impor_soal.py`
  - `docs/cpns/format-batch.md`
  - `apps/cpns/tests/data/batch_contoh.json` (5 soal contoh: 2 TIU, 1 TWK, 1 TKP, 1 MATERI_RPL)
- Delete: `apps/cpns/management/commands/seed_cpns_starter.py`, `import_cpns.py`, `scrape_cpns.py`. Command lama ini menulis ke tabel lama dan memuat kata "Resmi".
- Test: `apps/cpns/tests/test_impor.py`

**Interfaces:**
- **Format batch:** sebuah list objek berisi field `Soal` berikut:
  - wajib: `jenis_ujian`, `subtes`, `subtopik`, `teks`, `opsi_a` sampai `opsi_e`, `pembahasan_konsep`, `pembahasan_pengecoh`, `pembahasan_cepat`
  - salah satu dari `kunci` atau `bobot`
  - opsional: `tingkat`, `rujukan`, `perlu_cek`, `sumber` (bawaan `draf_ai`)

  Nama batch diambil dari nama file tanpa `.json`. Field yang tidak dikenal ditolak supaya salah ketik ketahuan.
- **Hasil:** `@dataclass class HasilImpor: masuk: list[int]; gagal: list[tuple[int, list[str]]]` (nomor baris mulai dari 1, lalu daftar pesan).
- **`impor_batch(data: list, batch: str, coba: bool = False) -> HasilImpor`.** Aturan per baris:
  1. Jalankan `validasi_soal`.
  2. `subtopik` harus terdaftar di kisi-kisi untuk subtes itu. Kalau kisi-kisi kosong, pemeriksaan ini dilewati.
  3. Soal TWK dengan `rujukan` kosong wajib `perlu_cek=true`. Kalau tidak, muncul pesan "Soal TWK tanpa rujukan harus diberi perlu_cek=true. Jangan mengarang rujukan."
  4. `sidik_teks` tidak boleh sama dengan baris lain di file yang sama, atau dengan soal mana pun di database.

  Semua baris yang lolos disimpan sebagai `draf` dalam **satu** `transaction.atomic()`. Kalau `coba=True`, tidak ada yang disimpan. Baris yang gagal tidak disimpan.
- **Command `cpns_impor_soal <file> [--coba]`:**
  - Mencetak "Masuk: N soal (draf). Gagal: M baris." diikuti satu baris per kegagalan dengan format `Baris 3: <pesan>; <pesan>`.
  - Exit code 1 kalau ada baris yang gagal.
  - File yang tidak ada atau JSON yang rusak menghasilkan `CommandError` berbahasa Indonesia.
- **`docs/cpns/format-batch.md`:** lokasi file batch `data/cpns/batch/<nama-batch>.json` (contoh nama `2026-11-tiu-deret-01`), contoh 1 soal TIU dan 1 soal TKP, daftar field, aturan rujukan TWK, dan perintah impor. Dokumen ini dipakai sesi penulis draf.

- [ ] **Step 1: Tulis tes yang gagal.**
  - `test_impor_contoh_masuk_sebagai_draf`
  - `test_opsi_angka_json_diterima` (Review Focus 3)
  - `test_ganda_dalam_file_ditolak_dengan_baris` (Review Focus 3)
  - `test_sama_dengan_bank_ditolak` (Review Focus 3), termasuk soal berstatus `ditolak`
  - `test_twk_tanpa_rujukan_wajib_perlu_cek`
  - `test_subtopik_di_luar_kisi_kisi_ditolak`
  - `test_field_tak_dikenal_ditolak`
  - `test_coba_tidak_menyimpan`
  - `test_command_kode_keluar_dan_ringkasan`
  - `test_command_file_rusak`
  - `test_command_lama_sudah_dihapus`: `call_command("import_cpns")` melempar `CommandError` "Unknown command".
- [ ] **Step 2:** Jalankan tes. Harus FAIL.
- [ ] **Step 3:** Implementasikan.
- [ ] **Step 4:** Jalankan tes sampai PASS, lalu pastikan seluruh suite PASS.
- [ ] **Step 5:** Commit dengan pesan `feat(cpns): impor batch soal dan hapus command lama`.

---

### Task 5: Halaman Tinjau Soal

**Files:**
- Create:
  - `apps/cpns/views/kelola.py`
  - `templates/cpns/kelola/base_kelola.html`
  - `templates/cpns/kelola/tinjau.html`
- Modify: `apps/cpns/urls.py`, `apps/cpns/views/__init__.py`
- Test: `apps/cpns/tests/test_kelola_tinjau.py`

**Interfaces:**
- **Akses:** decorator `wajib_superuser`. Tamu diarahkan ke `cpns:masuk?next=...`. Yang bukan superuser mendapat 403.
- **Rute:**
  - `kelola/` mengalihkan ke `cpns:kelola_tinjau`
  - `kelola/tinjau/` diberi nama `kelola_tinjau`
  - `kelola/tinjau/<int:soal_id>/` diberi nama `kelola_tinjau_soal`
  - `kelola/tinjau/<int:soal_id>/aksi/` (POST) diberi nama `kelola_aksi`
- **`base_kelola.html`** (mengikuti mockup 08):
  - Header "CPNS Hub · Admin" dengan nav: Tinjau Soal, Cakupan Bank Soal, Laporan Soal (jumlah laporan `baru`), Voucher (`admin:cpns_voucher_changelist`), Pengaturan (Django Admin, `admin:index`).
  - Menu "Menu" muncul di bawah lebar 1024 px.
- **Antrean tinjau:**
  - Filter GET: `status` (bawaan `draf`), `subtes`, `subtopik`, `batch`.
  - Urutan: `batch`, lalu `dibuat_pada`, lalu `id`.
  - `kelola_tinjau` menampilkan soal pertama di antrean, atau keadaan kosong "Tidak ada soal di antrean ini." beserta tautan ke Cakupan.
- **Isi halaman soal** (mengikuti mockup):
  - Baris meta: "Soal X dari Y di batch ini", subtes, subtopik, tingkat, sumber.
  - Teks dan opsi. Kunci ditandai dengan teks "Kunci", atau bobot ditampilkan per opsi untuk TKP.
  - Panel "Pemeriksaan otomatis": hasil `validasi_soal(..., untuk_tayang=False)` per syarat, ditambah "Tidak mirip soal lain di bank" berdasarkan `sidik_teks` yang sama dengan soal lain.
  - Lencana "Perlu cek fakta" kalau `perlu_cek`.
  - Pembahasan tiga bagian dan rujukan.
  - Penghitung "Hari ini: N ditinjau · Draf tersisa: M". N adalah soal dengan `ditinjau_pada` hari ini (zona waktu lokal) oleh user ini.
- **Aksi POST** dengan field `aksi` (`setujui` | `tolak` | `lewati`), `status_awal`, `alasan`, dan query filter yang dibawa:
  - `setujui`:
    - Isi `ditinjau_oleh` dan `ditinjau_pada`, `status="tayang"`, lalu `full_clean()`.
    - Kalau gagal validasi: status tetap, dan pesan error ditampilkan di halaman soal yang sama.
  - `tolak`:
    - `alasan` wajib diisi. Kalau kosong, muncul pesan "Tulis alasan penolakan."
    - `status="ditolak"`, `catatan_tinjau=alasan`, isi peninjau dan waktunya.
  - `lewati`: tidak mengubah apa pun, langsung ke soal berikutnya.
  - **Konflik (Review Focus 1):**
    - Diproses dengan `select_for_update` dalam `atomic`.
    - Kalau `soal.status != status_awal`, tidak ada perubahan. Pesan "Soal ini sudah diubah di tab lain. Muat ulang untuk melihat keadaan terbaru." ditampilkan, dan halaman tetap di soal itu.
  - Setelah aksi berhasil, redirect ke soal berikutnya di antrean filter yang sama. Kalau habis, ke keadaan kosong.
- **Keyboard:**
  - `S` untuk Setujui, `E` untuk Edit (tautan ke Task 6), `T` untuk memfokuskan kolom alasan, `→` untuk Lewati.
  - Alpine dengan `@keydown.window`. Abaikan modifier, dan abaikan kalau target berupa input, textarea, atau select (Review Focus 2).
  - Tombol menampilkan huruf pintasannya seperti di mockup.
  - Kolom alasan diberi `aria-label="Alasan tolak"`.

- [ ] **Step 1: Tulis tes yang gagal.**
  - `test_tamu_ke_masuk_non_superuser_403`
  - `test_antrean_bawaan_draf_dan_filter`
  - `test_setujui_menayangkan_dan_isi_peninjau`
  - `test_setujui_soal_tidak_valid_tetap_draf_dengan_pesan`
  - `test_tolak_wajib_alasan`
  - `test_tolak_menyimpan_catatan`
  - `test_lewati_ke_berikutnya`
  - `test_konflik_tab_lain` (Review Focus 1)
  - `test_penghitung_hari_ini_dan_tersisa`
  - `test_pemeriksaan_mirip_soal_lain`
  - `test_markup_pintasan_abaikan_input`: `tinjau.html` memuat pemeriksaan tagName input, textarea, dan select serta ctrl, meta, dan alt.
  - `test_keadaan_kosong`
- [ ] **Step 2:** Jalankan tes. Harus FAIL.
- [ ] **Step 3:** Implementasikan, lalu build CSS.
- [ ] **Step 4:** Jalankan tes sampai PASS, lalu pastikan seluruh suite PASS.
- [ ] **Step 5:** Commit dengan pesan `feat(cpns): halaman tinjau soal`.

---

### Task 6: Edit soal dari halaman tinjau

**Files:**
- Create: `templates/cpns/kelola/ubah_soal.html`, `SoalForm` (di `apps/cpns/views/kelola.py` atau `apps/cpns/forms.py`)
- Modify: `apps/cpns/urls.py`
- Test: `apps/cpns/tests/test_kelola_ubah.py`

**Interfaces:**
- **Rute:** `kelola/soal/<int:soal_id>/ubah/` (GET dan POST) diberi nama `kelola_ubah`. Filter antrean dibawa lewat query.
- **`SoalForm`:**
  - ModelForm dengan field: `subtes`, `subtopik`, `tingkat`, `teks`, `opsi_a` sampai `opsi_e`, `kunci`, `bobot_a` sampai `bobot_e` (angka, hanya untuk TKP), tiga pembahasan, `rujukan`, `perlu_cek`.
  - `jenis_ujian` hanya ditampilkan, tidak bisa diubah.
  - Validasi memakai `validasi_soal`. Untuk soal `tayang` dipakai `untuk_tayang=True`.
  - Pesan error tampil per field atau di bagian atas formulir.
- **Simpan:**
  - **Soal draf** tetap `draf`.
  - **Soal tayang** tetap `tayang`, dan `ditinjau_oleh` serta `ditinjau_pada` diperbarui ke pengedit.
  - **Soal ditolak** kembali ke `draf` lewat kotak centang "Kembalikan ke draf". Kalau tidak dicentang, tetap `ditolak`.
- **Edit tidak valid:** tidak ada yang tersimpan (Review Focus 4).
- **Setelah simpan:** redirect ke `kelola_tinjau_soal` untuk soal yang sama dengan pesan "Perubahan disimpan."

- [ ] **Step 1: Tulis tes yang gagal.**
  - `test_ubah_draf_tersimpan`
  - `test_ubah_tidak_valid_tidak_menyimpan`
  - `test_ubah_tayang_tetap_tayang_peninjau_diperbarui`
  - `test_ubah_tayang_tidak_mengubah_hasil_lama` (memakai snapshot dari Task 2)
  - `test_bobot_tkp_lewat_form`
  - `test_akses_non_superuser_403`
- [ ] **Step 2:** Jalankan tes. Harus FAIL.
- [ ] **Step 3:** Implementasikan, lalu build CSS.
- [ ] **Step 4:** Jalankan tes sampai PASS, lalu pastikan seluruh suite PASS.
- [ ] **Step 5:** Commit dengan pesan `feat(cpns): edit soal dari halaman tinjau`.

---

### Task 7: Halaman Cakupan

**Files:**
- Create:
  - `apps/cpns/cakupan.py`
  - `templates/cpns/kelola/cakupan.html`
- Modify: `apps/cpns/views/kelola.py`, `apps/cpns/urls.py`
- Test: `apps/cpns/tests/test_cakupan.py`

**Interfaces:**
- `hitung_cakupan() -> dict` dengan dua kunci:
  - **`baris`:** list dict berisi `jenis_ujian`, `subtes`, `subtopik`, `target`, `tayang`, `draf`, `kurang`.
    - Gabungan subtopik dari kisi-kisi dan subtopik yang sudah ada di database.
    - Subtopik yang tidak ada di kisi-kisi diberi `target=None`.
    - `kurang = max(target - tayang, 0)`.
  - **`skema`:** list dict berisi `kode`, `nama`, `aktif`, `cukup_untuk`.
    - `cukup_untuk` adalah nilai terkecil dari `tayang_subtes // jumlah_soal` di antara semua bagian skema.
    - Bagian dengan `jumlah_soal == 0` dilewati. Skema tanpa bagian bernilai 0.
- **Rute:** `kelola/cakupan/` diberi nama `kelola_cakupan`.
- **Isi halaman:**
  - Tabel per subtes dengan kolom Target, Tayang, Draf, dan Kurang.
  - Kolom Kurang diberi teks "Kurang N" atau "Cukup", jadi tidak hanya ditandai warna.
  - Setiap baris bertaut ke Tinjau dengan filter subtopik itu.
  - Di atas tabel, kartu per skema: "Cukup untuk N simulasi tanpa soal berulang".

- [ ] **Step 1: Tulis tes yang gagal.**
  - `test_cakupan_bank_kosong` (Review Focus 5)
  - `test_cukup_untuk_minimum_bagian`
  - `test_jumlah_soal_nol_tidak_error` (Review Focus 5)
  - `test_subtopik_di_luar_kisi_kisi_tampil_tanpa_target`
  - `test_halaman_cakupan_superuser_saja`
- [ ] **Step 2:** Jalankan tes. Harus FAIL.
- [ ] **Step 3:** Implementasikan, lalu build CSS.
- [ ] **Step 4:** Jalankan tes sampai PASS, lalu pastikan seluruh suite PASS.
- [ ] **Step 5:** Commit dengan pesan `feat(cpns): halaman cakupan bank soal`.

---

### Task 8: Antrean Laporan Soal

**Files:**
- Create: `templates/cpns/kelola/laporan.html`
- Modify: `apps/cpns/views/kelola.py`, `apps/cpns/urls.py`
- Test: `apps/cpns/tests/test_kelola_laporan.py`

**Interfaces:**
- **Rute:**
  - `kelola/laporan/` diberi nama `kelola_laporan`. Filter `status` bawaannya `baru`.
  - `kelola/laporan/<int:laporan_id>/selesai/` (POST) diberi nama `kelola_laporan_selesai`.
- **Daftar laporan:**
  - Setiap baris memuat: tanggal, alasan (label), catatan, potongan teks soal, status soal, dan nama tampilan pelapor (`first_name` atau username, **tanpa email**).
  - Tautan "Tinjau soal ini" mengarah ke `kelola_tinjau_soal`, dan tombol "Tandai selesai".
  - Laporan untuk soal yang sama dikelompokkan dengan jumlahnya.
- **Keadaan kosong:** "Belum ada laporan baru."
- **Tandai selesai:** mengubah status laporan menjadi `selesai`, lalu redirect kembali ke daftar dengan filter yang sama.
- **Jumlah di nav:** jumlah laporan `baru` tampil di nav `base_kelola.html` (sudah disiapkan di Task 5).

- [ ] **Step 1: Tulis tes yang gagal.**
  - `test_daftar_laporan_baru`
  - `test_tanpa_email_pelapor`
  - `test_tandai_selesai`
  - `test_kelompok_per_soal`
  - `test_nav_menampilkan_jumlah`
  - `test_akses_superuser_saja`
- [ ] **Step 2:** Jalankan tes. Harus FAIL.
- [ ] **Step 3:** Implementasikan, lalu build CSS.
- [ ] **Step 4:** Jalankan tes sampai PASS, lalu pastikan seluruh suite PASS.
- [ ] **Step 5:** Commit dengan pesan `feat(cpns): antrean laporan soal`.

---

### Task 9: Verifikasi browser dan Delivery Gate antislop (pengendali)

**Files:**
- Create: `anti-slop/audit-005-<tanggal>.md`

- [ ] **Step 1: Siapkan data lokal.** Impor `apps/cpns/tests/data/batch_contoh.json` ke database lokal dengan `cpns_impor_soal --coba`, lalu impor sungguhan. Buat 2 laporan soal dari akun peserta uji.
- [ ] **Step 2: Coba alur di lebar 375, 768, dan 1280 px.** Urutannya:
  1. Tinjau → Setujui (S) → Tolak tanpa alasan (pesan muncul) → Tolak dengan alasan → Lewati (→) → Edit (E) → simpan.
  2. Konflik dua tab.
  3. Cakupan → tautan ke Tinjau.
  4. Laporan → Tinjau soal ini → Tandai selesai.

  Untuk setiap layar, cek: tidak ada overflow, tidak ada target di bawah 44 px, dan konsol bersih.
- [ ] **Step 3: Uji keyboard.** Mengetik "set" di kolom alasan tidak memicu pintasan, dan Ctrl+S tidak menyetujui.
- [ ] **Step 4:** Tulis laporan Delivery Gate dengan bukti per butir.
- [ ] **Step 5:** Commit dengan pesan `docs(cpns): laporan verifikasi rencana 3`. **Tidak di-deploy.**
