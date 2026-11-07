# Audit cpns.agunggumelarsaputra.com — 7 November 2026

Projek: `agunggumelarsaputra-django` (commit terakhir `f1e0312`, 8 Okt 2026)
Bagian yang diaudit: `apps/cpns/`, `config/cpns_urls.py`, `templates/cpns/`, situs live.

Cara cek:
- membaca seluruh kode app cpns
- menjalankan 11 tes app cpns (semua lolos)
- membaca isi bank soal di database lokal
- mengirim input aneh ke form kirim jawaban di lokal (bukan ke server live)
- mengecek situs live tanpa mengubah data. Hanya membuka halaman, tidak pernah mengirim jawaban.

Fakta di situs live:
- Halaman login di subdomain cpns selalu error 500. Di domain utama, login normal.
- Paket SKD berisi 110 soal, tapi hanya 45 yang berbeda. Paket SKB Guru berisi 100 soal, tapi hanya 5 yang berbeda.
- Kunci jawaban ikut terkirim ke halaman di mode Drilling.

---

## Status perbaikan (7 Nov 2026, belum di-commit, belum di-deploy)

| No | Temuan | Status |
|---|---|---|
| 1 | Login 500 di subdomain cpns | **Diperbaiki.** `config/cpns_urls.py` sekarang ikut mendaftarkan semua rute situs utama |
| 5 | Kirim jawaban error 500 | **Diperbaiki.** Input rusak ditolak dengan status 400. Jawaban selain A–E atau soal dari paket lain dibuang |
| 10 | Label mode selalu "Simulasi CAT" | **Diperbaiki** |
| 11 | Mode tidak divalidasi | **Diperbaiki.** Mode tak dikenal di halaman ujian menjadi Simulasi; saat kirim jawaban ditolak 400 |
| baru | `?next=` di login bisa mengarahkan ke situs luar (open redirect) | **Diperbaiki** di `apps/accounts/views.py` dengan `url_has_allowed_host_and_scheme` |

- Tes baru: `apps/cpns/tests/test_hardening.py` (13 tes).
- Seluruh tes projek: 97 tes lolos.
- Langkah setelah deploy:
  - Login Google dari cpns memakai alamat balik `https://cpns.agunggumelarsaputra.com/accounts/google/callback/`. Alamat ini harus didaftarkan di Google Cloud Console. Kalau belum terdaftar, Google akan menolak dengan pesan `redirect_uri_mismatch`.
  - Login di cpns hanya berlaku di cpns. Supaya satu kali login berlaku di kedua domain, perlu `SESSION_COOKIE_DOMAIN`. Ini belum dikerjakan.

---

## KRITIS — perbaiki dulu

### 1. Tombol "Masuk Akun" di cpns error 500
- Gejala: `https://cpns.agunggumelarsaputra.com/accounts/login/` selalu menampilkan "Server Error (500)".
- Penyebab: halaman login memakai navbar utama. Navbar itu memanggil `{% url 'pembelajaran:modul_list' %}` ([navbar.html:29](../templates/components/navbar.html), juga baris 175). Di `config/cpns_urls.py`, namespace `pembelajaran` tidak terdaftar, jadi muncul `NoReverseMatch`.
- Akibat: peserta tidak bisa login di cpns. XP, riwayat, dan skor terbaik tidak pernah tersimpan atas nama akun.
- Masalah tambahan: `SESSION_COOKIE_DOMAIN` belum diatur. Orang yang login di domain utama tetap dianggap tamu di cpns.
- Saran perbaikan:
  - Arahkan tombol login di cpns ke `https://agunggumelarsaputra.com/accounts/login/?next=https://cpns.agunggumelarsaputra.com/...`.
  - Atur `SESSION_COOKIE_DOMAIN = '.agunggumelarsaputra.com'` dan `CSRF_COOKIE_DOMAIN` yang sama.
  - Cara lain: daftarkan semua namespace yang dipakai navbar ke `cpns_urls.py`.

### 2. Bank soal penuh duplikat
| Paket | Jumlah soal | Soal berbeda | Keterangan |
|---|---|---|---|
| SKD-BKN-01 | 110 | **45** | TWK 15 soal diulang 2x, TIU 15 soal diulang sampai 35, TKP 15 soal diulang 3x |
| SKB-GURU-01 | 100 | **5** | 5 soal, masing-masing diulang 20x |

- Penyebab: `seed_cpns_starter.py` mengisi paket penuh dengan `src = pool[i % len(pool)]` (baris sekitar 621, 645, 669, 781).
- Akibat: peserta mengerjakan soal yang sama berulang kali. Skor tidak menggambarkan kemampuan yang sebenarnya.
- Saran: tambah soal sampai jumlahnya benar-benar 110 dan 100 soal berbeda. Selama soalnya belum cukup, tampilkan jumlah apa adanya (misalnya "45 soal").

### 3. Kunci jawaban mudah ditebak
- SKB Guru: kuncinya hanya A, B, atau C. Tidak pernah D atau E.
- Dengan menjawab **B semua**, peserta mendapat 200 poin dan dinyatakan **LULUS** (ambang batas 70).
- SKD: tidak ada satu pun kunci E, dan 46% kuncinya B. Jawab B semua menghasilkan TWK 80 (lolos) dan TKP 174 (lolos).
- Drill TIU: kuncinya hanya A, B, atau C.
- Saran:
  - Sebar kunci merata dari A sampai E.
  - Acak urutan opsi untuk setiap peserta, dan simpan pemetaan acakannya di server.
  - Naikkan ambang batas SKB supaya masuk akal. Saat ini 70 dari 500.

### 4. Bisa curang dan menimbun XP
- Mode Simulasi bisa dibocorkan: buka `?mode=DRILLING_BEBAS`, maka **semua kunci jawaban ada di source halaman**. Ini terbukti di live.
- Mode diambil dari form, jadi orang bisa menyalin kunci lalu mengirim jawaban dengan `mode=SIMULASI_CAT`.
- Form kirim jawaban (`cpns_cbt_submit_view`) bisa dipakai berkali-kali tanpa batas. Setiap kiriman, termasuk lembar kosong, memberi XP minimal `xp_base + 5`. Kiriman yang lulus mendapat +20.
- Saran:
  - Buat sesi ujian di server ("attempt dimulai") dengan token, lalu cocokkan saat jawaban dikirim.
  - Untuk Simulasi, ambil mode dari server, bukan dari form.
  - Beri XP sekali per paket per hari, atau hanya kalau skor naik.
  - Beri batas jumlah kiriman (rate limit).
  - Di mode Drilling, kirim pembahasan per soal lewat permintaan terpisah setelah peserta menjawab, jangan sekaligus di awal.

---

## TINGGI

### 5. Kirim jawaban bisa error 500 (terbukti di lokal)
| Input | Hasil |
|---|---|
| `answers_payload=[]` | `AttributeError: 'list' object has no attribute 'get'` |
| `time_spent_seconds=abc` | `ValueError` |
| `time_spent_seconds=-5` | `IntegrityError: CHECK constraint failed: waktu_detik` |
| nilai jawaban bukan teks, misalnya `{"<id soal>": 5}` | `.upper()` gagal |

- Saran: periksa bahwa isinya `dict` dengan nilai `A` sampai `E`, waktunya `int` di antara 0 dan durasi, dan modenya salah satu dari dua pilihan.

### 6. Jawaban hilang kalau halaman di-refresh
- Ujian 110 soal selama 100 menit. Kalau tab tertutup, halaman di-refresh, atau sinyal putus, semua jawaban hilang.
- Tidak ada penyimpanan otomatis dan tidak ada peringatan sebelum keluar (`beforeunload`).
- Saran: simpan jawaban ke `localStorage` setiap kali memilih, dan pulihkan saat halaman dibuka lagi. Lebih baik lagi kalau disimpan juga ke server berkala.

### 7. Timer hanya berjalan di browser
- `setInterval` mengurangi 1 detik setiap tik. Di tab latar belakang, browser memperlambat tik ini, jadi waktunya molor.
- Server tidak memeriksa batas waktu. `waktu_detik` dikirim dari browser dan bisa diisi sembarang.
- Di mode Drilling, `timeSpent` tidak pernah bertambah, sehingga durasi selalu 0.
- Saran: simpan jam mulai di server, lalu hitung sisa waktu dari `deadline - Date.now()`.

### 8. Klaim "resmi" dan "soal autentik BKN" menyesatkan
- Teks yang dipakai: "Simulasi Resmi SKD CAT BKN", "simulator CAT resmi", "Bank Soal BKN", dan pesan seed "bank soal autentik BKN".
- Soal asli BKN bersifat rahasia. Soal di sini buatan sendiri.
- Klaim seperti ini berisiko hukum dan menyesatkan peserta.
- Saran: ganti dengan "Tryout / Latihan SKD sesuai kisi-kisi PermenPAN-RB". Tambahkan kalimat "tidak berafiliasi dengan BKN".
- `scrape_cpns.py` sebaiknya dihapus:
  - mengambil soal dari situs lain berisiko hak cipta
  - parsernya selalu mengisi kunci `'A'`, jadi soal yang masuk pasti salah kunci

### 9. Situs lambat dan kadang tidak merespons
- Waktu tunggu awal (TTFB) 1–4 detik untuk setiap halaman.
- Selama pengecekan, beberapa permintaan putus atau timeout (lebih dari 45–90 detik), termasuk halaman ujian.
- Dugaan:
  - database berada jauh dari server (di `.env` ada URL Neon)
  - worker gunicorn terlalu sedikit
  - atau koneksi saya sendiri
- Perlu dicek di VPS lewat `journalctl` / log gunicorn dan log nginx.

---

## SEDANG

10. **Label mode selalu "Simulasi CAT"**: `{{ mode|yesno:"Simulasi CAT,Drilling Bebas" }}` di `cbt_room.html`. Teks yang tidak kosong selalu dianggap "ya", jadi mode Drilling ikut berlabel "Simulasi CAT".
11. **Mode tidak divalidasi**: `?mode=XYZ` membuka ujian tanpa timer dan tanpa pembahasan, lalu nilai `XYZ` tersimpan ke database.
12. **Sorotan tab filter hasil tidak pindah**: setelah filter HTMX diklik (Semua / Salah / TWK…), tombol "Semua Butir" tetap tersorot karena tombolnya berada di luar area yang diganti.
13. **Bobot TKP tidak realistis**: ada dua opsi bernilai sama, misalnya `{'A':3,'B':1,'C':5,'D':2,'E':1}`. Di TKP BKN, kelima opsi bernilai 1–5 yang berbeda. Opsi C sering bernilai 5.
14. **Angka ditulis langsung di template**:
    - ambang batas 65/80/166 di `package_detail.html`, tidak memakai field paket
    - "Maksimum: 550 Poin" di halaman hasil
    - slug paket di navbar dan beranda. Kalau slug diganti, halaman 404.
15. **Skor TKP tanpa bobot tidak konsisten**: model memberi 5 poin kalau jawaban sama dengan kunci, tapi halaman review menampilkan 0.
16. **`{{ questions_json|safe }}` di dalam `<script>`**: kalau ada teks soal berisi `</script>`, halaman rusak atau bisa disusupi XSS. Risikonya rendah karena hanya admin yang mengisi soal. Ganti dengan `{{ questions|json_script:"cbt-data" }}`.
17. **Pengaturan keamanan di produksi**:
    - cookie `csrftoken` di live tidak memakai flag `Secure`
    - tidak ada header HSTS
    - `SESSION_COOKIE_SECURE`, `CSRF_COOKIE_SECURE`, dan `SECURE_SSL_REDIRECT` bawaannya `False`
    - `ALLOWED_HOSTS` bawaannya `'*'`
    - Saran: atur lewat `.env` di VPS dan tambahkan `SECURE_HSTS_SECONDS`.
18. **XP bisa hilang kalau dua kiriman bersamaan**: `request.user.xp += bonus` lalu `save()`. Gunakan `F('xp') + bonus` di dalam `transaction.atomic()` bersama pembuatan attempt.

## RENDAH / Kenyamanan pengguna

19. Di HP, menu navigasi `hidden md:flex` disembunyikan tanpa pengganti, jadi tidak ada menu sama sekali.
20. Opsi jawaban berupa `<div @click>`, tidak bisa dipilih dengan tombol Tab, dan tidak punya `role`/`aria`. Shortcut huruf tidak memeriksa tombol Ctrl/Cmd, jadi Ctrl+C ikut memilih jawaban C.
21. Durasi tampil sebagai "5400 Detik". Lebih jelas kalau ditulis "90 menit 0 detik".
22. `robots.txt`, `favicon.ico`, dan `sitemap.xml` mengembalikan 404.
23. Statistik beranda ikut menghitung soal dari paket draft. `total_questions_count` menjalankan satu query per kartu paket; bisa diganti `annotate(Count('questions'))`.
24. Tamu tidak diberi tahu bahwa hasilnya hanya tersimpan di sesi browser dan tidak menambah XP.

## Yang sudah baik
- 11 tes app cpns lolos.
- CSRF aktif di form kirim jawaban.
- Halaman hasil hanya bisa dibuka pemiliknya. Akun dicek per user, tamu dicek per session key.
- HTTP otomatis dialihkan ke HTTPS (301). Header `X-Frame-Options`, `nosniff`, dan `Referrer-Policy` sudah ada.
- Format penilaian SKD (5/0, TKP 1–5) dan ambang batas 65/80/166 sesuai aturan yang berlaku.

## Urutan perbaikan yang disarankan
1. Login cpns (#1). Perbaikan kecil yang dampaknya besar.
2. Validasi input kirim jawaban (#5), mode (#10, #11), dan penyimpanan otomatis (#6).
3. Anti-curang dan batas XP (#4).
4. Ganti klaim "resmi/autentik" (#8).
5. Tambah dan perbaiki bank soal (#2, #3, #13). Ini pekerjaan konten terbesar.
6. Pengaturan keamanan dan performa server (#9, #17).
