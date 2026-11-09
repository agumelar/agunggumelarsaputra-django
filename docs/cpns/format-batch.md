# Format batch soal

Dokumen ini dipakai sesi penulis draf. Batch adalah satu file JSON berisi daftar soal. Soal yang masuk selalu berstatus draf dan baru tayang setelah ditinjau pemilik.

## Lokasi dan nama file

`data/cpns/batch/<nama-batch>.json`, contoh `2026-11-tiu-deret-01.json`. Nama batch diambil dari nama file tanpa `.json`.

## Contoh soal TIU

```json
{
  "jenis_ujian": "SKD",
  "subtes": "TIU",
  "subtopik": "Deret Angka",
  "tingkat": "mudah",
  "teks": "Lanjutkan deret berikut: 2, 4, 8, 16, ...",
  "opsi_a": "18",
  "opsi_b": "24",
  "opsi_c": "30",
  "opsi_d": "32",
  "opsi_e": "36",
  "kunci": "D",
  "pembahasan_konsep": "Setiap suku dikali 2.",
  "pembahasan_pengecoh": "18 dan 24 hanya menambah, bukan mengali.",
  "pembahasan_cepat": "Kali 2 dari 16 hasilnya 32."
}
```

## Contoh soal TKP

```json
{
  "jenis_ujian": "SKD",
  "subtes": "TKP",
  "subtopik": "Pelayanan Publik",
  "teks": "Seorang warga datang saat jam istirahat untuk mengurus berkas. Sikap Anda ...",
  "opsi_a": "Meminta warga kembali besok",
  "opsi_b": "Meminta warga menunggu tanpa penjelasan",
  "opsi_c": "Menjelaskan jam layanan lalu mengarahkan ke petugas piket",
  "opsi_d": "Melayani sambil tetap meminta waktu singkat untuk merapikan meja",
  "opsi_e": "Segera melayani dengan ramah meski sedang istirahat",
  "bobot": {"A": 1, "B": 2, "C": 3, "D": 4, "E": 5},
  "pembahasan_konsep": "Pelayan publik mengutamakan kebutuhan warga.",
  "pembahasan_pengecoh": "A dan B menunda layanan tanpa solusi.",
  "pembahasan_cepat": "Pilih sikap yang paling membantu warga."
}
```

## Field

Wajib, semuanya teks:

- `jenis_ujian`: `SKD` atau `SKB_GURU`
- `subtes`: `TWK`, `TIU`, `TKP` (SKD), `PEDAGOGIK`, `MATERI_RPL` (SKB_GURU)
- `subtopik`: harus sama persis dengan nama di `docs/cpns/kisi-kisi.md` untuk subtes itu
- `teks`
- `opsi_a` sampai `opsi_e`: lima opsi, isinya tidak boleh sama. Angka JSON seperti `85` disimpan sebagai teks `"85"`.
- `pembahasan_konsep`, `pembahasan_pengecoh`, `pembahasan_cepat`

Jawaban, pilih salah satu:

- `kunci`: huruf `A` sampai `E` (TWK, TIU, PEDAGOGIK, MATERI_RPL)
- `bobot`: objek A sampai E dengan nilai 1 sampai 5, semuanya berbeda (TKP)

Opsional:

- `tingkat`: `mudah`, `sedang` (bawaan), atau `sulit`
- `rujukan`: teks
- `perlu_cek`: `true` atau `false` (bawaan `false`)
- `sumber`: `draf_ai` (bawaan), `tulisan_sendiri`, atau `lama`

Field lain ditolak supaya salah ketik ketahuan.

## Batas dan pembersihan

- Spasi di tepi `jenis_ujian`, `subtes`, `subtopik`, `kunci`, `tingkat`, dan `sumber` dipangkas sebelum disimpan.
- Panjang maksimal: `subtopik` 120 karakter, `kunci` 1 karakter, nama batch (nama file tanpa `.json`) 100 karakter.
- Karakter NUL (`\u0000`) di teks mana pun ditolak.
- `kunci` dan `bobot` tidak boleh ada bersamaan. Soal TKP hanya memakai `bobot`, soal lain hanya memakai `kunci`.
- File boleh disimpan dengan BOM (misalnya dari Notepad).

## Aturan rujukan TWK

Soal TWK yang `rujukan`-nya kosong wajib diberi `"perlu_cek": true`. Jangan mengarang rujukan. Kalau tidak yakin sumbernya, kosongkan `rujukan` dan beri `perlu_cek`.

## Soal ganda

Soal ditolak kalau teksnya sama (huruf besar kecil dan tanda baca diabaikan) dengan baris lain di file yang sama, atau dengan soal mana pun di bank, apa pun statusnya.

## Perintah impor

Periksa dulu tanpa menyimpan:

```
python manage.py cpns_impor_soal data/cpns/batch/<nama-batch>.json --coba
```

Lalu impor:

```
python manage.py cpns_impor_soal data/cpns/batch/<nama-batch>.json
```

Hasilnya `Masuk: N soal (draf). Gagal: M baris.` diikuti satu baris per kegagalan, misalnya `Baris 3: <pesan>`. Baris yang gagal tidak disimpan, baris lain tetap masuk. Perintah keluar dengan kode 1 kalau ada baris yang gagal. Perbaiki baris itu, lalu impor ulang file yang sama: baris yang sudah masuk akan ditolak sebagai ganda, jadi pindahkan baris yang gagal ke file batch baru.
