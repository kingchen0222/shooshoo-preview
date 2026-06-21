"""
員瑛 — 低難度 SEO 修復一次跑完
1. 作者名稱改「咻咻打包編輯團隊」
2. /flow/ H1 修正
3. /wms/ H1 修正
4. sitemap 狀態確認
"""
import requests, re
from requests.auth import HTTPBasicAuth

auth = HTTPBasicAuth("admin001", "X0Zq 1xEz ejyY IeKW iBbn ioQy")
WP = "https://www.shooshoo.com.tw"

# ── 1. 作者名稱 ──────────────────────────────────────────
bio = (
    "咻咻打包是台南在地三方倉儲（3PL）團隊，專注電商代出貨服務。"
    "本站文章由倉儲營運與電商行銷專業人員撰寫，"
    "提供台灣電商賣家實用的物流、庫存管理與出貨知識。"
)
r = requests.post(f"{WP}/wp-json/wp/v2/users/2", auth=auth,
    json={"name": "咻咻打包編輯團隊", "display_name": "咻咻打包編輯團隊", "description": bio})
info = r.json()
print(f"✅ 作者更新 → {info.get('name')}（status {r.status_code}）")

# ── 2. 取得 /flow/ 和 /wms/ 的 page ID ──────────────────
pages = requests.get(f"{WP}/wp-json/wp/v2/pages?per_page=50", auth=auth).json()
slug_map = {p["slug"]: p for p in pages}

for slug, new_h1 in [
    ("flow", "咻咻打包代出貨完整流程｜從入庫到寄件全程搞定"),
    ("wms",  "智慧 WMS 庫存管理系統｜電商賣家即時掌握庫存"),
]:
    page = slug_map.get(slug)
    if not page:
        print(f"⚠️  找不到 slug={slug}")
        continue

    pid = page["id"]
    raw = requests.get(f"{WP}/wp-json/wp/v2/pages/{pid}",
                       auth=auth, params={"context": "edit"}).json()["content"]["raw"]

    # 替換第一個 H1（無論是區塊或 HTML 格式）
    old_h1 = "把後勤交給咻咻，咻！就搞定"
    if old_h1 in raw:
        new_raw = raw.replace(old_h1, new_h1, 1)
        r2 = requests.post(f"{WP}/wp-json/wp/v2/pages/{pid}", auth=auth,
                           json={"content": new_raw})
        print(f"✅ /{slug}/ H1 已更新 → {new_h1}（status {r2.status_code}）")
    else:
        print(f"ℹ️  /{slug}/ 未找到舊 H1 文字，可能已改或在主題模板中（需後台手動）")

# ── 3. 確認 sitemap ──────────────────────────────────────
for url in [
    f"{WP}/sitemap_index.xml",
    f"{WP}/sitemap.xml",
    f"{WP}/wp-sitemap.xml",
    f"{WP}/page-sitemap.xml",
]:
    code = requests.head(url, timeout=8).status_code
    flag = "✅" if code == 200 else "❌"
    print(f"{flag}  {url} → {code}")

print("\n=== 完成 ===")
