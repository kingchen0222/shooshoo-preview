"""
KIE image_input 要 string array（URL 陣列）
流程：
1. 上傳 IP 角色去背 PNG 到 WP 取得公開 URL
2. 加上現有文章封面 URL 作為 style ref
3. 全部傳給 KIE 生圖
"""
import requests, os, json, time
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(dotenv_path='D:/咻咻打包CLAUDE/.env')
WP   = os.getenv('WP_SITE_URL').rstrip('/')
USER = os.getenv('WP_USERNAME')
PASS = os.getenv('WP_APP_PASSWORD')
KIE  = os.getenv('KIE_API_KEY')
AUTH = (USER, PASS)
KIE_H = {"Authorization": f"Bearer {KIE}", "Content-Type": "application/json"}

OUT      = Path('D:/咻咻打包CLAUDE/social-cards/文章配圖')
CHAR_DIR = Path('D:/咻咻打包CLAUDE/影片素材/角色去背')

# Style ref：現有文章封面（讓 KIE 對齊這個 3D Pixar 暖橘風格）
STYLE_REF = "https://www.shooshoo.com.tw/wp-content/uploads/2026/06/shooshoo-3pl-hero-ip.png"
STYLE_REF2 = "https://www.shooshoo.com.tw/wp-content/uploads/2026/06/shooshoo-outsourcing-hero-ip.png"

CHAR_NAME_MAP = {
    '揀貨喵喵.png': 'shooshoo-pickcat-ref.png',
    '咚咚膠帶.png': 'shooshoo-tapetape-ref.png',
    '電商老闆.png': 'shooshoo-boss-ref.png',
}

def wp_upload(img_path):
    """上傳到 WP Media Library，回傳公開 URL（用 ASCII 檔名）"""
    img = Path(img_path)
    ascii_name = CHAR_NAME_MAP.get(img.name, 'shooshoo-ref.png')
    r = requests.post(f'{WP}/wp-json/wp/v2/media', auth=AUTH,
        headers={'Content-Disposition': f'attachment; filename="{ascii_name}"',
                 'Content-Type': 'image/png'},
        data=img.read_bytes(), timeout=60)
    if r.status_code not in (200, 201):
        raise Exception(f'WP upload failed {r.status_code}: {r.text[:100]}')
    url = r.json()['source_url']
    print(f'  WP uploaded: {ascii_name} -> {url}')
    return url

# ── Phase 1：上傳 IP 角色到 WP 取得 URL ──────────────────────────
print('=== Phase 1: Upload IP chars to WP ===')
chars_to_upload = {
    '揀貨喵喵.png': None,
    '咚咚膠帶.png': None,
    '電商老闆.png': None,
}
for fname in chars_to_upload:
    path = CHAR_DIR / fname
    if path.exists():
        chars_to_upload[fname] = wp_upload(path)
        time.sleep(1)
    else:
        print(f'  MISSING: {fname}')

pickcat_url = chars_to_upload['揀貨喵喵.png']
tape_url    = chars_to_upload['咚咚膠帶.png']
boss_url    = chars_to_upload['電商老闆.png']

# ── Phase 2：KIE 生圖 ─────────────────────────────────────────────
TASKS = [
    {
        'filename': 'shooshoo-convenience-store-shipping-hero.png',
        'image_input': [STYLE_REF, STYLE_REF2, pickcat_url, boss_url],
        'prompt': (
            "Create a 16:9 commercial illustration EXACTLY matching the style of the first two reference images: "
            "warm amber-orange 3D Pixar clay toy art style, same soft rounded edges, same color palette, "
            "same embedded Chinese text infographic layout. "
            "USE the character designs from reference images 3 and 4 as the characters. "
            "SCENE: Split left/right comparison. "
            "LEFT (cool blue tones, '自己出貨' label): "
            "The human boss character — exhausted, buried under a tower of cardboard boxes, "
            "standing in a convenience store queue. "
            "Red cross bullet points: '自己跑超商' '耗時1-2小時' '扛箱找停車'. "
            "RIGHT (warm amber, '交給咻咻' label): "
            "The orange cat mascot — cheerfully carrying packages, happy eyes. "
            "Boss character relaxed at laptop, smiling. "
            "Gold checkmark bullets: '在家等上門' '省時省力' '咻咻全包辦'. "
            "CENTER: Orange '咻咻' circle divider. "
            "TOP banner: '台南超商代寄推薦｜咻咻打包'. "
            "Same 3D clay warm orange brand style as reference images."
        ),
    },
    {
        'filename': 'shooshoo-convenience-store-pickup-hero.png',
        'image_input': [STYLE_REF, STYLE_REF2, pickcat_url, tape_url],
        'prompt': (
            "Create a 16:9 commercial illustration EXACTLY matching the style of the first two reference images: "
            "warm amber-orange 3D Pixar clay toy art style, same soft rounded edges, same color palette, "
            "same embedded Chinese text infographic layout. "
            "USE the character designs from reference images 3 and 4 as the main characters. "
            "SCENE: Modern organized warehouse interior, wide shot. "
            "LEFT side: Article title '超商收件完整說明' in large orange text. "
            "Store badges row: '7-11' (green), '全家' (blue), '萊爾富' (red), '蝦皮' (orange). "
            "Subtitle: '賣家只要接單，出貨咻咻全包'. "
            "RIGHT side: Two orange cat mascots working in warehouse — "
            "one scanning packages, one sealing boxes with tape, both cheerful. "
            "Background: warm amber warehouse shelving. "
            "Three colored delivery portal arches (green/blue/red) hinting at three convenience chains. "
            "Brand badge '咻咻打包 shooshoo.com.tw' at bottom. "
            "Same 3D clay warm orange brand style as reference images."
        ),
    },
]

def kie_create(prompt, image_input_urls):
    # 過濾掉 None
    urls = [u for u in image_input_urls if u]
    payload = {
        "model": "nano-banana-2",
        "input": {
            "prompt": prompt,
            "image_input": urls,
            "aspect_ratio": "16:9",
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
    raise TimeoutError('timeout')

def kie_download(url, path):
    r = requests.get(url, timeout=60)
    Path(path).write_bytes(r.content)
    print(f'  Saved {Path(path).name} ({len(r.content):,} bytes)')

print('\n=== Phase 2: KIE Generate ===')
for task in TASKS:
    out_path = OUT / task['filename']
    print(f'\n[{task["filename"]}]')
    print(f'  image_input count: {len([u for u in task["image_input"] if u])}')
    try:
        tid = kie_create(task['prompt'], task['image_input'])
        print(f'  task_id={tid}')
        url = kie_poll(tid)
        kie_download(url, out_path)
    except Exception as e:
        print(f'  ERROR: {e}')
    time.sleep(5)

print('\nDone.')
