import json
import urllib.request
import urllib.error

API_KEY = "napi_g1zg2qf8at5thrd1ffr8nxl1v46wk40el6dz4dj2ls5zaecz2i1egrwaz5bip1b5"
CONN_STR = "postgresql://neondb_owner:npg_qkbJ5hEmKs7Z@ep-fancy-tooth-ausd8kl6.c-10.us-east-1.aws.neon.tech/neondb?sslmode=require"

url = "https://ep-fancy-tooth-ausd8kl6.c-10.us-east-1.aws.neon.tech/sql"
payload = json.dumps({"query": "SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'"}).encode('utf-8')

req = urllib.request.Request(
    url,
    data=payload,
    headers={
        "Content-Type": "application/json",
        "Neon-Connection-String": CONN_STR,
        "Authorization": f"Bearer {API_KEY}"
    }
)

try:
    with urllib.request.urlopen(req) as resp:
        res = json.loads(resp.read().decode())
        print("HTTP SQL Result:", res)
except urllib.error.HTTPError as e:
    print(f"HTTPError: {e.code} - {e.read().decode()}")
except Exception as e:
    print(f"Error: {e}")
