"""
楚然 — 為兩篇文章生成 IP 角色 hero 圖，並上傳至 WordPress
"""
import os, time, json, requests
from pathlib import Path
from dotenv import load_dotenv
from requests.auth import HTTPBasicAuth

load_dotenv()
KIE_KEY = os.getenv("KIE_API_KEY")
WP_URL   = os.getenv("WP_SITE_URL")
WP_AUTH  = HTTPBasicAuth(os.getenv("WP_USERNAME"), os.getenv("WP_APP_PASSWORD"))

KIE_HEADERS = {"Authorization": f"Bearer {KIE_KEY}", "Content-Type": "application/json"}
OUT_DIR = Path("D:/咻咻打包claude/影片素材")
OUT_DIR.mkdir(parents=True, exist_ok=True)

def _gdrive(file_id):
    return f"https://drive.google.com/uc?export=download&id={file_id}"

CHARACTERS = {
    "咻咻":     _gdrive("1nKHKHljt4A3X8QLoQJhgeU4ubhcuHxt5"),
    "行政喵喵": _gdrive("10rCSo3o9gKqj2xX_rWl6cQXYkTEN_jmT"),
    "揀貨喵喵": _gdrive("19hncQSYnQOFeS4ihoxUdhyNlV1Ql6NJY"),
    "電商老闆": _gdrive("1vPeOv82fPgvm6GqwNEfdSI20WdM7yE4M"),
    "倉倉老闆": _gdrive("11rB9avhrdR3eiHusu2pzi36jGZWkijxq"),
}

ARTICLES = {
    "shooshoo-sop-hero-ip": {
        "post_id": 3243,
        "chars": ["行政喵喵", "揀貨喵喵"],
        "aspect": "16:9",
        "prompt": (
            "咻咻打包電商出貨流程SOP場景，"
            "行政喵喵拿著訂單清單核對，揀貨喵喵在倉庫架子旁取出商品，"
            "背景是整潔的台灣三方倉庫，貨架上有整齊的紙箱，"
            "牆上有大型橘色「咻咻打包」logo，"
            "六個出貨步驟圖示飄浮在旁：收單 揀貨 包裝 貼標 核對 交件，"
            "暖橘色系，IP 角色可愛扁平插畫風，橫式構圖 16:9，高解析度。"
        ),
    },
    "shooshoo-outsourcing-hero-ip": {
        "post_id": 3244,
        "chars": ["電商老闆", "咻咻"],
        "aspect": "16:9",
        "prompt": (
            "咻咻打包倉儲外包優缺點比較場景，"
            "左側電商老闆被成堆紙箱包圍、滿頭大汗自己打包出貨，"
            "右側同一個電商老闆輕鬆坐在電腦前微笑，旁邊是咻咻打包IP角色扛著大包裹大力幫忙，"
            "中間有一條比較線，左寫「自己出貨 😓」右寫「交給咻咻 😊」，"
            "暖橘色系，IP 角色可愛扁平插畫風，橫式構圖 16:9，高解析度。"
        ),
    },
}


def create_task(prompt, chars, aspect):
    payload = {
        "model": "gpt-image-2-image-to-image",
        "input": {
            "prompt": prompt,
            "input_urls": [CHARACTERS[c] for c in chars],
            "aspect_ratio": aspect,
        }
    }
    r = requests.post("https://api.kie.ai/api/v1/jobs/createTask",
                      headers=KIE_HEADERS, json=payload, timeout=30)
    data = r.json()
    if data.get("code") != 200:
        raise Exception(f"建立失敗: {data}")
    return data["data"]["taskId"]


def poll(task_id, timeout=300):
    for _ in range(timeout // 5):
        time.sleep(5)
        r = requests.get("https://api.kie.ai/api/v1/jobs/recordInfo",
                         headers=KIE_HEADERS, params={"taskId": task_id}, timeout=15)
        data = r.json().get("data", {})
        state = data.get("state")
        print(f"  [{state}] ...", end="\r")
        if state == "success":
            urls = json.loads(data["resultJson"])["resultUrls"]
            return urls[0]
        elif state == "fail":
            raise Exception(f"失敗: {data.get('failMsg')}")
    raise TimeoutError("超時")


def upload_to_wp(img_path, filename):
    with open(img_path, "rb") as f:
        data = f.read()
    r = requests.post(
        f"{WP_URL}/wp-json/wp/v2/media",
        auth=WP_AUTH,
        headers={"Content-Disposition": f'attachment; filename="{filename}"',
                 "Content-Type": "image/png"},
        data=data, timeout=60
    )
    if r.status_code == 201:
        info = r.json()
        return info["id"], info["source_url"]
    raise Exception(f"上傳失敗: {r.text[:200]}")


def set_featured(post_id, media_id):
    r = requests.post(
        f"{WP_URL}/wp-json/wp/v2/posts/{post_id}",
        auth=WP_AUTH,
        json={"featured_media": media_id},
        timeout=15
    )
    return r.status_code in (200, 201)


def update_hero_in_content(post_id, old_url, new_url):
    """把文章 HTML 裡的 hero img src 換成新圖"""
    r = requests.get(f"{WP_URL}/wp-json/wp/v2/posts/{post_id}",
                     auth=WP_AUTH, params={"context": "edit"}, timeout=15)
    content = r.json()["content"]["raw"]
    if old_url in content:
        new_content = content.replace(old_url, new_url)
        requests.post(f"{WP_URL}/wp-json/wp/v2/posts/{post_id}",
                      auth=WP_AUTH, json={"content": new_content}, timeout=15)
        print(f"  文章 hero 圖已替換")
    else:
        print(f"  未在文章 HTML 找到舊圖 URL，請手動確認")


if __name__ == "__main__":
    for name, cfg in ARTICLES.items():
        print(f"\n=== {name} ===")
        out_path = OUT_DIR / f"{name}.png"

        # 1. 生成圖片
        print(f"  生成中（chars={cfg['chars']}）...")
        task_id = create_task(cfg["prompt"], cfg["chars"], cfg["aspect"])
        print(f"  task_id: {task_id}")
        img_url = poll(task_id)
        print(f"\n  生成完成: {img_url}")

        # 2. 下載
        img_data = requests.get(img_url, timeout=60).content
        out_path.write_bytes(img_data)
        print(f"  下載至: {out_path}")

        # 3. 上傳 WordPress
        media_id, wp_url = upload_to_wp(out_path, f"{name}.png")
        print(f"  WP media_id={media_id}, url={wp_url}")

        # 4. 設 featured_media
        ok = set_featured(cfg["post_id"], media_id)
        print(f"  featured_media 設定: {'OK' if ok else 'FAIL'}")

        # 5. 替換文章 hero src（現在是舊的 IP 圖）
        old_hero = {
            3243: "https://www.shooshoo.com.tw/wp-content/uploads/2026/06/shooshoo-wms-inventory-ip.png",
            3244: "https://www.shooshoo.com.tw/wp-content/uploads/2026/06/shooshoo-branded-packaging-ip.png",
        }[cfg["post_id"]]
        update_hero_in_content(cfg["post_id"], old_hero, wp_url)

    print("\n=== 全部完成 ===")
