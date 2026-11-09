# Daftar Periksa Rilis CPNS Hub

Dokumen ini dipakai saat CPNS Hub baru dipasang di `cpns.agunggumelarsaputra.com`. Ikuti urutannya dari atas ke bawah. Setiap langkah yang menyentuh server baru dijalankan setelah pemilik menyetujuinya.

## A. Tugas pemilik sebelum deploy

1. **Syarat Layanan dan Kebijakan Privasi.** Baca kedua halaman. Isi `[KEBIJAKAN PENGEMBALIAN DANA]` dan `[NAMA DAN KONTAK PENGELOLA]`, lalu hapus kalimat "Draf, menunggu tinjauan pengelola.". Lokasinya `templates/cpns/publik/syarat.html` dan `templates/cpns/publik/privasi.html`.
2. **Google Cloud Console.** Tambahkan alamat balik ini pada OAuth client yang sama dengan situs utama:
   `https://cpns.agunggumelarsaputra.com/accounts/oauth/google/callback/`
3. **Admin produksi** (setelah deploy). Buka Django Admin, lalu isi Pengaturan CPNS: nomor WhatsApp, harga per durasi, dan pesan WA.
4. **Opsional:** nomor KepmenPAN-RB sebagai sumber ambang batas SKD. Tidak memblokir rilis.

## B. Isi `.env` di server

File `.env` ada di folder repo di VPS. Nilai rahasia tidak pernah ditulis di repo.

**Wajib ada:**
- `DJANGO_SECRET_KEY`: kunci acak baru, minimal 50 karakter. Tidak boleh diawali `django-insecure-`. Mengganti kunci membuat semua orang keluar dari akun satu kali, dan itu wajar.
- `DB_PASSWORD`: harus sama dengan kata sandi yang sudah dipakai database Postgres sekarang.
- `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD`: isinya sama dengan `DB_NAME`, `DB_USER`, dan `DB_PASSWORD`.

**Sebaiknya diisi:** `DB_NAME`, `DB_USER`, `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET`, `GURU_EMAILS`.

**Periksa, lalu hapus atau betulkan kalau ada:**
- `ALLOWED_HOSTS`: tidak boleh `*`, dan tidak boleh hanya berisi localhost. Kalau ragu, hapus saja supaya nilai bawaan yang aman dipakai.
- `CSRF_TRUSTED_ORIGINS`: hapus supaya nilai bawaan `https://` yang dipakai.
- `DATABASE_URL`: hapus kalau ada. Server memakai `DB_*`.
- `SESSION_COOKIE_SECURE` dan `CSRF_COOKIE_SECURE`: hapus, atau isi `True`.
- `SECURE_SSL_REDIRECT`: hapus, atau isi `False`, karena nginx yang mengalihkan ke https.
- `CPNS_URL`: hapus, atau isi `https://cpns.agunggumelarsaputra.com/`.
- `SECURE_HSTS_SECONDS`: hapus, atau isi angka bulat. Mulai dari 3600.

**Catatan:** kalau nilai berisi tanda `$`, bungkus dengan kutip tunggal.

## C. Pemeriksaan nginx

Untuk kedua domain (`agunggumelarsaputra.com` dan `cpns.agunggumelarsaputra.com`):
- `proxy_set_header Host $host;`
- `proxy_set_header X-Forwarded-Proto $scheme;`
- http dialihkan ke https.

Tanpa header Host, setiap halaman akan menjawab 400 karena domain sekarang didaftar satu per satu.

## D. Urutan deploy

1. **Uji di Postgres.** Jalankan suite tes di kontainer Postgres sementara. Ini tidak menyentuh database produksi.
2. **Pemeriksaan hanya baca.** Periksa cabang dan commit di VPS, nama-nama kunci `.env` (tanpa nilainya), konfigurasi nginx, dan status kontainer.
3. **Backup database:**
   `docker exec ags-postgres pg_dump -U <DB_USER> <DB_NAME> > ~/backup/ags_db-<tanggal>.sql`
4. **Gabung ke master**, lalu push ke GitHub.
5. **Lengkapi `.env`** sesuai bagian B.
6. **Perbarui kode di VPS** (fast-forward), lalu jalankan `docker compose up -d --build web`. Pantau log sampai migrasi, collectstatic, dan gunicorn berjalan.
7. **Periksa data produksi:**
   - `docker exec ags-django-app python manage.py cpns_cek_produksi`
   - `docker exec ags-django-app python manage.py cpns_impor_soal_lama --coba`

   Bandingkan angka "Dilewati karena sama" dengan jumlah soal lama, lalu periksa beberapa contoh. Normalisasi teks mengabaikan simbol, jadi "12 + 3" dan "12 - 3" dianggap sama. Setelah setuju, jalankan tanpa `--coba`. Cukup **sekali saja**.
8. **Uji asap di browser** tanpa login:
   - beranda, masuk, daftar, premium, syarat, privasi;
   - alamat lama `/exam/...` harus menjawab 301;
   - situs sekolah tetap jalan;
   - konsol browser bersih.

## E. Cara mundur kalau ada masalah

1. **Kode:** di VPS, `git reset --hard <commit sebelum deploy>`, lalu `docker compose up -d --build web`.
2. **Database** (hanya kalau migrasi merusak data): hentikan kontainer web, pulihkan backup dengan `psql`, lalu jalankan web lagi dengan kode lama.
3. **`.env`:** kembalikan dari salinan yang dibuat sebelum langkah D.5.

## Catatan rilis

(Diisi setelah deploy: tanggal, commit, hasil `cpns_cek_produksi`, jumlah soal lama yang disalin, dan hasil uji asap.)
