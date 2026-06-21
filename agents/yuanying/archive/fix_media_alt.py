import os, requests, json
from requests.auth import HTTPBasicAuth
from dotenv import load_dotenv

load_dotenv()
WP_URL = os.getenv('WP_SITE_URL')
AUTH = HTTPBasicAuth(os.getenv('WP_USERNAME'), os.getenv('WP_APP_PASSWORD'))

# Orphan images - set brand alt text
UPDATES = [
    {'id': 3215, 'alt': '咻咻打包台灣第三方物流CTA，電商賣家LINE@免費諮詢', 'title': '咻咻打包3PL服務諮詢'},
    {'id': 3214, 'alt': '咻咻打包台灣第三方物流倉儲，電商代出貨服務', 'title': '咻咻打包3PL倉儲服務'},
    {'id': 3164, 'alt': '咻咻打包品牌IP角色，台南電商物流代出貨', 'title': '咻咻家族IP角色'},
    {'id': 3163, 'alt': '咻咻打包品牌IP角色，台南電商物流代出貨', 'title': '咻咻家族IP角色'},
    {'id': 3162, 'alt': '咻咻打包品牌IP角色，台南電商物流代出貨', 'title': '咻咻家族IP角色'},
    {'id': 3161, 'alt': '咻咻打包品牌IP角色，台南電商物流代出貨', 'title': '咻咻家族IP角色'},
    {'id': 3160, 'alt': '咻咻打包品牌IP角色，台南電商物流代出貨', 'title': '咻咻家族IP角色'},
    {'id': 3159, 'alt': '咻咻打包品牌IP角色，台南電商物流代出貨', 'title': '咻咻家族IP角色'},
    {'id': 3158, 'alt': '咻咻打包品牌IP角色，台南電商物流代出貨', 'title': '咻咻家族IP角色'},
    {'id': 3157, 'alt': '咻咻打包品牌IP角色，台南電商物流代出貨', 'title': '咻咻家族IP角色'},
    {'id': 3156, 'alt': '咻咻打包品牌IP角色，台南電商物流代出貨', 'title': '咻咻家族IP角色'},
]

ok = 0
for item in UPDATES:
    r = requests.post(f'{WP_URL}/wp-json/wp/v2/media/{item["id"]}', auth=AUTH,
        json={'alt_text': item['alt'], 'title': item['title']}, timeout=15)
    if r.status_code == 200:
        ok += 1
    else:
        print(f'  FAIL {item["id"]}: {r.status_code}')

print(f'Updated {ok}/{len(UPDATES)} media items')
