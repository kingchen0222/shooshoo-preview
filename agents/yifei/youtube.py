"""
亦菲 — YouTube 頻道管理
需要 YouTube Data API v3 OAuth2（與 GSC 不同的憑證）
"""
import os, json
from dotenv import load_dotenv

load_dotenv()

YT_CLIENT_ID     = os.getenv('YT_CLIENT_ID', '')
YT_CLIENT_SECRET = os.getenv('YT_CLIENT_SECRET', '')
YT_REFRESH_TOKEN = os.getenv('YT_REFRESH_TOKEN', '')

CHANNEL_ID = os.getenv('YT_CHANNEL_ID', '')


def get_access_token():
    import requests
    r = requests.post('https://oauth2.googleapis.com/token', data={
        'client_id':     YT_CLIENT_ID,
        'client_secret': YT_CLIENT_SECRET,
        'refresh_token': YT_REFRESH_TOKEN,
        'grant_type':    'refresh_token'
    })
    return r.json().get('access_token')


def get_channel_stats():
    import requests
    token = get_access_token()
    r = requests.get('https://www.googleapis.com/youtube/v3/channels', params={
        'part': 'statistics,snippet',
        'id': CHANNEL_ID,
    }, headers={'Authorization': f'Bearer {token}'})
    return r.json()


def get_recent_videos(max_results=10):
    import requests
    token = get_access_token()
    r = requests.get('https://www.googleapis.com/youtube/v3/search', params={
        'part': 'snippet',
        'channelId': CHANNEL_ID,
        'order': 'date',
        'maxResults': max_results,
        'type': 'video'
    }, headers={'Authorization': f'Bearer {token}'})
    return r.json()


def get_video_analytics(video_id):
    """取得單一影片觀看數、留存率等"""
    import requests
    token = get_access_token()
    r = requests.get('https://youtubeanalytics.googleapis.com/v2/reports', params={
        'ids': 'channel==MINE',
        'startDate': '2026-01-01',
        'endDate': '2026-12-31',
        'metrics': 'views,estimatedMinutesWatched,averageViewDuration,likes,comments',
        'filters': f'video=={video_id}',
        'dimensions': 'day'
    }, headers={'Authorization': f'Bearer {token}'})
    return r.json()


if __name__ == '__main__':
    if not YT_REFRESH_TOKEN:
        print('尚未設定 YouTube OAuth2 憑證')
        print('需要在 .env 設定：YT_CLIENT_ID, YT_CLIENT_SECRET, YT_REFRESH_TOKEN, YT_CHANNEL_ID')
    else:
        stats = get_channel_stats()
        print(json.dumps(stats, ensure_ascii=False, indent=2))
