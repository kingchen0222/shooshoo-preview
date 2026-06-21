"""
亦菲 — Facebook / Instagram 發文與數據查詢
使用 Meta Graph API v21.0
"""
import os, requests, json, time
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

ACCESS_TOKEN = os.getenv('META_ACCESS_TOKEN')
FB_PAGE_ID   = os.getenv('FB_PAGE_ID', '')
IG_USER_ID   = os.getenv('IG_USER_ID', '')
WP_SITE_URL  = os.getenv('WP_SITE_URL', '')
WP_USER      = os.getenv('WP_USERNAME', '')
WP_PASS      = os.getenv('WP_APP_PASSWORD', '')
BASE         = 'https://graph.facebook.com/v21.0'


def get_page_info():
    """取得 FB 粉絲頁基本資訊與粉絲數"""
    r = requests.get(f'{BASE}/me', params={
        'fields': 'id,name,fan_count,followers_count',
        'access_token': ACCESS_TOKEN
    })
    return r.json()


def post_to_facebook(message, image_url=None):
    """發文到 FB 粉絲頁"""
    if image_url:
        r = requests.post(f'{BASE}/{FB_PAGE_ID}/photos', data={
            'url': image_url,
            'caption': message,
            'access_token': ACCESS_TOKEN
        })
    else:
        r = requests.post(f'{BASE}/{FB_PAGE_ID}/feed', data={
            'message': message,
            'access_token': ACCESS_TOKEN
        })
    return r.json()


def post_to_instagram(caption, image_url):
    """發圖文到 IG（需先建立媒體容器再發布）"""
    # Step 1: 建立媒體容器
    r1 = requests.post(f'{BASE}/{IG_USER_ID}/media', data={
        'image_url': image_url,
        'caption': caption,
        'access_token': ACCESS_TOKEN
    })
    creation_id = r1.json().get('id')
    if not creation_id:
        return {'error': r1.json()}

    # Step 2: 發布
    r2 = requests.post(f'{BASE}/{IG_USER_ID}/media_publish', data={
        'creation_id': creation_id,
        'access_token': ACCESS_TOKEN
    })
    return r2.json()


def post_video_to_facebook(video_path: str, description: str, title: str = ''):
    """上傳本地 MP4 影片到 FB 粉絲頁"""
    video_path = Path(video_path)
    if not video_path.exists():
        return {'error': f'找不到影片：{video_path}'}

    print(f'上傳 FB 影片：{video_path.name}...')
    with open(video_path, 'rb') as f:
        r = requests.post(
            f'https://graph-video.facebook.com/v21.0/{FB_PAGE_ID}/videos',
            data={
                'description': description,
                'title': title or video_path.stem,
                'access_token': ACCESS_TOKEN
            },
            files={'source': (video_path.name, f, 'video/mp4')},
            timeout=300
        )
    result = r.json()
    if 'id' in result:
        print(f'  FB 影片已上傳，ID：{result["id"]}')
    else:
        print(f'  FB 上傳失敗：{result}')
    return result


def post_reels_to_instagram(video_url: str, caption: str, cover_url: str = None):
    """
    發布 IG Reels（需要公開影片 URL）
    video_url：可用 upload_video_to_wp() 取得 WordPress 公開連結
    """
    print('建立 IG Reels 容器...')
    data = {
        'media_type': 'REELS',
        'video_url': video_url,
        'caption': caption,
        'share_to_feed': 'true',
        'access_token': ACCESS_TOKEN
    }
    if cover_url:
        data['cover_url'] = cover_url

    r1 = requests.post(f'{BASE}/{IG_USER_ID}/media', data=data)
    creation_id = r1.json().get('id')
    if not creation_id:
        print(f'  容器建立失敗：{r1.json()}')
        return {'error': r1.json()}

    # 等待影片處理完成（輪詢最多 5 分鐘）
    print(f'  容器 ID：{creation_id}，等待處理...')
    for i in range(30):
        time.sleep(10)
        status_r = requests.get(f'{BASE}/{creation_id}', params={
            'fields': 'status_code',
            'access_token': ACCESS_TOKEN
        })
        status = status_r.json().get('status_code', '')
        print(f'  [{(i+1)*10}s] 狀態：{status}')
        if status == 'FINISHED':
            break
        if status == 'ERROR':
            return {'error': '影片處理失敗', 'detail': status_r.json()}

    # 發布
    print('  發布 Reels...')
    r2 = requests.post(f'{BASE}/{IG_USER_ID}/media_publish', data={
        'creation_id': creation_id,
        'access_token': ACCESS_TOKEN
    })
    result = r2.json()
    if 'id' in result:
        print(f'  IG Reels 已發布，ID：{result["id"]}')
    else:
        print(f'  IG 發布失敗：{result}')
    return result


def upload_video_to_wp(video_path: str) -> str:
    """
    上傳本地影片到 WordPress 媒體庫，回傳公開 URL
    （供 IG Reels 使用）
    """
    video_path = Path(video_path)
    if not video_path.exists():
        return ''

    print(f'上傳影片至 WordPress：{video_path.name}...')
    with open(video_path, 'rb') as f:
        r = requests.post(
            f'{WP_SITE_URL}/wp-json/wp/v2/media',
            auth=(WP_USER, WP_PASS),
            headers={'Content-Disposition': f'attachment; filename="{video_path.name}"'},
            files={'file': (video_path.name, f, 'video/mp4')},
            timeout=300
        )
    result = r.json()
    url = result.get('source_url', '')
    if url:
        print(f'  WordPress 影片 URL：{url}')
    else:
        print(f'  上傳失敗：{result}')
    return url


def publish_video_all(video_path: str, caption: str, fb_title: str = ''):
    """
    一鍵發布影片到 FB + IG Reels
    1. 上傳影片到 WordPress（取得公開 URL 供 IG 使用）
    2. 發布到 FB（multipart 直接上傳）
    3. 發布到 IG Reels（用 WP URL）
    """
    results = {}

    # FB（直接上傳本地檔案）
    results['fb'] = post_video_to_facebook(video_path, caption, fb_title)

    # 上傳到 WP 取得 URL
    video_url = upload_video_to_wp(video_path)
    if video_url:
        results['ig'] = post_reels_to_instagram(video_url, caption)
    else:
        results['ig'] = {'error': 'WordPress 上傳失敗，無法取得 IG 用 URL'}

    return results


def get_fb_insights(days=7):
    """取得 FB 粉絲頁近期數據"""
    r = requests.get(f'{BASE}/{FB_PAGE_ID}/insights', params={
        'metric': 'page_impressions,page_reach,page_post_engagements,page_fan_adds',
        'period': 'day',
        'since': _days_ago(days),
        'until': _days_ago(0),
        'access_token': ACCESS_TOKEN
    })
    return r.json()


def get_ig_insights():
    """取得 IG 帳號基本數據"""
    r = requests.get(f'{BASE}/{IG_USER_ID}', params={
        'fields': 'followers_count,media_count,profile_views',
        'access_token': ACCESS_TOKEN
    })
    return r.json()


def get_recent_posts(limit=10):
    """取得最近 FB 貼文及互動數"""
    r = requests.get(f'{BASE}/{FB_PAGE_ID}/posts', params={
        'fields': 'message,created_time,likes.summary(true),comments.summary(true),shares',
        'limit': limit,
        'access_token': ACCESS_TOKEN
    })
    return r.json()


def _days_ago(n):
    from datetime import date, timedelta
    return int((date.today() - timedelta(days=n)).strftime('%s') if hasattr(date.today(), '__format__') else
               __import__('time').mktime((__import__('datetime').date.today() - __import__('datetime').timedelta(days=n)).timetuple()))


if __name__ == '__main__':
    print('=== 亦菲：社群數據報告 ===\n')
    info = get_page_info()
    print('FB 粉絲頁:', info)
    with open('tmp_fb_info.json', 'w', encoding='utf-8') as f:
        json.dump(info, f, ensure_ascii=False, indent=2)
