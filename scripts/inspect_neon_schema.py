import psycopg2
from dotenv import dotenv_values

env1 = dotenv_values('d:/DATA/PROJEK/agunggumelarsaputra.com/.env.learninghub2.tmp')
env2 = dotenv_values('d:/DATA/PROJEK/agunggumelarsaputra.com/.env.production')

conn1 = psycopg2.connect(f"postgresql://neondb_owner:{env1.get('NEON2_PGPASSWORD')}@ep-delicate-breeze-aukvojoq.c-10.us-east-1.aws.neon.tech/neondb?sslmode=require")
cur1 = conn1.cursor()

tables = ['users', 'user_gamification', 'enrollment_tokens', 'user_enrollments', 'user_progress', 'user_submissions', 'tka_attempts', 'literasi_reports', 'literasi_peer_reviews']

for t in tables:
    cur1.execute(f"SELECT column_name, data_type FROM information_schema.columns WHERE table_name = '{t}' ORDER BY ordinal_position")
    cols = cur1.fetchall()
    print(f"\nTable '{t}':")
    for c, dt in cols:
        print(f"  - {c} ({dt})")

cur1.close()
conn1.close()
