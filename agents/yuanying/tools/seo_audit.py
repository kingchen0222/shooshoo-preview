import os
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv

load_dotenv()

SITE_URL = "https://www.shooshoo.com.tw"

KEYWORDS = {
    "高優先": ["電商代出貨", "代客出貨", "電商倉儲", "第三方物流", "台南倉儲", "3PL"],
    "長尾": ["蝦皮代出貨", "Shopify倉儲", "旺季出貨外包", "多平台出貨"],
}

def audit_page(url):
    r = requests.get(url, timeout=10, headers={"User-Agent": "Mozilla/5.0"})
    soup = BeautifulSoup(r.text, "html.parser")

    title = soup.find("title")
    description = soup.find("meta", attrs={"name": "description"})
    h1_tags = soup.find_all("h1")
    h2_tags = soup.find_all("h2")
    og_title = soup.find("meta", property="og:title")
    og_desc = soup.find("meta", property="og:description")

    print(f"\n{'='*50}")
    print(f"頁面：{url}")
    print(f"{'='*50}")
    print(f"Title：{title.get_text() if title else '❌ 沒有 Title'}")
    print(f"Meta Description：{description['content'] if description else '❌ 沒有 Meta Description'}")
    h1_ok = "OK" if len(h1_tags)==1 else "WARN 應該只有1個"
    print(f"H1 數量：{len(h1_tags)} [{h1_ok}]")
    for h in h1_tags:
        print(f"  H1：{h.get_text().strip()}")
    print(f"H2 數量：{len(h2_tags)}")
    for h in h2_tags[:5]:
        print(f"  H2：{h.get_text().strip()}")

    body_text = soup.get_text()
    print(f"\n--- 關鍵字出現次數 ---")
    for priority, kws in KEYWORDS.items():
        print(f"[{priority}]")
        for kw in kws:
            count = body_text.count(kw)
            status = "OK" if count >= 2 else ("WARN" if count == 1 else "MISSING")
            print(f"  {status} {kw}：{count} 次")

    print(f"\nOG Title：{og_title['content'] if og_title else '❌ 沒有'}")
    print(f"OG Description：{og_desc['content'] if og_desc else '❌ 沒有'}")

if __name__ == "__main__":
    print("=== 員瑛：咻咻打包 SEO 健診 ===\n")
    pages = [
        SITE_URL + "/",
    ]
    for page in pages:
        try:
            audit_page(page)
        except Exception as e:
            print(f"錯誤：{e}")
