"""
員瑛 — 生成 WMS 頁面 IP 品牌主視覺並替換現有 stock 圖
"""
import os, json, time, requests, re
from requests.auth import HTTPBasicAuth
from dotenv import load_dotenv

load_dotenv()
KIE_KEY = os.getenv('KIE_API_KEY')
auth = HTTPBasicAuth(os.getenv('WP_USERNAME'), os.getenv('WP_APP_PASSWORD'))
WP = os.getenv('WP_SITE_URL')

# 倉倉老闆 IP 參考圖
CHAR_URL = 'https://drive.google.com/uc?export=view&id=11rB9avhrdR3eiHusu2pzi36jGZWkijxq'

PROMPT = (
    '咻咻打包WMS智慧倉儲管理系統，台灣電商庫存管理，'
    '倉倉老闆角色站在大型觸控螢幕前，螢幕顯示庫存圖表與訂單數據，'
    '背景是現代化倉庫，橘色主題，繁體中文文字「智慧庫存管理」，'
    '專業卡通風格，無英文字，溫暖活潑'
)
FILENAME = 'shooshoo-wms-hero-ip.png'
ALT = '咻咻打包WMS智慧倉儲管理系統，電商庫存管理介面，台南3PL倉儲服務'
TITLE = '咻咻打包WMS庫存管理系統｜電商賣家即時掌握庫存，台南3PL智慧倉儲'
WMS_PAGE_ID = 2536

# 1. 生成圖片
print('生成 WMS IP 主視覺...')
r = requests.post('https://api.kie.ai/api/v1/jobs/createTask',
    headers={'Authorization': f'Bearer {KIE_KEY}'},
    json={
        'model': 'gpt-image-2-image-to-image',
        'input': {'prompt': PROMPT, 'imageUrl': CHAR_URL, 'size': '1024x1024'}
    }, timeout=30)
data = r.json()
task_id = data.get('data', {}).get('taskId')
if not task_id:
    print('KIE 任務建立失敗:', data)
    exit(1)
print(f'  taskId: {task_id}')

img_url = None
for i in range(30):
    time.sleep(8)
    pr = requests.get(f'https://api.kie.ai/api/v1/jobs/recordInfo?taskId={task_id}',
        headers={'Authorization': f'Bearer {KIE_KEY}'}, timeout=15)
    pd = pr.json().get('data', {})
    state = pd.get('state', '')
    if state in ('success', 'completed', 'COMPLETED', 'SUCCESS', '2'):
        rj = pd.get('resultJson', '{}')
        if isinstance(rj, str): rj = json.loads(rj)
        urls = rj.get('resultUrls', [])
        img_url = urls[0] if urls else None
        break
    if state in ('failed', 'FAILED', '3'):
        print('  KIE 生成失敗:', pd.get('failMsg'))
        exit(1)
    print(f'  polling [{i+1}] state={state}')

if not img_url:
    print('圖片生成逾時')
    exit(1)
print(f'  圖片 URL: {img_url[:70]}...')

# 2. 上傳到 WP Media Library
print('上傳到 WP...')
img_data = requests.get(img_url, timeout=30).content
r2 = requests.post(f'{WP}/wp-json/wp/v2/media', auth=auth,
    headers={'Content-Disposition': f'attachment; filename="{FILENAME}"',
             'Content-Type': 'image/png'},
    data=img_data, timeout=30)
media = r2.json()
media_id = media.get('id')
wp_url = media.get('source_url', '')
if not media_id:
    print('上傳失敗:', media)
    exit(1)
requests.post(f'{WP}/wp-json/wp/v2/media/{media_id}', auth=auth,
    json={'alt_text': ALT, 'title': TITLE}, timeout=15)
print(f'  Media ID={media_id} | {wp_url}')

# 3. 更新 /wms/ 頁面：換掉 server rack 圖
print('更新 /wms/ 頁面...')
raw = requests.get(f'{WP}/wp-json/wp/v2/pages/{WMS_PAGE_ID}', auth=auth,
    params={'context': 'edit'}, timeout=15).json()['content']['raw']

# 找 server rack 圖 src 並替換
old_pattern = r'src="[^"]*server[^"]*"'
new_src = f'src="{wp_url}"'
new_raw = re.sub(old_pattern, new_src, raw, flags=re.IGNORECASE)

# 也更新 alt
new_raw = re.sub(
    r'alt="Detailed image of a server[^"]*"',
    f'alt="{ALT}"',
    new_raw, flags=re.IGNORECASE
)

if new_raw != raw:
    r3 = requests.post(f'{WP}/wp-json/wp/v2/pages/{WMS_PAGE_ID}', auth=auth,
        json={'content': new_raw, 'featured_media': media_id}, timeout=20)
    print(f'  頁面更新 -> HTTP {r3.status_code}')
else:
    print('  未找到 server rack 圖，需手動在 Elementor 換圖')
    print(f'  新圖 URL: {wp_url}')

print('\n=== done ===')
