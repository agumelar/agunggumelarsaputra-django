# CPNS Hub Rencana 2: Akun Publik, Premium, dan Voucher

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Membuka CPNS Hub untuk umum. Isinya pendaftaran dan masuk khusus cpns (email/kata sandi dan Google), pemisahan peserta dari situs sekolah, beranda publik, Syarat Layanan dan Kebijakan Privasi, halaman Premium dengan tombol WhatsApp, penukaran kode voucher, panel admin voucher/skema/paket/pengaturan, ringkasan subtopik lemah untuk premium, serta perapian sebelum deploy dari catatan Rencana 1.

**Architecture:**
- Model baru `PengaturanCPNS`, `Voucher`, `PercobaanVoucher` di `apps/cpns/models/premium.py`. Layanan murni ada di `apps/cpns/voucher.py` dan `apps/cpns/analitik.py`.
- View tipis di `apps/cpns/views/akun.py`, `publik.py`, dan `premium.py`.
- Middleware `PesertaHanyaCpnsMiddleware` menjaga situs sekolah.
- Panel admin memakai Django Admin dengan view tambahan untuk membuat voucher massal.

**Tech Stack:** Python 3.12, Django 5.1, HTMX 2.0.4, Alpine.js 3.14.8, Tailwind CSS 3.4 (`npm run build:css`, `output.css` ikut di-commit).

**Spec:** `docs/superpowers/specs/2026-11-07-cpns-hub-design.md` (bagian 3.5, 3.6, 4, 7, 9, 11). Catatan bawaan: `docs/superpowers/plans/2026-11-07-cpns-hub-rencana-1-catatan.md`. Mockup: `design/png/01-beranda.png`, `02-masuk.png`, `03-dasbor-trial.png`, `07-premium-voucher.png`.

**Di luar rencana ini:**
- **Rencana 3:** impor soal, Tinjau Soal, Cakupan, antrean Laporan, kisi-kisi.
- **Rencana 4:** data lama, pengalihan 301, keamanan produksi, deploy.

Server **tetap tidak di-deploy** selama Rencana 2 dikerjakan.

## Global Constraints

- **Branch:** semua task dikerjakan di branch `feat/cpns-hub-2`, dibuat dari `master` lokal.
- **Git:** stage dengan path eksplisit, tidak pernah `git add -A`.
- **Menjalankan tes:** `.venv/Scripts/python.exe manage.py test <label>`. Seluruh suite harus lolos di akhir setiap task.
- **Teks UI** berbahasa Indonesia sederhana. Dilarang memakai: em dash, emoji, kata "resmi", "soal asli BKN", titik berkedip dekoratif, dan angka atau testimoni karangan. Placeholder ditulis apa adanya dalam kurung siku, misalnya `[KEBIJAKAN PENGEMBALIAN DANA]`.
- **Warna dan font** mengikuti `DESIGN.md`:
  - latar `#090D16`; permukaan `#111827` / `#162032` / `#1C293E`
  - garis `rgba(255,255,255,0.08)` dan `0.14`
  - teks `#F3F4F6` / `#CBD5E1` / `#94A3B8`
  - aksen tunggal sky `#38BDF8`, teks di atasnya `#082F49`
  - sukses `#34D399`, bahaya `#F87171`, premium `#FBBF24`
  - font Outfit / Inter / JetBrains Mono
- **Aksesibilitas:** target sentuh minimal 44 px (`min-h-11`). Fokus terlihat. Escape menutup dialog. Status tidak boleh hanya ditandai warna. Formulir punya label.
- **Alamat:** semua tautan dan redirect memakai `reverse`/`{% url %}` (awalan `/cpns/` di domain utama harus tetap jalan). Tautan ke host cpns dari situs utama memakai `settings.CPNS_URL`.
- **Voucher:**
  - format `XXXX-XXXX` dari alfabet `ABCDEFGHJKMNPQRSTUVWXYZ23456789` (tanpa 0, O, 1, I, L), dibuat dengan `secrets`
  - sekali pakai; masa aktif baru = `max(sekarang, premium_sampai) + durasi_hari`
  - maksimal 5 percobaan gagal per user per jam
- **Peserta:**
  - daftar atau login Google pertama kali di host cpns membuat user `role='peserta'`, tanpa XP
  - login Google di host cpns mengisi `AksesPeserta.via_google=True`
  - peserta yang membuka situs sekolah diarahkan ke `CPNS_URL`
- **CSS:** task yang menambah kelas Tailwind menjalankan `npm run build:css` dan `collectstatic --noinput`, lalu meng-commit `static/css/output.css`.

## Review Focus

1. **Email yang sudah terdaftar sebagai siswa dipakai untuk mendaftar di cpns.** Pendaftaran ditolak dengan pesan "Email ini sudah terdaftar. Silakan masuk.", dan akun siswa tidak berubah peran. Diuji di Task 4.
2. **Dua tab menukar kode voucher yang sama pada waktu bersamaan.** Hanya satu yang berhasil, dan masa premium tidak bertambah dua kali. Diuji di Task 2 (kunci baris) dan Task 7.
3. **Kode diketik dengan huruf kecil, spasi, atau tanpa tanda hubung.** Kode tetap diterima. Diuji di Task 2.
4. **Peserta membuka `/cpns/...` di domain utama atau logout di domain utama.** Tidak terjebak redirect berulang. Diuji di Task 5.
5. **Pengaturan harga atau nomor WhatsApp masih kosong.** Halaman Premium dan Beranda tetap tampil dengan teks jujur, tanpa tautan WhatsApp yang rusak. Diuji di Task 6 dan Task 7.

---

## Peta file

```
apps/cpns/models/premium.py              (baru)  PengaturanCPNS, Voucher, PercobaanVoucher
apps/cpns/models/skema.py                (ubah)  SkemaUjian.urutan + ordering
apps/cpns/voucher.py                     (baru)  buat_kode, buat_voucher, normalisasi_kode, pakai_voucher, sisa_percobaan, VoucherDitolak
apps/cpns/analitik.py                    (baru)  kelemahan_subtopik
apps/cpns/admin.py                       (ubah)  admin skema, paket, pengaturan, voucher (+ view buat massal)
apps/cpns/middleware.py                  (ubah)  PesertaHanyaCpnsMiddleware
apps/cpns/views/_bantu.py                (ubah)  wajib_masuk
apps/cpns/views/akun.py                  (baru)  masuk, daftar
apps/cpns/views/publik.py                (baru)  beranda_publik, syarat, privasi
apps/cpns/views/premium.py               (baru)  premium, tukar_voucher
apps/accounts/views.py                   (ubah)  callback Google sadar host cpns
config/settings/base.py                  (ubah)  CPNS_URL, middleware
templates/cpns/akun/*, publik/*, premium/*, admin/cpns/voucher/*   (baru)
```

---

### Task 1: Model premium dan urutan skema

**Files:**
- Create: `apps/cpns/models/premium.py` dan migrasinya
- Modify: `apps/cpns/models/skema.py` (`SkemaUjian.urutan`), `apps/cpns/models/__init__.py`
- Create: migrasi data yang mengisi `urutan` SKD-CAT=1 dan SKB-GURU-LATIHAN=2
- Test: `apps/cpns/tests/test_model_premium.py`

**Interfaces:**
- Produces: `PengaturanCPNS`
  - field: `nomor_wa` CharField(20, blank), `teks_harga` JSONField(default=dict) yang memetakan durasi hari (string) ke teks harga, misalnya `{"30": "Rp49.000"}`, dan `pesan_wa` TextField
  - nilai bawaan `pesan_wa`: `"Halo Admin CPNS Hub, saya ingin membeli Premium {durasi} hari. Email akun saya: {email}"`
  - `PengaturanCPNS.ambil() -> PengaturanCPNS` (get_or_create pk=1)
  - `durasi_tersedia() -> list[int]` (kunci `teks_harga` yang berupa angka, diurutkan naik)
  - `tautan_wa(durasi: int, email: str) -> str | None`: `https://wa.me/<nomor_wa digit saja>?text=<pesan_wa terisi, url-encoded>`, atau `None` kalau `nomor_wa` kosong
- Produces: `Voucher`
  - field: `kode` CharField(9, unique), `durasi_hari` PositiveIntegerField, `catatan` CharField(200, blank)
  - `dibuat_oleh` FK user null SET_NULL related_name `voucher_dibuat`, `dibuat_pada` auto_now_add
  - `dipakai_oleh` FK user null SET_NULL related_name `voucher_dipakai`, `dipakai_pada` null
  - `dibatalkan` bool default False; ordering `['-dibuat_pada']`
  - property `status -> str` bernilai `'dibatalkan' | 'dipakai' | 'belum_dipakai'`
- Produces: `PercobaanVoucher`
  - field: `user` FK CASCADE related_name `percobaan_voucher`, `waktu` DateTimeField(default=timezone.now, db_index=True), `berhasil` bool
- Produces: `SkemaUjian.urutan` PositiveSmallIntegerField(default=0); Meta ordering `['urutan', 'kode']`

- [ ] **Step 1:** Buat branch: `git switch -c feat/cpns-hub-2`
- [ ] **Step 2: Tulis tes yang gagal:**
  - `test_pengaturan_ambil_satu_baris`: `ambil()` dua kali menghasilkan pk yang sama, dan `count() == 1`
  - `test_tautan_wa_kosong_bila_nomor_kosong`
  - `test_tautan_wa_terisi`:
    - `nomor_wa="+62 812-3456"` menghasilkan tautan berawalan `https://wa.me/628123456?text=`
    - teks memuat `Premium 30 hari` dan email (sudah url-encoded)
  - `test_durasi_tersedia_urut`: `teks_harga={"90":"x","30":"y","abc":"z"}` menghasilkan `[30, 90]`
  - `test_status_voucher`: untuk ketiga status
  - `test_kode_voucher_unik`: kode ganda melempar `IntegrityError`
  - `test_skema_skd_lebih_dulu`: `list(SkemaUjian.objects.values_list('kode', flat=True))[:2] == ['SKD-CAT', 'SKB-GURU-LATIHAN']`
- [ ] **Step 3:** Jalankan tesnya. Hasil yang diharapkan: FAIL.
- [ ] **Step 4:** Implementasikan model, migrasi, dan migrasi data `urutan`.
- [ ] **Step 5:** Jalankan tes PASS, seluruh suite PASS, dan `makemigrations --check` bersih.
- [ ] **Step 6:** Commit `feat(cpns): model pengaturan, voucher, urutan skema`.

---

### Task 2: Layanan voucher

**Files:**
- Create: `apps/cpns/voucher.py`
- Test: `apps/cpns/tests/test_voucher.py`

**Interfaces:**
- Produces:
  - `ALFABET = "ABCDEFGHJKMNPQRSTUVWXYZ23456789"`
  - `BATAS_GAGAL_PER_JAM = 5`
  - `class VoucherDitolak(Exception)` dengan atribut `alasan` (`'tidak_valid' | 'terlalu_sering'`) dan `sisa` (int)
- Produces: `buat_kode() -> str` dengan format `XXXX-XXXX`
- Produces: `buat_voucher(jumlah: int, durasi_hari: int, catatan: str = "", oleh=None) -> list[Voucher]`
  - `ValueError` kalau `jumlah` tidak di 1..100 atau `durasi_hari` < 1
  - kode yang bentrok dibuat ulang
- Produces: `normalisasi_kode(teks: str) -> str`
  - huruf besar, buang spasi dan tanda hubung; kalau hasilnya 8 karakter, sisipkan `-` di tengah; selain itu kembalikan apa adanya
- Produces: `sisa_percobaan(user, now=None) -> int`
  - `5 -` jumlah `PercobaanVoucher(berhasil=False)` user ini dalam 1 jam terakhir, minimal 0
- Produces: `pakai_voucher(user, kode: str, now=None) -> AksesPeserta`, dengan urutan:
  1. Kalau `sisa_percobaan` sudah 0, lempar `VoucherDitolak('terlalu_sering', 0)` tanpa mencatat percobaan.
  2. `normalisasi_kode`.
  3. Di dalam `transaction.atomic()`: `Voucher.objects.select_for_update().filter(kode=..., dibatalkan=False, dipakai_oleh__isnull=True).first()`.
  4. Kalau tidak ada: catat `PercobaanVoucher(berhasil=False)` lalu lempar `VoucherDitolak('tidak_valid', sisa_setelahnya)`.
  5. Kalau ada:
     - isi `dipakai_oleh` dan `dipakai_pada`
     - `AksesPeserta` dikunci (`select_for_update`, dibuat kalau belum ada)
     - `premium_sampai = max(now, premium_sampai or now) + timedelta(days=durasi_hari)`
     - catat percobaan berhasil, lalu kembalikan akses

- [ ] **Step 1: Tulis tes yang gagal:**
  - `test_format_kode`: 200 kode cocok dengan `^[A-HJKMNP-Z2-9]{4}-[A-HJKMNP-Z2-9]{4}$`
  - `test_buat_voucher_jumlah_dan_validasi`: `buat_voucher(3, 30)` menghasilkan 3 baris; `buat_voucher(0, 30)` dan `buat_voucher(1, 0)` melempar `ValueError`
  - `test_normalisasi`: `" k7pm 3qxr "` dan `"k7pm-3qxr"` keduanya menjadi `"K7PM-3QXR"` (Review Focus 3)
  - `test_pakai_mulai_dari_sekarang`: user tanpa premium, voucher 30 hari, sehingga `premium_sampai == now + 30 hari`
  - `test_pakai_menambah_masa_aktif`: premium sampai `now + 10 hari`, voucher 30 hari, sehingga `premium_sampai == now + 40 hari`
  - `test_voucher_sekali_pakai`: pemakaian kedua oleh user lain melempar `VoucherDitolak` dengan alasan `tidak_valid`, dan `premium_sampai` user kedua tidak berubah
  - `test_voucher_dibatalkan_ditolak`
  - `test_batas_lima_gagal`:
    - 5 kode salah menghasilkan `sisa` 4, 3, 2, 1, 0
    - percobaan keenam melempar `terlalu_sering` dan tidak menambah baris percobaan
    - setelah `now + 61 menit`, user bisa mencoba lagi
  - `test_berhasil_tidak_mengurangi_sisa`
- [ ] **Step 2:** Jalankan tesnya. Hasil yang diharapkan: FAIL.
- [ ] **Step 3:** Implementasikan.
- [ ] **Step 4:** Jalankan tesnya. Hasil yang diharapkan: PASS.
- [ ] **Step 5:** Commit `feat(cpns): layanan voucher premium`.

---

### Task 3: Panel admin (Django Admin)

**Files:**
- Modify: `apps/cpns/admin.py` (admin lama untuk model legacy tetap ada)
- Create: `templates/admin/cpns/voucher/change_list.html` (tambah tombol "Buat kode voucher"), `templates/admin/cpns/voucher/buat_banyak.html`
- Test: `apps/cpns/tests/test_admin_cpns.py`

**Interfaces:**
- **VoucherAdmin:**
  - `list_display = ('kode','durasi_hari','status_teks','catatan','dipakai_oleh','dipakai_pada','dibuat_pada')`
  - filter status (belum dipakai / dipakai / dibatalkan); `search_fields = ('kode','catatan','dipakai_oleh__email')`
  - semua field read-only kecuali `catatan` dan `dibatalkan`; `has_add_permission` False (pembuatan lewat view massal)
  - aksi "Batalkan kode yang belum dipakai" (hanya mengubah yang statusnya `belum_dipakai`)
  - URL tambahan `buat-banyak/` (name `admin:cpns_voucher_buat_banyak`):
    - form berisi `jumlah` (1..100), `durasi_hari` (pilihan dari `PengaturanCPNS.ambil().durasi_tersedia()`, ditambah isian angka lain), dan `catatan`
    - setelah POST, menampilkan halaman hasil dengan `<textarea readonly>` berisi kode satu per baris, siap disalin ke WhatsApp
- **SkemaUjianAdmin** dengan inline `SkemaBagian`:
  - form inline menolak subtes yang tidak cocok dengan jenis ujian: SKD hanya TWK/TIU/TKP; SKB_GURU hanya PEDAGOGIK/MATERI_RPL
  - menolak `ambang_batas` di atas nilai maksimal (`jumlah_soal * poin_benar`, atau `* 5` untuk bobot)
- **PaketBelajarAdmin** dengan inline `PaketSoal` (`raw_id_fields=('soal',)`), dan kolom daftar `jumlah_tayang` (jumlah soal berstatus `tayang`)
- **PengaturanCPNSAdmin:** `has_add_permission` hanya kalau belum ada baris; `has_delete_permission` False

- [ ] **Step 1: Tulis tes yang gagal** (superuser lewat `Client.force_login`):
  - `test_buat_banyak_menghasilkan_kode`: POST `jumlah=3, durasi_hari=30` menghasilkan 3 voucher, dan halaman hasil memuat ketiga kodenya
  - `test_buat_banyak_tolak_jumlah_101`
  - `test_aksi_batalkan_hanya_yang_belum_dipakai`
  - `test_bagian_subtes_tidak_cocok_ditolak`: SKD dengan bagian PEDAGOGIK menghasilkan error form
  - `test_bagian_ambang_melebihi_maks_ditolak`
  - `test_pengaturan_tidak_bisa_ditambah_dua`
  - `test_non_staff_tidak_bisa_buka`
- [ ] **Step 2:** Jalankan tesnya. Hasil yang diharapkan: FAIL.
- [ ] **Step 3:** Implementasikan.
- [ ] **Step 4:** Jalankan tesnya. Hasil yang diharapkan: PASS.
- [ ] **Step 5:** Commit `feat(cpns): admin voucher, skema, paket, pengaturan`.

---

### Task 4: Daftar dan masuk peserta

**Files:**
- Create: `apps/cpns/views/akun.py`, `templates/cpns/akun/masuk.html` (layar 02), `templates/cpns/akun/daftar.html`
- Modify:
  - `apps/cpns/views/_bantu.py`: `wajib_masuk = login_required(login_url='cpns:masuk')`; semua view cpns yang sekarang memakai `login_required` beralih ke `wajib_masuk`
  - `apps/cpns/urls.py`
  - `apps/accounts/views.py`: callback Google
  - `templates/cpns/base_cpns.html`: tamu melihat tombol "Masuk", user login melihat "Keluar" (POST ke `accounts:logout` kalau view itu meminta POST; ikuti yang ada)
- Test: `apps/cpns/tests/test_akun.py`

**Interfaces:**
- Route:
  - `masuk/` → `masuk` (name `masuk`)
  - `daftar/` → `daftar` (name `daftar`)
- **masuk:**
  - user yang sudah login diarahkan ke `cpns:dasbor`
  - POST `identitas` (email atau username) dan `kata_sandi`; berhasil, lalu redirect ke `next` (hanya kalau aman menurut `url_has_allowed_host_and_scheme`) atau `cpns:dasbor`
  - gagal menampilkan "Email atau kata sandi salah."
  - halaman memuat tombol "Masuk dengan Google" (`accounts:google_login`), kalimat "Simulasi CAT gratis hanya tersedia untuk akun Google.", dan "Lupa kata sandi? Hubungi admin lewat WhatsApp untuk mengatur ulang." (tautan WhatsApp hanya kalau `nomor_wa` ada)
- **daftar:**
  - field `nama`, `email`, `kata_sandi`, `ulang_kata_sandi`, dan kotak centang `setuju` berlabel "Saya setuju dengan Syarat Layanan dan Kebijakan Privasi" (bertautan)
  - kata sandi divalidasi `validate_password` dan harus sama dengan ulangannya
  - email yang sudah ada (case-insensitive) menampilkan "Email ini sudah terdaftar. Silakan masuk." (Review Focus 1)
  - kalau berhasil:
    - buat `User(username=<bagian lokal email dibuat unik>, email, first_name=nama, role='peserta')` dengan kata sandi diset
    - buat `AksesPeserta(via_google=False)`, login, lalu redirect ke dasbor dengan pesan "Akun dibuat. Selamat berlatih."
- **Callback Google** (`apps/accounts/views.py`), kalau `getattr(request, 'is_cpns_subdomain', False)`:
  - user baru dibuat dengan `role='peserta'`, `xp=0`, tanpa `XPHistory` (kecuali `_is_teacher_email`, yang tetap guru)
  - user baru maupun lama mendapat `AksesPeserta.via_google=True` lewat `update_or_create`
  - redirect `reverse('cpns:dasbor')`
  - perilaku di host utama **tidak berubah**

- [ ] **Step 1: Tulis tes yang gagal:**
  - `test_daftar_membuat_peserta`: role peserta, `via_google` False, sudah login, `xp == 0`
  - `test_daftar_email_siswa_ditolak`: email milik siswa (huruf berbeda) memunculkan pesan di atas, dan peran siswa tetap
  - `test_daftar_tanpa_setuju_ditolak`
  - `test_daftar_sandi_tidak_sama_ditolak`
  - `test_masuk_dengan_email_dan_username`
  - `test_masuk_next_eksternal_diabaikan`
  - `test_tamu_ke_dasbor_diarahkan_ke_masuk_cpns`: `Location` berawalan `reverse('cpns:masuk')`
  - `test_callback_google_host_cpns_buat_peserta`: patch fungsi pengambil token dan profil Google yang ada (lihat isi view); dengan `HTTP_HOST` cpns, user baru ber-role peserta, `via_google` True, dan redirect ke dasbor
  - `test_callback_google_host_utama_tetap_siswa`
- [ ] **Step 2:** Jalankan tesnya. Hasil yang diharapkan: FAIL.
- [ ] **Step 3:** Implementasikan, lalu build CSS.
- [ ] **Step 4:** Jalankan tes PASS dan seluruh suite PASS.
- [ ] **Step 5:** Commit `feat(cpns): daftar dan masuk peserta`.

---

### Task 5: Peserta terpisah dari situs sekolah

**Files:**
- Modify: `apps/cpns/middleware.py` (tambah `PesertaHanyaCpnsMiddleware`), `config/settings/base.py`
  - `CPNS_URL = os.getenv('CPNS_URL', 'https://cpns.agunggumelarsaputra.com/')`
  - middleware dipasang setelah `AuthenticationMiddleware` dan `CpnsSubdomainMiddleware`
- Test: `apps/cpns/tests/test_isolasi.py`

**Interfaces:**
- **PesertaHanyaCpnsMiddleware:** kalau `request.user.is_authenticated`, `user.is_peserta`, dan `not request.is_cpns_subdomain`, serta path TIDAK berawalan salah satu dari `('/cpns/', '/accounts/logout/', '/accounts/oauth/', '/static/', '/media/')`, kembalikan redirect 302 ke `settings.CPNS_URL + 'dasbor/'`.

- [ ] **Step 1: Tulis tes yang gagal:**
  - `test_peserta_di_situs_sekolah_diarahkan`: GET `/` dan `/pembelajaran/` di host utama menghasilkan 302 ke `CPNS_URL + 'dasbor/'`
  - `test_peserta_boleh_cpns_prefix_dan_logout` (Review Focus 4): tidak ada redirect berulang
  - `test_siswa_tidak_terpengaruh`
  - `test_peserta_tidak_ada_di_leaderboard`: layanan leaderboard (`apps/gamification/services.py`) tidak memuat peserta
  - `test_peserta_tidak_ada_di_panel_guru`: dasbor `admin_panel` tidak memuat nama peserta
- [ ] **Step 2:** Jalankan tesnya. Hasil yang diharapkan: FAIL.
- [ ] **Step 3:** Implementasikan.
- [ ] **Step 4:** Jalankan tesnya. Hasil yang diharapkan: PASS.
- [ ] **Step 5:** Commit `feat(cpns): pisahkan peserta dari situs sekolah`.

---

### Task 6: Beranda publik, Syarat Layanan, Kebijakan Privasi

**Files:**
- Create: `apps/cpns/views/publik.py`, `templates/cpns/publik/beranda.html` (layar 01), `templates/cpns/publik/syarat.html`, `templates/cpns/publik/privasi.html`
- Modify:
  - `apps/cpns/urls.py`: `''` menjadi `beranda_publik` untuk tamu (user login tetap diarahkan ke dasbor); `syarat-layanan/` (name `syarat`); `kebijakan-privasi/` (name `privasi`)
  - footer di `base_cpns.html` memakai `{% url %}`
  - hapus view `beranda` yang lama kalau sudah tergantikan
- Test: `apps/cpns/tests/test_publik.py`

**Interfaces:**
- **Beranda tamu** (mengikuti mockup 01):
  - judul "Latihan SKD dan SKB Guru, dinilai dengan aturan CAT"
  - CTA "Daftar dan coba gratis" (`cpns:daftar`) dan "Saya sudah punya akun" (`cpns:masuk`)
  - kalimat "Latihan mandiri. Tidak berafiliasi dengan BKN."
  - bagian "Dua cara berlatih"
  - bagian "Cara nilai SKD": dibaca dari `SkemaUjian` SKD-CAT dan bagiannya, bukan angka yang ditulis langsung; kalimat penutup "Ambang batas mengikuti ketentuan terbaru dan bisa berubah."
  - bagian "Akun gratis dan Premium": harga dari `PengaturanCPNS`; kalau `teks_harga` kosong, tulis "Harga Premium: hubungi admin." (Review Focus 5)
- **Syarat Layanan dan Kebijakan Privasi:** draf berbahasa sederhana. Isinya:
  - data yang disimpan (nama, email, riwayat latihan) dan tujuannya
  - pembayaran manual lewat WhatsApp; tidak ada data kartu atau rekening yang disimpan
  - masa aktif premium dan aturan voucher
  - cara meminta penghapusan akun
  - `[KEBIJAKAN PENGEMBALIAN DANA]` dan `[NAMA DAN KONTAK PENGELOLA]` sebagai placeholder yang terlihat
  - kalimat pembuka "Draf, menunggu tinjauan pengelola." (wajib ditinjau pemilik sebelum deploy)

- [ ] **Step 1: Tulis tes yang gagal:**
  - `test_tamu_melihat_beranda_publik`: 200, memuat CTA "Daftar dan coba gratis" dan "Tidak berafiliasi dengan BKN"
  - `test_login_diarahkan_ke_dasbor`
  - `test_ambang_dari_database`: ubah ambang TWK menjadi 70 di database, halaman memuat "70"
  - `test_harga_kosong_teks_jujur` dan `test_harga_terisi_tampil`
  - `test_syarat_dan_privasi_200_dan_footer_tertaut`: footer memuat `reverse('cpns:syarat')` dan `reverse('cpns:privasi')`
  - `test_tanpa_klaim_resmi_publik`: beranda, syarat, dan privasi tidak memuat "resmi" maupun "soal asli"
- [ ] **Step 2:** Jalankan tesnya. Hasil yang diharapkan: FAIL.
- [ ] **Step 3:** Implementasikan, lalu build CSS.
- [ ] **Step 4:** Jalankan tes PASS dan seluruh suite PASS.
- [ ] **Step 5:** Commit `feat(cpns): beranda publik, syarat layanan, kebijakan privasi`.

---

### Task 7: Halaman Premium dan penukaran voucher

**Files:**
- Create: `apps/cpns/views/premium.py`, `templates/cpns/premium/halaman.html` (layar 07), `templates/cpns/premium/_hasil_voucher.html`
- Modify: `apps/cpns/urls.py`; nav "Premium" di `base_cpns.html` dan bagian `#premium` di dasbor sekarang bertaut ke `cpns:premium` (teks "segera tersedia" dihapus)
- Test: `apps/cpns/tests/test_premium_views.py`

**Interfaces:**
- Route:
  - `premium/` → `premium` (name `premium`), terbuka untuk tamu
  - `premium/voucher/` POST → `tukar_voucher` (name `tukar_voucher`), memakai `wajib_masuk`
- **Halaman Premium:**
  - status akun (Trial, atau "Premium sampai <tanggal>")
  - pilihan durasi dari `durasi_tersedia()` beserta teks harga
  - daftar isi premium
  - langkah "Cara membeli"
  - tombol "Hubungi admin via WhatsApp" untuk setiap durasi (`tautan_wa(durasi, email user atau '')`, `target="_blank" rel="noopener"`). Kalau `nomor_wa` kosong, tidak ada tombol dan muncul teks "Kontak admin belum diatur." (Review Focus 5)
  - formulir kode voucher hanya untuk user yang sudah login; tamu melihat tautan "Masuk untuk menukar kode"
- **tukar_voucher:**
  - memanggil `pakai_voucher`
  - berhasil: "Premium aktif sampai <tanggal d M Y>."
  - `tidak_valid`: "Kode tidak ditemukan atau sudah dipakai. Periksa lagi huruf dan angkanya. Sisa percobaan: {sisa} dari 5 per jam."
  - `terlalu_sering`: "Terlalu banyak percobaan. Coba lagi dalam satu jam."
  - permintaan HTMX dibalas partial `role="status"` dengan status 200; permintaan biasa memakai messages lalu redirect ke `cpns:premium`
  - saat permintaan berjalan, tombol dinonaktifkan dan berbunyi "Memeriksa kode…" (`hx-disabled-elt` dan `hx-indicator`)

- [ ] **Step 1: Tulis tes yang gagal:**
  - `test_premium_tamu_200_tanpa_form`
  - `test_premium_tautan_wa_ada_dan_aman`: `href` berawalan `https://wa.me/`, ada `rel="noopener"`, dan email user tercantum di teks
  - `test_premium_tanpa_nomor_wa`
  - `test_tukar_berhasil_htmx` dan `test_tukar_salah_menampilkan_sisa`
  - `test_tukar_terlalu_sering`
  - `test_tukar_tamu_diarahkan_ke_masuk`
  - `test_tukar_dua_kali_kode_sama` (Review Focus 2): permintaan kedua dari user lain mendapat "Kode tidak ditemukan atau sudah dipakai"
- [ ] **Step 2:** Jalankan tesnya. Hasil yang diharapkan: FAIL.
- [ ] **Step 3:** Implementasikan, lalu build CSS.
- [ ] **Step 4:** Jalankan tes PASS dan seluruh suite PASS.
- [ ] **Step 5:** Commit `feat(cpns): halaman premium dan tukar voucher`.

---

### Task 8: Dasbor: subtopik lemah, riwayat, dan bar skor

**Files:**
- Create: `apps/cpns/analitik.py`
- Modify: `apps/cpns/views/dasbor.py`, `templates/cpns/dasbor.html`, `templates/cpns/riwayat.html`, `templates/cpns/komponen/bar_skor.html`
- Test: `apps/cpns/tests/test_analitik.py` (dan tambahan di `test_dasbor.py`)

**Interfaces:**
- Produces: `kelemahan_subtopik(user, minimal_dijawab: int = 3, batas: int = 3) -> list[dict]`
  - setiap dict berisi `subtes`, `subtopik`, `benar`, `dijawab`, `persen`
  - dihitung dari butir **sesi belajar** milik user yang sudah dijawab
  - "benar" memakai `adalah_benar`
  - hanya subtopik dengan `dijawab >= minimal_dijawab`, diurutkan dari persen terendah (seri: dijawab terbanyak), maksimal `batas` subtopik
- **Dasbor bagian "Subtopik yang perlu dilatih":**
  - premium: daftar "TIU · Silogisme 40% (2/5)" beserta tautan "Latih subtopik ini", yang POST ke `belajar_mulai` dengan subtes, subtopik, dan jumlah 10
  - premium tanpa data: "Belum cukup data. Jawab minimal 3 soal per subtopik di Mode Belajar."
  - trial: kartu terkunci "Ringkasan subtopik yang masih lemah khusus Premium." bertaut ke `cpns:premium`
- **Riwayat:** CAT berjalan yang sudah lewat waktu ditutup (`selesaikan_jika_kedaluwarsa`) sebelum ditampilkan, sehingga tampil "Selesai".
- **bar_skor:** lebar isian dan posisi penanda dibatasi 0..100%.

- [ ] **Step 1: Tulis tes yang gagal:**
  - `test_kelemahan_urut_dan_ambang_minimal`
  - `test_kelemahan_abaikan_cat`
  - `test_dasbor_premium_tampil_kelemahan`, `test_dasbor_trial_kartu_terkunci`, `test_dasbor_premium_belum_cukup_data`
  - `test_riwayat_cat_kedaluwarsa_tampil_selesai`
  - `test_bar_skor_dibatasi_100`: skor 200 dari maks 150 menghasilkan width 100%
- [ ] **Step 2:** Jalankan tesnya. Hasil yang diharapkan: FAIL.
- [ ] **Step 3:** Implementasikan, lalu build CSS.
- [ ] **Step 4:** Jalankan tes PASS dan seluruh suite PASS.
- [ ] **Step 5:** Commit `feat(cpns): ringkasan subtopik lemah dan perapian dasbor`.

---

### Task 9: Perapian sebelum deploy (aksesibilitas dan umpan balik)

**Files:**
- Modify: `templates/cpns/cat/ruang.html`, `templates/cpns/base_cpns.html`, `templates/cpns/komponen/_laporkan_slot.html`, `templates/cpns/komponen/_laporkan_hasil.html` (atau nama partial yang ada), dan partial umpan balik belajar
- Test: tambahan di `test_cat_views.py`, `test_dasbor.py`, `test_belajar_views.py`, serta `apps/accounts/tests/test_peran_guru.py`

**Interfaces / perubahan:**
- **Ruang CAT:**
  - panel "Daftar soal" dan dialog konfirmasi menjebak fokus (Tab dan Shift+Tab berputar di dalam dialog)
  - 409 `sudah_selesai` ditampilkan sebagai "Ujian sudah dikumpulkan.", lalu diarahkan ke hasil
  - saat timer 0, indikator berbunyi "Waktu habis, mengumpulkan…"
  - respons 400 ditampilkan "Jawaban tidak tersimpan. Coba pilih lagi.", bukan "Tersimpan"
- **Umpan balik 4xx untuk HTMX:**
  - satu handler global di `base_cpns.html`: pada event `htmx:responseError`, tampilkan teks dari respons (kalau ada) atau "Permintaan gagal. Muat ulang halaman lalu coba lagi." di elemen `role="alert"` dekat form pemicu
  - endpoint yang dipakai (laporkan, jawab belajar, tukar voucher) membalas 400/403/409 dengan teks singkat berbahasa Indonesia
- **Live region laporkan:** wadah `role="status"` sudah ada sejak halaman dimuat, lalu isinya diganti, sehingga pembaca layar mengumumkannya
- **Tes login (catatan Rencana 1):** `_is_teacher_email` dengan `None`, `""`, dan email berspasi; serta parsing env `GURU_EMAILS` (`"a@x.id, B@x.id,"` menghasilkan dua email). Pakai `override_settings` atau `importlib.reload` sesuai cara settings dibaca.

- [ ] **Step 1: Tulis tes yang gagal** (tes markup untuk perilaku JS: atribut dan teks yang dirender; perilaku JS diverifikasi di Task 10):
  - `test_ruang_teks_status_baru_ada`
  - `test_laporkan_wadah_status_ada_sejak_awal`
  - `test_endpoint_htmx_400_berteks`
  - `test_is_teacher_email_kasus_tepi`
  - `test_parsing_guru_emails`
- [ ] **Step 2:** Jalankan tesnya. Hasil yang diharapkan: FAIL.
- [ ] **Step 3:** Implementasikan, lalu build CSS.
- [ ] **Step 4:** Jalankan tes PASS dan seluruh suite PASS.
- [ ] **Step 5:** Commit `fix(cpns): fokus dialog, umpan balik HTMX, teks status`.

---

### Task 10: Verifikasi browser dan Delivery Gate antislop (pengendali)

**Files:**
- Create: `anti-slop/audit-004-<tanggal>.md`

- [ ] **Step 1:** Data lokal. Isi `PengaturanCPNS` (nomor WA contoh `[NOMOR_WA]` dari pemilik, atau kosong) dan buat 2 voucher lewat admin. Data hanya di database lokal.
- [ ] **Step 2:** Klik alur ini di lebar 375, 768, dan 1280 px:
  - beranda tamu → daftar → dasbor (trial non-Google: tombol simulasi berisi alasan)
  - premium → tombol WA (`href` benar, tidak diklik ke luar) → tukar kode salah (sisa 4) → tukar kode benar ("Premium aktif sampai …")
  - dasbor premium (subtopik lemah)
  - admin buat voucher massal → salin
  - keluar → masuk lagi
  - syarat dan privasi
  - peserta membuka situs sekolah di `localhost:8010` → diarahkan ke cpns

  Untuk setiap layar: tidak ada overflow, tidak ada target di bawah 44 px, konsol bersih.
- [ ] **Step 3:** Uji keyboard:
  - fokus terjebak di dialog ruang CAT
  - Escape menutup dialog
  - formulir daftar bisa diisi dengan Tab saja
- [ ] **Step 4:** Tulis laporan Delivery Gate dengan bukti per butir. R-24 sekarang harus PASS.
- [ ] **Step 5:** Commit `docs(cpns): laporan verifikasi rencana 2`. **Tidak di-deploy.**
