import psycopg2
from dotenv import dotenv_values

env1 = dotenv_values('d:/DATA/PROJEK/agunggumelarsaputra.com/.env.learninghub2.tmp')
conn = psycopg2.connect(f"postgresql://neondb_owner:{env1.get('NEON2_PGPASSWORD')}@ep-delicate-breeze-aukvojoq.c-10.us-east-1.aws.neon.tech/neondb?sslmode=require")
cur = conn.cursor()

cur.execute('SELECT email, password_hash, role FROM users LIMIT 5')
for r in cur.fetchall():
    print(r[0], r[1][:25] if r[1] else None, r[2])

cur.close()
conn.close()
