import psycopg2
from dotenv import dotenv_values

env_vals2 = dotenv_values('d:/DATA/PROJEK/agunggumelarsaputra.com/.env.production')
env_vals1 = dotenv_values('d:/DATA/PROJEK/agunggumelarsaputra.com/.env.learninghub2.tmp')

host2 = 'ep-fancy-tooth-ausd8kl6.c-10.us-east-1.aws.neon.tech'
pwd2 = env_vals2.get('PGPASSWORD') or 'npg_qkbJ5hEmKs7Z'

host1 = 'ep-delicate-breeze-aukvojoq.c-10.us-east-1.aws.neon.tech'
pwd1 = env_vals1.get('NEON2_PGPASSWORD')

conn2 = psycopg2.connect(f"postgresql://neondb_owner:{pwd2}@{host2}/neondb?sslmode=require")
cur2 = conn2.cursor()

conn1 = psycopg2.connect(f"postgresql://neondb_owner:{pwd1}@{host1}/neondb?sslmode=require")
cur1 = conn1.cursor()

print("--- Project 1 (green-shape / ep-delicate-breeze) ---")
cur1.execute("SELECT MIN(created_at), MAX(created_at), COUNT(*) FROM users")
print("Users:", cur1.fetchone())
cur1.execute("SELECT MIN(submitted_at), MAX(submitted_at), COUNT(*) FROM user_submissions")
print("Submissions:", cur1.fetchone())
cur1.execute("SELECT column_name FROM information_schema.columns WHERE table_name = 'tka_attempts'")
print("TKA cols:", [c[0] for c in cur1.fetchall()])
cur1.execute("SELECT COUNT(*) FROM tka_attempts")
print("TKA attempts:", cur1.fetchone())
cur1.execute("SELECT DISTINCT student_class FROM users")
print("Classes:", [c[0] for c in cur1.fetchall() if c[0]])

print("\n--- Project 2 (wild-surf / ep-fancy-tooth) ---")
cur2.execute("SELECT MIN(created_at), MAX(created_at), COUNT(*) FROM users")
print("Users:", cur2.fetchone())
cur2.execute("SELECT MIN(submitted_at), MAX(submitted_at), COUNT(*) FROM user_submissions")
print("Submissions:", cur2.fetchone())
cur2.execute("SELECT DISTINCT student_class FROM users")
print("Classes:", [c[0] for c in cur2.fetchall() if c[0]])

# Check overlap of user emails
cur1.execute("SELECT email FROM users WHERE email IS NOT NULL")
emails1 = set(r[0].lower() for r in cur1.fetchall())
cur2.execute("SELECT email FROM users WHERE email IS NOT NULL")
emails2 = set(r[0].lower() for r in cur2.fetchall())

print(f"\nUnique emails in DB1: {len(emails1)}")
print(f"Unique emails in DB2: {len(emails2)}")
print(f"Overlap emails: {len(emails1.intersection(emails2))}")
print(f"Emails only in DB1: {len(emails1 - emails2)}")
print(f"Emails only in DB2: {len(emails2 - emails1)}")

cur1.close()
conn1.close()
cur2.close()
conn2.close()
