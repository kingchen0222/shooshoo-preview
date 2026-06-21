import requests, re
from requests.auth import HTTPBasicAuth
from pathlib import Path

auth = HTTPBasicAuth("admin001", "X0Zq 1xEz ejyY IeKW iBbn ioQy")
WP = "https://www.shooshoo.com.tw"

html = Path("agents/yuanying/article_3244.html").read_text(encoding="utf-8")
old = "https://www.shooshoo.com.tw/wp-content/uploads/2026/06/shooshoo-branded-packaging-ip.png"
new = "https://www.shooshoo.com.tw/wp-content/uploads/2026/06/shooshoo-outsourcing-hero-ip.png"
html = html.replace(old, new)
print("hero src in html:", new in html)

r = requests.post(f"{WP}/wp-json/wp/v2/posts/3244", auth=auth,
                  json={"content": html, "featured_media": 3251}, timeout=20)
print("status:", r.status_code)

r2 = requests.get(f"{WP}/wp-json/wp/v2/posts/3244", auth=auth, timeout=10)
imgs = re.findall(r'src="(https://www\.shooshoo\.com\.tw[^"]+\.png)"',
                  r2.json()["content"]["rendered"])
print("imgs in post:", imgs[:3])
