import os
import re
from pathlib import Path
from django.core.management.base import BaseCommand
from apps.pembelajaran.models import Modul


class Command(BaseCommand):
    help = 'Seeder otomatis untuk mengimpor 16 Modul Orientasi PPLG / RPL dari repositori agunggumelarsaputra.com'

    def handle(self, *args, **options):
        # Path sumber markdown
        source_dir = Path('d:/DATA/PROJEK/agunggumelarsaputra.com/src/content/pembelajaran')

        if not source_dir.exists():
            self.stderr.write(self.style.ERROR(f"Direktori sumber tidak ditemukan di: {source_dir}"))
            return

        files = sorted(list(source_dir.glob('*.md')))
        self.stdout.write(f"Menemukan {len(files)} file modul di {source_dir}...")

        created_count = 0
        updated_count = 0

        for file_path in files:
            with open(file_path, 'r', encoding='utf-8') as f:
                raw_content = f.read()

            # Ekstrak Frontmatter dan Body
            frontmatter = {}
            body_content = raw_content

            if raw_content.startswith('---'):
                parts = raw_content.split('---', 2)
                if len(parts) >= 3:
                    fm_text = parts[1]
                    body_content = parts[2].strip()

                    # Parse key-value frontmatter sederhana
                    for line in fm_text.strip().split('\n'):
                        if ':' in line:
                            key, val = line.split(':', 1)
                            key = key.strip()
                            val = val.strip().strip('"').strip("'")
                            frontmatter[key] = val

            slug = file_path.stem
            # Ekstrak nomor urutan dari nama file, misal: orientasi-pplg-01-... -> 1
            order_match = re.search(r'orientasi-pplg-(\d+)', slug)
            order = int(order_match.group(1)) if order_match else int(frontmatter.get('order', 1))
            kode = f"OR-{order:02d}"

            title = frontmatter.get('title', slug.replace('-', ' ').title())
            description = frontmatter.get('description', '')
            category = frontmatter.get('category', 'Orientasi PPLG')
            level = frontmatter.get('level', 'Pemula')
            duration = frontmatter.get('duration', '2 JP (90 Menit)')
            teacher_tip = frontmatter.get('teacherTip', '')

            modul_obj, created = Modul.objects.update_or_create(
                slug=slug,
                defaults={
                    'kode': kode,
                    'judul': title,
                    'deskripsi': description,
                    'kategori': category,
                    'level': level,
                    'durasi': duration,
                    'urutan': order,
                    'content_materi': body_content,
                    'teacher_tip': teacher_tip,
                    'xp_materi': 10,
                    'xp_lkpd': 25,
                    'xp_reflection': 15,
                    'is_published': True,
                }
            )

            if created:
                created_count += 1
                self.stdout.write(self.style.SUCCESS(f"  + [Baru] {kode}: {title}"))
            else:
                updated_count += 1
                self.stdout.write(self.style.WARNING(f"  ~ [Update] {kode}: {title}"))

        self.stdout.write(self.style.SUCCESS(f"\nSelesai! {created_count} modul baru dibuat, {updated_count} modul diperbarui."))
