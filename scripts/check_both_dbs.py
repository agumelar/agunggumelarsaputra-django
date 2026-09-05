import psycopg2
import time

def inspect_db(name, host, pwd):
    print(f"\n================ Inspecting {name} ({host}) ================")
    url = f"postgresql://neondb_owner:{pwd}@{host}/neondb?sslmode=require"
    try:
        conn = psycopg2.connect(url, connect_timeout=10)
        cur = conn.cursor()
        cur.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'")
        tables = cur.fetchall()
        print(f"[+] Connected! Found {len(tables)} tables:")
        total_rows = 0
        for (tbl,) in sorted(tables):
            cur.execute(f'SELECT COUNT(*) FROM "{tbl}"')
            cnt = cur.fetchone()[0]
            total_rows += cnt
            print(f"    - {tbl}: {cnt} rows")
        print(f"Total rows in {name}: {total_rows}")
        cur.close()
        conn.close()
        return True
    except Exception as e:
        print(f"[-] Error: {e}")
        return False

# Database 2 (learninghub-db-v2, wild-surf-59251405)
inspect_db("learninghub-db-v2 (wild-surf)", "ep-fancy-tooth-ausd8kl6.c-10.us-east-1.aws.neon.tech", "npg_qkbJ5hEmKs7Z")

# Database 1 (learninghub-db, green-shape-47425412)
# Try possible passwords
for pwd in ["npg_6mPekFf0XrhL", "npg_qkbJ5hEmKs7Z"]:
    if inspect_db("learninghub-db (green-shape)", "ep-delicate-breeze-aukvojoq.c-10.us-east-1.aws.neon.tech", pwd):
        break
