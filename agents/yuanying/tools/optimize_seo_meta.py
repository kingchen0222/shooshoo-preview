"""
員瑛 — 批次優化 15 篇文章 SEO Meta
使用 Rank Math REST API /rankmath/v1/updateMeta
meta 必須傳 dict（非 JSON string）
"""
import os, requests
from dotenv import load_dotenv
load_dotenv('D:/咻咻打包claude/.env')

WP   = os.getenv('WP_SITE_URL')
AUTH = (os.getenv('WP_USERNAME'), os.getenv('WP_APP_PASSWORD'))

SEO_DATA = [
    {
        'id': 1,
        'focus_kw': '第三方物流 3PL',
        'title': '第三方物流 3PL 是什麼？電商賣家降低營運成本完整指南 | 咻咻打包',
        'desc': '不知道 3PL 是什麼？從零解釋第三方物流運作方式、費用結構，以及電商賣家什麼時候該導入 3PL 服務，降低倉儲與出貨成本。',
    },
    {
        'id': 2662,
        'focus_kw': '手機管理電商訂單',
        'title': '手機管理電商訂單？咻咻打包 WMS 系統完整介紹 | 咻咻打包',
        'desc': '用手機就能看庫存、追訂單、確認出貨狀態。咻咻打包 WMS 整合蝦皮、MOMO、Shopify，讓電商賣家隨時掌握全局不漏單。',
    },
    {
        'id': 2664,
        'focus_kw': '食品美妝倉儲',
        'title': '食品美妝電商怎麼選倉儲？恆溫倉儲與效期管理完整指南 | 咻咻打包',
        'desc': '食品有效期疏失全批損毀，美妝溫度不對影響品質。本篇說明食品美妝電商選倉儲的關鍵注意事項，以及效期管理 SOP 完整介紹。',
    },
    {
        'id': 2665,
        'focus_kw': '倉儲揀貨 SOP',
        'title': '電商倉儲揀貨怎麼做？零失誤出貨 SOP 完整說明 | 咻咻打包',
        'desc': '揀錯貨一次，退換貨成本是原訂單 3 倍以上。咻咻打包揀貨 SOP 從收單到出貨全程零失誤，本篇完整介紹流程與品管機制。',
    },
    {
        'id': 2666,
        'focus_kw': '電商包裝破損',
        'title': '電商包裝破損客訴怎麼辦？全程錄影防損包裝完整說明 | 咻咻打包',
        'desc': '「商品破了」是電商最怕的客訴。咻咻打包提供全程出貨錄影＋防損包裝，讓你有憑有據，有效降低糾紛與退換貨損失。',
    },
    {
        'id': 2670,
        'focus_kw': '電商退貨處理',
        'title': '電商退貨怎麼處理？高效退貨 SOP 讓顧客滿意度提升 | 咻咻打包',
        'desc': '退貨進來要檢查、判斷、退款、重新入庫，一個人處理超崩潰。咻咻打包代執行退貨 SOP，每筆退貨都有紀錄、有追蹤。',
    },
    {
        'id': 2671,
        'focus_kw': 'B2B B2C 電商物流',
        'title': 'B2B 與 B2C 電商物流有什麼不同？一個倉庫全搞定 | 咻咻打包',
        'desc': '同時跑批發和零售的賣家，出貨邏輯完全不同。本篇說明 B2B vs B2C 物流差異，以及如何用一個倉庫同時搞定兩種出貨模式。',
    },
    {
        'id': 2672,
        'focus_kw': '旺季代出貨',
        'title': '節慶爆單出貨怎麼辦？貼標加工分裝倉儲服務完整說明 | 咻咻打包',
        'desc': '雙11、母親節訂單暴增，一個人根本出不來？咻咻打包提供旺季代出貨、貼標加工、分裝服務，讓你安心接單、準時出貨。',
    },
    {
        'id': 2673,
        'focus_kw': '電商庫存管理',
        'title': '電商庫存管理怎麼做？WMS 系統商品主檔與條碼管理指南 | 咻咻打包',
        'desc': '庫存混亂、超賣、找不到商品？WMS 倉儲管理系統幫電商賣家解決庫存問題，從商品主檔設定到條碼掃描全說明。',
    },
    {
        'id': 2674,
        'focus_kw': '代出貨品牌包裝',
        'title': '電商代出貨也能有品牌感？客製化打包服務讓客人驚喜 | 咻咻打包',
        'desc': '外包出貨不代表失去品牌感。咻咻打包提供客製化包裝、品牌貼紙、專屬紙箱，讓每一個包裹都說出你的品牌故事。',
    },
    {
        'id': 2883,
        'focus_kw': '電商代出貨',
        'title': '電商代出貨怎麼選？3PL 倉儲完整攻略 2026 | 咻咻打包',
        'desc': '訂單多到出不來？本篇完整介紹電商代出貨怎麼運作、費用怎麼算、選哪家最適合，幫你告別自己打包寄件的日子。',
    },
    {
        'id': 2913,
        'focus_kw': '台南倉儲',
        'title': '台南倉儲推薦 2026｜電商賣家代出貨完整指南 | 咻咻打包',
        'desc': '台南電商賣家出貨量增加，找台南倉儲代出貨最省時省力。整理台南倉儲選擇重點、費用說明，以及咻咻打包服務介紹。',
    },
    {
        'id': 2920,
        'focus_kw': '超商寄件費用',
        'title': '超商寄件 vs 宅配到府費用比較 2026｜電商賣家完整指南 | 咻咻打包',
        'desc': '超商寄件還是宅配到府哪個划算？2026 年最新費用比較、限重規定、適合品類一次說清楚，幫電商賣家選對出貨方式。',
    },
    {
        'id': 3094,
        'focus_kw': '電商代出貨費用',
        'title': '電商代出貨費用怎麼算？倉儲外包收費邏輯完整說明 | 咻咻打包',
        'desc': '代出貨到底收什麼費？入庫費、揀貨費、包材費全說明，附試算範例，幫你判斷外包是否比自己出貨更划算。',
    },
    {
        'id': 3213,
        'focus_kw': '第三方物流推薦',
        'title': '台灣第三方物流推薦 2026｜電商賣家必看 3PL 選擇指南 | 咻咻打包',
        'desc': '想把出貨外包給台灣第三方物流卻不知道怎麼選？整理 6 大評估重點、自己出貨 vs 3PL 完整比較，幫你找到對的倉儲夥伴。',
    },
]


def update_seo(post_id, focus_kw, title, desc):
    r = requests.post(
        f'{WP}/wp-json/rankmath/v1/updateMeta',
        auth=AUTH,
        json={
            'objectID':   post_id,
            'objectType': 'post',
            'meta': {
                'rank_math_focus_keyword': focus_kw,
                'rank_math_title':         title,
                'rank_math_description':   desc,
            }
        }
    )
    return r.status_code, r.json()


print('員瑛 — Rank Math SEO Meta 批次寫入\n')
ok = 0
for item in SEO_DATA:
    code, resp = update_seo(item['id'], item['focus_kw'], item['title'], item['desc'])
    success = code == 200 and resp.get('slug') is True
    status = 'OK' if success else f'FAIL({code})'
    print(f'[{status}] ID {item["id"]:>5} | {item["focus_kw"]}')
    if not success:
        print(f'         回應：{resp}')
    else:
        ok += 1

print(f'\n完成：{ok}/{len(SEO_DATA)} 篇成功')
