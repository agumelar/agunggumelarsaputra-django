#!/bin/sh
set -e

echo "[*] Menunggu PostgreSQL siap..."
python << END
import sys
import time
import os
import psycopg2

db_name = os.getenv('DB_NAME', 'ags_db')
db_user = os.getenv('DB_USER', 'ags_user')
db_password = os.getenv('DB_PASSWORD', 'ags_password_secure2026')
db_host = os.getenv('DB_HOST', 'db')
db_port = os.getenv('DB_PORT', '5432')

for i in range(30):
    try:
        conn = psycopg2.connect(
            dbname=db_name,
            user=db_user,
            password=db_password,
            host=db_host,
            port=db_port,
            connect_timeout=3
        )
        conn.close()
        print("[+] PostgreSQL siap dan terhubung!")
        sys.exit(0)
    except Exception as e:
        print(f"[-] Menunggu database ({i+1}/30)... {e}")
        time.sleep(2)

print("[-] Gagal terhubung ke database setelah 30 percobaan.")
sys.exit(1)
END

echo "[*] Menjalankan migrasi database Django..."
python manage.py migrate --noinput

echo "[*] Mengumpulkan static files (WhiteNoise)..."
python manage.py collectstatic --noinput

echo "[*] Menginisialisasi Master Data Kurikulum (Guru, 16 Modul, CBT TKA, Token)..."
python manage.py seed_master_curriculum

echo "[+] Memulai Gunicorn Production Server..."
exec gunicorn config.wsgi:application \
    --bind 0.0.0.0:8000 \
    --workers 3 \
    --timeout 120 \
    --access-logfile - \
    --error-logfile -
