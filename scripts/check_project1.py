import psycopg2
from dotenv import dotenv_values

env_vals = dotenv_values('d:/DATA/PROJEK/agunggumelarsaputra.com/.env.learninghub2.tmp')
pwd1 = env_vals.get('NEON2_PGPASSWORD') or env_vals.get('POSTGRES_PASSWORD')
host1 = 'ep-delicate-breeze-aukvojoq.c-10.us-east-1.aws.neon.tech'

print(f"Connecting to Project 1 ({host1})...")
try:
    url = f"postgresql://neondb_owner:{pwd1}@{host1}/neondb?sslmode=require"
    conn = psycopg2.connect(url, connect_timeout=10)
    cur = conn.cursor()
    cur.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'")
    tables = cur.fetchall()
    print(f"[+] Connected to Project 1! Found {len(tables)} tables:")
    for (tbl,) in sorted(tables):
        cur.execute(f'SELECT COUNT(*) FROM "{tbl}"')
        cnt = cur.fetchone()[0]
        print(f"    - {tbl}: {cnt} rows")
    cur.close()
    conn.close()
except Exception as e:
    print(f"[-] Error: {e}")
