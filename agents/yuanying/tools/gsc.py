import os, requests
from dotenv import load_dotenv

load_dotenv()

CLIENT_ID     = os.getenv('GOOGLE_CLIENT_ID')
CLIENT_SECRET = os.getenv('GOOGLE_CLIENT_SECRET')
REFRESH_TOKEN = os.getenv('GOOGLE_REFRESH_TOKEN')
SITE          = 'https://www.shooshoo.com.tw/'


def get_access_token():
    r = requests.post('https://oauth2.googleapis.com/token', data={
        'client_id':     CLIENT_ID,
        'client_secret': CLIENT_SECRET,
        'refresh_token': REFRESH_TOKEN,
        'grant_type':    'refresh_token'
    })
    return r.json()['access_token']


def query_rankings(days=30, rows=20):
    token = get_access_token()
    r = requests.post(
        f'https://www.googleapis.com/webmasters/v3/sites/{requests.utils.quote(SITE, safe="")}/searchAnalytics/query',
        headers={'Authorization': f'Bearer {token}'},
        json={
            'startDate': _days_ago(days),
            'endDate':   _days_ago(1),
            'dimensions': ['page', 'query'],
            'rowLimit':   rows,
            'orderBy':    [{'fieldName': 'clicks', 'sortOrder': 'DESCENDING'}]
        }
    )
    return r.json().get('rows', [])


def submit_url(url):
    token = get_access_token()
    r = requests.post(
        f'https://www.googleapis.com/webmasters/v3/sites/{requests.utils.quote(SITE, safe="")}/sitemaps/{requests.utils.quote(url, safe="")}',
        headers={'Authorization': f'Bearer {token}'}
    )
    return r.status_code


def inspect_url(url):
    token = get_access_token()
    r = requests.post(
        'https://searchconsole.googleapis.com/v1/urlInspection/index:inspect',
        headers={'Authorization': f'Bearer {token}'},
        json={'inspectionUrl': url, 'siteUrl': SITE}
    )
    data = r.json()
    result = data.get('inspectionResult', {})
    index = result.get('indexStatusResult', {})
    return {
        'verdict':      index.get('verdict', 'N/A'),
        'coverageState': index.get('coverageState', 'N/A'),
        'lastCrawlTime': index.get('lastCrawlTime', 'N/A'),
        'robotsTxtState': index.get('robotsTxtState', 'N/A'),
    }


def _days_ago(n):
    from datetime import date, timedelta
    return (date.today() - timedelta(days=n)).strftime('%Y-%m-%d')


if __name__ == '__main__':
    print('=== 員瑛：GSC 排名報告 ===\n')
    rows = query_rankings(days=30, rows=15)
    if rows:
        print(f'{"關鍵字":<30} {"頁面":<45} {"點擊":>5} {"曝光":>7} {"排名":>6}')
        print('-' * 100)
        for row in rows:
            kw   = row['keys'][1][:28]
            page = row['keys'][0].replace('https://www.shooshoo.com.tw','')[:43]
            print(f'{kw:<30} {page:<45} {int(row["clicks"]):>5} {int(row["impressions"]):>7} {row["position"]:>6.1f}')
    else:
        print('暫無資料')
