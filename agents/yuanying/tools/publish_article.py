"""
咻咻打包 一鍵發文工具
用法：把下方 ARTICLE 區塊填好，直接 python publish_article.py

流程：
1. KIE 生封面圖（帶 IP 角色 + 現有文章 style ref）
2. 建立 / 更新 WordPress 文章（inline HTML 格式）
3. 上傳封面圖，設定 featured image
4. Rank Math SEO meta（title / desc / OG / focus keyword）
5. Google Indexing API 推送

需要的環境變數（.env）：
  WP_SITE_URL, WP_USERNAME, WP_APP_PASSWORD
  KIE_API_KEY
  GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET, GOOGLE_REFRESH_TOKEN  ← sitemap 用
  SERVICE_ACCOUNT_FILE（或直接改 SA_KEY_PATH 常數）
"""
import requests, json, time, os
from pathlib import Path
from dotenv import load_dotenv
from google.oauth2 import service_account
import google.auth.transport.requests as ga_requests

load_dotenv(dotenv_path='D:/咻咻打包CLAUDE/.env')
WP   = os.getenv('WP_SITE_URL', '').rstrip('/')
USER = os.getenv('WP_USERNAME')
PASS = os.getenv('WP_APP_PASSWORD')
KIE  = os.getenv('KIE_API_KEY')
AUTH = (USER, PASS)
KIE_H = {'Authorization': f'Bearer {KIE}', 'Content-Type': 'application/json'}

SA_KEY_PATH = 'D:/咻咻打包CLAUDE/gen-lang-client-0901966054-8a6f63d2e942.json'
GSC_SITE    = 'https://www.shooshoo.com.tw/'

# Style refs：現有文章封面（讓 KIE 對齊暖橘色 3D Pixar 風格）
STYLE_REFS = [
    'https://www.shooshoo.com.tw/wp-content/uploads/2026/06/shooshoo-3pl-hero-ip.png',
    'https://www.shooshoo.com.tw/wp-content/uploads/2026/06/shooshoo-outsourcing-hero-ip.png',
]
# IP 角色 WP 公開 URL（已上傳過）
IP_URLS = {
    'pickcat': 'https://www.shooshoo.com.tw/wp-content/uploads/2026/06/shooshoo-pickcat-ref.png',
    'tape':    'https://www.shooshoo.com.tw/wp-content/uploads/2026/06/shooshoo-tapetape-ref.png',
    'boss':    'https://www.shooshoo.com.tw/wp-content/uploads/2026/06/shooshoo-boss-ref.png',
    'shooshoo':'https://www.shooshoo.com.tw/wp-content/uploads/2026/06/shooshoo-pickcat-ref.png',
}

OUT_DIR = Path('D:/咻咻打包CLAUDE/social-cards/文章配圖')

# ══════════════════════════════════════════════════════════════════
# ★ 填這裡 ★
# ══════════════════════════════════════════════════════════════════
ARTICLE = {
    # ── 文章基本資料 ──────────────────────────────────────────────
    'post_id':  None,          # None = 新建文章；填數字 = 更新現有文章
    'slug':     'your-slug',   # URL slug（英文 kebab-case）
    'title':    '文章標題',
    'status':   'publish',     # 'publish' 或 'draft'

    # ── SEO ───────────────────────────────────────────────────────
    'focus_kw':  '主關鍵字',
    'meta_desc': '150 字左右的 meta description，包含主關鍵字和 CTA',
    'og_title':  'OG 標題（50-60字）',

    # ── 封面圖 ────────────────────────────────────────────────────
    'img_filename': 'shooshoo-article-hero.png',   # 輸出檔名
    'img_alt':      '圖片 alt text',
    'img_chars':    ['pickcat', 'tape'],            # 要出現的 IP 角色
                                                    # 可選: pickcat / tape / boss / shooshoo
    'img_prompt': (
        "Create a 16:9 commercial illustration EXACTLY matching the style of the first two reference images: "
        "warm amber-orange 3D Pixar clay toy art style, same soft rounded edges, same color palette, "
        "same embedded Chinese text infographic layout. "
        # ↓↓↓ 在這裡描述你的圖片內容 ↓↓↓
        "SCENE: [描述場景]. "
        "CHARACTERS: Use the character designs from reference images 3 and 4. "
        "TEXT: Chinese title '[文章標題]' in large orange text. "
        "Brand badge '咻咻打包 shooshoo.com.tw' at bottom right. "
        "Same 3D clay warm orange brand style as reference images."
    ),

    # ── 文章內容（inline HTML 格式） ──────────────────────────────
    # 圖片 URL 用 HERO_IMG_URL 佔位，上傳後自動替換
    'content': """<div style="max-width:860px;margin:0 auto;font-family:'Noto Sans TC',sans-serif;color:#333;line-height:1.8;">

<div style="text-align:center;margin-bottom:32px;">
  <img decoding="async" src="HERO_IMG_URL" alt="[alt text]" style="width:100%;border-radius:12px;" />
</div>

<div style="background:#fff8f0;border-left:5px solid #f5a623;padding:20px 24px;border-radius:8px;margin-bottom:36px;">
  <p style="font-size:1.1em;margin:0;">[開頭 hook，打痛點，1-2句]</p>
</div>

<h2 style="font-size:1.6em;color:#c0580a;border-bottom:3px solid #f5a623;padding-bottom:8px;margin-top:48px;">[H2 標題]</h2>
<p>[內文]</p>

<div style="text-align:center;margin:40px 0 20px;">
  <a href="https://lin.ee/L9HtuyF" style="display:inline-block;background:#f5a623;color:#fff;font-size:1.1em;font-weight:700;padding:16px 40px;border-radius:50px;text-decoration:none;box-shadow:0 4px 16px rgba(245,166,35,0.4);">加 LINE 詢問 →</a>
  <p style="margin-top:10px;color:#999;font-size:0.85em;">LINE ID：@911ycmhl</p>
</div>

</div>

<script type="application/ld+json">
{"@context":"https://schema.org","@type":"FAQPage","mainEntity":[
  {"@type":"Question","name":"[問題1]","acceptedAnswer":{"@type":"Answer","text":"[答案1]"}},
  {"@type":"Question","name":"[問題2]","acceptedAnswer":{"@type":"Answer","text":"[答案2]"}}
]}
</script>""",
}
# ══════════════════════════════════════════════════════════════════


def kie_generate(prompt, char_keys, img_filename):
    out_path = OUT_DIR / img_filename
    if out_path.exists():
        print(f'[KIE] Skip (exists): {img_filename}')
        return out_path

    image_input = STYLE_REFS + [IP_URLS[k] for k in char_keys if k in IP_URLS]
    print(f'[KIE] Generating {img_filename} (refs={len(image_input)})')
    r = requests.post('https://api.kie.ai/api/v1/jobs/createTask',
        headers=KIE_H,
        json={'model': 'nano-banana-2', 'input': {
            'prompt': prompt, 'image_input': image_input,
            'aspect_ratio': '16:9', 'resolution': '2K', 'output_format': 'png'
        }}, timeout=30)
    d = r.json()
    if d.get('code') != 200:
        raise Exception(f'KIE error: {d}')
    tid = d['data']['taskId']
    print(f'[KIE] task_id={tid}')

    for _ in range(45):
        time.sleep(8)
        rd = requests.get('https://api.kie.ai/api/v1/jobs/recordInfo',
            headers=KIE_H, params={'taskId': tid}, timeout=15).json().get('data', {})
        state = rd.get('state', '')
        print(f'  [{state}]', end=' ', flush=True)
        if state == 'success':
            print()
            url = json.loads(rd['resultJson'])['resultUrls'][0]
            img_bytes = requests.get(url, timeout=60).content
            out_path.write_bytes(img_bytes)
            print(f'[KIE] Saved {img_filename} ({len(img_bytes):,} bytes)')
            return out_path
        elif state == 'fail':
            raise Exception(f'KIE fail: {rd.get("failMsg")}')
    raise TimeoutError('KIE timeout')


def wp_upload_image(img_path, alt_text, title):
    img = Path(img_path)
    ascii_name = img.name if img.name.isascii() else 'shooshoo-article-hero.png'
    r = requests.post(f'{WP}/wp-json/wp/v2/media', auth=AUTH,
        headers={'Content-Disposition': f'attachment; filename="{ascii_name}"',
                 'Content-Type': 'image/png'},
        data=img.read_bytes(), timeout=60)
    if r.status_code not in (200, 201):
        raise Exception(f'Upload failed {r.status_code}')
    media = r.json()
    requests.post(f'{WP}/wp-json/wp/v2/media/{media["id"]}', auth=AUTH,
        json={'alt_text': alt_text, 'title': title}, timeout=15)
    print(f'[WP] Uploaded media_id={media["id"]}')
    return media['id'], media['source_url']


def wp_publish(post_id, title, content, slug, media_id, status):
    payload = {'title': title, 'content': content,
                'featured_media': media_id, 'status': status, 'slug': slug}
    if post_id:
        r = requests.post(f'{WP}/wp-json/wp/v2/posts/{post_id}', auth=AUTH,
            json=payload, timeout=20)
        print(f'[WP] Update post {post_id}: {r.status_code}')
        return post_id
    else:
        r = requests.post(f'{WP}/wp-json/wp/v2/posts', auth=AUTH,
            json=payload, timeout=20)
        pid = r.json().get('id')
        print(f'[WP] New post id={pid}: {r.status_code}')
        return pid


def wp_seo(post_id, a):
    r = requests.post(f'{WP}/wp-json/rankmath/v1/updateMeta', auth=AUTH,
        json={'objectID': post_id, 'objectType': 'post', 'meta': {
            'rank_math_focus_keyword':       a['focus_kw'],
            'rank_math_description':         a['meta_desc'],
            'rank_math_og_title':            a['og_title'],
            'rank_math_og_description':      a['meta_desc'],
            'rank_math_og_image_id':         str(a['_media_id']),
            'rank_math_twitter_title':       a['og_title'],
            'rank_math_twitter_description': a['meta_desc'],
            'rank_math_twitter_image_id':    str(a['_media_id']),
        }}, timeout=15)
    print(f'[SEO] Rank Math: {r.status_code}')


def gsc_index(url):
    creds = service_account.Credentials.from_service_account_file(
        SA_KEY_PATH, scopes=['https://www.googleapis.com/auth/indexing'])
    creds.refresh(ga_requests.Request())
    r = requests.post('https://indexing.googleapis.com/v3/urlNotifications:publish',
        headers={'Authorization': f'Bearer {creds.token}', 'Content-Type': 'application/json'},
        json={'url': url, 'type': 'URL_UPDATED'})
    print(f'[GSC] {r.status_code} | {url}')


def gsc_sitemap():
    from google.oauth2.credentials import Credentials
    r = requests.post('https://oauth2.googleapis.com/token', data={
        'client_id':     os.getenv('GOOGLE_CLIENT_ID'),
        'client_secret': os.getenv('GOOGLE_CLIENT_SECRET'),
        'refresh_token': os.getenv('GOOGLE_REFRESH_TOKEN'),
        'grant_type':    'refresh_token',
    })
    token = r.json().get('access_token')
    site_enc = requests.utils.quote(GSC_SITE, safe='')
    sm_enc   = requests.utils.quote('https://www.shooshoo.com.tw/sitemap_index.xml', safe='')
    r2 = requests.put(
        f'https://www.googleapis.com/webmasters/v3/sites/{site_enc}/sitemaps/{sm_enc}',
        headers={'Authorization': f'Bearer {token}'}
    )
    print(f'[GSC] Sitemap: {r2.status_code}')


# ── 執行 ──────────────────────────────────────────────────────────
if __name__ == '__main__':
    a = ARTICLE
    print(f'\n=== 發文：{a["title"][:30]} ===\n')

    # 1. 生圖
    img_path = kie_generate(a['img_prompt'], a['img_chars'], a['img_filename'])

    # 2. 上傳圖片
    media_id, media_url = wp_upload_image(img_path, a['img_alt'], a['title'])
    a['_media_id'] = media_id

    # 3. 發文
    content = a['content'].replace('HERO_IMG_URL', media_url)
    post_id = wp_publish(a['post_id'], a['title'], content,
                         a['slug'], media_id, a['status'])

    # 4. SEO
    wp_seo(post_id, a)

    # 5. GSC
    post_url = f'{GSC_SITE.rstrip("/")}/{a["slug"]}/'
    gsc_sitemap()
    gsc_index(post_url)

    print(f'\n=== 完成 ===')
    print(f'  {post_url}')
