import json
import re
from pathlib import Path
from django.core.management.base import BaseCommand
from apps.tka.models import TkaPackage, TkaQuestion


class Command(BaseCommand):
    help = 'Seeder otomatis untuk mengimpor 10 Paket Drilling & 600 Soal TKA PPLG dari repositori agunggumelarsaputra.com'

    def handle(self, *args, **options):
        md_dir = Path('d:/DATA/PROJEK/agunggumelarsaputra.com/src/content/tka-drilling')
        json_dir = Path('d:/DATA/PROJEK/agunggumelarsaputra.com/src/data/tka-questions')

        if not md_dir.exists() or not json_dir.exists():
            self.stderr.write(self.style.ERROR(f"Direktori sumber tidak ditemukan di {md_dir} atau {json_dir}"))
            return

        json_files = sorted(list(json_dir.glob('*.json')))
        self.stdout.write(f"Menemukan {len(json_files)} paket bank soal di {json_dir}...")

        index_to_letter = {0: 'A', 1: 'B', 2: 'C', 3: 'D', 4: 'E'}
        total_packages = 0
        total_questions = 0

        for json_file in json_files:
            slug = json_file.stem  # e.g. tka-01-algoritma-logika
            order_match = re.search(r'tka-(\d+)', slug)
            order = int(order_match.group(1)) if order_match else 1
            kode = f"TKA-{order:02d}"

            # Cek file markdown pendamping untuk konten materi & frontmatter
            md_file = md_dir / f"{slug}.md"
            title = f"Paket {order}: {slug.replace('-', ' ').title()}"
            description = ""
            category = "Drilling TKA PPLG"
            level = "Lanjutan"
            duration_str = "60 min"
            durasi_menit = 60
            teacher_tip = ""
            body_content = ""

            if md_file.exists():
                with open(md_file, 'r', encoding='utf-8') as f:
                    raw_content = f.read()

                if raw_content.startswith('---'):
                    parts = raw_content.split('---', 2)
                    if len(parts) >= 3:
                        fm_text = parts[1]
                        body_content = parts[2].strip()

                        for line in fm_text.strip().split('\n'):
                            if ':' in line:
                                key, val = line.split(':', 1)
                                key = key.strip()
                                val = val.strip().strip('"').strip("'")
                                if key == 'title':
                                    title = val
                                elif key == 'description':
                                    description = val
                                elif key == 'category':
                                    category = val
                                elif key == 'level':
                                    level = val
                                elif key == 'duration':
                                    duration_str = val
                                elif key == 'teacherTip':
                                    teacher_tip = val

                # Parse duration minutes
                dur_match = re.search(r'(\d+)', duration_str)
                if dur_match:
                    durasi_menit = int(dur_match.group(1))

            package, created = TkaPackage.objects.update_or_create(
                slug=slug,
                defaults={
                    'kode': kode,
                    'judul': title,
                    'kategori': category,
                    'level': level,
                    'durasi_menit': durasi_menit,
                    'passing_grade': 75,
                    'deskripsi': description,
                    'content_materi': body_content,
                    'teacher_tip': teacher_tip,
                    'urutan': order,
                    'xp_base': 25,
                    'is_published': True,
                }
            )
            total_packages += 1

            # Baca bank soal JSON
            with open(json_file, 'r', encoding='utf-8') as f:
                questions_data = json.load(f)

            pkg_questions_count = 0
            for idx, q in enumerate(questions_data, start=1):
                q_text = q.get('question', '')
                options = q.get('options', ['', '', '', '', ''])
                correct_idx = q.get('correctAnswer', 0)
                correct_letter = index_to_letter.get(correct_idx, 'A')
                explanation = q.get('explanation', '')
                q_category = q.get('category', category)

                # Pastikan minimal 5 opsi ada
                opt_a = options[0] if len(options) > 0 else ''
                opt_b = options[1] if len(options) > 1 else ''
                opt_c = options[2] if len(options) > 2 else ''
                opt_d = options[3] if len(options) > 3 else ''
                opt_e = options[4] if len(options) > 4 else ''

                TkaQuestion.objects.update_or_create(
                    package=package,
                    urutan=idx,
                    defaults={
                        'question_text': q_text,
                        'option_a': opt_a,
                        'option_b': opt_b,
                        'option_c': opt_c,
                        'option_d': opt_d,
                        'option_e': opt_e,
                        'correct_answer': correct_letter,
                        'explanation': explanation,
                        'category': q_category,
                    }
                )
                pkg_questions_count += 1
                total_questions += 1

            self.stdout.write(self.style.SUCCESS(f"  + [{kode}] {title}: {pkg_questions_count} butir soal dimuat."))

        self.stdout.write(self.style.SUCCESS(f"\nSelesai! {total_packages} paket dan total {total_questions} butir soal berhasil diimpor ke database."))
