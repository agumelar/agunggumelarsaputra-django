---
title: "Pertemuan 6: Web Development Lanjutan & REST API"
description: "Kuasai HTTP Methods, Status Codes (200, 201, 401, 403, 404, 500), Express Middleware, JWT, CORS, OAuth2, Async/Await, hingga Edge Functions."
category: "Drilling TKA PPLG"
level: "Lanjutan"
order: 6
duration: "160 min"
tags: ["REST API", "Backend", "Node.js", "Express", "JWT", "HTTP"]
teacherTip: "Perhatikan perbedaan HTTP Status Code 401 vs 403, struktur 3 bagian JWT, serta syarat Idempotent pada metode HTTP."
---

Halo, _Backend Engineer & API Architect_! ⚙️

Selamat datang di Pertemuan 6 Drilling TKA PPLG! Sebuah aplikasi modern yang responsif membutuhkan fondasi server **Backend & REST API** yang handal, aman, dan dapat diandalkan. REST API bertindak sebagai jembatan komunikasi antara aplikasi *client* (Web, Mobile, Desktop) dengan *database*.

Di pertemuan ini, kita bedah tuntas arsitektur **RESTful**, penggunaan Metode HTTP & Status Codes yang presisi, alur *Middleware Express.js*, mekanisme keamanan token **JWT (JSON Web Token)** & **OAuth2**, isu perbatasan **CORS**, hingga optimasi jaringan *Edge Runtime*. Mari kita sikat! 🚀

---

## 💡 Bedah Materi: The Anatomy of REST API & Web Security

### 1. Peta Metode HTTP & Sifat Idempotent

<div class="p-6 my-6 bg-slate-900/50 border border-slate-700/50 rounded-2xl flex flex-col items-center space-y-4 shadow-inner text-sm font-mono text-slate-300">
<div class="text-center font-bold text-slate-100 mb-2 font-sans">Karakteristik Metode HTTP</div>

<div class="grid grid-cols-1 md:grid-cols-4 gap-3 w-full text-center text-xs">
<div class="p-3 border border-emerald-500/50 bg-emerald-500/10 rounded-lg">
<div class="font-bold text-emerald-400">GET</div>
<div class="text-[10px] text-slate-300 mt-1">Membaca Data</div>
<div class="text-[9px] text-emerald-300 font-bold mt-1">Idempotent: YES</div>
</div>

<div class="p-3 border border-cyan-500/50 bg-cyan-500/10 rounded-lg">
<div class="font-bold text-cyan-400">POST</div>
<div class="text-[10px] text-slate-300 mt-1">Membuat Data Baru</div>
<div class="text-[9px] text-rose-400 font-bold mt-1">Idempotent: NO</div>
</div>

<div class="p-3 border border-amber-500/50 bg-amber-500/10 rounded-lg">
<div class="font-bold text-amber-400">PUT / PATCH</div>
<div class="text-[10px] text-slate-300 mt-1">Update Total / Partial</div>
<div class="text-[9px] text-emerald-300 font-bold mt-1">Idempotent: YES</div>
</div>

<div class="p-3 border border-rose-500/50 bg-rose-500/10 rounded-lg">
<div class="font-bold text-rose-400">DELETE</div>
<div class="text-[10px] text-slate-300 mt-1">Menghapus Resource</div>
<div class="text-[9px] text-emerald-300 font-bold mt-1">Idempotent: YES</div>
</div>
</div>
</div>

---

### 2. Anatomi JSON Web Token (JWT)

<div class="p-6 my-6 bg-slate-900/50 border border-slate-700/50 rounded-2xl flex flex-col items-center space-y-4 shadow-inner text-sm font-mono text-slate-300">
<div class="text-center font-bold text-slate-100 mb-2 font-sans">Struktur 3 Bagian JWT</div>

<div class="flex flex-wrap items-center justify-center gap-2 w-full text-xs font-bold">
<span class="px-3 py-2 rounded-lg bg-rose-500/20 text-rose-400 border border-rose-500/40">1. HEADER (Algoritma)</span>
<span class="text-slate-500">•</span>
<span class="px-3 py-2 rounded-lg bg-purple-500/20 text-purple-400 border border-purple-500/40">2. PAYLOAD (Data Claims)</span>
<span class="text-slate-500">•</span>
<span class="px-3 py-2 rounded-lg bg-cyan-500/20 text-cyan-400 border border-cyan-500/40">3. SIGNATURE (Secret Key)</span>
</div>
<div class="text-[11px] text-slate-400 text-center max-w-md mt-2">
⚠️ <b>Catatan Penting TKA:</b> Payload JWT <i>TIDAK terenkripsi</i> (hanya di-encode Base64Url). Siapapun bisa membaca isinya. Jangan pernah menyimpan password polos di dalam payload JWT!
</div>
</div>

---

## ⚡ Jebakan Batman Soal TKA Web Backend

> **Jebakan 1: Status Code 401 vs 403**
> - **`401 Unauthorized`**: Pengguna belum terautentikasi (belum login / token tidak ada/kadaluwarsa).
> - **`403 Forbidden`**: Pengguna **SUDAH login**, tetapi **TIDAK MEMILIKI HAK AKSES / PERMISSION** (misal siswa mencoba buka halaman Admin).

> **Jebakan 2: Penyimpanan Token Paling Aman**
> Menyimpan Access Token di `localStorage` rentan dicuri oleh serangan **XSS**. Praktik terbaik industri adalah menggunakan **Cookie ber-atribut `HttpOnly` dan `Secure`**!

---

## 🎯 Jurnal Refleksi (Check-Out)

Setelah menyelesaikan 60 soal Pre-Test Web Backend & REST API:
1. Materi mana yang paling menantang: membedakan HTTP status codes (401 vs 403), perambatan CORS, atau penanganan `async/await` Promise?
2. Tuliskan analisis refleksimu di *tab* **Post-Test & Refleksi**! 🚀
