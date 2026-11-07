# CPNS Hub Rencana 3: Catatan Keputusan dan Temuan Tertunda

Dokumen ini menyimpan isi ledger kerja Rencana 3. Ledger itu dihapus setelah rencana selesai, jadi untuk Rencana 4 dan pekerjaan konten, pakai catatan ini.

Branch: `feat/cpns-hub-3`, dibuat dari master `d7ff8bc`. Belum di-push dan belum di-deploy.

## Keputusan pelaksana (rulings) dan risikonya

| No | Keputusan | Risiko kalau keliru |
|---|---|---|
| Snapshot | Benar/Salah dan poin setiap butir dibekukan saat dinilai. Pembahasan selalu memakai isi soal terkini. | Pesan pembahasan bisa tampak bertentangan dengan label lama (lihat "Boleh menunggu"). |
| R3-1 | Isi JSON yang bukan teks: angka diubah ke teks; `bool`, list, dict, dan `None` dianggap kosong. | Sedikit kode. |
| R3-2 | Target kisi-kisi hanya boleh berisi angka ASCII. Pesan error menyebut nilai yang salah. | Sedikit kode. |
| R3-3 | File batch boleh mengandung BOM (Notepad). Kunci dan bobot tidak boleh diisi bersamaan. | Sedikit kode. |
| R3-4 | Pesan flash di halaman kelola dibedakan berhasil, gagal, dan info. Setujui ditolak untuk soal yang sudah tayang. Pengiriman ganda dicegah. | Sedikit kerja tambahan. |
| R3-5 | Task 7 dan 8 dikerjakan satu pelaksana dan ditinjau sekali. | Paket tinjauan lebih besar. |
| R3-6 | Subtes dikunci di form edit bila soal pernah dipakai di sesi. | Untuk mengganti subtes, pemilik harus menolak soal itu lalu membuat soal baru. |
| R3-7 | Soal yang ditandai "perlu cek fakta" tidak bisa disetujui sebelum tandanya dihapus. Teks dan subtopik wajib diisi. | Pemilik punya sedikit langkah tambahan. |

## Wajib sebelum deploy (Rencana 4)

- **Suite di Postgres:** jalankan seluruh suite sekali di Postgres. Tes saat ini memakai SQLite, jadi indeks unik parsial dan `select_for_update` belum diuji di Postgres.
- **Tes CSRF:** tambahkan tes yang memaksa CSRF (`enforce_csrf_checks`), termasuk untuk aksi kelola.
- **Batch kosong:** "Soal X dari Y di batch ini" untuk batch kosong. Soal lama hasil impor Rencana 4 semuanya akan memakai `batch=""`.

## Pekerjaan konten (setelah pemilik menyetujui kisi-kisi)

1. Pemilik menyetujui atau mengubah `docs/cpns/kisi-kisi.md`.
2. Sesi penulis draf membuat batch soal di `data/cpns/batch/<nama-batch>.json` mengikuti `docs/cpns/format-batch.md`.
3. Batch diimpor dengan `python manage.py cpns_impor_soal <file>`, lalu ditinjau di `/kelola/tinjau/`.
4. Setelah ada soal tayang, pemilik menyusun paket belajar trial di admin. Teks trial di beranda ("1 paket, 30 soal, 1 simulasi") masih ditulis langsung dan perlu diambil dari data paket itu (bawaan dari Rencana 2).

## Boleh menunggu

**Hasil peserta:**
- Halaman hasil lama bisa menyorot kunci terkini di samping label "Benar" yang sudah dibekukan. Pertimbangkan catatan "Kunci soal ini diperbarui setelah kamu mengerjakan."
- Poin dan total sesi belajar tidak dibekukan. Keduanya saat ini tidak ditampilkan di mana pun.

**Form edit soal:**
- Pilihan subtes belum dibatasi menurut jenis ujian, dan masih ada opsi kosong.
- Subtopik bisa berbeda dari kisi-kisi. Pertimbangkan `datalist` atau peringatan.
- Pesan wajib-isi muncul dua kali.
- Belum ada peringatan duplikat saat mengedit.
- Belum memakai `select_for_update`.

**Impor dan kisi-kisi:**
- Pengecekan duplikat menjalankan satu query per baris.
- Pengecekan duplikat subtopik kisi-kisi hanya mencocokkan teks yang persis sama.
- Isi baris kepala tabel kisi-kisi tidak dicek.
- Tabel kedua yang hanya dipisah baris kosong akan gagal dengan pesan yang jelas.

**Halaman Tinjau:**
- Tamu yang mengirim POST diarahkan dengan `next` ke URL aksi, yang lalu menghasilkan 405.
- Belum ada pesan "satu-satunya soal".
- Label "Draf tersisa" menghitung global, tidak mengikuti filter.

**Halaman Cakupan dan Laporan:**
- Tautan baris Cakupan selalu memakai `status=tayang`, sehingga baris yang hanya punya draf membuka antrean kosong.
- Filter "semua" di Laporan belum memakai paginasi.

**Tes:** sejumlah celah tes. Rinciannya ada di riwayat tinjauan per task:
- filter laporan
- zona waktu penghitung
- rollback impor
- tes markup pintasan
