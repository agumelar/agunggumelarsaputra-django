import os
import json
import re
from pathlib import Path
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.conf import settings
from apps.admin_panel.models import EnrollmentToken
from apps.pembelajaran.models import Modul
from apps.tka.models import TkaPackage, TkaQuestion

User = get_user_model()


class Command(BaseCommand):
    help = 'Seeder Master: Inisialisasi Akun Guru, 16 Modul Orientasi PPLG, 10 Paket CBT TKA, dan Token Rombel'

    def handle(self, *args, **options):
        self.stdout.write(self.style.MIGRATE_HEADING('=== MEMULAI INITIAL SEEDING MASTER DATA ===\n'))

        # 1. Superuser / Guru Pengampu RPL
        self.stdout.write('[1/4] Menyiapkan Akun Guru Pengampu RPL (Superadmin)...')
        teacher, created = User.objects.get_or_create(
            email='agumelarsaputra@gmail.com',
            defaults={
                'username': 'agumelar',
                'first_name': 'Agung Gumelar',
                'last_name': 'Saputra, S.Tr.T.',
                'role': User.ROLE_GURU,
                'is_staff': True,
                'is_superuser': True,
            }
        )
        if created:
            teacher.set_password('RPL@Rongga2026')
            teacher.save()
            self.stdout.write(self.style.SUCCESS('  + Akun Guru Baru Dibuat: agumelarsaputra@gmail.com (Default password: RPL@Rongga2026)'))
        else:
            teacher.first_name = 'Agung Gumelar'
            teacher.last_name = 'Saputra, S.Tr.T.'
            teacher.role = User.ROLE_GURU
            teacher.is_staff = True
            teacher.is_superuser = True
            teacher.save()
            self.stdout.write(self.style.SUCCESS(f"  [OK] Akun Guru Sudah Tersedia: agumelarsaputra@gmail.com"))

        # Pastikan akun legacy guru_agung juga ada jika diperlukan
        User.objects.get_or_create(
            username='guru_agung',
            defaults={
                'email': 'agung@smkn1rongga.sch.id',
                'first_name': 'Agung Gumelar',
                'last_name': 'Saputra, S.Tr.T.',
                'role': User.ROLE_GURU,
                'is_staff': True,
                'is_superuser': True,
            }
        )

        # 2. Token Enrollment KBM per Rombel
        self.stdout.write('\n[2/4] Menyiapkan Token Enrollment KBM per Rombel...')
        rombel_list = [
            ('10RPL1-2026', 'KBM Orientasi PPLG & Praktikum 10 RPL 1', '10 RPL 1'),
            ('10RPL2-2026', 'KBM Orientasi PPLG & Praktikum 10 RPL 2', '10 RPL 2'),
            ('11RPL1-2026', 'KBM Konsentrasi Keahlian 11 RPL 1', '11 RPL 1'),
            ('11RPL2-2026', 'KBM Konsentrasi Keahlian 11 RPL 2', '11 RPL 2'),
            ('12RPL1-2026', 'KBM Uji Kompetensi & TKA 12 RPL 1', '12 RPL 1'),
            ('12RPL2-2026', 'KBM Uji Kompetensi & TKA 12 RPL 2', '12 RPL 2'),
            ('RPL-DEMO', 'Sesi Uji Coba Umum Lab Komputer RPL', 'Semua Kelas'),
        ]

        for token_code, title, target_class in rombel_list:
            t, t_created = EnrollmentToken.objects.get_or_create(
                token=token_code,
                defaults={
                    'title': title,
                    'target_class': target_class,
                    'target_type': 'all',
                    'created_by': teacher,
                    'is_active': True,
                    'max_uses': 36,
                }
            )
            status_txt = "Baru" if t_created else "Aktif"
            self.stdout.write(self.style.SUCCESS(f"  + [{status_txt}] Token {token_code} -> {target_class}"))

        # 3. 16 Modul Kanonik Orientasi PPLG
        self.stdout.write('\n[3/4] Mengimpor 16 Modul Kanonik Orientasi PPLG...')
        base_dir = Path(settings.BASE_DIR)
        modul_dir = base_dir / 'data' / 'content' / 'pembelajaran'
        if not modul_dir.exists():
            modul_dir = Path('d:/DATA/PROJEK/agunggumelarsaputra.com/src/content/pembelajaran')

        if modul_dir.exists():
            files = sorted(list(modul_dir.glob('*.md')))
            modul_count = 0
            for file_path in files:
                with open(file_path, 'r', encoding='utf-8') as f:
                    raw = f.read()

                frontmatter = {}
                body = raw
                if raw.startswith('---'):
                    parts = raw.split('---', 2)
                    if len(parts) >= 3:
                        for line in parts[1].strip().split('\n'):
                            if ':' in line:
                                k, v = line.split(':', 1)
                                frontmatter[k.strip()] = v.strip().strip('"').strip("'")
                        body = parts[2].strip()

                slug = file_path.stem
                order_match = re.search(r'orientasi-pplg-(\d+)', slug)
                order = int(order_match.group(1)) if order_match else int(frontmatter.get('order', 1))
                kode = f"OR-{order:02d}"

                Modul.objects.update_or_create(
                    slug=slug,
                    defaults={
                        'kode': kode,
                        'judul': frontmatter.get('title', slug.replace('-', ' ').title()),
                        'deskripsi': frontmatter.get('description', ''),
                        'kategori': frontmatter.get('category', 'Orientasi PPLG'),
                        'level': frontmatter.get('level', 'Pemula'),
                        'durasi': frontmatter.get('duration', '2 JP (90 Menit)'),
                        'urutan': order,
                        'content_materi': body,
                        'teacher_tip': frontmatter.get('teacherTip', ''),
                        'xp_materi': 10,
                        'xp_lkpd': 25,
                        'xp_reflection': 15,
                        'is_published': True,
                    }
                )
                modul_count += 1
            self.stdout.write(self.style.SUCCESS(f"  [OK] {modul_count} Modul Orientasi PPLG berhasil dimuat."))
        else:
            self.stdout.write(self.style.WARNING(f"  [-] Folder modul tidak ditemukan di {modul_dir}"))

        # 4. 10 Paket Soal CBT TKA PPLG
        self.stdout.write('\n[4/4] Mengimpor 10 Paket Ujian CBT TKA PPLG & Bank Soal...')
        tka_md_dir = base_dir / 'data' / 'content' / 'tka-drilling'
        tka_json_dir = base_dir / 'data' / 'tka-questions'

        if not tka_json_dir.exists():
            tka_json_dir = Path('d:/DATA/PROJEK/agunggumelarsaputra.com/src/data/tka-questions')
        if not tka_md_dir.exists():
            tka_md_dir = Path('d:/DATA/PROJEK/agunggumelarsaputra.com/src/content/tka-drilling')

        if tka_json_dir.exists():
            json_files = sorted(list(tka_json_dir.glob('*.json')))
            index_to_letter = {0: 'A', 1: 'B', 2: 'C', 3: 'D', 4: 'E'}
            total_pkg = 0
            total_q = 0

            for jf in json_files:
                slug = jf.stem
                order_match = re.search(r'tka-(\d+)', slug)
                order = int(order_match.group(1)) if order_match else 1
                kode = f"TKA-{order:02d}"

                # Cek markdown metadata
                title = f"Paket {order}: {slug.replace('-', ' ').title()}"
                description = ""
                category = "Drilling TKA PPLG"
                level = "Lanjutan"
                durasi = 60
                teacher_tip = ""
                body = ""

                md_file = tka_md_dir / f"{slug}.md"
                if md_file.exists():
                    with open(md_file, 'r', encoding='utf-8') as f:
                        raw = f.read()
                    if raw.startswith('---'):
                        parts = raw.split('---', 2)
                        if len(parts) >= 3:
                            for line in parts[1].strip().split('\n'):
                                if ':' in line:
                                    k, v = line.split(':', 1)
                                    k = k.strip()
                                    v = v.strip().strip('"').strip("'")
                                    if k == 'title': title = v
                                    elif k == 'description': description = v
                                    elif k == 'category': category = v
                                    elif k == 'level': level = v
                                    elif k == 'teacherTip': teacher_tip = v
                            body = parts[2].strip()

                pkg, _ = TkaPackage.objects.update_or_create(
                    slug=slug,
                    defaults={
                        'kode': kode,
                        'judul': title,
                        'kategori': category,
                        'level': level,
                        'durasi_menit': durasi,
                        'passing_grade': 75,
                        'deskripsi': description,
                        'content_materi': body,
                        'teacher_tip': teacher_tip,
                        'urutan': order,
                        'xp_base': 25,
                        'is_published': True,
                    }
                )
                total_pkg += 1

                with open(jf, 'r', encoding='utf-8') as f:
                    q_data = json.load(f)

                for idx, q in enumerate(q_data, start=1):
                    opts = q.get('options', ['', '', '', '', ''])
                    c_idx = q.get('correctAnswer', 0)
                    TkaQuestion.objects.update_or_create(
                        package=pkg,
                        urutan=idx,
                        defaults={
                            'question_text': q.get('question', ''),
                            'option_a': opts[0] if len(opts) > 0 else '',
                            'option_b': opts[1] if len(opts) > 1 else '',
                            'option_c': opts[2] if len(opts) > 2 else '',
                            'option_d': opts[3] if len(opts) > 3 else '',
                            'option_e': opts[4] if len(opts) > 4 else '',
                            'correct_answer': index_to_letter.get(c_idx, 'A'),
                            'explanation': q.get('explanation', ''),
                            'category': q.get('category', category),
                        }
                    )
                    total_q += 1

            self.stdout.write(self.style.SUCCESS(f"  [OK] {total_pkg} Paket CBT TKA dan {total_q} butir soal berhasil dimuat."))

        self.stdout.write(self.style.MIGRATE_HEADING('\n=== MASTER DATA BERHASIL DIINISIALISASI 100% ===\n'))
