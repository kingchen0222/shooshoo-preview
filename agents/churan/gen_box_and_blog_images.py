"""
楚然生圖任務：紙箱訂製 3 格 + Blog 縮圖 3 張
流程：
1. 上傳 IP 角色去背 PNG 到 WP 取得公開 URL
2. 加上現有 style ref 對齊 3D Pixar 暖橘風格
3. 傳給 KIE nano-banana-2 生圖
4. 下載存到 social-cards/
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

CHAR_DIR  = Path('D:/咻咻打包CLAUDE/影片素材/角色去背')
OUT_BOX   = Path('D:/咻咻打包CLAUDE/social-cards/紙箱訂製')
OUT_BLOG  = Path('D:/咻咻打包CLAUDE/social-cards/blog-thumbnails')
OUT_BOX.mkdir(parents=True, exist_ok=True)
OUT_BLOG.mkdir(parents=True, exist_ok=True)

# 風格參考：現有文章封面（3D Pixar 暖橘底）
STYLE_REF  = "https://www.shooshoo.com.tw/wp-content/uploads/2026/06/shooshoo-3pl-hero-ip.png"
STYLE_REF2 = "https://www.shooshoo.com.tw/wp-content/uploads/2026/06/shooshoo-outsourcing-hero-ip.png"

# 角色 → ASCII 上傳名稱對照
CHAR_NAME_MAP = {
    '咻咻.png':      'shooshoo-box-mascot-ref.png',
    '倉倉老闆.png':  'shooshoo-warehouse-boss-ref.png',
    '揀貨喵喵.png':  'shooshoo-pickcat-ref.png',
    '福福叉車.png':  'shooshoo-forklift-ref.png',
    '咻卡.png':      'shooshoo-car-ref.png',
    '電商老闆.png':  'shooshoo-boss-ref.png',
}

# ── 上傳角色到 WP ──────────────────────────────────────────────────
def wp_upload(img_path):
    img = Path(img_path)
    ascii_name = CHAR_NAME_MAP.get(img.name, 'shooshoo-char-ref.png')
    r = requests.post(f'{WP}/wp-json/wp/v2/media', auth=AUTH,
        headers={'Content-Disposition': f'attachment; filename="{ascii_name}"',
                 'Content-Type': 'image/png'},
        data=img.read_bytes(), timeout=60)
    if r.status_code not in (200, 201):
        raise Exception(f'WP upload failed {r.status_code}: {r.text[:200]}')
    url = r.json()['source_url']
    print(f'  OK WP: {ascii_name} -> {url}')
    return url

print('=== Phase 1: 上傳角色到 WP ===')
chars_needed = ['咻咻.png', '倉倉老闆.png', '揀貨喵喵.png', '福福叉車.png', '咻卡.png', '電商老闆.png']
char_urls = {}
for fname in chars_needed:
    path = CHAR_DIR / fname
    if path.exists():
        char_urls[fname] = wp_upload(path)
        time.sleep(1.5)
    else:
        print(f'  ❌ MISSING: {fname}')
        char_urls[fname] = None

shooshoo    = char_urls['咻咻.png']
boss_wh     = char_urls['倉倉老闆.png']
pickcat     = char_urls['揀貨喵喵.png']
forklift    = char_urls['福福叉車.png']
car         = char_urls['咻卡.png']
ec_boss     = char_urls['電商老闆.png']

# ── KIE 工具函式 ───────────────────────────────────────────────────
def kie_create(prompt, image_urls, aspect_ratio='1:1'):
    urls = [u for u in image_urls if u]
    payload = {
        "model": "nano-banana-2",
        "input": {
            "prompt": prompt,
            "image_input": urls,
            "aspect_ratio": aspect_ratio,
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
    raise TimeoutError('KIE timeout')

def kie_download(url, path):
    r = requests.get(url, timeout=60)
    Path(path).write_bytes(r.content)
    print(f'  Saved {Path(path).name} ({len(r.content):,} bytes)')

# ── 任務清單 ───────────────────────────────────────────────────────
TASKS = [
    # ── 紙箱訂製 3 格（1:1）──────────────────────────────
    {
        'out': OUT_BOX / 'box-plain-corrugated.png',
        'aspect_ratio': '1:1',
        'image_input': [STYLE_REF, STYLE_REF2, shooshoo],
        'prompt': (
            "Create a square product illustration in warm amber 3D Pixar clay toy style, "
            "matching the reference images' color palette and soft rounded aesthetic. "
            "USE the box mascot character from reference image 3 as the main character. "
            "SCENE: The cute cardboard box character standing proudly next to a neat stack of 3 plain brown "
            "corrugated shipping boxes. Clean warm cream background. "
            "Bottom label in Chinese: '公版瓦楞紙箱'. "
            "Simple, clean product card composition. No busy details."
        ),
    },
    {
        'out': OUT_BOX / 'box-branded-custom.png',
        'aspect_ratio': '1:1',
        'image_input': [STYLE_REF, STYLE_REF2, boss_wh],
        'prompt': (
            "Create a square product illustration in warm amber 3D Pixar clay toy style, "
            "matching the reference images' color palette. "
            "USE the suited box-head boss character from reference image 3. "
            "SCENE: The boss character proudly presenting a beautiful orange-branded custom printed shipping box "
            "with a logo stamped on it. Clean cream background, warm studio lighting feel. "
            "Bottom label in Chinese: '品牌訂製箱'. "
            "Premium quality feel, confident pose."
        ),
    },
    {
        'out': OUT_BOX / 'box-fruit-packaging.png',
        'aspect_ratio': '1:1',
        'image_input': [STYLE_REF, STYLE_REF2, pickcat],
        'prompt': (
            "Create a square product illustration in warm amber 3D Pixar clay toy style, "
            "matching the reference images' color palette. "
            "USE the grey cat character from reference image 3. "
            "SCENE: The cute grey cat carefully arranging bright fresh oranges and apples "
            "into an open flat cardboard fruit tray with protective mesh netting. "
            "Clean cream background. Bottom label in Chinese: '果盒包裝'. "
            "Fresh, clean, professional agricultural packaging feel."
        ),
    },
    # ── Blog Thumbnails（16:9）───────────────────────────
    {
        'out': OUT_BLOG / 'blog-shipping-cost-comparison.png',
        'aspect_ratio': '16:9',
        'image_input': [STYLE_REF, STYLE_REF2, ec_boss, car],
        'prompt': (
            "Create a 16:9 commercial illustration in warm amber 3D Pixar clay toy style, "
            "matching the reference images exactly. "
            "USE the human e-commerce boss character (ref 3) and the cute delivery car character (ref 4). "
            "SCENE: The boss sitting at laptop looking at cost comparison chart on screen. "
            "The cute delivery car parked beside with packages loaded. "
            "Background: clean warm amber home office / warehouse blend. "
            "Left side: large orange title text in Chinese: '蝦皮出貨費用完整比較'. "
            "Three delivery method icons: 黑貓 vs 宅配通 vs 超商 with price tags. "
            "Bottom: '咻咻打包 shooshoo.com.tw' brand badge. "
            "Infographic editorial feel, same 3D clay style as refs."
        ),
    },
    {
        'out': OUT_BLOG / 'blog-double11-prep.png',
        'aspect_ratio': '16:9',
        'image_input': [STYLE_REF, STYLE_REF2, pickcat],
        'prompt': (
            "Create a 16:9 commercial illustration in warm amber 3D Pixar clay toy style, "
            "matching the reference images exactly. "
            "USE the grey cat packing character from reference image 3. "
            "SCENE: Energetic warehouse moment — the grey cat mascot quickly sealing boxes, "
            "surrounded by a mountain of packages. "
            "Giant '11.11' countdown floating in background with warm golden glow. "
            "Left: bold Chinese title '雙11備戰清單'. "
            "Checklist items: '提前備貨' '庫存控制' '物流安排'. "
            "Urgent but fun, high-energy composition. "
            "Bottom: '咻咻打包 shooshoo.com.tw' brand badge."
        ),
    },
    {
        'out': OUT_BLOG / 'blog-what-is-3pl.png',
        'aspect_ratio': '16:9',
        'image_input': [STYLE_REF, STYLE_REF2, forklift],
        'prompt': (
            "Create a 16:9 commercial illustration in warm amber 3D Pixar clay toy style, "
            "matching the reference images exactly. "
            "USE the yellow forklift character from reference image 3. "
            "SCENE: Wide warehouse interior with the cheerful forklift character in center. "
            "Simple flow diagram overlaid: '賣家' → (arrow) → '咻咻倉庫' → (arrow) → '買家'. "
            "Each step has a small icon: phone/laptop, warehouse building, delivery box. "
            "Left: large orange Chinese title '什麼是 3PL？'. "
            "Subtitle: '電商新手完整入門'. "
            "Clean educational infographic feel. "
            "Bottom: '咻咻打包 shooshoo.com.tw' brand badge."
        ),
    },
]

# ── 執行 ───────────────────────────────────────────────────────────
print('\n=== Phase 2: KIE 生圖 ===')
for task in TASKS:
    out_path = task['out']
    print(f'\n[{out_path.name}]')
    print(f'   refs: {len([u for u in task["image_input"] if u])} 張')
    try:
        tid = kie_create(task['prompt'], task['image_input'], task['aspect_ratio'])
        print(f'   task_id={tid}')
        result_url = kie_poll(tid)
        kie_download(result_url, out_path)
    except Exception as e:
        print(f'   ERROR: {e}')
    time.sleep(5)

print('\nDone!')
print(f'紙箱圖：{OUT_BOX}')
print(f'Blog 縮圖：{OUT_BLOG}')
