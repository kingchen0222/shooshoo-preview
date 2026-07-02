import os, requests
from requests.auth import HTTPBasicAuth
from dotenv import load_dotenv
load_dotenv()
WP_URL = os.getenv("WP_SITE_URL")
AUTH = HTTPBasicAuth(os.getenv("WP_USERNAME"), os.getenv("WP_APP_PASSWORD"))

renames = [
    ("ecommerce-trends", "電商趨勢"),
    ("tainan-seller", "台南特輯"),
]
r = requests.get(f"{WP_URL}/wp-json/wp/v2/categories", auth=AUTH, params={"per_page": 100}, timeout=10)
cats = {c["slug"]: c for c in r.json()}
for slug, new_name in renames:
    if slug in cats:
        cid = cats[slug]["id"]
        r2 = requests.post(f"{WP_URL}/wp-json/wp/v2/categories/{cid}", auth=AUTH, json={"name": new_name}, timeout=10)
        old_name = cats[slug]["name"]
        print(f"[{r2.status_code}] {old_name} -> {new_name} (ID {cid})")
    else:
        print(f"[SKIP] {slug}")
