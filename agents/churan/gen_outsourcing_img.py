import os, time, json, requests
from pathlib import Path
from dotenv import load_dotenv
from requests.auth import HTTPBasicAuth

load_dotenv()
KIE_KEY = os.getenv("KIE_API_KEY")
WP_URL  = os.getenv("WP_SITE_URL")
WP_AUTH = HTTPBasicAuth(os.getenv("WP_USERNAME"), os.getenv("WP_APP_PASSWORD"))
KIE_H   = {"Authorization": f"Bearer {KIE_KEY}", "Content-Type": "application/json"}
OUT_DIR = Path("D:/咻咻打包claude/影片素材")
OUT_DIR.mkdir(parents=True, exist_ok=True)

def gdrive(fid):
    return f"https://drive.google.com/uc?export=download&id={fid}"

XUXU = gdrive("1nKHKHljt4A3X8QLoQJhgeU4ubhcuHxt5")
BOSS = gdrive("1vPeOv82fPgvm6GqwNEfdSI20WdM7yE4M")

PROMPT = (
    "IP character illustration, Taiwan 3PL warehouse outsourcing pros cons comparison. "
    "Left half: stressed e-commerce seller overwhelmed by messy cardboard boxes piled everywhere, sweating. "
    "Right half: same seller relaxed smiling at laptop, cute Shooshoo orange mascot character "
    "carries packages happily beside him. "
    "Center divider with label left=自己出貨, right=交給咻咻. "
    "Warm orange color palette #F5A623, flat cute cartoon IP style, "
    "horizontal 16:9 wide format, professional blog hero banner quality."
)

payload = {
    "model": "gpt-image-2-image-to-image",
    "input": {
        "prompt": PROMPT,
        "input_urls": [XUXU, BOSS],
        "aspect_ratio": "16:9",
    }
}

print("生成倉儲外包 hero 圖...")
r = requests.post("https://api.kie.ai/api/v1/jobs/createTask", headers=KIE_H, json=payload, timeout=30)
data = r.json()
task_id = data["data"]["taskId"]
print(f"task_id: {task_id}")

img_url = None
for i in range(60):
    time.sleep(5)
    r2 = requests.get("https://api.kie.ai/api/v1/jobs/recordInfo",
                      headers=KIE_H, params={"taskId": task_id}, timeout=15)
    d = r2.json().get("data", {})
    state = d.get("state")
    print(f"  [{i*5}s] {state}")
    if state == "success":
        img_url = json.loads(d["resultJson"])["resultUrls"][0]
        break
    elif state == "fail":
        print(f"FAIL: {d}")
        break

if not img_url:
    print("未取得圖片 URL，結束")
    exit(1)

print(f"img_url: {img_url}")

# 下載
img_data = requests.get(img_url, timeout=60).content
out = OUT_DIR / "shooshoo-outsourcing-hero-ip.png"
out.write_bytes(img_data)
print(f"下載至: {out}")

# 上傳 WordPress
fname = "shooshoo-outsourcing-hero-ip.png"
up = requests.post(
    f"{WP_URL}/wp-json/wp/v2/media",
    auth=WP_AUTH,
    headers={
        "Content-Disposition": f"attachment; filename={fname}",
        "Content-Type": "image/png",
    },
    data=img_data,
    timeout=60,
)
info = up.json()
media_id = info["id"]
wp_url = info["source_url"]
print(f"WP media_id={media_id}, url={wp_url}")

# 設 featured_media
requests.post(f"{WP_URL}/wp-json/wp/v2/posts/3244", auth=WP_AUTH,
              json={"featured_media": media_id}, timeout=15)
print("featured_media 設定 OK")

# 替換文章 hero src
r3 = requests.get(f"{WP_URL}/wp-json/wp/v2/posts/3244",
                  auth=WP_AUTH, params={"context": "edit"}, timeout=15)
old_url = "https://www.shooshoo.com.tw/wp-content/uploads/2026/06/shooshoo-branded-packaging-ip.png"
raw = r3.json()["content"]["raw"]
if old_url in raw:
    new_raw = raw.replace(old_url, wp_url)
    requests.post(f"{WP_URL}/wp-json/wp/v2/posts/3244", auth=WP_AUTH,
                  json={"content": new_raw}, timeout=15)
    print("文章 hero 圖替換 OK")
else:
    print(f"找不到舊圖 URL，WP URL 已上傳：{wp_url}")

print("=== 完成 ===")
