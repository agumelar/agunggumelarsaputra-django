# Daftar Periksa Rilis CPNS Hub

Dokumen ini dipakai saat CPNS Hub baru dipasang di `cpns.agunggumelarsaputra.com`. Ikuti urutannya dari atas ke bawah. Setiap langkah yang menyentuh server baru dijalankan setelah pemilik menyetujuinya.

Tanda `<...>` berarti ganti dengan nilai Anda. Nilai rahasia tidak pernah ditulis di dokumen ini.

## A. Tugas pemilik sebelum deploy

1. **Syarat Layanan dan Kebijakan Privasi.** Baca kedua halaman. Isi `[KEBIJAKAN PENGEMBALIAN DANA]` dan `[NAMA DAN KONTAK PENGELOLA]`, lalu hapus kalimat "Draf, menunggu tinjauan pengelola.". Lokasinya `templates/cpns/publik/syarat.html` dan `templates/cpns/publik/privasi.html`.
   - Teks yang Anda tulis tidak boleh memuat kata "resmi". Ada tes yang memeriksa kata itu di halaman publik, dan situs ini bukan layanan pemerintah.
2. **Google Cloud Console.** Tambahkan alamat balik ini pada OAuth client yang sama dengan situs utama:
   `https://cpns.agunggumelarsaputra.com/accounts/oauth/google/callback/`
3. **Admin produksi** (setelah deploy). Buka Django Admin, lalu isi Pengaturan CPNS: nomor WhatsApp, harga per durasi, dan pesan WA.
4. **Opsional:** nomor KepmenPAN-RB sebagai sumber ambang batas SKD. Tidak memblokir rilis.

## B. Isi `.env` di server

File `.env` ada di folder repo di VPS. Nilai rahasia tidak pernah ditulis di repo. Contoh lengkapnya ada di `.env.example`: bagian WAJIB berisi `[ISI]`, bagian OPSIONAL berupa baris komentar.

Server produksi menolak start kalau ada nilai yang masih berisi `[ISI]`. Pesannya menyebut nama variabelnya, misalnya `DB_NAME masih berisi [ISI]. Isi nilainya atau hapus barisnya.`

**Wajib ada:**
- `DJANGO_SECRET_KEY`: kunci acak baru, minimal 50 karakter. Tidak boleh diawali `django-insecure-`. Buat dengan perintah ini (di komputer mana saja yang punya Python):

  ```
  python -c "import secrets; print(secrets.token_urlsafe(64))"
  ```

  Mengganti kunci membuat semua orang keluar dari akun satu kali, dan itu wajar.
- `DB_NAME`, `DB_USER`, `DB_PASSWORD`: `DB_PASSWORD` harus sama dengan kata sandi yang sudah dipakai database Postgres sekarang.
- `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD`: isinya sama dengan `DB_NAME`, `DB_USER`, dan `DB_PASSWORD`.

**Sebaiknya diisi:** `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET`. Tanpa keduanya tombol Masuk dengan Google tidak jalan.

**Biarkan sebagai komentar** kecuali perlu nilai lain: `ALLOWED_HOSTS`, `CSRF_TRUSTED_ORIGINS`, `SECURE_HSTS_SECONDS`, `CPNS_URL`, `GURU_EMAILS`. Nilai bawaannya sudah aman.

**Periksa, lalu hapus atau betulkan kalau ada:**
- `ALLOWED_HOSTS`: tidak boleh `*`, dan tidak boleh hanya berisi localhost. Kalau ragu, hapus saja supaya nilai bawaan yang aman dipakai.
- `CSRF_TRUSTED_ORIGINS`: hapus supaya nilai bawaan `https://` yang dipakai.
- `DATABASE_URL`: hapus kalau ada. Server memakai `DB_*`.
- `SESSION_COOKIE_SECURE` dan `CSRF_COOKIE_SECURE`: hapus, atau isi `True`.
- `SECURE_SSL_REDIRECT`: hapus, atau isi `False`, karena nginx yang mengalihkan ke https.
- `CPNS_URL`: hapus, atau isi `https://cpns.agunggumelarsaputra.com/`.
- `SECURE_HSTS_SECONDS`: hapus, atau isi bilangan bulat. Mulai dari 3600. Nilai seperti `1 jam` atau `3600.5` membuat server menolak start.

**Catatan:** kalau nilai berisi tanda `$`, bungkus dengan kutip tunggal.

## C. Pemeriksaan nginx dan TLS

Untuk kedua domain (`agunggumelarsaputra.com` dan `cpns.agunggumelarsaputra.com`):
- `proxy_set_header Host $host;`
- `proxy_set_header X-Forwarded-Proto $scheme;`
- http dialihkan ke https.
- Catat target `proxy_pass` di laporan rilis (contoh: `http://127.0.0.1:8080`). Target ini dipakai di langkah port di bawah.

Tanpa header Host, setiap halaman akan menjawab 400 karena domain sekarang didaftar satu per satu. Akibat yang sama: membuka situs lewat `http://<IP VPS>:8080` akan menjawab 400. Itu wajar, buka lewat nama domain.

**TLS untuk cpns.** Sertifikat harus valid untuk subdomain cpns. Jalankan dari VPS atau komputer Anda:

```
curl -I https://cpns.agunggumelarsaputra.com/
```

Hasil yang benar: ada baris `HTTP/` dengan status 200 atau 30x, tanpa galat sertifikat. Kalau muncul galat SSL, perbaiki sertifikat dulu sebelum lanjut.

**Saran batas laju di nginx** (tindak lanjut, tidak memblokir rilis). Aplikasi sudah membatasi percobaan login per akun, tetapi nginx bisa menahan banjir permintaan lebih awal. Pasang `limit_req` untuk tiga alamat login ini di kedua domain:
- `/admin/login/`
- `/accounts/login/`
- `/masuk/`

Contoh: `limit_req_zone $binary_remote_addr zone=login:10m rate=10r/m;` di blok `http`, lalu `limit_req zone=login burst=5 nodelay;` di blok `location` untuk alamat-alamat tadi.

**Saran port** (tindak lanjut). Sekarang `docker-compose.yml` membuka port `8080:8000` ke semua alamat. Setelah memastikan `proxy_pass` nginx memakai `127.0.0.1:8080`, pertimbangkan mengganti menjadi `127.0.0.1:8080:8000` supaya port 8080 tidak bisa dibuka dari luar.

## D. Urutan deploy

### D.1 Uji di Postgres

Suite tes dijalankan di kontainer Postgres sementara. Ini tidak menyentuh database produksi. Kerjakan di VPS, di folder terpisah (`~/uji-cpns`), **bukan** di folder repo yang sedang dipakai situs.

1. **Ambil kode branch fitur.** Pilih salah satu:
   - Push branch fitur dulu (butuh persetujuan pemilik), lalu di VPS:

     ```
     git clone --branch feat/cpns-hub-4 --depth 1 <alamat repo GitHub> ~/uji-cpns
     ```

   - Atau tanpa push: di komputer lokal buat bundle, kirim ke VPS, lalu clone dari bundle:

     ```
     git bundle create cpns-hub-4.bundle feat/cpns-hub-4
     scp cpns-hub-4.bundle ubuntu@<IP VPS>:~/
     ```

     Di VPS:

     ```
     git clone --branch feat/cpns-hub-4 ~/cpns-hub-4.bundle ~/uji-cpns
     ```

2. **Nyalakan Postgres sementara:**

   ```
   docker network create uji-cpns
   docker run -d --rm --name uji-pg --network uji-cpns -e POSTGRES_PASSWORD=uji -e POSTGRES_DB=uji postgres:17-alpine
   until docker exec uji-pg pg_isready -U postgres; do sleep 1; done
   ```

3. **Bangun image dari clone tadi:**

   ```
   cd ~/uji-cpns
   docker build -t uji-cpns .
   ```

4. **Jalankan suite tes:**

   ```
   docker run --rm --network uji-cpns --entrypoint python -e DATABASE_URL=postgres://postgres:uji@uji-pg:5432/uji -e DJANGO_SETTINGS_MODULE=config.settings.uji_postgres uji-cpns manage.py test
   ```

   Hasil yang benar: baris terakhir `OK`. Tes konkurensi di `apps/cpns/tests/test_postgres.py` hanya jalan di sini, jadi jumlah tes yang dilewati lebih sedikit daripada di laptop.

5. **Bersihkan:**

   ```
   docker stop uji-pg
   docker network rm uji-cpns
   docker rmi uji-cpns
   rm -rf ~/uji-cpns ~/cpns-hub-4.bundle
   ```

### D.2 Pemeriksaan hanya baca

Tidak ada perintah di langkah ini yang menulis ke database.

1. Periksa cabang dan commit di VPS, nama-nama kunci `.env` (tanpa nilainya, contoh `cut -d= -f1 .env`), konfigurasi nginx, dan status kontainer (`docker compose ps`).
2. **Kata sandi akun superuser seed.** Seed lama membuat akun admin dengan kata sandi bawaan lama yang ada di riwayat git. Periksa apakah akun itu masih memakainya. Perintah ini meminta Anda mengetik kata sandi bawaan lama tersebut (tidak tampil di layar) dan hanya membandingkan, tanpa menyimpan apa pun:

   ```
   docker exec -it ags-django-app python manage.py shell -c "import getpass; from django.contrib.auth import get_user_model; from django.contrib.auth.hashers import check_password; u = get_user_model().objects.filter(email__iexact='agumelarsaputra@gmail.com').first(); print('Akun tidak ada' if u is None else ('MASIH KATA SANDI BAWAAN, segera ganti' if check_password(getpass.getpass('Kata sandi bawaan lama: '), u.password) else 'Bukan kata sandi bawaan'))"
   ```

   Kalau hasilnya "MASIH KATA SANDI BAWAAN", ganti setelah deploy dengan `docker exec -it ags-django-app python manage.py changepassword <username>`. Seed baru tidak lagi memasang kata sandi dan tidak mengubah akun yang sudah ada.
3. **Daftar akun staf dan superuser** untuk ditinjau. Setiap akun yang tidak dikenal atau tidak dipakai sebaiknya dinonaktifkan lewat admin:

   ```
   docker exec -i ags-django-app python manage.py shell <<'EOF'
   from django.contrib.auth import get_user_model
   from django.db.models import Q
   for u in get_user_model().objects.filter(Q(is_staff=True) | Q(is_superuser=True)).order_by("pk"):
       print(u.username, "staf" if u.is_staff else "-", "superuser" if u.is_superuser else "-",
             "sandi aktif" if u.has_usable_password() else "tanpa sandi", u.last_login)
   EOF
   ```

   Kalau akun `guru_agung` dari seed lama belum pernah diberi kata sandi, akun itu tetap tampil "sandi aktif" walaupun kata sandinya kosong dan tidak bisa dipakai masuk. Agar rapi, nonaktifkan kata sandinya lewat admin.
4. **Soal lama dengan sidik sama tetapi isi berbeda.** Impor soal lama melewati soal yang teksnya sama (sidik sama). Kalau dua soal teksnya sama tetapi opsi, kunci, atau bobotnya beda, salah satunya akan hilang diam-diam. Periksa sebelum impor sungguhan:

   ```
   docker exec -i ags-django-app python manage.py shell <<'EOF'
   from collections import defaultdict
   from apps.cpns.impor_lama import _bentuk
   from apps.cpns.models import CpnsQuestion, Soal

   def isi(s):
       return repr((s.opsi_a, s.opsi_b, s.opsi_c, s.opsi_d, s.opsi_e, s.kunci, s.bobot))

   grup = defaultdict(list)
   for s in Soal.objects.all():
       grup[s.sidik_teks].append(("bank", s.pk, isi(s)))
   for q in CpnsQuestion.objects.select_related("package"):
       s = _bentuk(q)
       grup[s.hitung_sidik()].append(("lama", q.pk, isi(s)))
   n = 0
   for anggota in grup.values():
       if any(a[0] == "lama" for a in anggota) and len({a[2] for a in anggota}) > 1:
           n += 1
           print(", ".join(f"{a[0]} #{a[1]}" for a in anggota))
   print(f"Grup sidik sama tetapi opsi/kunci/bobot beda: {n}")
   EOF
   ```

   Kalau angkanya bukan 0, buka soal-soal yang disebut (nomor `lama #` adalah id soal lama, `bank #` id di bank soal) dan putuskan mana yang benar sebelum langkah D.7.

### D.3 Backup database

```
mkdir -p ~/backup
docker exec ags-postgres pg_dump -U <DB_USER> -Fc <DB_NAME> > ~/backup/ags_db-<tanggal>.dump
ls -lh ~/backup/
```

Pastikan ukuran file tidak 0 sebelum lanjut. Cara memulihkannya ada di bagian E.

### D.4 Gabung ke master, lalu push ke GitHub

### D.5 Lengkapi `.env`

Simpan salinan dulu, lalu ubah sesuai bagian B:

```
cp .env .env.bak-<tanggal>
```

**Kalau `POSTGRES_*` berubah.** Kalau `POSTGRES_DB`, `POSTGRES_USER`, atau `POSTGRES_PASSWORD` di `.env` berbeda dari yang dipakai kontainer `ags-postgres` sekarang, `docker compose up` di langkah D.6 akan membuat ulang kontainer database. Data tetap aman di volume `ags_pgdata`. Nilai `POSTGRES_*` hanya dipakai saat volume masih kosong, jadi kata sandi di dalam database tidak ikut berubah. Karena itu `DB_PASSWORD` dan `POSTGRES_PASSWORD` harus sama dengan kata sandi yang sudah ada. Urutannya: backup D.3 sudah ada, lalu D.6, lalu pastikan `docker compose ps` menunjukkan `ags-postgres` berjalan sebelum melihat log web.

### D.6 Perbarui kode di VPS

1. Fast-forward kode: `git pull --ff-only`.
2. Bangun image baru: `docker compose build web`.
3. Lihat migrasi yang akan dijalankan, tanpa menjalankannya:

   ```
   docker compose run --rm --no-deps --entrypoint python web manage.py migrate --plan
   ```

   Pastikan daftarnya sesuai dugaan (migrasi accounts dan cpns dari branch ini). Kalau ada migrasi yang menghapus tabel atau kolom berisi data, berhenti dan tanyakan dulu.
4. Nyalakan: `docker compose up -d web`. Pantau log (`docker compose logs -f web`) sampai migrasi, collectstatic, dan gunicorn berjalan. Seed sekarang mencetak "Akun admin dibuat tanpa kata sandi" hanya kalau akun admin belum ada.
5. Pemeriksaan keamanan Django di kontainer baru:

   ```
   docker exec ags-django-app python manage.py check --deploy
   ```

   Hasil yang benar: tanpa galat (ERROR). Peringatan (WARNING) dicatat di laporan rilis.

### D.7 Periksa data produksi

- `docker exec ags-django-app python manage.py cpns_cek_produksi`
- `docker exec ags-django-app python manage.py cpns_impor_soal_lama --coba`

Butir "Akun staf/guru" menyebut setiap akun staf, superuser, atau guru yang masih punya kata sandi. Pastikan semuanya milik orang yang sah dan kata sandinya dibuat sendiri.

Bandingkan angka "Dilewati karena sama" dengan jumlah soal lama, lalu periksa beberapa contoh. Normalisasi teks mengabaikan simbol, jadi "12 + 3" dan "12 - 3" dianggap sama. Hasil kueri di D.2 butir 4 harus sudah ditangani. Setelah setuju, jalankan tanpa `--coba`. Cukup **sekali saja**.

Soal lama masuk dengan status draf. Subtopiknya diambil apa adanya dari data lama, jadi sebelum menyetujui soal untuk tayang, samakan subtopiknya dengan kisi-kisi (`docs/cpns/kisi-kisi.md`) lewat halaman Edit soal.

### D.8 Uji asap di browser tanpa login

- beranda, masuk, daftar, premium, syarat, privasi;
- alamat lama `/exam/...` harus menjawab 301;
- situs sekolah tetap jalan;
- konsol browser bersih.

## E. Cara mundur kalau ada masalah

1. **Kode:** di VPS, `git reset --hard <commit sebelum deploy>`, lalu `docker compose up -d --build web`.
2. **Database** (hanya kalau migrasi merusak data): hentikan kontainer web (`docker compose stop web`), pulihkan backup D.3, lalu jalankan web lagi dengan kode lama:

   ```
   docker exec -i ags-postgres pg_restore -U <DB_USER> -d <DB_NAME> --clean --if-exists < ~/backup/ags_db-<tanggal>.dump
   ```

3. **`.env`:** kembalikan dari salinan D.5: `cp .env.bak-<tanggal> .env`.

## F. Catatan keamanan yang belum selesai

- **Kata sandi database lama ada di riwayat git.** Versi lama `docker-compose.yml` dan skrip pernah memuat kata sandi database secara langsung. File sekarang sudah bersih, tetapi riwayat git masih menyimpannya. Risikonya kecil karena port 5432 tidak dibuka ke luar (layanan `db` tidak punya `ports`), tetapi kata sandi itu tetap harus dianggap bocor. Tindak lanjut setelah rilis stabil: ganti kata sandi dengan `ALTER USER <DB_USER> WITH PASSWORD '<kata sandi baru>';` di dalam `ags-postgres`, lalu perbarui `DB_PASSWORD` dan `POSTGRES_PASSWORD` di `.env` dan jalankan ulang web.
- **Kata sandi bawaan admin dari seed lama** juga ada di riwayat git. Langkah D.2 butir 2 memeriksanya.

## Catatan rilis

(Diisi setelah deploy: tanggal, commit, hasil `cpns_cek_produksi`, jumlah soal lama yang disalin, dan hasil uji asap.)
