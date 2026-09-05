import psycopg2
from dotenv import dotenv_values

env1 = dotenv_values('d:/DATA/PROJEK/agunggumelarsaputra.com/.env.learninghub2.tmp')
conn1 = psycopg2.connect(f"postgresql://neondb_owner:{env1.get('NEON2_PGPASSWORD')}@ep-delicate-breeze-aukvojoq.c-10.us-east-1.aws.neon.tech/neondb?sslmode=require")
cur1 = conn1.cursor()

cur1.execute("SELECT COUNT(*), COUNT(avatar_url) FROM users WHERE avatar_url IS NOT NULL AND avatar_url != ''")
print("DB1 users with avatar_url:", cur1.fetchone())

cur1.execute("SELECT email, avatar_url FROM users WHERE email ILIKE '%agumelar%' OR email ILIKE '%agung%'")
print("Teacher in DB1:", cur1.fetchall())

env2 = dotenv_values('d:/DATA/PROJEK/agunggumelarsaputra.com/.env.production')
conn2 = psycopg2.connect(f"postgresql://neondb_owner:{env2.get('PGPASSWORD')}@ep-fancy-tooth-ausd8kl6.c-10.us-east-1.aws.neon.tech/neondb?sslmode=require")
cur2 = conn2.cursor()
cur2.execute("SELECT email, avatar_url FROM users WHERE email ILIKE '%agumelar%' OR email ILIKE '%agung%'")
print("Teacher in DB2:", cur2.fetchall())
cur2.close()
conn2.close()

cur1.close()
conn1.close()
