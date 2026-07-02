"""
生成 3pl-warehousing / tainan-3pl-warehousing 兩頁的 Hero 右側圖
使用 KIE nano-banana-2，帶入 style ref + 角色去背參考
輸出：social-cards/文章配圖/（供 KING 確認後再插入頁面）
"""
import requests, os, json, time
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(dotenv_path='D:/咻咻打包CLAUDE/.env')
WP   = os.getenv('WP_SITE_URL', '').rstrip('/')
USER = os.getenv('WP_USERNAME', '')
PASS = os.getenv('WP_APP_PASSWORD', '')
KIE  = os.getenv('KIE_API_KEY', '')
AUTH = (USER, PASS)
KIE_H = {"Authorization": f"Bearer {KIE}", "Content-Type": "application/json"}

OUT      = Path('D:/咻咻打包CLAUDE/social-cards/文章配圖')
CHAR_DIR = Path('D:/咻咻打包CLAUDE/影片素材/角色去背')
OUT.mkdir(parents=True, exist_ok=True)

# 已有的 style refs（3D Pixar 暖橘風格）
STYLE_REF  = "https://www.shooshoo.com.tw/wp-content/uploads/2026/06/shooshoo-3pl-hero-ip.png"
STYLE_REF2 = "https://www.shooshoo.com.tw/wp-content/uploads/2026/06/shooshoo-outsourcing-hero-ip.png"

# 角色 ASCII 檔名對照
CHAR_NAME_MAP = {
    '揀貨喵喵.png': 'shooshoo-pickcat-ref2.png',
    '倉倉老闆.png': 'shooshoo-boss-ref2.png',
    '福福叉車.png': 'shooshoo-forklift-ref.png',
}

def wp_upload(img_path):
    img = Path(img_path)
    ascii_name = CHAR_NAME_MAP.get(img.name, 'shooshoo-char-ref.png')
    r = requests.post(f'{WP}/wp-json/wp/v2/media', auth=AUTH,
        headers={'Content-Disposition': f'attachment; filename="{ascii_name}"',
                 'Content-Type': 'image/png'},
        data=img.read_bytes(), timeout=60)
    if r.status_code not in (200, 201):
        raise Exception(f'WP upload failed {r.status_code}: {r.text[:120]}')
    url = r.json()['source_url']
    print(f'  WP uploaded: {ascii_name} -> {url}')
    return url

# ── Phase 1：上傳角色參考圖 ───────────────────────────────────────
print('=== Phase 1: Upload character refs to WP ===')
char_urls = {}
for fname in CHAR_NAME_MAP:
    path = CHAR_DIR / fname
    if path.exists():
        char_urls[fname] = wp_upload(path)
        time.sleep(1)
    else:
        print(f'  MISSING: {fname}')
        char_urls[fname] = None

pickcat_url  = char_urls.get('揀貨喵喵.png')
boss_url     = char_urls.get('倉倉老闆.png')
forklift_url = char_urls.get('福福叉車.png')

# ── Phase 2：KIE 生圖 ─────────────────────────────────────────────
TASKS = [
    {
        'filename': 'shooshoo-3pl-hero.png',
        'image_input': [STYLE_REF, STYLE_REF2, pickcat_url, boss_url, forklift_url],
        'prompt': (
            "Create a 4:3 commercial illustration EXACTLY matching the style of the first two reference images: "
            "warm amber-orange 3D Pixar clay toy art style, same soft rounded edges, same color palette (#FFF8ED cream background, #DCA54A amber accents). "
            "USE the character designs from references 3, 4, 5 as the characters in this scene. "
            "SCENE: Interior of a modern, organized 3PL fulfillment warehouse. "
            "Characters working happily: the cat mascot (ref 3) is picking and scanning packages, "
            "the box-head manager character (ref 4) is overseeing with a tablet. "
            "The yellow forklift character (ref 5) is in the background moving pallets. "
            "BACKGROUND: Tall neat metal shelving units filled with cardboard boxes, warm overhead lighting. "
            "Small floating UI badges: '99.8% 準確率' and '24h 出貨'. "
            "No text in main scene, leave bottom-right corner empty for brand badge. "
            "Same 3D clay warm orange brand style as reference images. Wide shot, cheerful professional mood."
        ),
    },
    {
        'filename': 'shooshoo-tainan-3pl-hero.png',
        'image_input': [STYLE_REF, STYLE_REF2, pickcat_url, boss_url],
        'prompt': (
            "Create a 4:3 commercial illustration EXACTLY matching the style of the first two reference images: "
            "warm amber-orange 3D Pixar clay toy art style, same soft rounded edges, same color palette (#FFF8ED cream background, #DCA54A amber accents). "
            "USE the character designs from references 3 and 4 as the main characters. "
            "SCENE: Outdoor view of a small modern Taiwan logistics warehouse at golden hour. "
            "The cat mascot (ref 3) and the box-head manager character (ref 4) are standing in front of the warehouse, "
            "both waving cheerfully. "
            "BACKGROUND: Clean white warehouse building with an orange '咻咻打包' sign area (blank rectangle for text). "
            "Green rice fields or flat Tainan countryside visible in the background to suggest southern Taiwan location. "
            "Small delivery van parked beside. Warm sunset amber sky. "
            "Friendly, trustworthy local brand feel. No text in image. "
            "Same 3D clay warm orange brand style as reference images."
        ),
    },
]

def kie_create(prompt, image_input_urls):
    urls = [u for u in image_input_urls if u]
    payload = {
        "model": "nano-banana-2",
        "input": {
            "prompt": prompt,
            "image_input": urls,
            "aspect_ratio": "4:3",
            "resolution": "2K",
            "output_format": "png",
        }
    }
    r = requests.post('https://api.kie.ai/api/v1/jobs/createTask',
        headers=KIE_H, json=payload, timeout=30)
    d = r.json()
    print(f'  createTask: code={d.get("code")} msg={d.get("msg","")}')
    if d.get('code') != 200:
        raise Exception(f'KIE failed: {d}')
    return d['data']['taskId']

def kie_poll(task_id, interval=8, timeout=360):
    for _ in range(timeout // interval):
        r = requests.get('https://api.kie.ai/api/v1/jobs/recordInfo',
            headers=KIE_H, params={'taskId': task_id}, timeout=15)
        d = r.json().get('data', {})
        state = d.get('state', '')
        print(f'  [{state}]', end=' ', flush=True)
        if state == 'success':
            print()
            return json.loads(d['resultJson'])['resultUrls'][0]
        elif state == 'fail':
            raise Exception(f'Failed: {d.get("failMsg")}')
        time.sleep(interval)
    raise TimeoutError('KIE timeout after 6 min')

def kie_download(url, path):
    r = requests.get(url, timeout=60)
    Path(path).write_bytes(r.content)
    print(f'  Saved: {Path(path).name} ({len(r.content):,} bytes)')

print('\n=== Phase 2: KIE Generate ===')
for task in TASKS:
    out_path = OUT / task['filename']
    print(f'\n[{task["filename"]}]')
    try:
        tid = kie_create(task['prompt'], task['image_input'])
        print(f'  task_id={tid}')
        url = kie_poll(tid)
        kie_download(url, out_path)
    except Exception as e:
        print(f'  ERROR: {e}')
    time.sleep(5)

print('\n=== Done. Check social-cards/文章配圖/ for results ===')
