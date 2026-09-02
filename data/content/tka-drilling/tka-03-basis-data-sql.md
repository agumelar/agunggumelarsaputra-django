---
title: "Pertemuan 3: Basis Data & SQL (Structured Query Language)"
description: "Kuasai DDL/DML, Primary/Foreign Key, JOIN, Agregasi (GROUP BY/HAVING), Normalisasi 1NF-3NF, hingga Transaksi ACID & SQLi."
category: "Drilling TKA PPLG"
level: "Lanjutan"
order: 3
duration: "160 min"
tags: ["SQL", "Database", "MySQL", "PostgreSQL", "Normalisasi"]
teacherTip: "Fokus pada pemisahan WHERE vs HAVING serta analisis hasil JOIN dan jebakan SQL Injection di soal TKA."
---

Halo, _Data Engineer & Database Master_! 🗄️

Selamat datang di Pertemuan 3 Drilling TKA PPLG! Data adalah aset paling berharga dalam aplikasi modern. Mau sebagus apapun tampilan UI buatanmu, tanpa struktur **Database** yang tangguh dan query **SQL** yang optimal, aplikasimu bakal *lemot* atau malah rentan diakses peretas.

Di pertemuan ini, kita membedah konsep Relational Database Management System (RDBMS), pengelompokan perintah DDL/DML/DCL, Join tabel, Normalisasi data 1NF-3NF, hingga penanganan transaksi ACID. Yuk disimak! ⚡

---

## 💡 Bedah Materi: The Core of Database & SQL Mastery

### 1. Klasifikasi Perintah SQL (Jangan Sampai Tertukar!)

<div class="p-6 my-6 bg-slate-900/50 border border-slate-700/50 rounded-2xl flex flex-col items-center space-y-4 shadow-inner text-sm font-mono text-slate-300">
<div class="text-center font-bold text-slate-100 mb-2 font-sans">Peta Perintah SQL</div>

<div class="grid grid-cols-1 md:grid-cols-3 gap-4 w-full">
<div class="p-4 border-2 border-cyan-500 bg-cyan-500/10 rounded-xl text-center">
<div class="font-bold text-cyan-400 text-sm">DDL (Data Definition)</div>
<div class="text-xs text-slate-300 mt-2">Struktur Database & Tabel</div>
<div class="text-[11px] text-cyan-300 font-mono mt-1">CREATE, ALTER, DROP, TRUNCATE</div>
</div>

<div class="p-4 border-2 border-emerald-500 bg-emerald-500/10 rounded-xl text-center">
<div class="font-bold text-emerald-400 text-sm">DML (Data Manipulation)</div>
<div class="text-xs text-slate-300 mt-2">Manipulasi Isi Record</div>
<div class="text-[11px] text-emerald-300 font-mono mt-1">SELECT, INSERT, UPDATE, DELETE</div>
</div>

<div class="p-4 border-2 border-amber-500 bg-amber-500/10 rounded-xl text-center">
<div class="font-bold text-amber-400 text-sm">DCL / TCL (Control & Trans)</div>
<div class="text-xs text-slate-300 mt-2">Hak Akses & Transaksi</div>
<div class="text-[11px] text-amber-300 font-mono mt-1">GRANT, REVOKE, COMMIT, ROLLBACK</div>
</div>
</div>
</div>

- **DDL**: Berurusan dengan wadah/struktur tabel.
- **DML**: Berurusan dengan data di dalam tabel. *(Hati-hati: `DELETE` adalah DML, sedangkan `DROP` & `TRUNCATE` adalah DDL!)*

---

### 2. Membedah Jenis-Jenis JOIN

<div class="p-6 my-6 bg-slate-900/50 border border-slate-700/50 rounded-2xl flex flex-col items-center space-y-4 shadow-inner text-sm font-mono text-slate-300">
<div class="text-center font-bold text-slate-100 mb-2 font-sans">Visualisasi Hasil JOIN Tabel</div>

<div class="grid grid-cols-1 sm:grid-cols-2 gap-4 w-full max-w-lg">
<div class="p-3 border border-slate-600 bg-slate-800 rounded-lg text-center">
<div class="font-bold text-cyan-400 text-xs">INNER JOIN</div>
<div class="text-[10px] text-slate-300 mt-1">Hanya ambil data yang COCOK di kedua tabel (Intersection).</div>
</div>
<div class="p-3 border border-slate-600 bg-slate-800 rounded-lg text-center">
<div class="font-bold text-emerald-400 text-xs">LEFT JOIN</div>
<div class="text-[10px] text-slate-300 mt-1">Semua data tabel KIRI diambil, jika kanan tak cocok bernilai NULL.</div>
</div>
</div>
</div>

---

## ⚡ Jebakan Batman Soal TKA Database

> **Jebakan 1: WHERE vs HAVING**
> - `WHERE` digunakan untuk menyaring baris sebelum di-group. **TIDAK BISA** menggunakan fungsi agregat seperti `WHERE COUNT(*) > 5` (Error!).
> - `HAVING` khusus menyaring hasil setelah pengelompokan `GROUP BY`. `HAVING COUNT(*) > 5` (Valid!).

> **Jebakan 2: SQL Injection & Prepared Statement**
> Penyerang menyisipkan string `' OR '1'='1` untuk melewatin autentikasi. Pencegahan wajib di industri dan soal TKA: **Gunakan Prepared Statement / Parameterized Queries**!

---

## 🎯 Jurnal Refleksi (Check-Out)

Setelah menuntaskan 60 soal Basis Data di Pre-Test:
1. Mana yang lebih sering membuatmu ragu: menentukan bentuk normalisasi (1NF, 2NF, 3NF) atau menuliskan query `GROUP BY... HAVING`?
2. Tuliskan refleksimu untuk ditinjau oleh guru! 🚀
