import os, json, time, requests
from requests.auth import HTTPBasicAuth
from dotenv import load_dotenv

load_dotenv()
KIE_KEY = os.getenv('KIE_API_KEY')
WP_URL  = os.getenv('WP_SITE_URL')
AUTH    = HTTPBasicAuth(os.getenv('WP_USERNAME'), os.getenv('WP_APP_PASSWORD'))

# 倉倉老闆 IP reference
CHAR_URL = 'https://drive.google.com/uc?export=view&id=11rB9avhrdR3eiHusu2pzi36jGZWkijxq'

TASKS = [
    {
        'post_id': 2674,
        'slug': 'ecommerce-branded-packaging-service',
        'filename': 'shooshoo-branded-packaging-ip.png',
        'prompt': '咻咻打包品牌包裝服務，電商賣家客製化包裝盒，倉倉老闆角色站在整齊的品牌包裝箱旁邊，背景是整潔倉庫，繁體中文文字「品牌包裝代出貨」，橘色主題，專業卡通風格',
        'alt': '咻咻打包品牌包裝代出貨服務，電商賣家客製化包裝，台南3PL倉儲品牌包裝解決方案',
        'title': '咻咻打包品牌包裝代出貨｜電商賣家客製化包裝服務，台南3PL倉儲首選',
    },
    {
        'post_id': 2673,
        'slug': 'ecommerce-inventory-wms-barcode',
        'filename': 'shooshoo-wms-inventory-ip.png',
        'prompt': '咻咻打包WMS倉儲管理系統，電商庫存條碼掃描，倉倉老闆角色拿著掃碼槍站在貨架旁，螢幕顯示庫存數據，繁體中文文字「智慧庫存管理」，橘色主題，專業卡通風格',
        'alt': '咻咻打包WMS倉儲管理系統，電商庫存管理條碼掃描，台南3PL智慧倉儲服務',
        'title': '咻咻打包WMS庫存管理系統｜電商倉儲條碼掃描，台南3PL智慧倉儲',
    }
]

def generate_image(prompt):
    r = requests.post('https://api.kie.ai/api/v1/jobs/createTask',
        headers={'Authorization': f'Bearer {KIE_KEY}'},
        json={'model': 'gpt-image-2-image-to-image',
              'input': {'prompt': prompt, 'imageUrl': CHAR_URL, 'size': '1024x1024'}},
        timeout=30)
    data = r.json()
    task_id = data.get('data', {}).get('taskId')
    if not task_id:
        print('  KIE error:', data)
        return None
    # Poll — field is 'state', not 'status'
    for i in range(30):
        time.sleep(8)
        pr = requests.get(f'https://api.kie.ai/api/v1/jobs/recordInfo?taskId={task_id}',
            headers={'Authorization': f'Bearer {KIE_KEY}'}, timeout=15)
        pr_data = pr.json().get('data', {})
        state = pr_data.get('state', '')
        if state in ('success', 'completed', 'COMPLETED', 'SUCCESS', '2'):
            result_json = pr_data.get('resultJson', '{}')
            if isinstance(result_json, str):
                result_json = json.loads(result_json)
            urls = result_json.get('resultUrls', [])
            return urls[0] if urls else None
        if state in ('failed', 'FAILED', '3'):
            print('  KIE failed:', pr_data.get('failMsg'))
            return None
        print(f'    polling [{i+1}] state={state}')
    return None


def upload_to_wp(img_url, filename, alt, title):
    img_data = requests.get(img_url, timeout=30).content
    r = requests.post(f'{WP_URL}/wp-json/wp/v2/media',
        auth=AUTH,
        headers={'Content-Disposition': f'attachment; filename="{filename}"',
                 'Content-Type': 'image/png'},
        data=img_data, timeout=30)
    media = r.json()
    media_id = media.get('id')
    if not media_id:
        print('  Upload failed:', media)
        return None
    # Set alt + title
    requests.post(f'{WP_URL}/wp-json/wp/v2/media/{media_id}', auth=AUTH,
        json={'alt_text': alt, 'title': title}, timeout=15)
    wp_url = media.get('source_url', '')
    return media_id, wp_url


def prepend_image_to_post(post_id, img_wp_url, alt, title, filename):
    r = requests.get(f'{WP_URL}/wp-json/wp/v2/posts/{post_id}', auth=AUTH, timeout=15)
    content = r.json()['content']['rendered']
    img_tag = (f'<div style="text-align:center;margin-bottom:32px;">'
               f'<img decoding="async" src="{img_wp_url}" '
               f'alt="{alt}" title="{title}" '
               f'style="width:100%;border-radius:12px;" /></div>\n\n')
    new_content = img_tag + content
    r2 = requests.post(f'{WP_URL}/wp-json/wp/v2/posts/{post_id}', auth=AUTH,
        json={'content': new_content, 'featured_media': 0}, timeout=20)
    return r2.status_code


for task in TASKS:
    print(f"\n=== Post {task['post_id']} | {task['slug']} ===")
    print('  Generating image with KIE...')
    img_url = generate_image(task['prompt'])
    if not img_url:
        print('  Image generation failed, skipping')
        continue
    print(f'  Image ready: {img_url[:60]}...')
    result = upload_to_wp(img_url, task['filename'], task['alt'], task['title'])
    if not result:
        continue
    media_id, wp_url = result
    print(f'  Uploaded: ID={media_id} | {wp_url}')
    status = prepend_image_to_post(task['post_id'], wp_url, task['alt'], task['title'], task['filename'])
    print(f'  Post updated: HTTP {status}')

print('\nDone.')
