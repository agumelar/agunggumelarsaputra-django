import json
import urllib.request
import urllib.error

API_KEY = "napi_g1zg2qf8at5thrd1ffr8nxl1v46wk40el6dz4dj2ls5zaecz2i1egrwaz5bip1b5"
BASE_URL = "https://console.neon.tech/api/v2"
ORG_ID = "org-rapid-meadow-15033271"

headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Accept": "application/json",
    "Content-Type": "application/json"
}

def api_get(endpoint):
    req = urllib.request.Request(f"{BASE_URL}{endpoint}", headers=headers)
    try:
        with urllib.request.urlopen(req) as resp:
            return json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        print(f"HTTPError on {endpoint}: {e.code} - {e.read().decode()}")
        return None

for pid in ["wild-surf-59251405", "green-shape-47425412"]:
    print(f"\n================ Project: {pid} ================")
    branches = api_get(f"/projects/{pid}/branches")
    print("Branches:", branches)
    endpoints = api_get(f"/projects/{pid}/endpoints")
    print("Endpoints:", endpoints)
    if branches and 'branches' in branches:
        for b in branches['branches']:
            bid = b['id']
            dbs = api_get(f"/projects/{pid}/branches/{bid}/databases")
            print(f"Databases for branch {bid}:", dbs)
            roles = api_get(f"/projects/{pid}/branches/{bid}/roles")
            print(f"Roles for branch {bid}:", roles)
