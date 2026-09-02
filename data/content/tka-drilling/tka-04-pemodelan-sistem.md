---
title: "Pertemuan 4: Pemodelan Perangkat Lunak (UML & ERD)"
description: "Kuasai Use Case Diagram (include vs extend), Class Diagram (Aggregation vs Composition), Sequence Diagram, Activity Diagram, hingga ERD Crow's Foot."
category: "Drilling TKA PPLG"
level: "Lanjutan"
order: 4
duration: "160 min"
tags: ["UML", "ERD", "Use Case", "Class Diagram", "Sequence Diagram"]
teacherTip: "Fokus pada perbedaan <<include>> vs <<extend>>, relasi Composition (♦) vs Aggregation (◊), serta transformasi ERD N:M ke tabel pivot."
---

Halo, _System Architect_! 📐

Selamat datang di Pertemuan 4 Drilling TKA PPLG! Sebelum sebaris kode ditulis oleh para *developer*, arsitektur dan rancangan aplikasi harus digambar terlebih dahulu. Di dunia rekayasa perangkat lunak, kita mengenal dua standar utama: **UML (Unified Modeling Language)** untuk aspek berorientasi objek dan **ERD (Entity Relationship Diagram)** untuk aspek perancangan basis data.

Soal-soal TKA PPLG sangat gemar menguji pemahamanmu terhadap notasi diagram, pemisahan Use Case, alur kerja Activity, garis waktu Sequence, hingga transformasi relasi kardinalitas ERD ke bentuk skema relasional tabel. Mari kita kupas tuntas! 🚀

---

## 💡 Bedah Materi: Core Principles of UML & ERD

### 1. Peta Diagram Utama UML

<div class="p-6 my-6 bg-slate-900/50 border border-slate-700/50 rounded-2xl flex flex-col items-center space-y-4 shadow-inner text-sm font-mono text-slate-300">
<div class="text-center font-bold text-slate-100 mb-2 font-sans">Klasifikasi Diagram UML Utama</div>

<div class="grid grid-cols-1 md:grid-cols-2 gap-4 w-full">
<div class="p-4 border-2 border-cyan-500 bg-cyan-500/10 rounded-xl">
<div class="font-bold text-cyan-400 text-sm mb-2">1. Diagram Struktur (Structural)</div>
<ul class="text-xs text-slate-300 space-y-1 list-disc pl-4">
<li><b>Class Diagram</b>: Struktur kelas, atribut, method, visibilitas (+, -, #).</li>
<li><b>Deployment Diagram</b>: Fisik node hardware & penyebaran server.</li>
</ul>
</div>

<div class="p-4 border-2 border-emerald-500 bg-emerald-500/10 rounded-xl">
<div class="font-bold text-emerald-400 text-sm mb-2">2. Diagram Perilaku (Behavioral)</div>
<ul class="text-xs text-slate-300 space-y-1 list-disc pl-4">
<li><b>Use Case Diagram</b>: Persyaratan fungsionalitas & Aktor.</li>
<li><b>Activity Diagram</b>: Alur kerja (workflow), Swimlane, Fork/Join.</li>
<li><b>Sequence Diagram</b>: Interaksi pesan antar objek berdasar garis waktu.</li>
</ul>
</div>
</div>
</div>

---

### 2. Notasi Relasi Kunci pada Class Diagram

<div class="p-6 my-6 bg-slate-900/50 border border-slate-700/50 rounded-2xl flex flex-col items-center space-y-4 shadow-inner text-sm font-mono text-slate-300">
<div class="text-center font-bold text-slate-100 mb-2 font-sans">Perbandingan Aggregation vs Composition</div>

<div class="grid grid-cols-1 sm:grid-cols-2 gap-4 w-full max-w-lg">
<div class="p-3 border border-slate-600 bg-slate-800 rounded-lg text-center">
<div class="font-bold text-amber-400 text-xs">AGGREGATION ( ◊ )</div>
<div class="text-[10px] text-slate-300 mt-1">Kepemilikan Lemah (Has-A). Objek anak TETAP EKSIS meskipun objek induk dihancurkan. (Contoh: Dosen ◊— Jurusan)</div>
</div>
<div class="p-3 border border-slate-600 bg-slate-800 rounded-lg text-center">
<div class="font-bold text-rose-400 text-xs">COMPOSITION ( ♦ )</div>
<div class="text-[10px] text-slate-300 mt-1">Kepemilikan Kuat (Part-Of). Objek anak MUSNAH jika objek induk dihancurkan. (Contoh: Mobil ♦— Mesin)</div>
</div>
</div>
</div>

---

## ⚡ Jebakan Batman Soal TKA Pemodelan Sistem

> **Jebakan 1: `<<include>>` vs `<<extend>>` pada Use Case**
> - **`<<include>>`**: Wajib / Mutlak dieksekusi oleh Use Case utama. (Contoh: *Transfer Uang* `<<include>>` *Verifikasi PIN*).
> - **`<<extend>>`**: Opsional / Tambahan kondisional. (Contoh: *Belanja Online* `<<extend>>` *Masukan Kode Promo*).

> **Jebakan 2: Visibilitas & Simbol UML Class Diagram**
> - `+` = Public
> - `-` = Private
> - `#` = Protected
> - Garis bawah pada atribut/method (`+ getCount()`) = **Static Member**.
> - Teks miring (*Italic*) pada nama Class = **Abstract Class**.

---

## 🎯 Jurnal Refleksi (Check-Out)

Setelah menyelesaikan 60 soal Pre-Test Pemodelan Sistem:
1. Konsep pemodelan mana yang paling sering membuatmu ragu: membedakan relasi Use Case, Notasi Class Diagram, atau Transformasi Kardinalitas ERD (1:N & N:M) ke tabel?
2. Tuliskan analisis refleksimu di *tab* **Post-Test & Refleksi**! 🚀
