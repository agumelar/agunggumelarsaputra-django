---
title: "Pertemuan 7: Struktur Data Dasar (Data Structures)"
description: "Kuasai Array, Linked List, Stack (LIFO), Queue (FIFO), Hash Table (Collisions), Tree (BST Traversal), Graph (DFS/BFS), hingga B-Tree."
category: "Drilling TKA PPLG"
level: "Lanjutan"
order: 7
duration: "160 min"
tags: ["Struktur Data", "Array", "Stack", "Queue", "Tree", "Graph"]
teacherTip: "Fokus pada pemahaman operasi LIFO vs FIFO, penelusuran Tree (In-Order/Pre-Order/Post-Order), serta analisis time-complexity Big-O."
---

Halo, _Computer Scientist & Data Structure Engineer_! 🧬

Selamat datang di Pertemuan 7 Drilling TKA PPLG! Memilih **Struktur Data** yang tepat adalah kunci utama pembentuk aplikasi yang efisien dan berkinerja tinggi. Jika algoritma adalah langkah penyelesaian masalah, maka struktur data adalah kontainer pengorganisasian memori RAM untuk mengeksekusi langkah tersebut.

Di pertemuan ini, kita bedah tuntas mulai dari struktur data linier (**Array, Linked List, Stack LIFO, Queue FIFO**), struktur data asosiatif (**Hash Table & Penanganan Collision**), hingga struktur data hierarkis & jaringan (**Binary Search Tree, Heap, Graph DFS/BFS, dan B-Tree**). Mari kita sikat! 🚀

---

## 💡 Bedah Materi: The Core Data Structures

### 1. Karakteristik & Trade-off Struktur Data Linier

<div class="p-6 my-6 bg-slate-900/50 border border-slate-700/50 rounded-2xl flex flex-col items-center space-y-4 shadow-inner text-sm font-mono text-slate-300">
<div class="text-center font-bold text-slate-100 mb-2 font-sans">Perbandingan Array, Stack, dan Queue</div>

<div class="grid grid-cols-1 md:grid-cols-3 gap-3 w-full text-center text-xs">
<div class="p-3 border border-cyan-500/50 bg-cyan-500/10 rounded-lg">
<div class="font-bold text-cyan-400">ARRAY</div>
<div class="text-[10px] text-slate-300 mt-1">Blok Memori Kontigu</div>
<div class="text-[9px] text-cyan-300 font-bold mt-1">Akses Acak: O(1)</div>
</div>

<div class="p-3 border border-amber-500/50 bg-amber-500/10 rounded-lg">
<div class="font-bold text-amber-400">STACK (Tumpukan)</div>
<div class="text-[10px] text-slate-300 mt-1">Prinsip: LIFO</div>
<div class="text-[9px] text-amber-300 font-mono mt-1">Push() & Pop() di Top</div>
</div>

<div class="p-3 border border-emerald-500/50 bg-emerald-500/10 rounded-lg">
<div class="font-bold text-emerald-400">QUEUE (Antrean)</div>
<div class="text-[10px] text-slate-300 mt-1">Prinsip: FIFO</div>
<div class="text-[9px] text-emerald-300 font-mono mt-1">Enqueue(Rear) & Dequeue(Front)</div>
</div>
</div>
</div>

---

### 2. Traversal Binary Search Tree (BST)

<div class="p-6 my-6 bg-slate-900/50 border border-slate-700/50 rounded-2xl flex flex-col items-center space-y-4 shadow-inner text-sm font-mono text-slate-300">
<div class="text-center font-bold text-slate-100 mb-2 font-sans">Aturan Penelusuran (Traversal) Tree</div>

<div class="grid grid-cols-1 sm:grid-cols-3 gap-3 w-full text-center text-xs">
<div class="p-2 border border-slate-600 bg-slate-800 rounded">
<div class="font-bold text-cyan-400">Pre-Order</div>
<div class="text-[10px] text-slate-300">Root ➔ Left ➔ Right</div>
</div>
<div class="p-2 border border-slate-600 bg-slate-800 rounded">
<div class="font-bold text-emerald-400">In-Order</div>
<div class="text-[10px] text-slate-300">Left ➔ Root ➔ Right</div>
<div class="text-[9px] text-emerald-300 font-bold mt-0.5">(Hasil BST Terurut!)</div>
</div>
<div class="p-2 border border-slate-600 bg-slate-800 rounded">
<div class="font-bold text-amber-400">Post-Order</div>
<div class="text-[10px] text-slate-300">Left ➔ Right ➔ Root</div>
</div>
</div>
</div>

---

## ⚡ Jebakan Batman Soal TKA Struktur Data

> **Jebakan 1: In-Order Traversal pada BST**
> Penelusuran **In-Order** (`Left -> Root -> Right`) pada Binary Search Tree (BST) **SELALU** menghasilkan urutan data yang terurut dari terkecil ke terbesar!

> **Jebakan 2: Graph BFS vs DFS**
> - **BFS (Breadth-First Search)**: Menggunakan struktur data **Queue** (penelusuran melebar per level).
> - **DFS (Depth-First Search)**: Menggunakan struktur data **Stack / Rekursi** (penelusuran mendalam hingga ujung).

---

## 🎯 Jurnal Refleksi (Check-Out)

Setelah menyelesaikan 60 soal Pre-Test Struktur Data:
1. Konsep mana yang paling menantang: perhitungan ekspresi Postfix/Prefix, penelusuran Tree, atau analisis penanganan Hash Collision?
2. Tuliskan analisis refleksimu di *tab* **Post-Test & Refleksi**! 🚀
