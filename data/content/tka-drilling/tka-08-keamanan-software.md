---
title: "Pertemuan 8: Keamanan Perangkat Lunak (Software Security)"
description: "Kuasai CIA Triad, OWASP Top 10 (SQLi, XSS, CSRF, IDOR), Hashing vs Encryption, HTTPS/TLS, JWT Attacks, hingga Zero-Trust & Defense in Depth."
category: "Drilling TKA PPLG"
level: "Lanjutan"
order: 8
duration: "160 min"
tags: ["Security", "OWASP", "XSS", "SQLi", "Cryptography", "JWT"]
teacherTip: "Fokus pada pemisahan Hashing (1-arah) vs Encryption (2-arah), pencegahan XSS via textContent/CSP, serta perbaikan SQL Injection via Parameterized Query."
---

Halo, _Security Engineer & Cyber Guardian_! 🛡️

Selamat datang di Pertemuan 8 Drilling TKA PPLG! Dalam rekayasa perangkat lunak modern, keamanan bukan lagi sekadar fitur tambahan yang dipikirkan belakangan (*afterthought*), melainkan fondasi utama sejak hari pertama koding dimulai (*Security by Design*). Celah sekecil apapun dapat dimanfaatkan oleh peretas untuk mencuri data pengguna atau mengambil alih server aplikasi.

Di pertemuan ini, kita bedah tuntas mulai dari prinsip dasar **CIA Triad** (Confidentiality, Integrity, Availability), jajaran kerentanan web populer **OWASP Top 10** (SQL Injection, XSS, CSRF, IDOR), perbedaan **Hashing vs Enkripsi**, mitigasi **JWT Signature Bypass**, hingga arsitektur **Zero-Trust & Defense in Depth**. Mari kita sikat! 🚀

---

## 💡 Bedah Materi: The Core of Software Security

### 1. Peta Prinsip CIA Triad

<div class="p-6 my-6 bg-slate-900/50 border border-slate-700/50 rounded-2xl flex flex-col items-center space-y-4 shadow-inner text-sm font-mono text-slate-300">
<div class="text-center font-bold text-slate-100 mb-2 font-sans">Triad Keamanan Perangkat Lunak</div>

<div class="grid grid-cols-1 md:grid-cols-3 gap-3 w-full text-center text-xs">
<div class="p-3 border border-purple-500/50 bg-purple-500/10 rounded-lg">
<div class="font-bold text-purple-400">CONFIDENTIALITY</div>
<div class="text-[10px] text-slate-300 mt-1">Kerahasiaan Data</div>
<div class="text-[9px] text-purple-300 font-mono mt-1">Enkripsi, Akses Kontrol</div>
</div>

<div class="p-3 border border-cyan-500/50 bg-cyan-500/10 rounded-lg">
<div class="font-bold text-cyan-400">INTEGRITY</div>
<div class="text-[10px] text-slate-300 mt-1">Keutuhan Data</div>
<div class="text-[9px] text-cyan-300 font-mono mt-1">Hashing, Digital Signature</div>
</div>

<div class="p-3 border border-emerald-500/50 bg-emerald-500/10 rounded-lg">
<div class="font-bold text-emerald-400">AVAILABILITY</div>
<div class="text-[10px] text-slate-300 mt-1">Ketersediaan Layanan</div>
<div class="text-[9px] text-emerald-300 font-mono mt-1">DDoS Mitigation, Redundansi</div>
</div>
</div>
</div>

---

### 2. Membedah Hashing vs Enkripsi

<div class="p-6 my-6 bg-slate-900/50 border border-slate-700/50 rounded-2xl flex flex-col items-center space-y-4 shadow-inner text-sm font-mono text-slate-300">
<div class="text-center font-bold text-slate-100 mb-2 font-sans">Perbedaan Hashing dan Enkripsi</div>

<div class="grid grid-cols-1 sm:grid-cols-2 gap-4 w-full max-w-lg">
<div class="p-3 border border-slate-600 bg-slate-800 rounded-lg text-center">
<div class="font-bold text-rose-400 text-xs">HASHING (1-Arah)</div>
<div class="text-[10px] text-slate-300 mt-1">Tidak dapat didekripsi balik (Irreversible). Contoh: Bcrypt, Argon2 untuk password.</div>
</div>
<div class="p-3 border border-slate-600 bg-slate-800 rounded-lg text-center">
<div class="font-bold text-emerald-400 text-xs">ENKRIPSI (2-Arah)</div>
<div class="text-[10px] text-slate-300 mt-1">Dapat didekripsi kembali (Reversible) dengan Kunci Dekripsi. Contoh: AES-256, RSA.</div>
</div>
</div>
</div>

---

## ⚡ Jebakan Batman Soal TKA Keamanan Software

> **Jebakan 1: Autentikasi vs Otorisasi**
> - **Autentikasi (Authentication)**: Memverifikasi *Siapa Anda* (misal: Cek username & password). Status Error: `401 Unauthorized`.
> - **Otorisasi (Authorization)**: Memverifikasi *Apa Hak Akses Anda* (misal: Siswa tidak boleh hapus user). Status Error: `403 Forbidden`.

> **Jebakan 2: Pencegahan SQL Injection & XSS**
> - **SQL Injection**: Dicegah dengan **Parameterized Queries / Prepared Statements** (`?` placeholder).
> - **XSS**: Dicegah dengan **Input Sanitization, CSP Header**, dan mengganti `innerHTML` menjadi **`textContent`**!

---

## 🎯 Jurnal Refleksi (Check-Out)

Setelah menyelesaikan 60 soal Pre-Test Keamanan Perangkat Lunak:
1. Materi mana yang paling sering memicu keraguan: membedakan XSS vs CSRF, mekanisme serangan JWT, atau notasi Enkripsi Simetris vs Asimetris?
2. Tuliskan analisis refleksimu di *tab* **Post-Test & Refleksi**! 🚀
