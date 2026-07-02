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

# WP 上已有的 style refs（咻咻角色風格）
REFS = [
    "https://www.shooshoo.com.tw/wp-content/uploads/2026/06/shooshoo-char-admin-cat.png",
    "https://www.shooshoo.com.tw/wp-content/uploads/2026/06/shooshoo-char-pick-cat.png",
]

PROMPT = """
Create a professional product marketing image in 16:9 format.

OVERALL COMPOSITION:
Two modern smartphones floating side by side against a warm cream background (#FFF8ED).
Left phone tilts slightly left (-8 deg), right phone tilts slightly right (+5 deg).
Both cast soft drop shadows. Background has 4 soft pastel blue circles of varying sizes scattered decoratively.

━━ LEFT PHONE ━━
The screen shows a 2D kawaii chibi flat illustration titled "最萌打包團隊" at the top inside a red ribbon banner.
Top of screen: "咻咻打包 ➤ SHOOSHOO PACKING ➤" logo bar with dark brown background.
Bottom of screen: small "GoWarehouse" badge bottom-right corner.
Background of screen: warm tan/parchment color.
Characters shown together in a cheerful group scene:
1. Orange tabby cat (seated at a mini box-desk, using a laptop) — top-left
2. Gray tabby cat (wrapping/taping a cardboard box, sparkles around) — center
3. Cute yellow cartoon forklift with expressive face — top-right
4. Cardboard box character wearing a brown business suit, giving thumbs up — right
5. Brown tape-roll mascot with smiling face — lower center
6. Small cute white delivery mini-truck with a face — lower-left
7. Running cardboard box character (咻咻 mascot) with "TT" on chest — upper area
All characters drawn in 2D Japanese chibi flat illustration style, warm brown/tan color palette, thick outlines, super cute expressions.

━━ RIGHT PHONE ━━
Screen shows a dark-mode WMS warehouse management mobile app (GoWarehouse IBIZA).
Pure black (#0D0D0D) background, clean modern dark UI.
Top status bar area: shows "Operator / Warehouse Staff" with small user icon, dark gray card.
Below: "目前貨主  全部貨主 >" selector row in dark card.
Main content: vertical menu list with these items in white text on dark rows:
  • 儀表板 (highlighted/active, blue accent)
  • 入倉驗收
  • 上架作業
  • 揀貨作業
  • 揀貨庫位
  • 出貨品檢
  • 庫存盤點
  • 庫存查詢
  • 庫存移轉
Bottom of screen: notification bell icon (🔔), globe/language icon (🌐), and red 登出 (logout) text.
Overall: sleek, modern dark UI, professional WMS app aesthetic.

STYLE NOTES:
- Product shot quality, clean background, professional marketing image
- Left phone warm/colorful illustrated screen vs right phone sleek dark professional UI — intentional contrast
- Phones look like modern thin-bezel smartphones
- Image conveys: cute brand identity + powerful modern technology = ShooShoo WMS
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
