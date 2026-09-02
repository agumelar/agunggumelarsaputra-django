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

def create_branch(project_id, branch_name, parent_id):
    url = f"{BASE_URL}/projects/{project_id}/branches"
    payload = json.dumps({
        "branch": {
            "name": branch_name,
            "parent_id": parent_id
        },
        "endpoints": [
            {
                "type": "read_write"
            }
        ]
    }).encode('utf-8')
    req = urllib.request.Request(url, data=payload, headers=headers, method="POST")
    try:
        with urllib.request.urlopen(req) as resp:
            return json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        print(f"HTTPError: {e.code} - {e.read().decode()}")
        return None

res = create_branch("wild-surf-59251405", "backup-migrate", "br-broad-sky-au88m5hc")
print("Create Branch Result:", json.dumps(res, indent=2))
