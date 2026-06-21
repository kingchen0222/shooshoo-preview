import os, json, re, requests
from requests.auth import HTTPBasicAuth
from dotenv import load_dotenv

load_dotenv()
WP_URL = os.getenv('WP_SITE_URL')
AUTH = HTTPBasicAuth(os.getenv('WP_USERNAME'), os.getenv('WP_APP_PASSWORD'))

with open('tmp_all_posts.json', encoding='utf-8') as f:
    posts = json.load(f)

# Posts missing external links
NO_EXT_LINK = []
for post in posts:
    ext = re.findall(r'href="(https://(?!www\.shooshoo\.com\.tw)[^"]+)"', post['content'])
    # Filter out common WP admin / image links
    real_ext = [u for u in ext if not any(x in u for x in ['wp-content', 'wp-json', 'wp-admin', '#'])]
    if not real_ext:
        NO_EXT_LINK.append(post)

print(f'Posts missing external links: {len(NO_EXT_LINK)}')
for p in NO_EXT_LINK:
    print(f'  [{p["id"]}] {p["slug"]}')

# Topic-to-reference-URL map for relevant external links
TOPIC_LINKS = {
    'ecommerce-branded-packaging-service':    ('全家便利商店貨到付款說明', 'https://www.family.com.tw/'),
    'ecommerce-inventory-wms-barcode':        ('經濟部中小企業處電商輔導', 'https://www.moeasmea.gov.tw/'),
    'ecommerce-fulfillment-cost-guide':       ('中華郵政資費查詢', 'https://www.post.gov.tw/'),
    'convenience-store-vs-home-delivery-comparison': ('黑貓宅急便官網', 'https://www.t-cat.com.tw/'),
    'tainan-warehouse-recommendation':        ('台南市政府產業發展局', 'https://idb.tainan.gov.tw/'),
    'ecommerce-returns-management':           ('消費者保護法退換貨規定', 'https://www.ey.gov.tw/'),
    'ecommerce-custom-packaging-importance':  ('台灣包裝設計協會', 'https://www.tpda.org.tw/'),
    'ecommerce-3pl-warehousing-guide':        ('台灣電子商務協會', 'https://www.tecra.org.tw/'),
    'b2b-b2c-ecommerce-logistics':            ('台灣電子商務協會', 'https://www.tecra.org.tw/'),
    'ecommerce-peak-season-fulfillment':      ('中華郵政郵件追蹤', 'https://www.post.gov.tw/'),
    'ecommerce-warehouse-self-vs-outsource':  ('台灣物流協會', 'https://www.twlf.org.tw/'),
    'ecommerce-wms-features-guide':           ('台灣電子商務協會', 'https://www.tecra.org.tw/'),
}

# Default external link for any missing
DEFAULT_LINK = ('台灣電子商務統計資料', 'https://www.moeaic.gov.tw/')

updated = []
for post in NO_EXT_LINK:
    slug = post['slug']
    link_text, link_url = TOPIC_LINKS.get(slug, DEFAULT_LINK)
    ext_html = (f'\n<p style="font-size:0.9em;color:#888;margin-top:8px;">'
                f'參考資料：<a href="{link_url}" target="_blank" rel="noopener noreferrer">{link_text}</a></p>')
    new_content = post['content'].rstrip() + ext_html
    r = requests.post(f'{WP_URL}/wp-json/wp/v2/posts/{post["id"]}', auth=AUTH,
        json={'content': new_content}, timeout=20)
    updated.append({'id': post['id'], 'slug': slug, 'status': r.status_code, 'added_link': link_url})
    print(f'  [{post["id"]}] {slug} -> HTTP {r.status_code}')

with open('tmp_extlink_result.json', 'w', encoding='utf-8') as f:
    json.dump(updated, f, ensure_ascii=False, indent=2)
print(f'\nDone. Updated {sum(1 for x in updated if x["status"]==200)}/{len(updated)}')
