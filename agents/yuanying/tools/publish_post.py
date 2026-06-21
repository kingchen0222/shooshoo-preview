import os
import requests
from requests.auth import HTTPBasicAuth
from dotenv import load_dotenv

load_dotenv()

WP_URL = os.getenv("WP_SITE_URL")
AUTH = HTTPBasicAuth(os.getenv("WP_USERNAME"), os.getenv("WP_APP_PASSWORD"))


def publish_post(title: str, content: str, seo_description: str = "",
                 categories: list = None, tags: list = None, status: str = "draft"):
    """
    員瑛發文到官網 WordPress
    status: 'draft' 草稿 | 'publish' 直接發佈
    """
    payload = {
        "title": title,
        "content": content,
        "status": status,
        "excerpt": seo_description,
    }
    if categories:
        payload["categories"] = get_or_create_terms(categories, "categories")
    if tags:
        payload["tags"] = get_or_create_terms(tags, "tags")

    r = requests.post(f"{WP_URL}/wp-json/wp/v2/posts", auth=AUTH, json=payload, timeout=15)
    data = r.json()
    if r.status_code == 201:
        return {"success": True, "id": data["id"], "link": data["link"], "status": data["status"]}
    else:
        return {"success": False, "error": data.get("message", str(data))}


def get_or_create_terms(names: list, taxonomy: str) -> list:
    ids = []
    endpoint = f"{WP_URL}/wp-json/wp/v2/{taxonomy}"
    for name in names:
        r = requests.get(endpoint, auth=AUTH, params={"search": name}, timeout=10)
        results = r.json()
        if results:
            ids.append(results[0]["id"])
        else:
            r2 = requests.post(endpoint, auth=AUTH, json={"name": name}, timeout=10)
            if r2.status_code == 201:
                ids.append(r2.json()["id"])
    return ids


def delete_post(post_id: int):
    r = requests.delete(f"{WP_URL}/wp-json/wp/v2/posts/{post_id}",
                        auth=AUTH, params={"force": True}, timeout=10)
    return r.status_code == 200


def list_posts(count: int = 5):
    r = requests.get(f"{WP_URL}/wp-json/wp/v2/posts",
                     params={"per_page": count, "orderby": "date"}, timeout=10)
    posts = r.json()
    return [{"id": p["id"], "title": p["title"]["rendered"], "status": p["status"],
             "date": p["date"][:10], "link": p["link"]} for p in posts]


if __name__ == "__main__":
    # 刪除測試草稿
    print("刪除測試文章 3212...")
    ok = delete_post(3212)
    print("已刪除" if ok else "刪除失敗")

    # 列出最新文章
    print("\n最新文章：")
    for p in list_posts(5):
        print(f"  [{p['status']}] {p['title']} ({p['date']})")
