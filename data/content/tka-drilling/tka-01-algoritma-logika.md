---
title: "Pertemuan 1: Algoritma & Logika Pemrograman"
description: "Review dan latihan soal terkait tipe data, percabangan, perulangan, flowchart, dan pseudocode."
category: "Drilling TKA PPLG"
level: "Lanjutan"
order: 1
duration: "160 min"
tags: ["Algoritma", "Logika", "PPLG"]
teacherTip: "Fokus pada tracing nilai variabel dalam perulangan bersarang (nested loop) yang sering muncul di soal TKA."
---

Halo, calon _Software Engineer_ andalan! 🚀

Selamat datang di titik awal perjuangan kita menuju Tes Kemampuan Akademik (TKA) RPL. Ingat, *coding* itu bukan cuma soal ngetik kode di *keyboard* sampai berdarah-darah, tapi soal bagaimana cara otak kita memecahkan masalah (problem-solving). Kalau logikanya udah dapet, mau pakai bahasa Java, PHP, JavaScript, atau C++ sekalipun, *it's just a matter of syntax!* 

Di pertemuan pertama ini, kita bakal memanaskan mesin logika kalian. Fokus kita hari ini: **Algoritma Dasar, Tipe Data, Flowchart, dan Kontrol Alur (Percabangan & Perulangan)**. Mari kita sikat! 🔥

---

## 💡 Bedah Materi: The Core of Algorithm

Biar nggak kagok waktu ngerjain soal-soal TKA yang suka ngasih jebakan *Batman*, perhatikan poin-poin krusial di bawah ini:

### 1. Fondasi Algoritma & Flowchart
Algoritma adalah langkah logis dan sistematis. Nggak ada istilah "ya pokoknya gitu". Di soal-soal TKA, kamu akan sering disuruh menganalisis lambang *Flowchart*:
- <svg width="36" height="20" viewBox="0 0 36 20" class="inline-block align-middle mr-1 text-cyan-400"><rect x="1" y="1" width="34" height="18" rx="9" fill="currentColor" fill-opacity="0.1" stroke="currentColor" stroke-width="2"/></svg> **Oval / Terminator**: Start dan End. (Jangan sampai ketukar!)
- <svg width="36" height="20" viewBox="0 0 36 20" class="inline-block align-middle mr-1 text-emerald-400"><polygon points="8,1 35,1 28,19 1,19" fill="currentColor" fill-opacity="0.1" stroke="currentColor" stroke-width="2"/></svg> **Jajar Genjang**: Input & Output. Kalau ada kata `READ`, `INPUT`, atau `PRINT`, ini rumahnya.
- <svg width="32" height="24" viewBox="0 0 32 24" class="inline-block align-middle mr-1 text-amber-400"><polygon points="16,1 31,12 16,23 1,12" fill="currentColor" fill-opacity="0.1" stroke="currentColor" stroke-width="2"/></svg> **Belah Ketupat (Diamond)**: *Decision* (Kondisi). Semua pengecekan `IF` atau `SWITCH` masuk ke sini. Ingat, selalu ada *dua panah* yang keluar dari sini (TRUE dan FALSE).
- <svg width="36" height="20" viewBox="0 0 36 20" class="inline-block align-middle mr-1 text-blue-400"><rect x="1" y="1" width="34" height="18" fill="currentColor" fill-opacity="0.1" stroke="currentColor" stroke-width="2"/></svg> **Persegi Panjang**: *Process*. Tempat kamu ngitung, nambah variabel, atau assign nilai.

<div class="p-6 my-6 bg-slate-900/50 border border-slate-700/50 rounded-2xl flex flex-col items-center space-y-4 shadow-inner text-sm font-mono text-slate-300">
<div class="text-center font-bold text-slate-100 mb-2 font-sans">Contoh Flowchart Utuh: Cek Kelulusan</div>
  
<!-- Start -->
<div class="flex items-center justify-center w-32 h-10 border-2 border-cyan-500 bg-cyan-500/10 rounded-full text-cyan-400 font-bold">START</div>
  
<div class="w-0.5 h-6 bg-slate-600 relative"><div class="absolute -bottom-1 -left-1 w-2.5 h-2.5 border-r-2 border-b-2 border-slate-600 rotate-45"></div></div>
  
<!-- Input -->
<div class="flex items-center justify-center w-40 h-10 border-2 border-emerald-500 bg-emerald-500/10 text-emerald-400 font-bold" style="clip-path: polygon(10% 0, 100% 0, 90% 100%, 0% 100%);">READ nilai</div>

<div class="w-0.5 h-6 bg-slate-600 relative"><div class="absolute -bottom-1 -left-1 w-2.5 h-2.5 border-r-2 border-b-2 border-slate-600 rotate-45"></div></div>

<!-- Decision -->
<div class="relative flex items-center justify-center">
<div class="flex items-center justify-center w-40 h-20 border-2 border-amber-500 bg-amber-500/10 text-amber-400 font-bold text-center" style="clip-path: polygon(50% 0%, 100% 50%, 50% 100%, 0% 50%);">nilai >= 75?</div>
    
<!-- True Path -->
<div class="absolute left-full top-1/2 w-16 h-0.5 bg-slate-600"><div class="absolute -right-1 -top-1 w-2.5 h-2.5 border-r-2 border-t-2 border-slate-600 rotate-45"></div></div>
<div class="absolute left-full top-1/2 -mt-4 ml-4 text-xs font-bold text-emerald-400">TRUE</div>
<div class="absolute -right-[9rem] top-1/2 -mt-5 flex items-center justify-center w-28 h-10 border-2 border-emerald-500 bg-emerald-500/10 text-emerald-400 font-bold" style="clip-path: polygon(10% 0, 100% 0, 90% 100%, 0% 100%);">PRINT "Lulus"</div>

<!-- False Path -->
<div class="absolute right-full top-1/2 w-16 h-0.5 bg-slate-600"><div class="absolute -left-1 -top-1 w-2.5 h-2.5 border-l-2 border-b-2 border-slate-600 rotate-45"></div></div>
<div class="absolute right-full top-1/2 -mt-4 mr-4 text-xs font-bold text-rose-400">FALSE</div>
<div class="absolute -left-[9rem] top-1/2 -mt-5 flex items-center justify-center w-28 h-10 border-2 border-emerald-500 bg-emerald-500/10 text-emerald-400 font-bold" style="clip-path: polygon(10% 0, 100% 0, 90% 100%, 0% 100%);">PRINT "Remed"</div>
</div>

<div class="w-0.5 h-10 bg-slate-600 relative"></div>
  
<!-- Joining paths (Visual trick for vertical align) -->
<div class="flex w-[18rem] justify-between relative -top-5">
<div class="w-1/2 h-5 border-b-2 border-r-2 border-slate-600 rounded-br-lg"></div>
<div class="w-1/2 h-5 border-b-2 border-l-2 border-slate-600 rounded-bl-lg"></div>
</div>
  
<div class="w-0.5 h-6 bg-slate-600 relative -top-5"><div class="absolute -bottom-1 -left-1 w-2.5 h-2.5 border-r-2 border-b-2 border-slate-600 rotate-45"></div></div>

<!-- End -->
<div class="flex items-center justify-center w-32 h-10 border-2 border-cyan-500 bg-cyan-500/10 rounded-full text-cyan-400 font-bold relative -top-5">END</div>
</div>

### 2. Jebakan Tipe Data & Operator
Seringkali TKA ngasih soal sepele tapi nipu.
> "Hasil dari `5 % 2` adalah..." 

Modulus (`%`) itu **sisa bagi**, bukan hasil bagi! `5 / 2 = 2` dengan sisa `1`. Jadi jawabannya `1`.
Hati-hati juga dengan tipe data `Boolean`. TRUE and FALSE is the key. Ingat tabel kebenaran logika:
- `AND (&&)`: Semuanya harus TRUE biar hasilnya TRUE. (Ketat banget kayak satpam kompleks).
- `OR (||)`: Cukup satu aja yang TRUE, hasilnya udah TRUE. (Lebih santai).

### 3. Drama Percabangan (If-Else & Switch)
Kapan pakai `IF-ELSE`? Kapan pakai `SWITCH`?
- Pakai `SWITCH-CASE` kalau kamu cuma mau ngecek **persamaan nilai yang spesifik** (misal: menu 1, menu 2, menu 3). *Don't forget the `break;`!* Kalau kamu lupa naruh `break` di JavaScript atau Java, program bakal bablas ngeksekusi case di bawahnya (*fall-through*). 
- Pakai `IF-ELSE IF` untuk kondisi berupa rentang (range), misal nilai > 80.

### 4. Tracing Code: Hati-Hati dengan Perulangan Bersarang (Nested Loop)
Ini nih menu andalan pembuat soal TKA: *Tracing*. Kamu akan dikasih *snippet* kode dan disuruh nebak *output*-nya apa atau nilai akhir variabelnya berapa.

**Contoh Kasus:**
```javascript
let count = 0;
for(let i = 1; i <= 3; i++) {
   for(let j = 1; j <= 2; j++) {
      count++;
   }
}
console.log(count);
```
**Tips Menjawab:** Nggak usah panik. Hitung pelan-pelan. Loop luar jalan 3 kali. Tiap 1 kali loop luar jalan, loop dalam jalan 2 kali. Jadi, 3 x 2 = 6 kali eksekusi. Nilai `count` adalah 6! Selesai.

---

## 🎯 Jurnal Refleksi (Check-Out)

Gimana hasil simulasi 60 soal tadi? Udah ngerasa dapet pencerahan atau malah makin pusing? Nggak apa-apa, pusing itu tandanya otak lagi *upgrade* RAM! 🧠

Sebelum lanjut main atau *scroll* sosmed, tulis jurnal refleksimu di *tab* **Jurnal Refleksi**. Jawab dengan jujur:
1. Dari 60 soal tadi, materi apa yang menurutmu paling menjebak? (Apakah tracing variabel? Logika OR/AND? Atau flowchart?)
2. Strategi apa yang bakal kamu lakuin minggu ini buat ningkatin insting *debugging* dan logikamu?

Tulis sendiri ya, jangan minta tolong ChatGPT. Santai aja, guru bakal baca dan kasih *feedback* biar kamu makin jago! 🚀
