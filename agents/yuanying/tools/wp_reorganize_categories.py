"""
員瑛 — WP 分類重組腳本
舊 6 個 → 新 4 個 + 全部（前台）

新分類：
  出貨教學   (shipping-guide)   ← 超商出貨 + 電商出貨 SOP
  倉儲知識   (warehouse-knowledge) ← 倉儲外包指南 + 倉儲知識
  台南特輯   (tainan-seller)    ← 台南賣家特輯（保留 slug）
  電商趨勢   (ecommerce-trends) ← 電商新聞 + 電商經營趨勢

刪除舊分類：超商出貨、電商出貨 SOP、倉儲外包指南、電商新聞、電商經營趨勢
"""
import os
import requests
from requests.auth import HTTPBasicAuth
from dotenv import load_dotenv

load_dotenv()
WP_URL = os.getenv("WP_SITE_URL")
AUTH = HTTPBasicAuth(os.getenv("WP_USERNAME"), os.getenv("WP_APP_PASSWORD"))

# ── 新 4 個分類 ──────────────────────────────────────────────
NEW_CATEGORIES = [
    {"name": "出貨教學", "slug": "shipping-guide"},
    {"name": "倉儲知識", "slug": "warehouse-knowledge"},
    {"name": "台南特輯", "slug": "tainan-seller"},
    {"name": "電商趨勢", "slug": "ecommerce-trends"},
]

# ── 舊 slug → 新 slug 對應（文章重新歸類用）────────────────
MERGE_MAP = {
    "convenience-store-shipping": "shipping-guide",
    "ecommerce-shipping-sop":     "shipping-guide",
    "3pl-outsourcing-guide":      "warehouse-knowledge",
    "warehouse-knowledge":        "warehouse-knowledge",
    "tainan-seller":              "tainan-seller",
    "ecommerce-trends":           "ecommerce-trends",
}

# 電商新聞的中文 slug（URL encoded）
ECOMMERCE_NEWS_ENCODED = "%e9%9b%bb%e5%95%86%e6%96%b0%e8%81%9e"
ECOMMERCE_NEWS_NAME = "電商新聞"


def get_all_categories() -> dict:
    """取得全部分類，回傳 {slug: {id, name, slug}}"""
    cats = {}
    r = requests.get(f"{WP_URL}/wp-json/wp/v2/categories",
                     auth=AUTH, params={"per_page": 100}, timeout=10)
    for c in r.json():
        cats[c["slug"]] = c
    return cats


def get_or_create_category(name: str, slug: str, all_cats: dict) -> int:
    if slug in all_cats:
        print(f"  [EXISTS] {name} (ID {all_cats[slug]['id']})")
        return all_cats[slug]["id"]
    r = requests.post(f"{WP_URL}/wp-json/wp/v2/categories",
                      auth=AUTH, json={"name": name, "slug": slug}, timeout=10)
    if r.status_code == 201:
        cid = r.json()["id"]
        print(f"  [NEW]    {name} (ID {cid})")
        return cid
    print(f"  [ERR]    {name}: {r.text}")
    return None


def fetch_all_posts() -> list:
    posts = []
    page = 1
    while True:
        r = requests.get(f"{WP_URL}/wp-json/wp/v2/posts", auth=AUTH,
                         params={"per_page": 100, "page": page,
                                 "status": "publish,draft", "_fields": "id,title,categories"},
                         timeout=15)
        if r.status_code != 200:
            break
        batch = r.json()
        if not batch:
            break
        posts.extend(batch)
        if len(batch) < 100:
            break
        page += 1
    return posts


def delete_category(cat_id: int, name: str):
    r = requests.delete(f"{WP_URL}/wp-json/wp/v2/categories/{cat_id}",
                        auth=AUTH, params={"force": True}, timeout=10)
    if r.status_code == 200:
        print(f"  [DEL]    {name} (ID {cat_id})")
    else:
        print(f"  [ERR]    delete {name}: {r.text}")


def main():
    print("=" * 55)
    print("員瑛 — WP 分類重組")
    print("=" * 55)

    all_cats = get_all_categories()
    print(f"\n目前 WP 共有 {len(all_cats)} 個分類")

    # STEP 1：建立新分類
    print("\n[STEP 1] 建立新 4 個分類")
    new_slug_to_id = {}
    for cat in NEW_CATEGORIES:
        cid = get_or_create_category(cat["name"], cat["slug"], all_cats)
        if cid:
            new_slug_to_id[cat["slug"]] = cid

    # 重新抓（因為可能新建了）
    all_cats = get_all_categories()

    # STEP 2：找出電商新聞的 ID（中文 slug）
    ecommerce_news_id = None
    for slug, cat in all_cats.items():
        if cat["name"] == ECOMMERCE_NEWS_NAME:
            ecommerce_news_id = cat["id"]
            print(f"\n找到「電商新聞」ID={ecommerce_news_id}, slug={slug}")
            # 電商新聞 → 電商趨勢
            MERGE_MAP[slug] = "ecommerce-trends"
            break

    # STEP 3：批次更新文章分類
    print("\n[STEP 2] 批次更新文章分類")
    posts = fetch_all_posts()
    print(f"  共 {len(posts)} 篇文章")

    ok = skip = err = 0
    for post in posts:
        pid = post["id"]
        title = post.get("title", {}).get("rendered", "")[:35]
        old_cat_ids = post.get("categories", [])

        # 找出這些 ID 對應的 slug
        id_to_slug = {v["id"]: v["slug"] for v in all_cats.values()}
        new_cat_ids = set()

        for old_id in old_cat_ids:
            old_slug = id_to_slug.get(old_id, "")
            new_slug = MERGE_MAP.get(old_slug)
            if new_slug and new_slug in new_slug_to_id:
                new_cat_ids.add(new_slug_to_id[new_slug])

        if not new_cat_ids:
            print(f"  [SKIP] [{pid}] {title}")
            skip += 1
            continue

        r = requests.post(f"{WP_URL}/wp-json/wp/v2/posts/{pid}",
                          auth=AUTH, json={"categories": list(new_cat_ids)}, timeout=10)
        if r.status_code == 200:
            new_names = [c["name"] for c in NEW_CATEGORIES
                         if new_slug_to_id.get(c["slug"]) in new_cat_ids]
            print(f"  [OK]   [{pid}] {title} -> {', '.join(new_names)}")
            ok += 1
        else:
            print(f"  [ERR]  [{pid}] {title}: {r.text[:60]}")
            err += 1

    print(f"\n  結果：OK={ok} / SKIP={skip} / ERR={err}")

    # STEP 4：刪除舊分類
    print("\n[STEP 3] 刪除舊分類")
    TO_DELETE_SLUGS = [
        "convenience-store-shipping",
        "ecommerce-shipping-sop",
        "3pl-outsourcing-guide",
    ]
    for slug in TO_DELETE_SLUGS:
        if slug in all_cats:
            delete_category(all_cats[slug]["id"], all_cats[slug]["name"])
        else:
            print(f"  [SKIP] {slug} 不存在")

    # 電商新聞（中文 slug）
    if ecommerce_news_id:
        delete_category(ecommerce_news_id, ECOMMERCE_NEWS_NAME)

    # 電商經營趨勢（已合入電商趨勢）- 只有名稱不同才刪
    for slug, cat in all_cats.items():
        if cat["name"] == "電商經營趨勢" and slug != "ecommerce-trends":
            delete_category(cat["id"], cat["name"])

    print("\n" + "=" * 55)
    print("完成！WP 分類已重組為 4 個。")
    print("下一步：進 Elementor 開 Show All 啟用「全部」Tab")
    print("=" * 55)


if __name__ == "__main__":
    main()
