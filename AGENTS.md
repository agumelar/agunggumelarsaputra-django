# AGENTS.md — AI Agent Operating Guide & Django DATH Stack Blueprint

> **Proyek:** `agunggumelarsaputra-django` (Personal Website & Vocational Learning Hub RPL)  
> **Pemilik / Pengajar:** Agung Gumelar Saputra, S.Tr.T. (Guru Pengampu RPL SMKN 1 Rongga & Fullstack Software Engineer)  
> **Arsitektur Utama:** **DATH Stack** (Django + Alpine.js + Tailwind CSS M3 + HTMX)  
> **Konsep:** *HTML-over-the-Wire / Modern Monolith* dengan Google Material Design 3 (M3)  
> **Target Deployment:** VPS Production (Docker / Gunicorn / Nginx / PostgreSQL)

---

## 1. Core Directives & Vocational Brand Philosophy

1. **Gelar & Struktur Kurikulum Vokasi SMK:**
   - **Gelar:** `S.Tr.T.` (Sarjana Terapan Teknik). Dilarang mengubah gelar atau profil tanpa instruksi eksplisit.
   - **Program Keahlian:** **Pengembangan Perangkat Lunak dan Gim (PPLG)**
   - **Konsentrasi Keahlian:** **Rekayasa Perangkat Lunak (RPL)**
   - **Peran Pemilik / Pengajar:** **Guru Pengampu RPL / Guru Produktif RPL** & Fullstack Software Engineer.
   - **ATURAN NOMENKLATUR MUTLAK:**
     - Program Keahlian: **Pengembangan Perangkat Lunak dan Gim (PPLG)** atau **PPLG**.
     - Konsentrasi Keahlian: **Rekayasa Perangkat Lunak (RPL)** atau **RPL** (Bukan PPLG).
     - Penyebutan Pengajar: **Guru Pengampu RPL** atau **Guru Produktif RPL**.

2. **Filosofi Desain (Anti AI-Slop & High-Craft Material Design 3):**
   - **TIDAK ADA AI SLOP:** Dilarang menggunakan gradien neon ungu-cyan acak, aura blur berlebih di background, teks bergradien menyilaukan, atau glassmorphism kabur.
   - **Desain Bersih & Solid:** Gunakan palet warna solid bernilai kontras tinggi (Dark slate `#090d16`, `#111827`, border halus `rgba(255,255,255,0.08)`, teks terang `#f3f4f6`).
   - **Tipografi Bersih:** Display (`Outfit`), Body (`Inter`), Code/Numbers (`JetBrains Mono`).

3. **Alur Kerja Interaksi & Brainstorming (ATURAN MUTLAK):**
   - Sebelum pengguna secara eksplisit mengatakan **"proses"** atau memberikan perintah eksekusi, seluruh interaksi berstatus **BRAINSTORMING**.
   - Dilarang keras melakukan modifikasi file/kode secara sepihak sebelum ada instruksi *"proses"*.

4. **Jadwal Migrasi Data Neon Legacy (Scheduled on 1st of the Month):**
   - Data riwayat akun siswa, progres modul, LKPD, dan laporan RESIK dari database lama (Neon PostgreSQL) akan diekspor dan diimpor ke Django pada tanggal 1 setelah kuota bandwidth Neon reset via script `scripts/import_from_neon.py`.

---

## 2. Tech Stack & Environment

| Layer | Teknologi | Detail / Catatan |
|---|---|---|
| **Backend Framework** | Python 3.12+ / Django 5.x | Modular Apps (`apps/`), Django ORM, Custom User Auth |
| **Frontend Dynamic** | HTMX 2.x + Alpine.js 3.x | *HTML-over-the-Wire* (Partials swap tanpa full-reload) |
| **Styling & Theme** | Tailwind CSS v3.4 (M3 Tokens) | Standalone Tailwind CLI / Custom M3 Utility Classes |
| **Database** | SQLite (Dev) / PostgreSQL (VPS) | Django multi-environment settings |
| **Production Server** | Docker + Gunicorn + Nginx | VPS Self-Hosted |

---

## 3. Struktur Direktori Proyek

```text
agunggumelarsaputra-django/
├── config/                     # Konfigurasi Inti Django (settings, urls, wsgi, asgi)
│   ├── settings/
│   │   ├── base.py             # Konfigurasi dasar bersama
│   │   ├── development.py      # Konfigurasi lokal (SQLite, DEBUG=True)
│   │   └── production.py       # Konfigurasi VPS (PostgreSQL, Gunicorn, WhiteNoise)
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
├── apps/                       # Domain-Driven Modular Apps
│   ├── core/                   # Landing page, Showcase, CV, Contact, Global Context
│   ├── accounts/               # Custom User (Student & Teacher), Onboarding, Profil
│   ├── pembelajaran/           # 16 Modul Orientasi PPLG, 4-Tab Reader, LKPD & KKTP
│   ├── tka/                    # Simulator CBT TKA PPLG, Bank Soal A-E, Auto-Scoring
│   ├── literasi/               # Rabu Literasi (RESIK), Validasi Kata, Peer Review, Cetak PDF
│   ├── gamification/           # XP Engine, Levels, Daily Streak, Live Leaderboard
│   └── admin_panel/            # Generator Token Enrollment, Teacher Grading Hub, Monitoring
├── templates/                  # Base Layouts & Partials HTMX
│   ├── base.html               # Base layout M3 (Tailwind, HTMX, Alpine)
│   ├── components/             # Reusable UI (Cards, Buttons, Segmented Tabs, Modals)
│   └── partials/               # HTML fragment responses for HTMX swaps
├── static/                     # CSS, JS, Images (Logo AGS, Icon)
├── media/                      # Uploaded user avatars & attachments
├── scripts/                    # Utility scripts (e.g. import_from_neon.py)
├── Dockerfile                  # Production Container
├── docker-compose.yml          # Production Orchestration
├── requirements.txt            # Python Dependencies
├── DESIGN.md                   # M3 Design Token & Style Lock Reference
└── AGENTS.md                   # This Operational Guide
```

---

## 4. Cheat Sheet Perintah Utama

```bash
# 1. Jalankan Dev Server Django
python manage.py runserver

# 2. Kompilasi Tailwind CSS (Watch Mode)
npx tailwindcss -i static/css/input.css -o static/css/output.css --watch

# 3. Database Migration
python manage.py makemigrations
python manage.py migrate

# 4. Buat Superuser Guru / Admin
python manage.py createsuperuser
```
