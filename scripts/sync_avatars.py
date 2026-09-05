import os
import sys
import django
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import dotenv_values

# Setup Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
django.setup()

from django.contrib.auth import get_user_model
User = get_user_model()

def sync_avatars():
    base_env = dotenv_values(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '.env'))
    url1 = os.getenv('NEON_DB1_URL') or base_env.get('NEON_DB1_URL')
    url2 = os.getenv('NEON_DB2_URL') or base_env.get('NEON_DB2_URL')

    print("[*] Mengambil data foto profil dari Neon DB 1 & DB 2...")
    avatar_map = {} # email -> avatar_url

    # Dari DB 1
    if url1:
        try:
            conn1 = psycopg2.connect(url1, cursor_factory=RealDictCursor)
            cur1 = conn1.cursor()
            cur1.execute("SELECT email, avatar_url FROM users WHERE avatar_url IS NOT NULL AND avatar_url != ''")
            for r in cur1.fetchall():
                em = r['email'].strip().lower()
                avatar_map[em] = r['avatar_url']
            cur1.close()
            conn1.close()
            print(f"    -> Ditemukan {len(avatar_map)} foto profil di DB 1")
        except Exception as e:
            print(f"    [-] DB 1 Error: {e}")

    # Dari DB 2 (timpa jika ada yang lebih baru)
    if url2:
        try:
            conn2 = psycopg2.connect(url2, cursor_factory=RealDictCursor)
            cur2 = conn2.cursor()
            cur2.execute("SELECT email, avatar_url FROM users WHERE avatar_url IS NOT NULL AND avatar_url != ''")
            count_db2 = 0
            for r in cur2.fetchall():
                em = r['email'].strip().lower()
                avatar_map[em] = r['avatar_url']
                count_db2 += 1
            cur2.close()
            conn2.close()
            print(f"    -> Ditemukan {count_db2} foto profil di DB 2")
        except Exception as e:
            print(f"    [-] DB 2 Error: {e}")

    print(f"[*] Total foto profil unik yang akan disinkronkan: {len(avatar_map)}")

    updated_count = 0
    for email, av_url in avatar_map.items():
        user = User.objects.filter(email__iexact=email).first()
        if user:
            user.avatar_url = av_url
            user.save(update_fields=['avatar_url'])
            updated_count += 1

    print(f"[SUCCESS] Berhasil memperbarui {updated_count} foto profil pengguna di Django!")

if __name__ == '__main__':
    sync_avatars()
