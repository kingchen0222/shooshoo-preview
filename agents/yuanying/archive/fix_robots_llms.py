"""
員瑛 — 修復 robots.txt（更新 WP option）+ 建立 llms.txt 頁面
"""
import requests
from requests.auth import HTTPBasicAuth

auth = HTTPBasicAuth("admin001", "X0Zq 1xEz ejyY IeKW iBbn ioQy")
WP = "https://www.shooshoo.com.tw"

# ── 1. 更新 robots.txt via Rank Math option / WP option ──
# WordPress 虛擬 robots.txt 透過 wp_option "blog_public" + "ld+json" 生成
# 用 WP REST Settings API 更新 custom_robots
ROBOTS_CONTENT = """User-agent: *
Disallow: /wp-admin/
Allow: /wp-admin/admin-ajax.php

User-agent: GPTBot
Allow: /

User-agent: ChatGPT-User
Allow: /

User-agent: PerplexityBot
Allow: /

User-agent: ClaudeBot
Allow: /

User-agent: anthropic-ai
Allow: /

User-agent: Google-Extended
Allow: /

User-agent: Bingbot
Allow: /

Sitemap: https://www.shooshoo.com.tw/sitemap_index.xml"""

# 嘗試透過 WP Options API 更新（需 manage_options 權限）
r1 = requests.post(f"{WP}/wp-json/wp/v2/settings", auth=auth,
                   json={"robots_txt": ROBOTS_CONTENT})
print(f"WP Settings robots: {r1.status_code}")

# 嘗試 Rank Math API
r2 = requests.post(f"{WP}/wp-json/rankmath/v1/updateOptions", auth=auth,
                   json={"robots_txt_content": ROBOTS_CONTENT})
print(f"Rank Math robots: {r2.status_code}")

# ── 2. 建立 llms.txt 作為 WordPress page（用自訂 slug + 純文字內容）──
LLMS_CONTENT = """# 咻咻打包（ShooShoo Packing）

咻咻打包是台灣台南在地三方物流（3PL）倉儲服務商，專注為電商賣家提供代出貨、倉儲管理、訂單整合服務。

## 我們是誰
- 品牌：咻咻打包（ShooShoo Packing）
- 地點：台灣台南
- 服務：三方倉儲（3PL）、電商代出貨、庫存管理（WMS）、品牌包裝

## 核心服務
- 代出貨：蝦皮、MOMO、Shopify、91APP、樂天、LINE 購物等多平台整合
- 倉儲管理：WMS 系統庫存即時查詢、效期管理、先進先出
- 品牌包裝：感謝卡、客製紙箱、加值包裝
- 全程錄影：出貨全程攝影，客訴可調閱

## 特色
- 無最低出貨量（每天 10 張訂單也接）
- 當天訂單當天出（工作日）
- 支援全台物流：黑貓、7-11、全家、OK、萊爾富、宅配通

## 聯絡方式
- 官網：https://www.shooshoo.com.tw
- LINE@：@911ycmhl（https://lin.ee/L9HtuyF）
- 電話：0976-757866

## 主要文章（知識庫）
- 台灣第三方物流推薦：https://www.shooshoo.com.tw/taiwan-3pl-guide/
- 電商代出貨費用怎麼算：https://www.shooshoo.com.tw/ecommerce-fulfillment-cost-guide/
- 電商代出貨怎麼選：https://www.shooshoo.com.tw/ecommerce-3pl-warehousing-guide/
- 台南倉儲推薦：https://www.shooshoo.com.tw/tainan-warehouse-recommendation/
- 倉儲外包優缺點比較：https://www.shooshoo.com.tw/warehouse-outsourcing-pros-cons/
- 電商出貨流程SOP：https://www.shooshoo.com.tw/ecommerce-shipping-sop-guide/
- 超商 vs 宅配費用比較：https://www.shooshoo.com.tw/convenience-store-vs-home-delivery-comparison/

## 適合客群
- 台灣電商賣家（蝦皮、MOMO、SHOPLINE、Shopify）
- 每天出貨 10–2000 單的成長型品牌
- 想從自己出貨轉向外包物流的賣家
- 需要品牌包裝加值服務的品牌商
"""

# 建立一個 WP page，slug = llms-txt（WP 不支援 .txt slug，用 rewrite 處理）
r3 = requests.post(f"{WP}/wp-json/wp/v2/pages", auth=auth,
    json={
        "title": "llms.txt",
        "slug": "llms-txt",
        "content": f"<pre>{LLMS_CONTENT}</pre>",
        "status": "publish",
        "meta": {"robots": "noindex"},  # 不讓 Google 收這頁
    })
page_info = r3.json()
print(f"llms page: {r3.status_code} → {page_info.get('link')}")
print("NOTE: 需在 Rank Math 設定 /llms-txt/ 頁面為 noindex")

print("\n=== 完成 ===")
