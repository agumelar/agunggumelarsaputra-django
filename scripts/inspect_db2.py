import psycopg2

URL = 'postgresql://neondb_owner:npg_UHKA04wlpFxD@ep-delicate-breeze-aukvojoq.c-10.us-east-1.aws.neon.tech/neondb?sslmode=require'

try:
    print("Menghubungkan ke learninghub-db (2nd DB)...")
    conn = psycopg2.connect(URL, connect_timeout=10)
    cur = conn.cursor()
    cur.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'")
    tables = cur.fetchall()
    print("Koneksi SUKSES! Daftar tabel ditemukan:")
    for (t,) in tables:
        cur.execute(f'SELECT COUNT(*) FROM "{t}"')
        cnt = cur.fetchone()[0]
        print(f"  * {t}: {cnt} baris data")
    cur.close()
    conn.close()
except Exception as e:
    print("Gagal:", e)
