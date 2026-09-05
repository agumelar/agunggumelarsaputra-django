# apps/pembelajaran/checkpoints.py
# Bank Soal & Checkpoint Gamifikasi 16 Modul Orientasi PPLG / Kejuruan RPL

MODULE_GAMIFIED_QUESTS = {
    "orientasi-pplg-01-pengantar-skill-passport": {
        "id": "quest-or01",
        "moduleTitle": "Pengantar Skill Passport & Standar Portofolio",
        "badge": "🎮 Mini-Game Quest: Modul 1",
        "xpReward": 15,
        "stage1Match": {
            "instruction": "Pasangkan 3 Konsep Skill Passport dengan Definisi yang Tepat:",
            "pairs": [
                {
                    "id": "p1",
                    "left": "Skill Passport",
                    "right": "Buku rekam jejak portofolio & kompetensi industri"
                },
                {
                    "id": "p2",
                    "left": "Evidence Google Drive",
                    "right": "Bukti fisik file PDF laporan & link repositori tugas"
                },
                {
                    "id": "p3",
                    "left": "Standar KKM 73",
                    "right": "Ambang batas nilai minimal ketuntasan uji kompetensi"
                }
            ]
        },
        "stage2Detective": {
            "statement": "Klaim: \"Di industri software modern, recruiter hanya melihat nilai angka di ijazah dan tidak peduli pada portofolio proyek yang pernah kalian buat.\"",
            "isFact": False,
            "factLabel": "✅ FAKTA INDUSTRI",
            "mythLabel": "❌ MITOS / SALAH BESAR",
            "explanation": "MITOS! Di industri IT, portofolio nyata di GitHub/GDrive dan bukti karya adalah faktor nomor 1 yang menentukan kelulusan wawancara kerja."
        },
        "stage3Speed": {
            "question": "Mengapa izin akses link Google Drive tugas harus disetel ke \"Siapa saja yang memiliki link dapat melihat\"?",
            "options": [
                {
                    "label": "Agar guru pengampu dan penguji kompetensi dapat memverifikasi isi evidence karya tanpa terhalang gembok akses (Private).",
                    "isCorrect": True,
                    "explanation": "Tepat sekali! Evidence yang terkunci tidak dapat divalidasi dan akan menghambat verifikasi kelulusan."
                },
                {
                    "label": "Agar file otomatis terhapus setelah 24 jam.",
                    "isCorrect": False,
                    "explanation": "Izin akses view tidak menghapus file sama sekali."
                },
                {
                    "label": "Hanya agar tampilan link terlihat lebih panjang.",
                    "isCorrect": False,
                    "explanation": "Pengaturan akses murni untuk izin pembacaan dokumen oleh asesor."
                }
            ],
            "timerSeconds": 25
        }
    },
    "orientasi-pplg-02-profesi-peluang-karier": {
        "id": "quest-or02",
        "moduleTitle": "8 Profesi Utama & Sinergi Tim Industri PPLG",
        "badge": "🎮 Mini-Game Quest: Modul 2",
        "xpReward": 15,
        "stage1Match": {
            "instruction": "Pasangkan Profesi Software dengan Tanggung Jawab Kerjanya:",
            "pairs": [
                {
                    "id": "p1",
                    "left": "Frontend Developer",
                    "right": "Membangun antarmuka web interaktif di browser (HTML/CSS/JS)"
                },
                {
                    "id": "p2",
                    "left": "Backend Engineer",
                    "right": "Mengelola database server, API endpoint, dan logika bisnis"
                },
                {
                    "id": "p3",
                    "left": "QA / Software Tester",
                    "right": "Menguji bug, performa sistem, dan memastikan zero-error"
                }
            ]
        },
        "stage2Detective": {
            "statement": "Klaim: \"Aplikasi besar seperti Gojek dan Tokopedia dapat dirancang, diprogram, dan dirilis ke jutaan pengguna hanya oleh 1 orang programmer saja.\"",
            "isFact": False,
            "factLabel": "✅ FAKTA TIM",
            "mythLabel": "❌ MITOS / TIDAK REALISTIS",
            "explanation": "MITOS! Aplikasi skala industri dikembangkan oleh Tim Produk lintas disiplin (Product Manager, UI/UX, Frontend, Backend, DevOps, QA)."
        },
        "stage3Speed": {
            "question": "Profesi mana yang bertugas menjembatani riset kenyamanan pengguna ke dalam bentuk desain wireframe dan prototype interaktif?",
            "options": [
                {
                    "label": "UI/UX Designer (Product Designer)",
                    "isCorrect": True,
                    "explanation": "Benar! UI/UX Designer merancang arsitektur interaksi, wireframe visual, dan prototype sebelum dikodekan oleh programmer."
                },
                {
                    "label": "Database Administrator",
                    "isCorrect": False,
                    "explanation": "DBA fokus pada tuning query dan keamanan server basis data."
                },
                {
                    "label": "Network Security Engineer",
                    "isCorrect": False,
                    "explanation": "Security Engineer fokus pada proteksi jaringan dan firewall."
                }
            ],
            "timerSeconds": 25
        }
    },
    "orientasi-pplg-03-ekosistem-industri-pplg": {
        "id": "quest-or03",
        "moduleTitle": "Ekosistem Industri & Jalur Kerja Bidang Perangkat Lunak",
        "badge": "🎮 Mini-Game Quest: Modul 3",
        "xpReward": 15,
        "stage1Match": {
            "instruction": "Pasangkan Tipe Perusahaan Software dengan Karakteristiknya:",
            "pairs": [
                {
                    "id": "p1",
                    "left": "Software House",
                    "right": "Mengerjakan aplikasi pesanan klien pihak ketiga (Agency/Vendor)"
                },
                {
                    "id": "p2",
                    "left": "Product Company",
                    "right": "Mengembangkan produk digital milik sendiri (Contoh: Spotify)"
                },
                {
                    "id": "p3",
                    "left": "Open Source Community",
                    "right": "Mengembangkan framework bebas pakai secara kolaboratif global"
                }
            ]
        },
        "stage2Detective": {
            "statement": "Klaim: \"Model bisnis SaaS (Software as a Service) menjual software dengan skema langganan bulanan/tahunan berbasis Cloud ketimbang sekali beli putus.\"",
            "isFact": True,
            "factLabel": "✅ FAKTA MODEL BISNIS",
            "mythLabel": "❌ SALAH / BUKAN SAAS",
            "explanation": "FAKTA! SaaS (seperti Netflix, Figma, GitHub) menggunakan langganan berkala untuk terus memberikan update fitur dan pemeliharaan server."
        },
        "stage3Speed": {
            "question": "Apa keuntungan bekerja di Software House bagi seorang lulusan junior RPL di awal karier?",
            "options": [
                {
                    "label": "Berkesempatan menangani beragam variasi proyek klien sehingga wawasan teknologi dan portofolio berkembang pesat.",
                    "isCorrect": True,
                    "explanation": "Tepat sekali! Variasi industri klien mempercepat pengalaman hands-on developer muda."
                },
                {
                    "label": "Tidak perlu menulis kode program.",
                    "isCorrect": False,
                    "explanation": "Software House justru tempat praktik coding intensif."
                },
                {
                    "label": "Bebas dari deadline proyek.",
                    "isCorrect": False,
                    "explanation": "Software House memiliki timeline delivery proyek yang ketat."
                }
            ],
            "timerSeconds": 25
        }
    },
    "orientasi-pplg-04-matriks-skill-jenjang-karier": {
        "id": "quest-or04",
        "moduleTitle": "Matriks Skill, Kurikulum RPL, & Jenjang Karier PPLG",
        "badge": "🎮 Mini-Game Quest: Modul 4",
        "xpReward": 15,
        "stage1Match": {
            "instruction": "Pasangkan Level Karier Software Engineer dengan Tingkat Tanggung Jawabnya:",
            "pairs": [
                {
                    "id": "p1",
                    "left": "Junior Developer",
                    "right": "Mengerjakan tugas coding terarah di bawah bimbingan senior"
                },
                {
                    "id": "p2",
                    "left": "Mid-Level Developer",
                    "right": "Mampu menyelesaikan fitur kompleks secara mandiri dan efisien"
                },
                {
                    "id": "p3",
                    "left": "Senior / Tech Lead",
                    "right": "Merancang arsitektur sistem besar dan membimbing seluruh tim"
                }
            ]
        },
        "stage2Detective": {
            "statement": "Klaim: \"T-Shaped Skills berarti seorang developer memiliki keahlian mendalam pada satu bidang utama (vertikal) serta wawasan luas lintas disiplin untuk kolaborasi (horizontal).\"",
            "isFact": True,
            "factLabel": "✅ FAKTA STANDAR SKILL",
            "mythLabel": "❌ SALAH / BUKAN T-SHAPED",
            "explanation": "FAKTA! Konsep T-Shaped memadukan keahlian spesialis (Deep Specialist) dengan kemampuan berkolaborasi dengan peran lain (Broad Generalist)."
        },
        "stage3Speed": {
            "question": "Soft skill apa yang paling krusial bagi seorang programmer saat bekerja dalam tim Agile/Scrum?",
            "options": [
                {
                    "label": "Komunikasi proaktif, keterbukaan menerima code review, dan kerja sama tim.",
                    "isCorrect": True,
                    "explanation": "Luar biasa! Software engineering adalah olahraga tim yang mengandalkan komunikasi yang solid."
                },
                {
                    "label": "Bekerja sendiri tanpa memberi tahu progres kepada tim.",
                    "isCorrect": False,
                    "explanation": "Sikap tertutup (silo) menghambat kolaborasi dan sinkronisasi sprint."
                },
                {
                    "label": "Menolak saran perbaikan dari rekan sejawat.",
                    "isCorrect": False,
                    "explanation": "Menerima code review konstruktif adalah kunci kematangan seorang engineer."
                }
            ],
            "timerSeconds": 25
        }
    },
    "orientasi-pplg-05-job-fair-kelas": {
        "id": "quest-or05",
        "moduleTitle": "Job Fair Kelas PPLG & Eksplorasi Lintas Booth",
        "badge": "🎮 Mini-Game Quest: Modul 5",
        "xpReward": 15,
        "stage1Match": {
            "instruction": "Pasangkan Komponen Job Fair Kelas dengan Fungsinya:",
            "pairs": [
                {
                    "id": "p1",
                    "left": "Elevator Pitch",
                    "right": "Penjelasan singkat profil keahlian diri dalam waktu 30-60 detik"
                },
                {
                    "id": "p2",
                    "left": "Booth Exhibitor",
                    "right": "Peran memamerkan tech stack dan tanggung jawab profesi kelompok"
                },
                {
                    "id": "p3",
                    "left": "Curriculum Vitae (CV)",
                    "right": "Dokumen rangkuman riwayat keahlian dan tautan portofolio proyek"
                }
            ]
        },
        "stage2Detective": {
            "statement": "Klaim: \"Saat wawancara kerja teknis, jika kita tidak mengetahui jawaban secara pasti, sikap terbaik adalah mengarang jawaban palsu dengan percaya diri.\"",
            "isFact": False,
            "factLabel": "✅ FAKTA WAWANCARA",
            "mythLabel": "❌ MITOS / FATAL ERROR",
            "explanation": "MITOS! Kejujuran intelektual sangat dihargai. Lebih baik sampaikan pemahaman dasar dan alur logika bagaimana kamu akan mencari solusinya secara sistematis."
        },
        "stage3Speed": {
            "question": "Apa tujuan utama dari aktivitas simulasi Job Fair kelas bagi siswa Fase E RPL?",
            "options": [
                {
                    "label": "Melatih *communication skill*, *confidence*, dan membuka wawasan luas mengenai tuntutan riil industri perangkat lunak.",
                    "isCorrect": True,
                    "explanation": "Tepat sekali! Kemampuan berbicara di depan publik dan mengomunikasikan ide teknis adalah aset utama calon engineer."
                },
                {
                    "label": "Membeli barang dagangan di dalam kelas.",
                    "isCorrect": False,
                    "explanation": "Job Fair kelas adalah pameran profil karier teknologi, bukan bazar komersial."
                },
                {
                    "label": "Menghindari jam belajar coding.",
                    "isCorrect": False,
                    "explanation": "Job Fair melengkapi keterampilan coding dengan soft skills presentasi teknis."
                }
            ],
            "timerSeconds": 25
        }
    },
    "orientasi-pplg-06-rencana-minat-awal": {
        "id": "quest-or06",
        "moduleTitle": "Perumusan Rencana Minat Karier Awal 3 Tahun",
        "badge": "🎮 Mini-Game Quest: Modul 6",
        "xpReward": 15,
        "stage1Match": {
            "instruction": "Pasangkan Jalur Peminatan RPL dengan Fokus Praktik Utamanya:",
            "pairs": [
                {
                    "id": "p1",
                    "left": "Web Development",
                    "right": "Membangun aplikasi berbasis web interaktif (Frontend, Backend, Fullstack)"
                },
                {
                    "id": "p2",
                    "left": "Mobile Development",
                    "right": "Menciptakan aplikasi Android/iOS dengan Flutter, React Native, atau Kotlin"
                },
                {
                    "id": "p3",
                    "left": "Game Development",
                    "right": "Merancang mekanika permainan, fisika game, dan aset menggunakan Unity/Godot"
                }
            ]
        },
        "stage2Detective": {
            "statement": "Klaim: \"Metode SMART Goal (Specific, Measurable, Achievable, Relevant, Time-bound) membantu kita menetapkan target belajar coding yang realistis dan terukur.\"",
            "isFact": True,
            "factLabel": "✅ FAKTA METODOLOGI",
            "mythLabel": "❌ SALAH / BUKAN SMART",
            "explanation": "FAKTA! Target yang spesifik dan berjangka waktu (misal: Selesai membuat 1 landing page HTML/CSS dalam 2 minggu) jauh lebih efektif dibanding target abstrak."
        },
        "stage3Speed": {
            "question": "Manakah contoh target belajar coding yang memenuhi kaidah SMART Goal bagi siswa kelas 10 RPL?",
            "options": [
                {
                    "label": "\"Dalam 1 bulan ke depan, saya akan menyelesaikan 3 modul HTML/CSS dan membuat 1 website portofolio profil diri di GitHub Pages.\"",
                    "isCorrect": True,
                    "explanation": "Sempurna! Target ini spesifik (HTML/CSS portofolio), terukur (1 website), dan memiliki batas waktu jelas (1 bulan)."
                },
                {
                    "label": "\"Saya ingin menjadi programmer paling hebat di dunia suatu saat nanti.\"",
                    "isCorrect": False,
                    "explanation": "Terlalu abstrak, tidak terukur, dan tidak memiliki batas waktu."
                },
                {
                    "label": "\"Saya akan belajar jika sempat saja.\"",
                    "isCorrect": False,
                    "explanation": "Tidak memiliki komitmen dan metrik ketercapaian."
                }
            ],
            "timerSeconds": 25
        }
    },
    "orientasi-pplg-07-mind-map-profesi-pplg": {
        "id": "quest-or07",
        "moduleTitle": "Desain & Visualisasi Mind Map Profesi PPLG",
        "badge": "🎮 Mini-Game Quest: Modul 7",
        "xpReward": 15,
        "stage1Match": {
            "instruction": "Pasangkan Cabang Mind Map dengan Elemen Penjelasnya:",
            "pairs": [
                {
                    "id": "p1",
                    "left": "Cabang Profesi Utama",
                    "right": "Pengelompokan 8 profesi inti dari perancang, pembangun, hingga penguji"
                },
                {
                    "id": "p2",
                    "left": "Cabang Tech Stack",
                    "right": "Bahasa pemrograman, framework, dan tools yang dipakai setiap peran"
                },
                {
                    "id": "p3",
                    "left": "Cabang Interkoneksi",
                    "right": "Garis hubungan kolaborasi kerja antar-profesi dalam siklus software"
                }
            ]
        },
        "stage2Detective": {
            "statement": "Klaim: \"Mind Mapping hanya berguna untuk menggambar hiasan warna-warni dan tidak memiliki manfaat dalam memetakan arsitektur sistem software.\"",
            "isFact": False,
            "factLabel": "✅ FAKTA STRUKTUR VISUAL",
            "mythLabel": "❌ MITOS / SALAH TOTAL",
            "explanation": "MITOS! Pemetaan pikiran (Mind Mapping) terbukti ilmiah mempercepat pemahaman relasi konsep kompleks dan arsitektur data hingga 40%."
        },
        "stage3Speed": {
            "question": "Tools digital apa yang populer digunakan untuk membuat diagram alur, mind map, dan wireframe kolaboratif di industri?",
            "options": [
                {
                    "label": "Figma / FigJam, Miro, atau Draw.io",
                    "isCorrect": True,
                    "explanation": "Tepat sekali! Tools kolaboratif ini menjadi standar industri modern untuk visualisasi konsep dan arsitektur produk."
                },
                {
                    "label": "Aplikasi Kalkulator Sederhana",
                    "isCorrect": False,
                    "explanation": "Kalkulator untuk hitungan numerik, bukan visual mapping."
                },
                {
                    "label": "Notepad teks polos tanpa diagram",
                    "isCorrect": False,
                    "explanation": "Notepad tidak mendukung diagram visual interaktif."
                }
            ],
            "timerSeconds": 25
        }
    },
    "orientasi-pplg-08-finalisasi-validasi-or01": {
        "id": "quest-or08",
        "moduleTitle": "Finalisasi & Validasi Asesmen Sumatif Skill Passport OR-01",
        "badge": "🎮 Mini-Game Quest: Modul 8",
        "xpReward": 15,
        "stage1Match": {
            "instruction": "Pasangkan Berkas Kelengkapan Portofolio OR-01 dengan Standar Validitasnya:",
            "pairs": [
                {
                    "id": "p1",
                    "left": "Folder Google Drive",
                    "right": "Izin share \"Anyone with link (Viewer)\" dan tidak ada file yang corrupt"
                },
                {
                    "id": "p2",
                    "left": "Skill Passport Log",
                    "right": "Seluruh checklist LKPD P1 s/d P7 telah tuntas dan ditandatangani"
                },
                {
                    "id": "p3",
                    "left": "Nilai KKM 73",
                    "right": "Ketercapaian minimal Level 2 (Mencoba) pada rubrik asesmen guru"
                }
            ]
        },
        "stage2Detective": {
            "statement": "Klaim: \"Siswa yang mengumpulkan folder evidence dalam keadaan akses terkunci (Request Access) akan langsung otomatis dinyatakan lulus kompetensi tanpa perlu dicek guru.\"",
            "isFact": False,
            "factLabel": "✅ FAKTA VALIDASI",
            "mythLabel": "❌ MITOS / AUTO LEVEL 0",
            "explanation": "MITOS! Evidence yang terkunci berada pada status Level 0 (Belum Terlihat) dan wajib dibuka aksesnya sebelum guru dapat memberikan nilai kelulusan."
        },
        "stage3Speed": {
            "question": "Apa langkah yang wajib dilakukan siswa jika nilai evaluasi LKPD berada di bawah KKM 73?",
            "options": [
                {
                    "label": "Membaca catatan masukan guru pada banner evaluasi, merevisi isian LKPD, dan mengklik \"Kirim Ulang Hasil Perbaikan\".",
                    "isCorrect": True,
                    "explanation": "Benar sekali! Remedial adalah proses belajar untuk memastikan kompetensi tercapai secara tuntas."
                },
                {
                    "label": "Membiarkan saja karena tidak akan berpengaruh pada nilai akhir.",
                    "isCorrect": False,
                    "explanation": "Nilai di bawah KKM menghambat kelulusan modul dan gating berikutnya."
                },
                {
                    "label": "Membuat akun baru.",
                    "isCorrect": False,
                    "explanation": "Cukup revisi tugas pada akun yang sama melalui tombol remedial."
                }
            ],
            "timerSeconds": 25
        }
    },
    "orientasi-pplg-09-app-audit-produk-digital": {
        "id": "quest-or09",
        "moduleTitle": "App Audit: Membedah Produk Digital Sehari-hari",
        "badge": "🎮 Mini-Game Quest: Modul 9",
        "xpReward": 15,
        "stage1Match": {
            "instruction": "Pasangkan Parameter Audit Produk dengan Aspek yang Diuji:",
            "pairs": [
                {
                    "id": "p1",
                    "left": "Usability (UX)",
                    "right": "Kemudahan dan kejelasan alur interaksi pengguna saat memakai aplikasi"
                },
                {
                    "id": "p2",
                    "left": "Performance",
                    "right": "Kecepatan respon aplikasi, waktu loading halaman, dan konsumsi memori"
                },
                {
                    "id": "p3",
                    "left": "Reliability",
                    "right": "Kestabilan sistem saat terjadi error jaringan atau input tak terduga"
                }
            ]
        },
        "stage2Detective": {
            "statement": "Klaim: \"Melakukan App Audit pada aplikasi populer cukup dengan melihat warna tombolnya saja tanpa perlu menguji alur checkout atau transaksi.\"",
            "isFact": False,
            "factLabel": "✅ FAKTA AUDIT LENGKAP",
            "mythLabel": "❌ MITOS / AUDIT DANGKAL",
            "explanation": "MITOS! Audit profesional wajib menguji keseluruhan alur fungsional (End-to-End User Journey) dari awal hingga akhir."
        },
        "stage3Speed": {
            "question": "Apa tujuan utama menyertakan tangkapan layar (screenshot) beranotasi visual dalam laporan review aplikasi?",
            "options": [
                {
                    "label": "Memberikan bukti otentik (Evidence) yang presisi sehingga pengembang langsung memahami letak kekurangan fitur.",
                    "isCorrect": True,
                    "explanation": "Tepat sekali! Anotasi visual mencegah ambigu dan mempercepat tindak lanjut perbaikan."
                },
                {
                    "label": "Hanya sebagai hiasan gambar agar laporan tampak ramai.",
                    "isCorrect": False,
                    "explanation": "Screenshot beranotasi adalah bukti empiris utama dalam audit software."
                },
                {
                    "label": "Menutupi kelemahan data teks analisis.",
                    "isCorrect": False,
                    "explanation": "Anotasi visual melengkapi analisis teks secara ilmiah."
                }
            ],
            "timerSeconds": 25
        }
    },
    "orientasi-pplg-10-ui-ux-fungsi-produk": {
        "id": "quest-or10",
        "moduleTitle": "Anatomi UI, UX, & Analisis Komparasi Produk Digital",
        "badge": "🎮 Mini-Game Quest: Modul 10",
        "xpReward": 15,
        "stage1Match": {
            "instruction": "Pasangkan Ranah UI dan UX dengan Elemen Fokusnya:",
            "pairs": [
                {
                    "id": "p1",
                    "left": "User Interface (UI)",
                    "right": "Tipografi, palet warna, konsistensi icon, dan estetika visual layar"
                },
                {
                    "id": "p2",
                    "left": "User Experience (UX)",
                    "right": "Arsitektur informasi, alur navigasi cepat, dan kemudahan pengguna"
                },
                {
                    "id": "p3",
                    "left": "Design System",
                    "right": "Koleksi komponen UI standar yang reusable di seluruh halaman aplikasi"
                }
            ]
        },
        "stage2Detective": {
            "statement": "Klaim: \"Aplikasi dengan animasi visual yang sangat mewah dan berkilauan pasti memiliki UX yang bagus meskipun tombol login-nya sulit ditemukan.\"",
            "isFact": False,
            "factLabel": "✅ FAKTA KESEIMBANGAN",
            "mythLabel": "❌ MITOS / SALAH KAPRAH",
            "explanation": "MITOS! Jika pengguna kesulitan menyelesaikan tujuannya (misal tombol susah dicari), maka UX aplikasi tersebut dinyatakan buruk terlepas dari estetikanya."
        },
        "stage3Speed": {
            "question": "Prinsip desain apa yang menyatakan bahwa elemen yang memiliki fungsi serupa harus diletakkan pada posisi dan gaya visual yang seragam?",
            "options": [
                {
                    "label": "Konsistensi (Consistency & Standards)",
                    "isCorrect": True,
                    "explanation": "Benar! Konsistensi mengurangi beban kognitif pengguna karena mereka tidak perlu menebak pola baru di setiap halaman."
                },
                {
                    "label": "Kompleksitas Ekstrem",
                    "isCorrect": False,
                    "explanation": "Kompleksitas tinggi justru membingungkan user."
                },
                {
                    "label": "Variasi Acak",
                    "isCorrect": False,
                    "explanation": "Variasi acak merusak pengalaman navigasi."
                }
            ],
            "timerSeconds": 25
        }
    },
    "orientasi-pplg-11-framework-review-6-komponen": {
        "id": "quest-or11",
        "moduleTitle": "Framework Review Produk Digital 6 Komponen Terstruktur",
        "badge": "🎮 Mini-Game Quest: Modul 11",
        "xpReward": 15,
        "stage1Match": {
            "instruction": "Pasangkan Komponen Framework Review dengan Fokus Analisisnya:",
            "pairs": [
                {
                    "id": "p1",
                    "left": "Tujuan & Target User",
                    "right": "Siapa pengguna utama aplikasi dan problem apa yang diselesaikan"
                },
                {
                    "id": "p2",
                    "left": "Analisis Fitur Kunci",
                    "right": "Evaluasi keandalan dan alur fungsi inti dari produk digital"
                },
                {
                    "id": "p3",
                    "left": "Rekomendasi Solutif",
                    "right": "Usulan perbaikan konkrit dari sudut pandang software engineer"
                }
            ]
        },
        "stage2Detective": {
            "statement": "Klaim: \"Memberikan kritik pada aplikasi cukup dengan mengatakan 'Aplikasi ini jelek' tanpa perlu memberikan data pendukung atau solusi alternatif.\"",
            "isFact": False,
            "factLabel": "✅ FAKTA REVIEW PROFESIONAL",
            "mythLabel": "❌ MITOS / KRITIK NON-KONSTRUKTIF",
            "explanation": "MITOS! Review software engineering wajib berbasis bukti (evidence-based) dan menyertakan usulan perbaikan teknis yang solutif."
        },
        "stage3Speed": {
            "question": "Mengapa analisis aksesibilitas (Accessibility / a11y) penting diuji pada aplikasi digital?",
            "options": [
                {
                    "label": "Memastikan aplikasi dapat digunakan dengan nyaman oleh semua orang, termasuk pengguna dengan keterbatasan visual atau fisik.",
                    "isCorrect": True,
                    "explanation": "Tepat sekali! Aksesibilitas adalah standar inklusivitas software modern internasional (WCAG)."
                },
                {
                    "label": "Hanya agar aplikasi lolos verifikasi Play Store.",
                    "isCorrect": False,
                    "explanation": "Aksesibilitas adalah hak kenyamanan setiap pengguna, bukan sekadar syarat formal."
                },
                {
                    "label": "Supaya ukuran file aplikasi menjadi lebih besar.",
                    "isCorrect": False,
                    "explanation": "Aksesibilitas tidak menambah beban ukuran file secara signifikan."
                }
            ],
            "timerSeconds": 25
        }
    },
    "orientasi-pplg-12-latihan-analisis-anotasi-visual": {
        "id": "quest-or12",
        "moduleTitle": "Latihan Analisis Terpandu & Anotasi Bukti Visual Screenshot",
        "badge": "🎮 Mini-Game Quest: Modul 12",
        "xpReward": 15,
        "stage1Match": {
            "instruction": "Pasangkan Elemen Anotasi Visual dengan Fungsinya:",
            "pairs": [
                {
                    "id": "p1",
                    "left": "Callout Box Merah",
                    "right": "Menyorot titik error, typo, atau kelemahan alur UX yang fatal"
                },
                {
                    "id": "p2",
                    "left": "Callout Box Hijau",
                    "right": "Mengapresiasi fitur inovatif atau desain yang sangat efektif"
                },
                {
                    "id": "p3",
                    "left": "Deskripsi Anotasi",
                    "right": "Penjelasan ringkas dampak masalah bagi kenyamanan user"
                }
            ]
        },
        "stage2Detective": {
            "statement": "Klaim: \"Anotasi visual yang efektif adalah yang menutupi seluruh layar hingga teks aplikasi aslinya tidak terbaca sama sekali.\"",
            "isFact": False,
            "factLabel": "✅ FAKTA ANOTASI BERSIH",
            "mythLabel": "❌ MITOS / RUANG BERANTAKAN",
            "explanation": "MITOS! Anotasi harus rapi, proporsional, dan tetap memperlihatkan konteks layar asli dengan jelas."
        },
        "stage3Speed": {
            "question": "Alat bantu apa yang paling praktis untuk membuat screenshot beranotasi anak panah dan kotak teks di laptop?",
            "options": [
                {
                    "label": "Snipping Tool / Lightshot / Flameshot / Canva",
                    "isCorrect": True,
                    "explanation": "Benar! Tools ini memungkinkan penambahan highlight, panah, dan nomor langkah secara cepat."
                },
                {
                    "label": "Aplikasi Pemutar Musik",
                    "isCorrect": False,
                    "explanation": "Pemutar musik tidak memiliki fungsi manipulasi grafis."
                },
                {
                    "label": "Kamera HP difoto miring tanpa fokus",
                    "isCorrect": False,
                    "explanation": "Foto layar HP dari luar tampak buram dan tidak profesional."
                }
            ],
            "timerSeconds": 25
        }
    },
    "orientasi-pplg-13-review-show-peer-feedback": {
        "id": "quest-or13",
        "moduleTitle": "Review Show & Peer Feedback Kolaboratif",
        "badge": "🎮 Mini-Game Quest: Modul 13",
        "xpReward": 15,
        "stage1Match": {
            "instruction": "Pasangkan Prinsip Peer Feedback dengan Sikap yang Benar:",
            "pairs": [
                {
                    "id": "p1",
                    "left": "Konstruktif",
                    "right": "Memberikan saran perbaikan yang jelas dan dapat dieksekusi"
                },
                {
                    "id": "p2",
                    "left": "Objektif",
                    "right": "Menilai berdasarkan rubrik karya, bukan preferensi pribadi"
                },
                {
                    "id": "p3",
                    "left": "Apresiatif",
                    "right": "Mengakui kelebihan dan orisinalitas analisis yang telah dibuat rekan"
                }
            ]
        },
        "stage2Detective": {
            "statement": "Klaim: \"Metode Sandwich Feedback menyampaikan kritik dengan urutan: Pujian Positif -> Kritik/Masukan Konstruktif -> Dorongan Semangat Positif.\"",
            "isFact": True,
            "factLabel": "✅ FAKTA METODE KOMUNIKASI",
            "mythLabel": "❌ SALAH / BUKAN SANDWICH",
            "explanation": "FAKTA! Metode Sandwich Feedback membuat rekan kerja lebih nyaman menerima masukan perbaikan tanpa merasa diserang."
        },
        "stage3Speed": {
            "question": "Bagaimana respon seorang engineer profesional saat menerima kritik teknis dari rekan satu tim?",
            "options": [
                {
                    "label": "Mendengarkan dengan terbuka, mencatat poin evaluasi, dan mendiskusikan alternatif solusi terbaik bersama.",
                    "isCorrect": True,
                    "explanation": "Luar biasa! Kedewasaan menerima code review adalah modal utama engineer sukses."
                },
                {
                    "label": "Marah dan menolak berbicara lagi dengan rekan tersebut.",
                    "isCorrect": False,
                    "explanation": "Sikap tidak profesional merusak dinamika kerja tim."
                },
                {
                    "label": "Menghapus proyek secara sepihak.",
                    "isCorrect": False,
                    "explanation": "Tindakan destruktif sangat dilarang di dunia kerja."
                }
            ],
            "timerSeconds": 25
        }
    },
    "orientasi-pplg-14-finalisasi-dokumen-review": {
        "id": "quest-or14",
        "moduleTitle": "Finalisasi & Standarisasi Dokumen Review OR-02",
        "badge": "🎮 Mini-Game Quest: Modul 14",
        "xpReward": 15,
        "stage1Match": {
            "instruction": "Pasangkan Bab Laporan Dokumen Review dengan Isinya:",
            "pairs": [
                {
                    "id": "p1",
                    "left": "Executive Summary",
                    "right": "Ringkasan singkat hasil audit, skor total, dan kesimpulan utama"
                },
                {
                    "id": "p2",
                    "left": "Tabel Temuan Masalah",
                    "right": "Daftar temuan bug, kendala UX, beserta tingkat keparahannya (Severity)"
                },
                {
                    "id": "p3",
                    "left": "Rekomendasi Roadmap",
                    "right": "Urutan prioritas fitur yang harus diperbaiki pada update selanjutnya"
                }
            ]
        },
        "stage2Detective": {
            "statement": "Klaim: \"Executive Summary harus ditulis sebanyak 50 halaman agar terlihat tebal dan meyakinkan bagi manajer proyek.\"",
            "isFact": False,
            "factLabel": "✅ FAKTA RINGKASAN PADAT",
            "mythLabel": "❌ MITOS / BERTELE-TELE",
            "explanation": "MITOS! Executive Summary dirancang ringkas (1-2 halaman) agar pimpinan dan stakeholder dapat mengambil keputusan dalam hitungan menit."
        },
        "stage3Speed": {
            "question": "Format dokumen akhir apa yang standar digunakan untuk laporan resmi audit produk agar tata letaknya tidak berantakan di berbagai perangkat?",
            "options": [
                {
                    "label": "Portable Document Format (PDF)",
                    "isCorrect": True,
                    "explanation": "Tepat sekali! PDF mengunci format font, margin, dan gambar sehingga konsisten di HP, tablet, maupun PC."
                },
                {
                    "label": "File teks .txt mentah tanpa format gambar",
                    "isCorrect": False,
                    "explanation": "TXT tidak mendukung gambar screenshot beranotasi."
                },
                {
                    "label": "File executable .exe",
                    "isCorrect": False,
                    "explanation": "EXE adalah aplikasi program, bukan format dokumen laporan."
                }
            ],
            "timerSeconds": 25
        }
    },
    "orientasi-pplg-15-pengumpulan-validasi-or02": {
        "id": "quest-or15",
        "moduleTitle": "Pengumpulan & Validasi Portofolio Skill Passport OR-02",
        "badge": "🎮 Mini-Game Quest: Modul 15",
        "xpReward": 15,
        "stage1Match": {
            "instruction": "Pasangkan Aspek Validasi OR-02 dengan Standar Kelulusannya:",
            "pairs": [
                {
                    "id": "p1",
                    "left": "Dokumen PDF Laporan",
                    "right": "Memuat 6 komponen review dan screenshot beranotasi lengkap"
                },
                {
                    "id": "p2",
                    "left": "Link Portofolio GDrive",
                    "right": "Dapat diakses publik dan memiliki folder terstruktur"
                },
                {
                    "id": "p3",
                    "left": "Pencapaian Level 2",
                    "right": "Memenuhi KKM 73 pada seluruh kriteria rubrik guru pengampu"
                }
            ]
        },
        "stage2Detective": {
            "statement": "Klaim: \"Asesmen Sumatif OR-02 menguji kemampuan berpikir kritis siswa dalam membedah produk digital serta merumuskan solusi rekayasa perangkat lunak.\"",
            "isFact": True,
            "factLabel": "✅ FAKTA SUMATIF KOMPETENSI",
            "mythLabel": "❌ SALAH / BUKAN OR-02",
            "explanation": "FAKTA! OR-02 membekali calon software engineer dengan insting audit kualitas dan pemahaman standar kepuasan pengguna."
        },
        "stage3Speed": {
            "question": "Apa manfaat jangka panjang mengumpulkan portofolio review produk digital yang rapi sejak kelas 10 RPL?",
            "options": [
                {
                    "label": "Menjadi bukti kompetensi nyata (*proof of work*) saat melamar magang industri (PKL) dan sertifikasi keahlian.",
                    "isCorrect": True,
                    "explanation": "Sempurna! Rekam jejak portofolio yang konsisten membedakan kalian dari ribuan lulusan lainnya."
                },
                {
                    "label": "Hanya untuk memenuhi kuota penyimpanan Google Drive.",
                    "isCorrect": False,
                    "explanation": "Portofolio adalah investasi karier masa depan kalian."
                },
                {
                    "label": "Tidak memiliki manfaat sama sekali.",
                    "isCorrect": False,
                    "explanation": "Portofolio adalah aset terpenting seorang praktisi IT."
                }
            ],
            "timerSeconds": 25
        }
    },
    "orientasi-pplg-16-rekap-skill-clinic-refleksi": {
        "id": "quest-or16",
        "moduleTitle": "Rekapitulasi Level, Skill Clinic, & Refleksi Akhir Semester 1",
        "badge": "🎮 Mini-Game Quest: Modul 16",
        "xpReward": 15,
        "stage1Match": {
            "instruction": "Pasangkan Tahapan Sesi Penutup Semester dengan Tujuannya:",
            "pairs": [
                {
                    "id": "p1",
                    "left": "Skill Clinic",
                    "right": "Sesi konsultasi bimbingan khusus untuk penuntasan target kompetensi"
                },
                {
                    "id": "p2",
                    "left": "Rekapitulasi Passport",
                    "right": "Pengecekan stempel kelulusan seluruh modul Sprint 1 & 2"
                },
                {
                    "id": "p3",
                    "left": "Refleksi Akhir Semester",
                    "right": "Evaluasi pertumbuhan pola pikir dan kesiapan melangkah ke semester genap"
                }
            ]
        },
        "stage2Detective": {
            "statement": "Klaim: \"Seorang programmer yang hebat adalah mereka yang merasa sudah tahu segalanya dan berhenti belajar setelah lulus satu mata pelajaran.\"",
            "isFact": False,
            "factLabel": "✅ FAKTA LIFELONG LEARNING",
            "mythLabel": "❌ MITOS / MINDSET JUMUD",
            "explanation": "MITOS! Dunia teknologi terus berkembang pesat. Pola pikir pembelajar sepanjang hayat (Continuous Learner) adalah kunci utama kesuksesan seorang software engineer."
        },
        "stage3Speed": {
            "question": "Setelah menuntaskan 16 modul Orientasi PPLG, apa modal utama yang telah kalian kuasai untuk menghadapi mata pelajaran kejuruan RPL berikutnya?",
            "options": [
                {
                    "label": "Pondasi logika software, wawasan ekosistem industri, kedisiplinan portofolio, dan etika kerja tim profesional.",
                    "isCorrect": True,
                    "explanation": "Selamat! Kalian telah menyelesaikan seluruh rangkaian Orientasi PPLG dengan luar biasa!"
                },
                {
                    "label": "Hanya hafalan istilah tanpa makna.",
                    "isCorrect": False,
                    "explanation": "Kalian telah mempraktikkan analisis dan pemecahan masalah riil."
                },
                {
                    "label": "Rasa lelah tanpa hasil.",
                    "isCorrect": False,
                    "explanation": "Portofolio Skill Passport kalian kini siap menjadi saksi kompetensi!"
                }
            ],
            "timerSeconds": 25
        }
    }
}

def get_gamified_quest_for_module(slug, module_title=""):
    """
    Mengambil quest 3-ronde interaktif berdasarkan slug modul.
    Jika modul baru belum terdaftar, gunakan fallback dinamis.
    """
    if slug in MODULE_GAMIFIED_QUESTS:
        return MODULE_GAMIFIED_QUESTS[slug]
    
    clean_title = module_title or "Materi Kejuruan Rekayasa Perangkat Lunak"
    return {
        "id": f"quest-{slug}",
        "moduleTitle": clean_title,
        "badge": "🎮 Mini-Game Quest Interaktif",
        "xpReward": 15,
        "stage1Match": {
            "instruction": f"Pasangkan Konsep Inti '{clean_title}' dengan Nilai Praktiknya:",
            "pairs": [
                {"id": "p1", "left": "Pemahaman Konsep", "right": "Fondasi logika dan teori sebelum mengeksekusi kode"},
                {"id": "p2", "left": "Evidence Portofolio", "right": "Bukti karya nyata yang diunggah ke repositori GDrive"},
                {"id": "p3", "left": "Standar KKM 73", "right": "Tolok ukur ketercapaian kompetensi vokasi RPL"},
            ],
        },
        "stage2Detective": {
            "statement": f"Klaim: 'Memahami substansi materi pada {clean_title} dan mendokumentasikan bukti pengerjaannya sangat krusial untuk kesiapan kerja di industri software.'",
            "isFact": True,
            "factLabel": "✅ FAKTA KOMPETENSI",
            "mythLabel": "❌ SALAH / TIDAK PENTING",
            "explanation": "FAKTA! Kompetensi software engineer dibangun melalui perpaduan pemahaman konsep yang kuat dan pembiasaan dokumentasi profesional.",
        },
        "stage3Speed": {
            "question": f"Apa sikap profesional yang harus ditunjukkan saat menyelesaikan tugas pada materi '{clean_title}'?",
            "options": [
                {
                    "label": "Mengerjakan dengan sungguh-sungguh, menjaga orisinalitas karya, dan mematuhi rubrik penilaian KKTP.",
                    "isCorrect": True,
                    "explanation": "Sempurna! Integritas dan kepatuhan standar adalah etika utama seorang Software Engineer.",
                },
                {
                    "label": "Menyalin pekerjaan teman tanpa memahami isinya.",
                    "isCorrect": False,
                    "explanation": "Plagiarisme merugikan perkembangan kompetensi diri sendiri.",
                },
                {
                    "label": "Mengabaikan petunjuk format file yang diminta guru.",
                    "isCorrect": False,
                    "explanation": "Kepatuhan format adalah bagian dari Quality Assurance.",
                },
            ],
            "timerSeconds": 25,
        },
    }
