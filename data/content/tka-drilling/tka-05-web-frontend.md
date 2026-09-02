---
title: "Pertemuan 5: Web Development Dasar (HTML, CSS & JavaScript)"
description: "Kuasai Semantik HTML5, CSS Box Model, Flexbox vs Grid, JS DOM Manipulation, Event Bubbling, hingga Event Loop & XSS Defense."
category: "Drilling TKA PPLG"
level: "Lanjutan"
order: 5
duration: "160 min"
tags: ["HTML5", "CSS3", "JavaScript", "DOM", "Flexbox"]
teacherTip: "Fokus pada pemahaman CSS Specificity, Box-Sizing border-box, Event Delegation, serta jebakan Event Loop di soal TKA."
---

Halo, _Frontend Master & Web Developer_! 🌐

Selamat datang di Pertemuan 5 Drilling TKA PPLG! Tampilan antarmuka (*User Interface*) aplikasi web adalah jembatan utama antara pengguna dan sistem. Untuk menjadi *Software Engineer* yang tangguh, kamu wajib menguasai 3 pilar utama web: **HTML5** untuk struktur semantik, **CSS3** untuk tata letak & gaya visual, serta **JavaScript (ES6+)** untuk logika interaktif DOM.

Di pertemuan ini, kita bedah tuntas mulai dari hirarki CSS Specificity, trik Flexbox vs Grid, manipulasi DOM, hingga rahasia perputaran *Event Loop* dan pertahanan terhadap *Cross-Site Scripting (XSS)*. Yuk disimak! 🚀

---

## 💡 Bedah Materi: The 3 Pillars of Web Development

### 1. Anatomi CSS Box Model & Specificity

<div class="p-6 my-6 bg-slate-900/50 border border-slate-700/50 rounded-2xl flex flex-col items-center space-y-4 shadow-inner text-sm font-mono text-slate-300">
<div class="text-center font-bold text-slate-100 mb-2 font-sans">CSS Box Model Anatomy</div>

<!-- Box Model Diagram -->
<div class="w-full max-w-md p-4 border-2 border-dashed border-amber-500 bg-amber-500/10 rounded-2xl text-center">
<div class="text-xs font-bold text-amber-400">MARGIN (Jarak Luar Eksterior)</div>
<div class="m-3 p-4 border-2 border-emerald-500 bg-emerald-500/10 rounded-xl">
<div class="text-xs font-bold text-emerald-400">BORDER (Bingkai Elemen)</div>
<div class="m-2 p-3 border-2 border-cyan-500 bg-cyan-500/10 rounded-lg">
<div class="text-xs font-bold text-cyan-400">PADDING (Jarak Ruang Interior)</div>
<div class="m-2 p-2 bg-slate-800 rounded font-bold text-white text-xs">CONTENT (Teks / Gambar)</div>
</div>
</div>
</div>
</div>
</div>

- **`box-sizing: content-box;` (Default)**: Lebar total = `width` + `padding` + `border`. Ukuran elemen bisa membengkak!
- **`box-sizing: border-box;` (Standar Industri)**: Lebar total dikunci pas sesuai `width` (padding & border memakan ruang dari dalam).
- **CSS Specificity**: `Inline Style (1000)` > `ID Selector (100)` > `Class / Attribute Selector (10)` > `Element Selector (1)`.

---

### 2. Flexbox vs CSS Grid

<div class="p-6 my-6 bg-slate-900/50 border border-slate-700/50 rounded-2xl flex flex-col items-center space-y-4 shadow-inner text-sm font-mono text-slate-300">
<div class="text-center font-bold text-slate-100 mb-2 font-sans">Kapan Menggunakan Flexbox vs Grid?</div>

<div class="grid grid-cols-1 sm:grid-cols-2 gap-4 w-full max-w-lg">
<div class="p-3 border border-slate-600 bg-slate-800 rounded-lg text-center">
<div class="font-bold text-cyan-400 text-xs">FLEXBOX (1-Dimensi)</div>
<div class="text-[10px] text-slate-300 mt-1">Sangat ideal untuk baris ATAU kolom tunggal (Navigasi, Card Row, Toolbar).</div>
</div>
<div class="p-3 border border-slate-600 bg-slate-800 rounded-lg text-center">
<div class="font-bold text-emerald-400 text-xs">CSS GRID (2-Dimensi)</div>
<div class="text-[10px] text-slate-300 mt-1">Sangat ideal untuk baris DAN kolom sekaligus (Dashboard Layout, Gallery Grid).</div>
</div>
</div>
</div>

---

## ⚡ Jebakan Batman Soal TKA Web Frontend

> **Jebakan 1: Asynchronous Event Loop Output**
> ```javascript
> console.log('1');
> setTimeout(() => console.log('2'), 0);
> Promise.resolve().then(() => console.log('3'));
> console.log('4');
> ```
> **Urutan Output:** `1, 4, 3, 2`!
> *Mengapa?* `1` dan `4` (Synchronous direct Stack), `3` (Microtask Promise queue - prioritas tinggi), `2` (Macrotask setTimeout queue - prioritas kedua).

> **Jebakan 2: XSS Defense (`innerHTML` vs `textContent`)**
> Menampilkan input pengguna dengan `innerHTML = input` rentan disisipi `<script>badCode()</script>`. Selalu gunakan `textContent` atau sanitasi encoding HTML!

---

## 🎯 Jurnal Refleksi (Check-Out)

Setelah menuntaskan 60 soal Pre-Test Web Dev Dasar:
1. Mana materi yang paling sering memicu kecerobohan: perhitung CSS Specificity, manipulasi DOM & Event Bubbling, atau urutan eksekusi Event Loop?
2. Tuliskan analisis refleksimu di *tab* **Post-Test & Refleksi**! 🚀
