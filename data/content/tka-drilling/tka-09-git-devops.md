---
title: "Pertemuan 9: Version Control (Git) & DevOps"
description: "Kuasai Perintah Git (commit, push, pull, branch, merge), Stash, Reset vs Revert, Merge Conflicts, Docker Containerization, hingga CI/CD Pipeline."
category: "Drilling TKA PPLG"
level: "Lanjutan"
order: 9
duration: "160 min"
tags: ["Git", "DevOps", "Docker", "CI/CD", "GitHub", "Version Control"]
teacherTip: "Fokus pada pemahaman area Git (Working Dir, Staging Area, Local Repo), beda git reset vs git revert, serta penyelamat git reflog & git bisect."
---

Halo, _DevOps Engineer & Release Master_! 🚀

Selamat datang di Pertemuan 9 Drilling TKA PPLG! Kodingan yang hebat tidak akan bisa berjalan di server produksi tanpa manajemen kontrol versi yang rapi dan rantai otomatisasi pengujian & peluncuran **DevOps**. Penguasaan **Git** (Distributed Version Control System) adalah keterampilan wajib nomor satu bagi setiap *Software Engineer* untuk berkolaborasi dalam tim.

Di pertemuan ini, kita bedah tuntas mulai dari alur kerja Git (Working Directory, Staging Area, Local/Remote Repo), penanganan **Merge Conflicts**, trik `git stash` & `git reflog`, perbedaan `git reset` vs `git revert`, strategi percabangan Git Flow, hingga kontainerisasi **Docker** dan pipeline **CI/CD**. Mari kita sikat! ⚡

---

## 💡 Bedah Materi: The Git Architecture & DevOps Lifecycle

### 1. Peta Tiga Area Utama Git

<div class="p-6 my-6 bg-slate-900/50 border border-slate-700/50 rounded-2xl flex flex-col items-center space-y-4 shadow-inner text-sm font-mono text-slate-300">
<div class="text-center font-bold text-slate-100 mb-2 font-sans">Alur Kerja Tiga Area Git</div>

<div class="grid grid-cols-1 md:grid-cols-3 gap-3 w-full text-center text-xs">
<div class="p-3 border border-rose-500/50 bg-rose-500/10 rounded-lg">
<div class="font-bold text-rose-400">1. WORKING DIRECTORY</div>
<div class="text-[10px] text-slate-300 mt-1">Perubahan Kode Lokal</div>
<div class="text-[9px] text-rose-300 font-mono mt-1">git add ➔</div>
</div>

<div class="p-3 border border-amber-500/50 bg-amber-500/10 rounded-lg">
<div class="font-bold text-amber-400">2. STAGING AREA</div>
<div class="text-[10px] text-slate-300 mt-1">Daftar Siap Commit</div>
<div class="text-[9px] text-amber-300 font-mono mt-1">git commit ➔</div>
</div>

<div class="p-3 border border-emerald-500/50 bg-emerald-500/10 rounded-lg">
<div class="font-bold text-emerald-400">3. LOCAL REPOSITORY</div>
<div class="text-[10px] text-slate-300 mt-1">Snapshot History (.git)</div>
<div class="text-[9px] text-emerald-300 font-mono mt-1">git push ➔ Remote</div>
</div>
</div>
</div>

---

### 2. Membedah Git Reset vs Git Revert

<div class="p-6 my-6 bg-slate-900/50 border border-slate-700/50 rounded-2xl flex flex-col items-center space-y-4 shadow-inner text-sm font-mono text-slate-300">
<div class="text-center font-bold text-slate-100 mb-2 font-sans">Kapan Menggunakan Reset vs Revert?</div>

<div class="grid grid-cols-1 sm:grid-cols-2 gap-4 w-full max-w-lg">
<div class="p-3 border border-slate-600 bg-slate-800 rounded-lg text-center">
<div class="font-bold text-rose-400 text-xs">GIT RESET (--hard)</div>
<div class="text-[10px] text-slate-300 mt-1">Memundurkan histori & MENGHAPUS commit (Bahaya untuk branch remote public!).</div>
</div>
<div class="p-3 border border-slate-600 bg-slate-800 rounded-lg text-center">
<div class="font-bold text-emerald-400 text-xs">GIT REVERT</div>
<div class="text-[10px] text-slate-300 mt-1">Membuat COMMIT BARU yang berisi kebalikan perubahan (Sangat aman untuk remote!).</div>
</div>
</div>
</div>

---

## ⚡ Jebakan Batman Soal TKA Git & DevOps

> **Jebakan 1: `git fetch` vs `git pull`**
> - **`git fetch`**: Hanya mengunduh metadata & commit baru dari remote TANPA langsung me-merge ke kodingan lokalmu.
> - **`git pull`**: Mengunduh sekaligus **LANGSUNG ME-MERGE** (`fetch + merge`) perubahan remote ke cabang lokal aktif.

> **Jebakan 2: Penyelamat Kode Terhapus (`git reflog`)**
> Jika kamu tidak sengaja me-reset hard commit penting, perintah **`git reflog`** adalah pahlawannya! `reflog` mencatat setiap pergerakan penunjuk HEAD di lokal sehingga commit terbuang dapat dipulihkan kembali.

---

## 🎯 Jurnal Refleksi (Check-Out)

Setelah menyelesaikan 60 soal Pre-Test Git & DevOps:
1. Materi mana yang paling menantang: membedakan merge vs rebase, penyelesaian merge conflict, atau perintah otomatisasi Dockerfile/CI-CD?
2. Tuliskan analisis refleksimu di *tab* **Post-Test & Refleksi**! 🚀
