---
title: "Pertemuan 2: Pemrograman Berorientasi Objek (PBO / OOP)"
description: "Kuasai 4 Pilar PBO, Class, Object, Constructor, Access Modifiers, Overloading vs Overriding, hingga Tracing Code & Polymorphism."
category: "Drilling TKA PPLG"
level: "Lanjutan"
order: 2
duration: "160 min"
tags: ["PBO", "OOP", "Java", "Encapsulation", "Polymorphism"]
teacherTip: "Perhatikan jebakan Field Hiding vs Dynamic Method Dispatch serta beda Overloading vs Overriding di soal TKA."
---

Halo, _Architect of Code_! 🧱

Selamat datang di Pertemuan 2 Drilling TKA PPLG! Kalau di pertemuan pertama kita sudah mengasah logika prosedural dan flowchart, sekarang saatnya kita menaikkan *level* ke paradigma industri: **Pemrograman Berorientasi Objek (Object-Oriented Programming / OOP)**.

Di dunia industri perangkat lunak modern, aplikasi skala besar dibangun dengan memodelkan dunia nyata menjadi **Objek**. Memahami PBO bukan cuma soal hafal istilah *Encapsulation* atau *Inheritance*, tapi tahu *kapan* dan *mengapa* kita menggunakannya! Mari kita bedah tuntas materi dan jebakan soal TKA-nya! 🚀

---

## 💡 Bedah Materi: The 4 Pillars of OOP & Essential Concepts

Biarkan pembuat soal TKA mencoba menjebakmu, dengan menguasai diagram dan prinsip di bawah ini kamu pasti bisa melibas 60 soal pre-test!

### 1. Anatomi Class vs Object

<div class="p-6 my-6 bg-slate-900/50 border border-slate-700/50 rounded-2xl flex flex-col items-center space-y-4 shadow-inner text-sm font-mono text-slate-300">
<div class="text-center font-bold text-slate-100 mb-2 font-sans">Visualisasi Instansiasi Objek dari Class</div>

<!-- Class Blueprint Box -->
<div class="w-full max-w-md p-4 border-2 border-cyan-500 bg-cyan-500/10 rounded-xl text-center">
<div class="font-bold text-cyan-400 text-base">CLASS: Mobil (Blueprint)</div>
<div class="text-xs text-slate-400 mt-1">Atribut: String merk, int kecepatan | Method: jalan(), rem()</div>
</div>

<div class="w-0.5 h-6 bg-slate-600 relative"><div class="absolute -bottom-1 -left-1 w-2.5 h-2.5 border-r-2 border-b-2 border-slate-600 rotate-45"></div></div>
<div class="text-xs font-bold text-amber-400 font-sans">new Mobil() (Instansiasi)</div>
<div class="w-0.5 h-6 bg-slate-600 relative"><div class="absolute -bottom-1 -left-1 w-2.5 h-2.5 border-r-2 border-b-2 border-slate-600 rotate-45"></div></div>

<!-- Objects Box -->
<div class="grid grid-cols-2 gap-4 w-full max-w-md">
<div class="p-3 border-2 border-emerald-500 bg-emerald-500/10 rounded-lg text-center">
<div class="font-bold text-emerald-400 text-xs">OBJECT 1: mobilA</div>
<div class="text-[10px] text-slate-300">merk = "Civic"<br/>kecepatan = 120</div>
</div>
<div class="p-3 border-2 border-emerald-500 bg-emerald-500/10 rounded-lg text-center">
<div class="font-bold text-emerald-400 text-xs">OBJECT 2: mobilB</div>
<div class="text-[10px] text-slate-300">merk = "Avanza"<br/>kecepatan = 80</div>
</div>
</div>
</div>

- **Class (Cetak Biru)**: Definisi struktur atribut dan behavior. Belum memakan memori instance.
- **Object (Wujud Nyata)**: Hasil instansiasi menggunakan keyword `new`. Memiliki status (*state*) di RAM.
- **Constructor**: Method khusus berpanggilan otomatis saat `new` dieksekusi. Nama constructor **sama persis** dengan nama Class (di Java/C++) dan tidak memiliki *return type* (bahkan `void` sekalipun!).

### 2. Membedah 4 Pilar OOP

1. 🛡️ **Encapsulation (Pembungkusan Data)**: 
   - Menyembunyikan atribut privat (`private`) dan membukanya hanya lewat method public `getter` & `setter`.
   - *Tujuan*: Menjaga integritas data (misal: setter mencegah nilai `umur` negatif).
2. 🏛️ **Inheritance (Pewarisan / Hierarki)**:
   - Hubungan **IS-A** (Adalah Jenis Dari). Menggunakan keyword `extends`.
   - Mengizinkan kelas anak (*subclass*) mewarisi atribut & method kelas induk (*superclass*).
3. 🎭 **Polymorphism (Banyak Bentuk)**:
   - **Overloading**: Method bernama sama di **SATU CLASS**, beda jumlah/tipe parameter. (Compile-time).
   - **Overriding**: Subclass menulis ulang method induk dengan nama dan parameter **SAMA PERSIS**. (Runtime).
4. 🌀 **Abstraction (Abstraksi)**:
   - Menyembunyikan kerumitan internal dan menyajikan antarmuka sederhana.
   - Menggunakan `abstract class` atau `interface` (kontrak murni).

---

## ⚡ Jebakan Batman Soal TKA PBO

> **Jebakan 1: Static Member vs Instance Member**
> `static` artinya atribut/method milik **Class**, bukan milik objek! Variabel `static` di-share bersama oleh seluruh objek. Diubah di satu objek, objek lain ikut berubah nilainya!

> **Jebakan 2: Variable Field Hiding vs Polymorphism Method**
> Di Java, **Method** bersifat *polymorphic* (mengikuti tipe objek nyata `new Child()`), tetapi **Variabel/Field** TIDAK *polymorphic* (mengikuti tipe variabel referensi `Parent p`). 
> ```java
> Parent p = new Child();
> System.out.println(p.x); // Mencetak variabel milik Parent!
> p.suara();              // Mengeksekusi method milik Child!
> ```

---

## 🎯 Jurnal Refleksi (Check-Out)

Setelah menuntaskan simulasi 60 soal PBO di Pre-Test, mari evaluasi pemahamanmu di *tab* **Post-Test & Refleksi**:
1. Apakah kamu sudah bisa membedakan secara spontan antara **Overloading** dan **Overriding** saat *tracing code*?
2. Konsep pilar manakah (Encapsulation, Inheritance, Polymorphism, Abstraction) yang paling sering membuatmu terkecoh?

Tulis jawaban jujurmu untuk ditinjau oleh guru pengampu! 🚀
