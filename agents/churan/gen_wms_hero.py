"""
WMS Hero 雙手機構圖
左手機：最萌打包團隊 2D chibi 卡通
右手機：GoWarehouse WMS 儀表板深色 UI
輸出：social-cards/文章配圖/shooshoo-wms-hero.png
"""
import requests, os, json, time
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(dotenv_path='D:/咻咻打包CLAUDE/.env')
KIE  = os.getenv('KIE_API_KEY', '')
KIE_H = {"Authorization": f"Bearer {KIE}", "Content-Type": "application/json"}
OUT = Path('D:/咻咻打包CLAUDE/social-cards/文章配圖')

# 參考圖：左手機來源（真實卡通圖）+ GoWarehouse style
REFS = [
    "https://www.shooshoo.com.tw/wp-content/uploads/2026/07/shooshoo-wms-team-cartoon.jpg",  # 左手機內容
    "https://www.shooshoo.com.tw/wp-content/uploads/2026/06/shooshoo-char-admin-cat.png",    # 角色風格 ref
]

PROMPT = """
Create a professional product marketing hero image, landscape 16:9 format.

COMPOSITION: Two floating smartphones displayed side by side against a soft warm cream background (#FFF8ED).
The left phone leans slightly to the left, the right phone leans slightly to the right.
Both phones float with subtle drop shadows beneath them.
Scattered in the corners: 4 soft pastel blue semi-transparent circles of varying sizes as decorative elements.
No text labels or annotations anywhere in the background — only the two phones and the decorative circles.

LEFT PHONE:
The screen displays the EXACT illustration from reference image 1 — a 2D kawaii chibi cartoon titled "最萌打包團隊" showing cute warehouse mascot characters together: running cardboard box mascot, orange cat with laptop, gray cat sealing a box, yellow forklift, box-head character in suit, tape-roll mascot, small white delivery truck. Warm tan/beige background, dark brown header bar with "咻咻打包 SHOOSHOO PACKING" text, red ribbon banner with "最萌打包團隊". Reproduce this screen faithfully.

RIGHT PHONE:
Screen shows a dark-mode mobile WMS app. Pure black background (#0D0D0D).
Top area: dark gray card with user icon, text "Operator / Warehouse Staff".
Below: "目前貨主  全部貨主 >" selector.
Main area: vertical list menu with icons, items in white text:
儀表板 (active, highlighted with blue), 入倉驗收, 上架作業, 揀貨作業, 揀貨庫位, 出貨品檢, 庫存盤點, 庫存查詢, 庫存移轉.
Bottom bar: bell icon, globe icon, red 登出 text.

TECHNICAL: Both phones are modern smartphones with thin bezels, rounded corners, silver/dark frames.
Professional tech product shot quality. Clean, polished, marketing-ready.
"""

def kie_create(prompt, refs):
    payload = {
        "model": "nano-banana-2",
        "input": {
            "prompt": prompt,
            "image_input": refs,
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

def kie_poll(task_id, interval=10, timeout=480):
    print('  Polling', end=' ', flush=True)
    for _ in range(timeout // interval):
        r = requests.get('https://api.kie.ai/api/v1/jobs/recordInfo',
            headers=KIE_H, params={'taskId': task_id}, timeout=15)
        d = r.json().get('data', {})
        state = d.get('state', '')
        print(f'[{state}]', end=' ', flush=True)
        if state == 'success':
            print()
            return json.loads(d['resultJson'])['resultUrls'][0]
        elif state == 'fail':
            raise Exception(f'KIE fail: {d.get("failMsg")}')
        time.sleep(interval)
    raise TimeoutError('KIE timeout after 8 min')

def kie_download(url, path):
    r = requests.get(url, timeout=60)
    Path(path).write_bytes(r.content)
    print(f'  Saved: {Path(path).name} ({len(r.content):,} bytes)')

print('=== WMS Hero 雙手機構圖 / KIE nano-banana-2 ===')
print(f'  Style refs: {len(REFS)} images')
tid = kie_create(PROMPT, REFS)
print(f'  task_id = {tid}')
img_url = kie_poll(tid)
kie_download(img_url, OUT / 'shooshoo-wms-hero.png')
print('\n=== Done! 查看 social-cards/文章配圖/shooshoo-wms-hero.png ===')
