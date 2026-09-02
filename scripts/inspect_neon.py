import psycopg2

URLS = [
    ("Pooler", "postgresql://neondb_owner:npg_qkbJ5hEmKs7Z@ep-fancy-tooth-ausd8kl6-pooler.c-10.us-east-1.aws.neon.tech/neondb?sslmode=require"),
    ("Direct", "postgresql://neondb_owner:npg_qkbJ5hEmKs7Z@ep-fancy-tooth-ausd8kl6.c-10.us-east-1.aws.neon.tech/neondb?sslmode=require"),
]

for name, url in URLS:
    print(f"Testing {name}...")
    try:
        conn = psycopg2.connect(url)
        cur = conn.cursor()
        cur.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'")
        tables = cur.fetchall()
        print(f"Success on {name}! Tables: {tables}")
        for (tbl,) in tables:
            cur.execute(f'SELECT COUNT(*) FROM "{tbl}"')
            cnt = cur.fetchone()[0]
            print(f"  - {tbl}: {cnt} rows")
        cur.close()
        conn.close()
    except Exception as e:
        print(f"Failed on {name}: {e}")
