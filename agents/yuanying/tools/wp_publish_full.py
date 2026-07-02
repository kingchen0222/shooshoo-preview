"""
咻咻打包 WordPress 完整發布流程
1. 上傳封面圖到 Media Library
2. 設定 Featured Image
3. 設定 Rank Math OG Image + SEO meta
4. 確認文章為 publish 狀態
"""
import requests, os, json
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(dotenv_path='D:/咻咻打包CLAUDE/.env')
WP   = os.getenv('WP_SITE_URL').rstrip('/')
USER = os.getenv('WP_USERNAME')
PASS = os.getenv('WP_APP_PASSWORD')
AUTH = (USER, PASS)

POSTS = [
    {
        'id': 3264,
        'slug': 'tainan-convenience-store-shipping',
        'title': '台南超商代寄推薦｜委託咻咻，在家等上門收，不用自己跑超商',
        'img': 'D:/咻咻打包CLAUDE/social-cards/文章配圖/超商代寄封面/成品/cover.png',
        'img_alt': '台南超商代寄服務｜咻咻打包 自己寄 vs 委託上門收 對比圖',
        'focus_kw': '台南超商代寄',
        'meta_desc': '台南電商賣家不用自己跑超商寄件！咻咻打包提供超商代寄服務，在家等上門收貨，訂單自動出貨到7-11、全家、萊爾富，讓你專心做老闆該做的事。',
        'og_title': '台南超商代寄推薦 2026｜在家等收，不用跑超商',
    },
    {
        'id': 3268,
        'slug': 'convenience-store-pickup-guide',
        'title': '超商收件完整說明｜7-11全家萊爾富蝦皮，咻咻幫你搞定',
        'img': 'D:/咻咻打包CLAUDE/social-cards/文章配圖/超商收件封面/成品/cover.png',
        'img_alt': '超商收件服務說明｜咻咻打包 7-11全家萊爾富蝦皮超商取件',
        'focus_kw': '超商收件',
        'meta_desc': '超商收件完整說明：7-ELEVEN、全家、萊爾富、蝦皮超商取件全支援。委託咻咻打包代寄，不用自己送件，賣家只要接單，出貨咻咻包辦。',
        'og_title': '超商收件完整說明 2026｜7-11全家萊爾富蝦皮咻咻代寄',
    },
]

def upload_image(img_path, alt_text, title):
    img = Path(img_path)
    with open(img, 'rb') as f:
        data = f.read()

    headers = {
        'Content-Disposition': f'attachment; filename="{img.name}"',
        'Content-Type': 'image/png',
    }
    r = requests.post(
        f'{WP}/wp-json/wp/v2/media',
        auth=AUTH,
        headers=headers,
        data=data,
        timeout=60,
    )
    if r.status_code not in (200, 201):
        print(f'  ERR upload {r.status_code}: {r.text[:200]}')
        return None

    media = r.json()
    media_id = media['id']
    print(f'  OK upload media_id={media_id}')

    # 更新 alt text
    r2 = requests.post(
        f'{WP}/wp-json/wp/v2/media/{media_id}',
        auth=AUTH,
        json={'alt_text': alt_text, 'title': title},
        timeout=15,
    )
    print(f'  OK alt_text {r2.status_code}')
    return media_id


def update_post(post_id, media_id, post_data):
    # 1. 設定 featured image + 確認 publish
    r = requests.post(
        f'{WP}/wp-json/wp/v2/posts/{post_id}',
        auth=AUTH,
        json={
            'featured_media': media_id,
            'status': 'publish',
        },
        timeout=15,
    )
    print(f'  OK featured_media + publish: {r.status_code}')

    # 2. Rank Math SEO meta
    rank_meta = {
        'rank_math_focus_keyword':       post_data['focus_kw'],
        'rank_math_description':         post_data['meta_desc'],
        'rank_math_og_title':            post_data['og_title'],
        'rank_math_og_description':      post_data['meta_desc'],
        'rank_math_twitter_title':       post_data['og_title'],
        'rank_math_twitter_description': post_data['meta_desc'],
        'rank_math_og_image_id':         str(media_id),
        'rank_math_twitter_image_id':    str(media_id),
    }
    r2 = requests.post(
        f'{WP}/wp-json/rankmath/v1/updateMeta',
        auth=AUTH,
        json={
            'objectID':   post_id,
            'objectType': 'post',
            'meta':       rank_meta,
        },
        timeout=15,
    )
    print(f'  OK Rank Math meta: {r2.status_code}')

    # 3. 確認 OG image via _thumbnail_id (yoast/rankmath fallback)
    r3 = requests.post(
        f'{WP}/wp-json/wp/v2/posts/{post_id}',
        auth=AUTH,
        json={'meta': {'_thumbnail_id': str(media_id)}},
        timeout=15,
    )
    print(f'  OK _thumbnail_id meta: {r3.status_code}')


# ── 執行 ──────────────────────────────────────────────────────────
for p in POSTS:
    print(f'\n[Post {p["id"]}] {p["slug"]}')
    media_id = upload_image(p['img'], p['img_alt'], p['title'])
    if media_id:
        update_post(p['id'], media_id, p)

print('\n=== DONE ===')
for p in POSTS:
    print(f'  https://www.shooshoo.com.tw/{p["slug"]}/')
