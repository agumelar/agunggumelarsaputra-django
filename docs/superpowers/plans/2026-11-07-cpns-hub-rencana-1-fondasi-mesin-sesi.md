# CPNS Hub Rencana 1: Fondasi dan Mesin Sesi

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Membangun ulang inti app `apps/cpns`: bank soal, skema ujian, sesi CAT dan Belajar dengan penilaian aturan BKN, aturan akses, serta halaman peserta inti (dasbor, ruang CAT, hasil, belajar, riwayat). Ditambah perbaikan celah peran guru di login Google.

**Architecture:**
- Model baru di paket `apps/cpns/models/`. Model lama dipindah utuh ke `legacy.py` tanpa perubahan tabel.
- Logika bisnis ada di modul layanan yang murni dan mudah diuji: `validasi.py`, `penilaian.py`, `perakitan.py`, `akses.py`, `sesi_layanan.py`.
- View Django tipis memanggil layanan. Interaksi memakai HTMX (Belajar) dan `fetch` JSON (simpan otomatis CAT).

**Tech Stack:** Python 3.12, Django 5.1, HTMX 2.0.4, Alpine.js 3.14.8, Tailwind CSS 3.4 (`npm run build:css`, `static/css/output.css` ikut di-commit), SQLite (dev) / PostgreSQL 17 (VPS).

**Spec:** `docs/superpowers/specs/2026-11-07-cpns-hub-design.md`. Mockup: `design/cpns-hub-mockup.figcraft` dan `design/png/`.

**Di luar rencana ini** (rencana berikutnya):
- **Rencana 2:** pendaftaran publik, Beranda publik, Syarat/Privasi, voucher, halaman Premium, `PengaturanCPNS`, Django Admin, middleware isolasi peserta.
- **Rencana 3:** impor soal, Tinjau Soal, Cakupan, antrean Laporan, kisi-kisi.
- **Rencana 4:** impor soal lama, pengalihan alamat lama, keamanan produksi, deploy.

Selama Rencana 1 dikerjakan, cpns live **tidak di-deploy**, kecuali Task 0.

## Global Constraints

- **Branch:** semua task kecuali Task 0 dikerjakan di branch `feat/cpns-hub`. Task 0 di `master` dan boleh dideploy sendiri.
- **Git:** stage dengan path eksplisit, tidak pernah `git add -A`.
- **Menjalankan tes:**
  - perintah: `.venv/Scripts/python.exe manage.py test <label>` (settings `config.settings.development`)
  - satu tes cpns: `apps.cpns.tests.test_<nama>`
  - seluruh projek harus lolos di akhir setiap task yang mengubah model
- **Teks UI** berbahasa Indonesia sederhana. Dilarang memakai: em dash, emoji, kata "resmi", "soal asli BKN", dan titik berkedip dekoratif.
- **Warna dan font** mengikuti `DESIGN.md`:
  - latar `#090D16`; permukaan `#111827` / `#162032` / `#1C293E`
  - garis `rgba(255,255,255,0.08)` dan `0.14`
  - teks `#F3F4F6` / `#CBD5E1` / `#94A3B8`
  - aksen tunggal sky `#38BDF8`, teks di atasnya `#082F49`
  - sukses `#34D399`, bahaya `#F87171`, ragu/premium `#FBBF24`
  - font Outfit (judul), Inter (isi), JetBrains Mono (angka/kode)
- **Aksesibilitas:** target sentuh minimal 44 px (`min-h-11`). Opsi jawaban berupa `<button aria-pressed>`. Escape menutup panel dan dialog. Pintasan huruf diabaikan saat Ctrl, Cmd, atau Alt ditekan. Status tidak boleh hanya ditandai warna.
- **Skema SKD-CAT:** 100 menit; TWK 30 soal benar 5 / salah 0, ambang 65; TIU 35 soal benar 5 / salah 0, ambang 80; TKP 45 soal bobot 1–5, ambang 166. Lulus kalau setiap bagian ≥ ambang.
- **Skema SKB-GURU-LATIHAN:** `aktif=False`; 90 menit; PEDAGOGIK 50 soal (5/0); MATERI_RPL 50 soal (5/0); ambang 0 (artinya tanpa ambang).
- **Toleransi** simpan setelah batas waktu: 30 detik. Lebih dari itu dibalas HTTP 409.
- **Trial:** paket belajar `untuk_trial` bisa diulang. Simulasi CAT SKD 1 kali, hanya kalau `AksesPeserta.via_google`. Pembahasan hasil CAT hanya untuk premium/superuser.
- **Premium:** `AksesPeserta.premium_sampai > timezone.now()` atau `user.is_superuser`.
- **Kerahasiaan:** HTML ruang CAT tidak boleh memuat kunci, bobot, maupun teks pembahasan.
- **CSS:** setiap task yang menambah kelas Tailwind baru menjalankan `npm run build:css` lalu `python manage.py collectstatic --noinput`, dan meng-commit `static/css/output.css`.

## Review Focus

1. **Peserta mengumpulkan dua kali** (klik ganda atau dua tab). Hasil dan skor harus sama dan tidak tercatat dua kali. Diuji di Task 8.
2. **Soal ditolak atau diedit admin saat sesi berjalan.** Sesi tetap bisa dinilai memakai soal yang sudah dibekukan di `SesiSoal`. Diuji di Task 8.
3. **Bank soal persis sebanyak kebutuhan, dan semuanya pernah dikerjakan user.** Perakitan tetap berhasil dengan memakai ulang soal. Diuji di Task 6.
4. **User lama (guru/siswa) tanpa `AksesPeserta`** membuka dasbor. Catatan aksesnya dibuat otomatis dan tidak error 500. Diuji di Task 7.
5. **Jawaban tampil di luar A–E atau nomor di luar jangkauan** dikirim ke endpoint simpan. Dibalas HTTP 400 tanpa mengubah data. Diuji di Task 10.

---

## Peta file

```
apps/accounts/models.py                  (ubah)  ROLE_PESERTA, is_peserta
apps/accounts/views.py                   (ubah)  _is_teacher_email()
config/settings/base.py                  (ubah)  GURU_EMAILS
apps/cpns/models/__init__.py             (baru)  ekspor semua model
apps/cpns/models/legacy.py               (pindah) CpnsPackage, CpnsQuestion, CpnsAttempt (tanpa perubahan)
apps/cpns/models/soal.py                 (baru)  Soal
apps/cpns/models/skema.py                (baru)  SkemaUjian, SkemaBagian, PaketBelajar, PaketSoal
apps/cpns/models/sesi.py                 (baru)  Sesi, SesiSoal
apps/cpns/models/akses.py                (baru)  AksesPeserta, LaporanSoal
apps/cpns/validasi.py                    (baru)  validasi_soal, sidik_teks
apps/cpns/penilaian.py                   (baru)  poin_soal, nilai_sesi
apps/cpns/perakitan.py                   (baru)  rakit_sesi_cat, rakit_sesi_belajar, BankSoalKurang
apps/cpns/akses.py                       (baru)  akses_untuk, is_premium, boleh_* 
apps/cpns/sesi_layanan.py                (baru)  simpan_jawaban, kumpulkan, selesaikan_jika_kedaluwarsa
apps/cpns/views/__init__.py, views/*.py  (ganti) dasbor, cat, belajar, riwayat
apps/cpns/urls.py                        (ganti)
templates/base.html                      (ubah)  blok main_class, title_suffix
templates/cpns/*                         (ganti)
apps/cpns/tests/*                        (ganti tes lama yang menguji view/model lama)
```

---

### Task 0: Tutup celah peran guru di login Google (di `master`, boleh dirilis sendiri)

**Files:**
- Modify: `config/settings/base.py` (tambah `GURU_EMAILS`)
- Modify: `apps/accounts/views.py:275` (ganti `is_teacher_email`)
- Test: `apps/accounts/tests/test_peran_guru.py` (buat folder `apps/accounts/tests/` dengan `__init__.py` kalau belum ada; kalau `apps/accounts/tests.py` sudah ada, pindahkan isinya ke `apps/accounts/tests/test_lama.py`)

**Interfaces:**
- Produces: `apps.accounts.views._is_teacher_email(email: str) -> bool`
- Produces: `settings.GURU_EMAILS: list[str]`, dibaca dari env `GURU_EMAILS` (dipisah koma). Nilai bawaan: `["agung@smkn1rongga.sch.id", "agunggumelar@smkn1rongga.sch.id"]`.

- [ ] **Step 1: Tulis tes yang gagal**

```python
from django.test import SimpleTestCase, override_settings
from apps.accounts.views import _is_teacher_email

@override_settings(GURU_EMAILS=["agung@smkn1rongga.sch.id"])
class PeranGuruTest(SimpleTestCase):
    def test_email_terdaftar_jadi_guru(self):
        self.assertTrue(_is_teacher_email("Agung@SMKN1Rongga.sch.id"))

    def test_email_berisi_kata_agung_bukan_guru(self):
        self.assertFalse(_is_teacher_email("agung123@gmail.com"))
        self.assertFalse(_is_teacher_email("siswa.agung@gmail.com"))
```

- [ ] **Step 2:** Jalankan `manage.py test apps.accounts.tests.test_peran_guru`. Hasil yang diharapkan: FAIL (ImportError `_is_teacher_email`).
- [ ] **Step 3:** Implementasikan `_is_teacher_email`: bandingkan `email.strip().lower()` dengan `{e.lower() for e in settings.GURU_EMAILS}`. Pakai fungsi ini di callback Google sebagai pengganti baris 275.
- [ ] **Step 4:** Jalankan tes tadi, lalu seluruh `manage.py test`. Hasil yang diharapkan: semua PASS.
- [ ] **Step 5:** Commit dengan pesan `fix(accounts): peran guru hanya untuk email di GURU_EMAILS`. Deploy mengikuti pola VPS yang sama seperti sebelumnya.

---

### Task 1: Paket model cpns, peran `peserta`, dan branch

**Files:**
- Create: `apps/cpns/models/__init__.py`, `apps/cpns/models/legacy.py` (isi persis `apps/cpns/models.py` sekarang)
- Delete: `apps/cpns/models.py`
- Modify: `apps/accounts/models.py` (ROLE_PESERTA)
- Create: migrasi `accounts` untuk choices baru
- Test: `apps/cpns/tests/test_fondasi.py`

**Interfaces:**
- Produces: `User.ROLE_PESERTA = 'peserta'`, `User.is_peserta -> bool` (property)
- Produces: `from apps.cpns.models import CpnsPackage, CpnsQuestion, CpnsAttempt` tetap berfungsi

- [ ] **Step 1:** `git switch -c feat/cpns-hub`
- [ ] **Step 2: Tulis tes yang gagal**: `test_peran_peserta`. Buat user `role='peserta'`, lalu pastikan `user.is_peserta` True dan `user.is_siswa` False.
- [ ] **Step 3:** Jalankan tesnya. Hasil yang diharapkan: FAIL.
- [ ] **Step 4:** Pindahkan model lama ke `legacy.py`, ekspor ulang di `__init__.py`, lalu tambahkan peran peserta. `makemigrations accounts` harus menghasilkan hanya AlterField choices. `makemigrations cpns --check` harus "No changes detected".
- [ ] **Step 5:** Jalankan seluruh `manage.py test`. Hasil yang diharapkan: PASS (tes lama cpns masih berjalan di model lama).
- [ ] **Step 6:** Commit `refactor(cpns): paket models dan peran peserta`.

---

### Task 2: Model `Soal` dan validator

**Files:**
- Create: `apps/cpns/models/soal.py`, `apps/cpns/validasi.py`, migrasi `cpns`
- Test: `apps/cpns/tests/test_validasi.py`

**Interfaces:**
- Produces: `Soal` dengan field sesuai spesifikasi 3.1. Konstanta:
  - `Soal.JENIS = ('SKD','SKB_GURU')`
  - `Soal.SUBTES = ('TWK','TIU','TKP','PEDAGOGIK','MATERI_RPL')`
  - `Soal.TINGKAT = ('mudah','sedang','sulit')`
  - `Soal.STATUS = ('draf','tayang','ditolak')`
  - `Soal.SUMBER = ('draf_ai','tulisan_sendiri','lama')`
  - `kunci` CharField(1, blank); `bobot` JSONField(null)
  - `sidik_teks` CharField(64, db_index), diisi otomatis di `save()`
- Produces: `validasi_soal(data: dict, untuk_tayang: bool = False) -> list[str]`. Mengembalikan daftar pesan error berbahasa Indonesia; kosong berarti valid. Key di `data` sama dengan nama field `Soal`.
- Produces: `sidik_teks(teks: str) -> str`. Hasilnya sha256 hex dari teks yang dihuruf-kecilkan, tanda bacanya dibuang, dan spasinya dirapatkan.
- Produces: `Soal.clean()` memanggil `validasi_soal(..., untuk_tayang=self.status=='tayang')` dan melempar `ValidationError` kalau ada pesan.

- [ ] **Step 1: Tulis tes yang gagal** (setiap tes memakai fixture `data_dasar()` berisi soal TIU valid):
  - `test_soal_valid_tanpa_error`: hasilnya `[]`
  - `test_opsi_kosong_ditolak`: `opsi_c=''` menghasilkan pesan yang memuat `"opsi C"`
  - `test_opsi_ganda_ditolak`: `opsi_b == opsi_a` menghasilkan pesan yang memuat `"sama"`
  - `test_kunci_wajib_untuk_benar_salah`: `kunci=''` di TIU menghasilkan pesan yang memuat `"kunci"`
  - `test_bobot_tkp_harus_1_sampai_5_berbeda`:
    - `{"A":3,"B":1,"C":5,"D":2,"E":1}` menghasilkan error
    - `{"A":3,"B":1,"C":5,"D":2,"E":4}` menghasilkan `[]`
  - `test_pembahasan_wajib`: `pembahasan_cepat=''` menghasilkan error
  - `test_tayang_wajib_ditinjau`: `untuk_tayang=True` tanpa `ditinjau_oleh` menghasilkan error
  - `test_sidik_teks_abaikan_spasi_dan_tanda_baca`: `sidik_teks("2, 5,  11 ...") == sidik_teks("2 5 11")`
- [ ] **Step 2:** Jalankan `manage.py test apps.cpns.tests.test_validasi`. Hasil yang diharapkan: FAIL.
- [ ] **Step 3:** Implementasikan `validasi.py`, model `Soal`, dan migrasi.
- [ ] **Step 4:** Jalankan tesnya. Hasil yang diharapkan: PASS.
- [ ] **Step 5:** Commit `feat(cpns): model Soal dan validator`.

---

### Task 3: Skema ujian, paket belajar, dan data awal

**Files:**
- Create: `apps/cpns/models/skema.py`, migrasi skema, dan migrasi data `00xx_skema_awal.py`
- Test: `apps/cpns/tests/test_skema.py`

**Interfaces:**
- Produces:
  - `SkemaUjian(kode unique, nama, jenis_ujian, durasi_menit, aktif, keterangan)`
  - `SkemaBagian(skema FK related_name='bagian', urutan, subtes, jumlah_soal, cara_nilai in ('benar_salah','bobot_opsi'), poin_benar=5, poin_salah=0, ambang_batas)`, ordering `['urutan']`
- Produces:
  - `PaketBelajar(nama, jenis_ujian, untuk_trial, aktif)`
  - `PaketSoal(paket FK related_name='isi', soal FK, urutan)`, unique `(paket, urutan)`
  - constraint unik: satu `untuk_trial=True, aktif=True` per `jenis_ujian`
- Produces: `SkemaUjian.total_soal -> int` (property)

- [ ] **Step 1: Tulis tes yang gagal:**
  - `test_skema_skd_terpasang`: `SkemaUjian.objects.get(kode='SKD-CAT')` berdurasi 100, bagian `[('TWK',30,'benar_salah',65),('TIU',35,'benar_salah',80),('TKP',45,'bobot_opsi',166)]`, dan `total_soal == 110`
  - `test_skema_skb_nonaktif`: `SKB-GURU-LATIHAN` dengan `aktif False`, durasi 90, bagian PEDAGOGIK 50 dan MATERI_RPL 50, ambang 0
  - `test_hanya_satu_paket_trial_aktif`: membuat paket trial aktif kedua untuk SKD melempar `IntegrityError`
- [ ] **Step 2:** Jalankan tesnya. Hasil yang diharapkan: FAIL.
- [ ] **Step 3:** Implementasikan model, migrasi, dan migrasi data (RunPython yang idempoten dengan `update_or_create`).
- [ ] **Step 4:** Jalankan tes PASS, lalu seluruh `manage.py test` juga PASS.
- [ ] **Step 5:** Commit `feat(cpns): skema ujian dan paket belajar`.

---

### Task 4: Model sesi, akses, dan laporan

**Files:**
- Create: `apps/cpns/models/sesi.py`, `apps/cpns/models/akses.py`, migrasi
- Test: `apps/cpns/tests/test_model_sesi.py`

**Interfaces:**
- Produces: `Sesi(user FK related_name='sesi_cpns', mode in ('cat','belajar'), skema FK null, paket FK null, filter_subtopik JSON null, status in ('berjalan','selesai'), dimulai_pada auto_now_add, batas_waktu null, selesai_pada null, skor_bagian JSON default=list, total int default 0, lulus bool default False)`
  - constraint unik parsial: `(user)` ketika `mode='cat' AND status='berjalan'`
- Produces: `SesiSoal(sesi FK related_name='butir', soal FK PROTECT, nomor, urutan_opsi CharField(5), jawaban CharField(1, blank), ragu bool, dijawab_pada null, poin int null)`
  - unique `(sesi, nomor)`, ordering `['nomor']`
- Produces: `Sesi.sisa_detik(now) -> int`. Nilainya `max(0, int((batas_waktu - now).total_seconds()))`, atau 0 kalau `batas_waktu` kosong.
- Produces: `AksesPeserta(user OneToOne related_name='akses_cpns', premium_sampai null, via_google bool default False)`
- Produces: `LaporanSoal(soal FK, user FK, alasan in ('kunci_salah','ambigu','typo','lainnya'), catatan, status in ('baru','selesai') default 'baru', dibuat_pada)`

- [ ] **Step 1: Tulis tes yang gagal:**
  - `test_satu_sesi_cat_berjalan_per_user`: CAT berjalan kedua untuk user yang sama melempar `IntegrityError`
  - `test_sesi_cat_selesai_tidak_dihitung`: CAT selesai + CAT berjalan baru tidak error
  - `test_sisa_detik_tidak_negatif`: batas waktu 10 detik lalu menghasilkan `sisa_detik(now) == 0`
- [ ] **Step 2:** Jalankan tesnya. Hasil yang diharapkan: FAIL.
- [ ] **Step 3:** Implementasikan model dan migrasi.
- [ ] **Step 4:** Jalankan tesnya. Hasil yang diharapkan: PASS.
- [ ] **Step 5:** Commit `feat(cpns): model sesi, akses, laporan`.

---

### Task 5: Penilaian

**Files:**
- Create: `apps/cpns/penilaian.py`
- Test: `apps/cpns/tests/test_penilaian.py`

**Interfaces:**
- Consumes: `SkemaBagian`, `SesiSoal`, `Soal`
- Produces: `poin_soal(soal: Soal, jawaban: str, bagian: SkemaBagian) -> int`
  - `benar_salah`: `poin_benar` kalau `jawaban == soal.kunci`, selain itu `poin_salah`
  - `bobot_opsi`: `soal.bobot[jawaban]`
  - jawaban kosong menghasilkan 0 untuk kedua cara
- Produces: `nilai_sesi(sesi: Sesi) -> None`
  - mengisi `butir.poin` dan `sesi.skor_bagian` = `[{"subtes","skor","maks","ambang","lulus"}]` sesuai urutan bagian
  - mengisi `sesi.total` dan `sesi.lulus`, lalu menyimpan
  - `maks` = `jumlah_soal * poin_benar`, atau `jumlah_soal * 5` untuk bobot
  - `lulus` per bagian: `skor >= ambang`; ambang 0 selalu lulus
  - **sesi belajar:** `skor_bagian` dikelompokkan per `soal.subtes` dengan `ambang` 0
- **Pencocokan butir ke bagian:** `butir.soal.subtes == bagian.subtes`

- [ ] **Step 1: Tulis tes yang gagal** (fixture: skema SKD dari migrasi, soal buatan pabrik `buat_soal(subtes, kunci=..., bobot=...)` di `apps/cpns/tests/pabrik.py`):
  - `test_twk_benar_5_salah_0_kosong_0`
  - `test_tkp_pakai_bobot_dan_kosong_0`
  - `test_lulus_jika_semua_bagian_capai_ambang`: TWK 65, TIU 80, TKP 166 menghasilkan `lulus True`
  - `test_gagal_jika_satu_bagian_kurang`: TIU 75 menghasilkan `lulus False`, dan `skor_bagian[1]["lulus"] is False`
  - `test_total_jumlah_semua_bagian`: 70 + 75 + 170 = 315
- [ ] **Step 2:** Jalankan tesnya. Hasil yang diharapkan: FAIL.
- [ ] **Step 3:** Implementasikan.
- [ ] **Step 4:** Jalankan tesnya. Hasil yang diharapkan: PASS.
- [ ] **Step 5:** Commit `feat(cpns): penilaian per skema`.

---

### Task 6: Perakitan sesi

**Files:**
- Create: `apps/cpns/perakitan.py`
- Test: `apps/cpns/tests/test_perakitan.py`

**Interfaces:**
- Produces: `class BankSoalKurang(Exception)` dengan atribut `subtes: str`, `tersedia: int`, `dibutuhkan: int`
- Produces: `rakit_sesi_cat(user, skema: SkemaUjian, rng: random.Random | None = None, now=None) -> Sesi`
  - membuat `Sesi(mode='cat', batas_waktu=now + durasi)` dan `SesiSoal` bernomor 1..N
  - dibungkus `transaction.atomic()`
- Produces: `rakit_sesi_belajar(user, *, paket: PaketBelajar | None = None, subtes: str | None = None, subtopik: str | None = None, jumlah: int = 10, rng=None) -> Sesi`
  - paket: urutan soal mengikuti `PaketSoal.urutan`, dan opsi tetap diacak
  - subtopik: maksimal `jumlah` soal tayang secara acak; kalau kurang, semua yang ada dipakai
- Produces: `acak_urutan_opsi(rng) -> str` (permutasi dari "ABCDE")
- Produces: `opsi_tampil_ke_asli(urutan_opsi: str, posisi: str) -> str`. Contoh: urutan "CAEBD" dengan posisi "A" menghasilkan "C".

Algoritme pemilihan per bagian (tidak ditentukan oleh signature):
```python
tayang = Soal.objects.filter(status='tayang', subtes=bagian.subtes, jenis_ujian=skema.jenis_ujian)
pernah = set(SesiSoal.objects.filter(sesi__user=user).values_list('soal_id', flat=True))
baru = [s for s in tayang if s.id not in pernah]; lama = [s for s in tayang if s.id in pernah]
if len(baru) + len(lama) < bagian.jumlah_soal: raise BankSoalKurang(...)
rng.shuffle(baru); rng.shuffle(lama)
terpilih = (baru + lama)[:bagian.jumlah_soal]
```

- [ ] **Step 1: Tulis tes yang gagal** (pakai `random.Random(1)`):
  - `test_komposisi_sesuai_skema`: dengan bank 30/35/45 tayang, sesi berisi 110 butir; nomor 1–30 TWK, 31–65 TIU, 66–110 TKP
  - `test_bank_kurang_tidak_membuat_sesi`: dengan TIU 34 tayang, melempar `BankSoalKurang(subtes='TIU', tersedia=34, dibutuhkan=35)` dan `Sesi.objects.count() == 0`
  - `test_utamakan_soal_belum_dikerjakan`: bank TWK 40, sesi pertama selesai; sesi kedua harus memuat ke-10 soal TWK yang belum pernah keluar
  - `test_bank_pas_semua_pernah_tetap_berhasil`: bank persis 30/35/45 dan semuanya pernah dikerjakan, sesi tetap terbentuk (Review Focus 3)
  - `test_hanya_soal_tayang`: soal `draf` dan `ditolak` tidak pernah terpilih
  - `test_opsi_tampil_ke_asli`: `opsi_tampil_ke_asli("CAEBD","A") == "C"` dan `opsi_tampil_ke_asli("CAEBD","E") == "D"`
  - `test_belajar_subtopik_kurang_pakai_semua`: hanya ada 4 soal subtopik, `jumlah=10` menghasilkan 4 butir
- [ ] **Step 2:** Jalankan tesnya. Hasil yang diharapkan: FAIL.
- [ ] **Step 3:** Implementasikan.
- [ ] **Step 4:** Jalankan tesnya. Hasil yang diharapkan: PASS.
- [ ] **Step 5:** Commit `feat(cpns): perakitan sesi CAT dan belajar`.

---

### Task 7: Aturan akses

**Files:**
- Create: `apps/cpns/akses.py`
- Test: `apps/cpns/tests/test_akses.py`

**Interfaces:**
- Produces: `akses_untuk(user) -> AksesPeserta` (get_or_create)
- Produces: `is_premium(user, now=None) -> bool`
- Produces: `boleh_mulai_cat(user, skema: SkemaUjian) -> tuple[bool, str]`. Pesan alasan ditampilkan apa adanya ke pengguna:
  - `"Skema ini belum tersedia."` kalau `skema.aktif` False dan user bukan superuser
  - `"Simulasi SKB Guru khusus Premium."` kalau SKB dan bukan premium
  - `"Simulasi gratis hanya untuk akun Google."` kalau trial dan `via_google` False
  - `"Kuota simulasi gratis sudah terpakai."` kalau trial dan pernah punya `Sesi` mode `cat`
  - `"Selesaikan dulu simulasi yang sedang berjalan."` kalau ada CAT berjalan
- Produces: `boleh_belajar_paket(user, paket) -> bool`: `paket.untuk_trial` atau premium
- Produces: `boleh_belajar_subtopik(user) -> bool`: premium
- Produces: `boleh_lihat_pembahasan(user, sesi) -> bool`: sesi milik user dan (mode belajar, atau premium)

- [ ] **Step 1: Tulis tes yang gagal:**
  - satu tes untuk setiap pesan di atas
  - `test_premium_aktif_dan_kedaluwarsa`
  - `test_superuser_selalu_premium`
  - `test_user_lama_tanpa_akses_dibuat_otomatis`: user `siswa` tanpa `AksesPeserta` → `akses_untuk(user)` tidak error dan `via_google` False (Review Focus 4)
  - `test_trial_tidak_lihat_pembahasan_cat` dan `test_trial_lihat_pembahasan_belajar`
- [ ] **Step 2:** Jalankan tesnya. Hasil yang diharapkan: FAIL.
- [ ] **Step 3:** Implementasikan.
- [ ] **Step 4:** Jalankan tesnya. Hasil yang diharapkan: PASS.
- [ ] **Step 5:** Commit `feat(cpns): aturan akses trial dan premium`.

---

### Task 8: Siklus sesi (simpan, kumpulkan, kedaluwarsa)

**Files:**
- Create: `apps/cpns/sesi_layanan.py`
- Test: `apps/cpns/tests/test_sesi_layanan.py`

**Interfaces:**
- Consumes: `opsi_tampil_ke_asli`, `nilai_sesi`
- Produces: `TOLERANSI_DETIK = 30`, `class WaktuHabis(Exception)`, `class SesiSudahSelesai(Exception)`
- Produces: `simpan_jawaban(sesi: Sesi, nomor: int, jawaban_tampil: str, ragu: bool, now=None) -> SesiSoal`
  - `jawaban_tampil` berisi `''` atau A–E; `ValueError` untuk nilai lain atau nomor di luar jangkauan
  - `WaktuHabis` kalau CAT dan `now > batas_waktu + 30 detik`
  - `SesiSudahSelesai` kalau status selesai
  - menyimpan jawaban **asli**
- Produces: `kumpulkan(sesi: Sesi, now=None) -> Sesi`. Idempoten: kalau sudah selesai, sesi dikembalikan tanpa dinilai ulang. Kalau belum, `nilai_sesi`, lalu `status='selesai'` dan `selesai_pada=now`.
- Produces: `selesaikan_jika_kedaluwarsa(sesi: Sesi, now=None) -> bool`: True kalau sesi baru saja dikumpulkan karena waktunya lewat.

- [ ] **Step 1: Tulis tes yang gagal:**
  - `test_simpan_menerjemahkan_posisi_ke_asli`: butir dengan urutan_opsi "CAEBD", jawaban tampil "A" tersimpan sebagai "C"
  - `test_simpan_idempoten`: dua kali simpan nilai yang sama menghasilkan satu butir dengan jawaban yang sama
  - `test_simpan_ditolak_setelah_toleransi`: batas + 31 detik melempar `WaktuHabis`; batas + 29 detik berhasil
  - `test_jawaban_tidak_valid_ditolak`: `"F"` dan nomor 999 melempar `ValueError`
  - `test_kumpulkan_dua_kali_hasil_sama` (Review Focus 1): total dan `selesai_pada` tidak berubah pada panggilan kedua
  - `test_soal_ditolak_setelah_sesi_dibuat_tetap_dinilai` (Review Focus 2): ubah soal ke `ditolak` lalu kumpulkan, skornya tetap terhitung
  - `test_kedaluwarsa_otomatis_dikumpulkan`
- [ ] **Step 2:** Jalankan tesnya. Hasil yang diharapkan: FAIL.
- [ ] **Step 3:** Implementasikan. `kumpulkan` memakai `select_for_update` pada sesi di dalam `transaction.atomic()`.
- [ ] **Step 4:** Jalankan tesnya. Hasil yang diharapkan: PASS.
- [ ] **Step 5:** Commit `feat(cpns): siklus sesi simpan dan kumpulkan`.

---

### Task 9: Kerangka tampilan cpns

**Files:**
- Modify: `templates/base.html`
  - `<title>` jadi `{% block title %}{{ SITE_TITLE }}{% endblock %}{% block title_suffix %} | RPL SMKN 1 Rongga{% endblock %}`
  - kelas `<main>` dipindah ke `{% block main_class %}flex-1 w-full max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6{% endblock %}`
- Rewrite: `templates/cpns/base_cpns.html`
  - `title_suffix` diisi ` | CPNS Hub`; `main_class` diisi `flex-1 w-full`; latar `#090D16`
  - header: logo teks "CPNS Hub"
  - navigasi peserta: Beranda, Belajar, Simulasi, Riwayat, Premium (tautan ke `cpns:premium` dibuat di Rencana 2; sementara menuju `cpns:dasbor#premium`), dan Akun
  - tombol Menu berlabel di bawah 1024 px, memakai pola dari audit #002 (aria-expanded, Escape)
  - footer: Syarat Layanan, Kebijakan Privasi, dan "Latihan mandiri. Tidak berafiliasi dengan BKN."
- Create: `templates/cpns/komponen/bar_skor.html` (motif bar dengan garis ambang; parameter `subtes, skor, maks, ambang, lulus`)
- Test: `apps/cpns/tests/test_kerangka.py`

**Interfaces:**
- Produces: blok template `title_suffix`, `main_class` (situs utama tidak berubah tampilannya)
- Produces: `{% include "cpns/komponen/bar_skor.html" with subtes=.. skor=.. maks=.. ambang=.. lulus=.. %}`

- [ ] **Step 1: Tulis tes yang gagal:**
  - `test_judul_tab_cpns`: `GET /` di host cpns berakhiran `" | CPNS Hub</title>"`
  - `test_halaman_utama_tetap_rpl`: `GET /` di host utama masih memuat `"| RPL SMKN 1 Rongga"`
  - `test_tanpa_klaim_resmi`: halaman cpns tidak memuat `"resmi"`, `"Resmi"`, maupun `"soal asli"`
- [ ] **Step 2:** Jalankan tesnya. Hasil yang diharapkan: FAIL.
- [ ] **Step 3:** Implementasikan, lalu `npm run build:css` dan `collectstatic`.
- [ ] **Step 4:** Jalankan tes PASS, lalu seluruh `manage.py test` juga PASS.
- [ ] **Step 5:** Commit `feat(cpns): kerangka tampilan CPNS Hub`.

---

### Task 10: View dan halaman Mode CAT

**Files:**
- Create: `apps/cpns/views/cat.py`
- Rewrite: `apps/cpns/urls.py` (route di Interfaces). Hapus `apps/cpns/views.py` lama dan template lama `package_list.html`, `package_detail.html`, `result_review.html`, `partials/review_list.html`, `landing.html`.
- Create: `templates/cpns/cat/ruang.html` (berdasarkan `cbt_room.html` versi audit #002, ditambah indikator simpan dan antrean `localStorage`), `templates/cpns/cat/hasil.html` (layar 06 mockup)
- Delete: `templates/cpns/cbt_room.html`; tes lama `test_views.py`, `test_models_scoring.py`, `test_ingestion.py`
- Move: kelas `CpnsSubdomainAccountPagesTest` dan `LoginNextRedirectTest` dari `test_hardening.py` dipindah **utuh** ke `apps/cpns/tests/test_akun_host.py`. Sisa `test_hardening.py` (submit dan mode versi lama) dihapus, karena perilakunya kini diuji di `test_cat_views.py` dan `test_sesi_layanan.py`.
- Test: `apps/cpns/tests/test_cat_views.py`

**Interfaces:**
- Route di `apps/cpns/urls.py` (namespace `cpns`):
  - `simulasi/<slug:kode>/mulai/` POST → `mulai_cat` (name `cat_mulai`)
  - `ujian/<int:sesi_id>/` GET → `ruang_cat` (`cat_ruang`)
  - `ujian/<int:sesi_id>/simpan/` POST JSON → `simpan_cat` (`cat_simpan`)
  - `ujian/<int:sesi_id>/kumpulkan/` POST → `kumpulkan_cat` (`cat_kumpulkan`)
  - `hasil/<int:sesi_id>/` GET → `hasil_cat` (`cat_hasil`)
- Semua route memakai `@login_required` dan hanya untuk pemilik sesi (selain itu 404).
- `simpan_cat` menerima `{"nomor": int, "jawaban": "A".."E"|"", "ragu": bool}`. Balasannya:
  - 200 `{"ok": true, "tersimpan_pada": iso}`
  - 400 untuk data tidak valid
  - 409 `{"ok": false, "alasan": "waktu_habis"}`
- Kode skema di URL: `SKD-CAT` → `skd-cat`. Pakai `SkemaUjian.kode` lowercase untuk perbandingan.

- [ ] **Step 1: Tulis tes yang gagal:**
  - `test_mulai_ditolak_tampilkan_alasan`: trial non-Google → redirect ke dasbor dengan pesan `"Simulasi gratis hanya untuk akun Google."`
  - `test_mulai_bank_kurang_pesan`: pesan memuat `"Bank soal untuk bagian TIU belum cukup"`
  - `test_ruang_tidak_bocorkan_kunci`: untuk setiap butir, HTML tidak memuat `pembahasan_konsep`, `pembahasan_pengecoh`, `pembahasan_cepat`, maupun JSON `bobot`, dan tidak memuat atribut `data-kunci`
  - `test_ruang_sesi_orang_lain_404`
  - `test_simpan_json_valid_200`, `test_simpan_jawaban_F_400` dan `test_simpan_nomor_999_400` (Review Focus 5), `test_simpan_setelah_waktu_409`
  - `test_ruang_setelah_waktu_habis_redirect_hasil`
  - `test_hasil_trial_tanpa_pembahasan`: memuat `"Pembahasan"` dan `"Premium"`, tapi tidak memuat teks pembahasan soal
  - `test_hasil_premium_ada_pembahasan`
- [ ] **Step 2:** Jalankan tesnya. Hasil yang diharapkan: FAIL.
- [ ] **Step 3:** Implementasikan view dan template.
  - Ruang CAT menerima `sisa_detik` dari server.
  - Timer browser menghitung dari `Date.now()` ke tenggat, bukan dengan mengurangi angka setiap detik.
  - Kalau waktu habis, browser memanggil `kumpulkan`.
- [ ] **Step 4:** `npm run build:css`, `collectstatic`, lalu jalankan tes PASS dan seluruh `manage.py test` juga PASS.
- [ ] **Step 5:** Commit `feat(cpns): mode CAT ruang ujian dan hasil`.

---

### Task 11: View dan halaman Mode Belajar

**Files:**
- Create: `apps/cpns/views/belajar.py`, `templates/cpns/belajar/pilih.html`, `templates/cpns/belajar/soal.html` (layar 04), `templates/cpns/belajar/_umpan_balik.html` (partial HTMX), `templates/cpns/belajar/ringkasan.html`
- Modify: `apps/cpns/urls.py`
- Test: `apps/cpns/tests/test_belajar_views.py`

**Interfaces:**
- Route:
  - `belajar/` GET → `pilih_belajar` (`belajar_pilih`)
  - `belajar/mulai/` POST → `mulai_belajar` (`belajar_mulai`), dengan field `paket_id` **atau** `subtes`, `subtopik`, `jumlah` in (10,20,30)
  - `belajar/<int:sesi_id>/<int:nomor>/` GET → `soal_belajar` (`belajar_soal`)
  - `belajar/<int:sesi_id>/<int:nomor>/jawab/` POST → `jawab_belajar` (`belajar_jawab`), membalas partial `_umpan_balik.html`
  - `belajar/<int:sesi_id>/ringkasan/` GET → `ringkasan_belajar` (`belajar_ringkasan`)
- Consumes: `rakit_sesi_belajar`, `simpan_jawaban`, `boleh_belajar_paket`, `boleh_belajar_subtopik`

- [ ] **Step 1: Tulis tes yang gagal:**
  - `test_halaman_soal_belum_jawab_tanpa_kunci`
  - `test_jawab_balas_kunci_dan_pembahasan`: partial memuat `"Kunci jawaban"`, `"Jawabanmu"`, dan ketiga teks pembahasan
  - `test_trial_tidak_boleh_subtopik`: POST subtopik oleh trial → 403
  - `test_trial_boleh_paket_trial`
  - `test_ringkasan_persen_per_subtopik`: 3 benar dari 4 di "Silogisme" menghasilkan `"75%"`
- [ ] **Step 2:** Jalankan tesnya. Hasil yang diharapkan: FAIL.
- [ ] **Step 3:** Implementasikan.
- [ ] **Step 4:** Build CSS, lalu jalankan tes PASS.
- [ ] **Step 5:** Commit `feat(cpns): mode belajar`.

---

### Task 12: Dasbor, riwayat, dan laporkan soal

**Files:**
- Create: `apps/cpns/views/dasbor.py`, `templates/cpns/dasbor.html` (layar 03), `templates/cpns/riwayat.html`
- Modify: `apps/cpns/urls.py`. Untuk sementara `''` → `dasbor` kalau sudah login; kalau belum, ke halaman masuk akun yang ada. Beranda publik dibuat di Rencana 2.
- Modify: `apps/cpns/tests/test_routing.py`. `GET /` di host cpns untuk tamu sekarang 302 ke `/accounts/login/?next=/`; untuk user login, 302 ke `/dasbor/`.
- Test: `apps/cpns/tests/test_dasbor.py`

**Interfaces:**
- Route:
  - `dasbor/` → `dasbor` (`dasbor`)
  - `riwayat/` → `riwayat` (`riwayat`)
  - `soal/<int:soal_id>/laporkan/` POST → `laporkan_soal` (`laporkan`). Hanya untuk user yang pernah mendapat soal itu di salah satu sesinya; selain itu 403.
- Dasbor menampilkan:
  - lencana "Akun Trial" atau "Premium sampai <tanggal>"
  - kartu "Lanjutkan ujian" kalau ada CAT berjalan
  - kartu SKD dan SKB (SKB nonaktif bertuliskan "Segera tersedia")
  - paket trial dengan progres
  - keadaan kosong skor, berbunyi persis: "Belum ada simulasi" dan "Setelah simulasi pertama, skor TWK, TIU, TKP dan jarak ke ambang batas muncul di sini."

- [ ] **Step 1: Tulis tes yang gagal:**
  - `test_dasbor_keadaan_kosong`
  - `test_dasbor_ada_lanjutkan_ujian`
  - `test_dasbor_skb_segera_tersedia`
  - `test_dasbor_user_lama_tanpa_akses_200` (Review Focus 4)
  - `test_laporkan_soal_tersimpan`
  - `test_laporkan_soal_bukan_miliknya_403`
  - `test_riwayat_hanya_milik_sendiri`
- [ ] **Step 2:** Jalankan tesnya. Hasil yang diharapkan: FAIL.
- [ ] **Step 3:** Implementasikan.
- [ ] **Step 4:** Build CSS, lalu jalankan tes PASS dan seluruh `manage.py test` juga PASS.
- [ ] **Step 5:** Commit `feat(cpns): dasbor, riwayat, laporkan soal`.

---

### Task 13: Verifikasi browser dan Delivery Gate antislop

**Files:**
- Create: `anti-slop/audit-003-<tanggal>.md` berisi laporan Delivery Gate dan hasil klik satu per satu
- Data uji lokal: `python manage.py shell` membuat superuser uji, soal tayang 30/35/45 dari pabrik tes, dan paket trial. **Hanya di database lokal.**

- [ ] **Step 1:** Jalankan server lokal (`ags-django` di `.claude/launch.json` induk, port 8010, `cpns.localhost`).
- [ ] **Step 2:** Klik alur ini di lebar 375, 768, dan 1280 px: dasbor → mulai SKD → jawab 3 soal → refresh (jawaban dan timer tetap) → daftar soal → kumpulkan → hasil (superuser: pembahasan muncul) → belajar paket trial → jawab → umpan balik → laporkan. Hasil yang diharapkan:
  - tidak ada overflow (`scrollWidth == clientWidth`)
  - tidak ada target di bawah 44 px
  - konsol bersih
- [ ] **Step 3:** Uji keyboard: Tab sampai ke opsi, Enter memilih, Escape menutup panel, Ctrl+C tidak memilih.
- [ ] **Step 4:** Matikan jaringan di DevTools, pilih jawaban (indikator "Gagal, mencoba lagi"), nyalakan lagi (indikator "Tersimpan"), lalu pastikan jawabannya ada di database.
- [ ] **Step 5:** Tulis laporan Delivery Gate (Hard Gate, Purpose-Gate, Liveliness, Craftsmanship) dengan bukti per butir.
- [ ] **Step 6:** Commit `docs(cpns): laporan verifikasi rencana 1`. **Tidak di-deploy.** Deploy dilakukan di Rencana 4.
