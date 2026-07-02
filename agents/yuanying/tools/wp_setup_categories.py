"""
員瑛 — WordPress 分類批次建立 & 歸類腳本
1. 建立 6 個分類（已存在則跳過）
2. 抓取全站文章
3. 依標題關鍵字批次歸類
"""
import os
import requests
from requests.auth import HTTPBasicAuth
from dotenv import load_dotenv

load_dotenv()

WP_URL = os.getenv("WP_SITE_URL")
AUTH = HTTPBasicAuth(os.getenv("WP_USERNAME"), os.getenv("WP_APP_PASSWORD"))

# ── 6 個分類定義 ──────────────────────────────────────────────
CATEGORIES = [
    {"name": "超商出貨",     "slug": "convenience-store-shipping"},
    {"name": "倉儲外包指南", "slug": "3pl-outsourcing-guide"},
    {"name": "電商出貨 SOP", "slug": "ecommerce-shipping-sop"},
    {"name": "電商經營趨勢", "slug": "ecommerce-trends"},
    {"name": "倉儲知識",     "slug": "warehouse-knowledge"},
    {"name": "台南賣家特輯", "slug": "tainan-seller"},
]

# ── 文章 title 關鍵字 → 分類名稱 對照 ────────────────────────
# 每筆可對應多個分類（list）
TITLE_MAP = [
    (["第三方物流", "3PL 是什麼"],              ["倉儲外包指南"]),
    (["手機管理訂單", "WMS 系統介紹"],          ["倉儲知識"]),
    (["食品", "美妝", "恆溫倉儲"],             ["倉儲外包指南"]),
    (["揀貨 SOP", "零失誤出貨"],               ["電商出貨 SOP"]),
    (["包裝破損", "客訴", "全程錄影"],          ["電商出貨 SOP"]),
    (["退貨處理 SOP"],                          ["電商出貨 SOP"]),
    (["B2B", "B2C", "電商物流"],               ["倉儲知識"]),
    (["節慶爆單", "貼標加工"],                  ["電商出貨 SOP"]),
    (["庫存管理", "WMS 條碼"],                  ["倉儲知識"]),
    (["客製化打包", "品牌感"],                  ["倉儲外包指南"]),
    (["3PL 代出貨攻略"],                        ["倉儲外包指南"]),
    (["台南倉儲推薦"],                          ["台南賣家特輯"]),
    (["超商寄件", "宅配費用比較"],              ["超商出貨"]),
    (["代出貨費用"],                            ["倉儲外包指南"]),
    (["台灣 3PL 推薦"],                         ["倉儲外包指南"]),
    (["電商出貨流程 SOP"],                      ["電商出貨 SOP"]),
    (["倉儲外包優缺點"],                        ["倉儲外包指南"]),
    (["台南超商代寄推薦"],                      ["超商出貨", "台南賣家特輯"]),
    (["超商收件"],                              ["超商出貨"]),
]


def get_or_create_category(name: str, slug: str) -> int:
    """取得或建立單一分類，回傳 ID。"""
    endpoint = f"{WP_URL}/wp-json/wp/v2/categories"
    r = requests.get(endpoint, auth=AUTH, params={"slug": slug}, timeout=10)
    results = r.json()
    if results:
        print(f"  [EXISTS] {name} (ID {results[0]['id']})")
        return results[0]["id"]
    r2 = requests.post(endpoint, auth=AUTH, json={"name": name, "slug": slug}, timeout=10)
    if r2.status_code == 201:
        cat_id = r2.json()["id"]
        print(f"  [NEW]    {name} (ID {cat_id})")
        return cat_id
    print(f"  [ERR]    {name} create failed: {r2.text}")
    return None


def fetch_all_posts() -> list:
    """分頁抓取全站文章（最多 500 篇）。"""
    posts = []
    page = 1
    while True:
        r = requests.get(
            f"{WP_URL}/wp-json/wp/v2/posts",
            auth=AUTH,
            params={"per_page": 100, "page": page, "status": "publish,draft"},
            timeout=15,
        )
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


def match_categories(title: str, cat_name_to_id: dict) -> list:
    """比對文章標題，回傳應歸屬的分類 ID 列表。"""
    ids = []
    for keywords, cat_names in TITLE_MAP:
        if any(kw in title for kw in keywords):
            for cn in cat_names:
                if cn in cat_name_to_id:
                    ids.append(cat_name_to_id[cn])
    return list(set(ids))


def update_post_categories(post_id: int, category_ids: list) -> bool:
    r = requests.post(
        f"{WP_URL}/wp-json/wp/v2/posts/{post_id}",
        auth=AUTH,
        json={"categories": category_ids},
        timeout=10,
    )
    return r.status_code == 200


def main():
    print("=" * 50)
    print("員瑛 — WP 分類批次設定")
    print("=" * 50)

    # STEP 1：建立分類
    print("\n[STEP 1] 建立 6 個分類")
    cat_name_to_id = {}
    for cat in CATEGORIES:
        cid = get_or_create_category(cat["name"], cat["slug"])
        if cid:
            cat_name_to_id[cat["name"]] = cid

    print(f"\n分類 ID 對照：{cat_name_to_id}")

    # STEP 2：抓取全站文章
    print("\n[STEP 2] 抓取全站文章")
    posts = fetch_all_posts()
    print(f"  Found {len(posts)} posts")

    # STEP 3：批次歸類
    print("\n[STEP 3] 批次歸類")
    success = 0
    skipped = 0
    failed = 0

    for post in posts:
        title = post.get("title", {}).get("rendered", "")
        post_id = post["id"]
        cat_ids = match_categories(title, cat_name_to_id)

        if not cat_ids:
            print(f"  [SKIP] [{post_id}] {title[:40]}")
            skipped += 1
            continue

        cat_names_matched = [k for k, v in cat_name_to_id.items() if v in cat_ids]
        ok = update_post_categories(post_id, cat_ids)
        if ok:
            print(f"  [OK]   [{post_id}] {title[:40]} -> {', '.join(cat_names_matched)}")
            success += 1
        else:
            print(f"  [ERR]  [{post_id}] {title[:40]} update failed")
            failed += 1

    print("\n" + "=" * 50)
    print(f"完成！成功 {success} 篇 / 跳過 {skipped} 篇 / 失敗 {failed} 篇")
    print("=" * 50)


if __name__ == "__main__":
    main()
