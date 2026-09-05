import psycopg2
from dotenv import dotenv_values

env1 = dotenv_values('d:/DATA/PROJEK/agunggumelarsaputra.com/.env.learninghub2.tmp')
conn = psycopg2.connect(f"postgresql://neondb_owner:{env1.get('NEON2_PGPASSWORD')}@ep-delicate-breeze-aukvojoq.c-10.us-east-1.aws.neon.tech/neondb?sslmode=require")
cur = conn.cursor()

cur.execute('SELECT DISTINCT lesson_slug FROM user_submissions')
print('Submissions lesson_slugs:', [r[0] for r in cur.fetchall()])

cur.execute('SELECT DISTINCT lesson_slug FROM user_progress')
print('Progress lesson_slugs:', [r[0] for r in cur.fetchall()])

cur.execute('SELECT COUNT(*), MIN(created_at), MAX(created_at) FROM tka_attempts WHERE lesson_slug IS NULL')
print('Null lesson_slug count:', cur.fetchone())
cur.execute('SELECT lesson_slug, COUNT(*) FROM tka_attempts GROUP BY lesson_slug')
print('TKA attempts by slug:', cur.fetchall())

cur.close()
conn.close()
