import fs from 'fs';

const tsPath = 'D:/DATA/PROJEK/agunggumelarsaputra.com/src/utils/moduleCheckpoints.ts';
const content = fs.readFileSync(tsPath, 'utf-8');

const startMarker = 'export const MODULE_GAMIFIED_QUESTS: Record<string, GamifiedQuest> = ';
const startIndex = content.indexOf(startMarker);
const endIndex = content.indexOf('export function getGamifiedQuestForModule');

let objectCode = content.substring(startIndex + startMarker.length, endIndex).trim();
if (objectCode.endsWith(';')) {
  objectCode = objectCode.slice(0, -1).trim();
}

const quests = new Function(`return (${objectCode});`)();

const pyContent = `# apps/pembelajaran/checkpoints.py
# Bank Soal & Checkpoint Gamifikasi 16 Modul Orientasi PPLG / Kejuruan RPL

MODULE_GAMIFIED_QUESTS = ${JSON.stringify(quests, null, 4).replace(/true/g, 'True').replace(/false/g, 'False')}

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
`;

fs.writeFileSync('apps/pembelajaran/checkpoints.py', pyContent, 'utf-8');
console.log('Successfully generated apps/pembelajaran/checkpoints.py with', Object.keys(quests).length, 'quests.');
