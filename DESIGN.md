---
name: "AGS High-Craft Material Design 3 (M3)"
version: "1.0.0"
author: "Agung Gumelar Saputra, S.Tr.T."
philosophy: "Anti AI-Slop, High-Craft, Border-Defined Depth, Vocational Technical Precision"
colors:
  background: "#090d16"
  foreground: "#f3f4f6"
  surface: "#090d16"
  surface-container-lowest: "#0d121e"
  surface-container-low: "#111827"
  surface-container: "#162032"
  surface-container-high: "#1c293e"
  surface-container-highest: "#23324d"
  primary: "#38bdf8"
  primary-container: "rgba(56, 189, 248, 0.12)"
  on-primary: "#082f49"
  on-primary-container: "#bae6fd"
  secondary: "#2dd4bf"
  secondary-container: "rgba(45, 212, 191, 0.12)"
  tertiary: "#fbbf24"
  tertiary-container: "rgba(251, 191, 36, 0.12)"
  outline: "rgba(255, 255, 255, 0.14)"
  outline-variant: "rgba(255, 255, 255, 0.08)"
  success: "#34d399"
  warning: "#fbbf24"
  danger: "#f87171"
typography:
  display: "Outfit, Inter, sans-serif"
  body: "Inter, system-ui, sans-serif"
  code: "JetBrains Mono, monospace"
rounded:
  xs: "4px"
  sm: "8px"
  md: "12px"
  lg: "16px"
  xl: "20px"
  2xl: "24px"
  full: "9999px"
---

# DESIGN.md — AGS High-Craft Design System (NeedMCP Style Lock)

> **Proyek:** `agunggumelarsaputra-django`  
> **Standar Arsitektur:** Material Design 3 (M3) + DATH Stack Theme Tokens  
> **Target Audiens:** Siswa Konsentrasi Keahlian Rekayasa Perangkat Lunak (RPL), Guru, dan Komunitas Rekayasa Perangkat Lunak.

---

## 1. Filosofi Inti & Anti AI-Slop (Core Design Directives)

1. **Border-Defined Depth (Bukan Shadow Blur Sembarangan):**
   - Kedalaman ditentukan oleh kombinasi warna permukaan (*surface container elevation*) dan border halus berdefinisi tinggi (`rgba(255, 255, 255, 0.08)`).
2. **Kelangkaan Aksen (Accent Scarcity):**
   - Warna aksen (`#38bdf8` Sky, `#2dd4bf` Teal/Emerald, `#fbbf24` Amber) digunakan secara terukur hanya untuk tombol aksi utama (*CTA*), chip indikator status, link interaktif, dan fokus visual.
3. **Tipografi Hierarkis Tegas:**
   - **Display / Heading:** Menggunakan font `Outfit`.
   - **Body / Penjelasan Materi:** Menggunakan font `Inter`.
   - **Angka / Token / XP / Kode:** Menggunakan font `JetBrains Mono`.
