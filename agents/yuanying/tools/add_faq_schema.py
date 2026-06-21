"""
員瑛 — 為首頁和台南倉儲推薦文章加入 FAQPage Schema
使用 Rank Math updateSchemas endpoint
"""
import requests, json, uuid
from requests.auth import HTTPBasicAuth

auth = HTTPBasicAuth('admin001', 'X0Zq 1xEz ejyY IeKW iBbn ioQy')
WP = 'https://www.shooshoo.com.tw'

def make_faq_schema(faqs):
    schema_id = str(uuid.uuid4())[:8]
    return {
        schema_id: {
            "@type": "FAQPage",
            "metadata": {
                "title": "FAQPage",
                "type": "template",
                "shortcode": ""
            },
            "mainEntity": [
                {
                    "@type": "Question",
                    "name": q,
                    "acceptedAnswer": {
                        "@type": "Answer",
                        "text": a
                    }
                }
                for q, a in faqs
            ]
        }
    }

# 首頁 FAQ
home_faqs = [
    ("台南代倉儲推薦哪家？",
     "咻咻打包是台南在地電商代倉儲品牌，提供蝦皮、MOMO、Shopify多平台整合出貨，支援超商代寄（7-11/全家/萊爾富）與宅配（黑貓/新竹）。無最低訂單限制，量少也 OK。"),
    ("電商代出貨服務怎麼運作？",
     "賣家將商品寄入咻咻倉庫後，由咻咻負責揀貨、包裝、出貨全流程。訂單透過 API 自動同步，出貨準確率 99.9%，讓賣家專心衝業績。"),
    ("小量訂單也可以找咻咻出貨嗎？",
     "可以！每天 10 張訂單也歡迎。咻咻提供彈性方案，無最低出貨量限制，適合剛起步的蝦皮賣家與個人品牌。"),
    ("支援哪些電商平台？",
     "支援蝦皮、MOMO、Shopify、Shopline、91APP、CYBERBIZ 等主流平台 API 串接，訂單自動同步不需手動操作。"),
    ("旺季爆單怎麼辦？",
     "咻咻提供旺季彈性擴容，大促期間出貨量增加小幅加價，不讓賣家因後勤爆掉而損失訂單。"),
]

# 台南倉儲推薦文章 FAQ（slug: tainan-warehouse-recommendation, 需查 post ID）
tainan_faqs = [
    ("台南倉儲適合小賣家嗎？",
     "完全適合。咻咻打包沒有最低出貨量限制，每天 10 張訂單也能合作，旺季爆量也能彈性接單。"),
    ("台南倉儲支援哪些電商平台？",
     "蝦皮、MOMO、91APP、自架官網都可以配合，訂單可透過系統自動傳入，不需手動操作。"),
    ("台南代出貨可以寄超商嗎？",
     "可以。咻咻打包支援 7-11、全家、萊爾富超商代寄，以及黑貓、新竹等宅配，全台可達。"),
    ("庫存怎麼查？需要自己盤點嗎？",
     "不需要。咻咻透過 WMS 倉儲管理系統，讓你隨時線上查看庫存數量與出貨狀態，完全透明。"),
]

targets = [
    {'id': 1318, 'name': 'home', 'faqs': home_faqs},
]

# 查 tainan-warehouse-recommendation post id
r = requests.get(f'{WP}/wp-json/wp/v2/posts', auth=auth,
    params={'slug': 'tainan-warehouse-recommendation'}, timeout=15)
posts = r.json()
if posts:
    pid = posts[0]['id']
    targets.append({'id': pid, 'name': 'tainan-warehouse-recommendation', 'faqs': tainan_faqs})
    print(f'tainan post id: {pid}')
else:
    print('tainan post not found')

for t in targets:
    schema = make_faq_schema(t['faqs'])
    r = requests.post(f'{WP}/wp-json/rankmath/v1/updateSchemas', auth=auth,
        json={
            'objectID': t['id'],
            'objectType': 'post',
            'schemas': schema,
        }, timeout=15)
    status = 'OK' if r.status_code == 200 else 'FAIL'
    print(f'[{status}] {t["name"]} (id={t["id"]}) -> {r.status_code} | {r.text[:100]}')

print('\n=== done ===')
