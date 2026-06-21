"""
員瑛 — 批次更新主要頁面 meta title / description / focus keyword
"""
import requests
from requests.auth import HTTPBasicAuth

auth = HTTPBasicAuth('admin001', 'X0Zq 1xEz ejyY IeKW iBbn ioQy')
WP = 'https://www.shooshoo.com.tw'

pages_meta = [
    {
        'id': 1318,
        'slug': 'home',
        'title': '台南代出貨倉儲｜電商代出貨首選－咻咻打包',
        'desc': '咻咻打包台南在地3PL倉儲，支援蝦皮、MOMO、Shopify多平台整合，無最低出貨量，當天出貨。讓你專心賣東西，出貨交給咻咻打包！',
        'kw': '電商代出貨,台南倉儲,3PL',
    },
    {
        'id': 2558,
        'slug': 'flow',
        'title': '電商代倉儲服務流程｜咻咻打包台南倉儲外包一站式出貨',
        'desc': '從入庫驗收、庫存管理到揀貨包裝、寄件出貨，咻咻打包一站式代出貨流程完整說明，支援黑貓、7-11、全家等全台主流物流，電商賣家出貨零煩惱。',
        'kw': '電商代出貨流程,倉儲服務流程,代出貨',
    },
    {
        'id': 2536,
        'slug': 'wms',
        'title': '智慧倉儲管理系統WMS｜咻咻打包電商庫存即時掌握',
        'desc': '咻咻打包 WMS 庫存管理系統，支援蝦皮、MOMO、Shopify 等 10+ 平台 API 串接，庫存即時同步、效期預警、訂單分流，電商庫存管理零失誤。',
        'kw': 'WMS庫存管理系統,電商庫存管理,倉儲管理',
    },
    {
        'id': 1319,
        'slug': 'about',
        'title': '關於咻咻打包｜台南電商代倉儲品牌 ShooShoo Packing',
        'desc': '咻咻打包是台南在地電商代出貨團隊，服務超過 500 個品牌，以透明溝通、當天出貨、品質把關為核心，是成長型電商賣家信賴的3PL倉儲夥伴。',
        'kw': '咻咻打包,台南倉儲,關於我們',
    },
    {
        'id': 2312,
        'slug': 'consult',
        'title': '免費諮詢・台南代倉儲出貨方案｜咻咻打包',
        'desc': '想外包電商出貨？填寫諮詢表單，咻咻打包專人 24 小時內回覆，提供客製化代出貨方案，無最低出貨量，台南在地3PL倉儲首選，立即預約免費諮詢！',
        'kw': '電商代出貨諮詢,免費諮詢,台南3PL',
    },
]

for p in pages_meta:
    r = requests.post(f'{WP}/wp-json/rankmath/v1/updateMeta', auth=auth,
        json={
            'objectID': p['id'],
            'objectType': 'post',
            'meta': {
                'rank_math_title': p['title'],
                'rank_math_description': p['desc'],
                'rank_math_focus_keyword': p['kw'],
            }
        }, timeout=15)
    status = 'OK' if r.status_code == 200 else 'FAIL'
    print(f'[{status}] {p["slug"]} -> {r.status_code} | {r.text[:80]}')

print('\n=== done ===')
