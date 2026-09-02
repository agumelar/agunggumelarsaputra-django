import psycopg2

NEON_HOST = "ep-fancy-tooth-ausd8kl6.c-10.us-east-1.aws.neon.tech"
USER = "neondb_owner"
PASSWORD = "npg_qkbJ5hEmKs7Z"

db_names = ["learninghub", "learninghub2", "learning_hub", "learning_hub_2", "learning-hub", "learning-hub-2", "neondb", "postgres"]

print("Testing Neon database names...")
for db in db_names:
    url = f"postgresql://{USER}:{PASSWORD}@{NEON_HOST}/{db}?sslmode=require"
    try:
        conn = psycopg2.connect(url, connect_timeout=5)
        print(f"[+] SUCCESS on Neon DB: {db}")
        cur = conn.cursor()
        cur.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'")
        tables = cur.fetchall()
        print(f"    Tables in {db}: {tables}")
        for (tbl,) in tables:
            cur.execute(f'SELECT COUNT(*) FROM "{tbl}"')
            cnt = cur.fetchone()[0]
            print(f"      - {tbl}: {cnt} rows")
        cur.close()
        conn.close()
    except Exception as e:
        print(f"[-] Failed on {db}: {e}")
