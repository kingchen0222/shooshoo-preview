"""
GSC 處理：
1. 用 refresh token 換 access token
2. 送 sitemap
3. 對兩個新文章 URL 呼叫 URL Inspection (request indexing)
"""
import requests, os
from dotenv import load_dotenv

load_dotenv(dotenv_path='D:/咻咻打包CLAUDE/.env')
CLIENT_ID     = os.getenv('GOOGLE_CLIENT_ID')
CLIENT_SECRET = os.getenv('GOOGLE_CLIENT_SECRET')
REFRESH_TOKEN = os.getenv('GOOGLE_REFRESH_TOKEN')
SITE          = 'https://www.shooshoo.com.tw/'

URLS = [
    'https://www.shooshoo.com.tw/tainan-convenience-store-shipping/',
    'https://www.shooshoo.com.tw/convenience-store-pickup-guide/',
]

# 1. 換 access token
r = requests.post('https://oauth2.googleapis.com/token', data={
    'client_id':     CLIENT_ID,
    'client_secret': CLIENT_SECRET,
    'refresh_token': REFRESH_TOKEN,
    'grant_type':    'refresh_token',
})
token_data = r.json()
if 'access_token' not in token_data:
    print(f'Token error: {token_data}')
    exit(1)
ACCESS = token_data['access_token']
H = {'Authorization': f'Bearer {ACCESS}', 'Content-Type': 'application/json'}
print(f'Access token OK (expires in {token_data.get("expires_in")}s)')

# 2. Submit sitemap
sitemap_url = 'https://www.shooshoo.com.tw/sitemap_index.xml'
r2 = requests.put(
    f'https://www.googleapis.com/webmasters/v3/sites/{requests.utils.quote(SITE, safe="")}/sitemaps/{requests.utils.quote(sitemap_url, safe="")}',
    headers=H
)
print(f'Sitemap submit: {r2.status_code}')

# 3. URL Inspection — request indexing for each URL
for url in URLS:
    r3 = requests.post(
        'https://searchconsole.googleapis.com/v1/urlInspection/index:inspect',
        headers=H,
        json={'inspectionUrl': url, 'siteUrl': SITE}
    )
    d = r3.json()
    verdict = d.get('inspectionResult', {}).get('indexStatusResult', {}).get('verdict', '')
    coverage = d.get('inspectionResult', {}).get('indexStatusResult', {}).get('coverageState', '')
    print(f'  {url}')
    print(f'    verdict={verdict} coverage={coverage} status={r3.status_code}')
