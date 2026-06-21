import json, re, requests, os
from requests.auth import HTTPBasicAuth
from dotenv import load_dotenv

load_dotenv()
WP_URL = os.getenv('WP_SITE_URL')
AUTH = HTTPBasicAuth(os.getenv('WP_USERNAME'), os.getenv('WP_APP_PASSWORD'))

# --- load data ---
with open('tmp_all_posts.json', encoding='utf-8') as f:
    posts = json.load(f)
with open('tmp_media_map.json', encoding='utf-8') as f:
    media_map = json.load(f)


def add_img_title(content):
    def replace_img(m):
        tag = m.group(0)
        if 'title=' in tag:
            return tag
        src_m = re.search(r'src="[^"]+/([^"/?]+\.(png|jpg|jpeg|webp|gif))"', tag)
        if not src_m:
            return tag
        filename = src_m.group(1)
        base = re.sub(r'-\d+x\d+', '', filename)
        media = media_map.get(filename) or media_map.get(base)
        if media and media.get('title'):
            title_text = media['title'].replace('"', '&quot;')
            # Insert title before closing />
            return re.sub(r'\s*/?>$', f' title="{title_text}" />', tag)
        return tag
    return re.sub(r'<img[^>]+/?>', replace_img, content)


to_update = []
skip_ids = []
for post in posts:
    new_content = add_img_title(post['content'])
    if new_content != post['content']:
        to_update.append({'id': post['id'], 'title': post['title'], 'content': new_content})
    else:
        skip_ids.append(post['id'])

results = []
for item in to_update:
    r = requests.post(
        f'{WP_URL}/wp-json/wp/v2/posts/{item["id"]}',
        auth=AUTH,
        json={'content': item['content']},
        timeout=20
    )
    results.append({'id': item['id'], 'status': r.status_code})

with open('tmp_batch_result.json', 'w', encoding='utf-8') as f:
    json.dump({'updated': results, 'skipped': skip_ids}, f, ensure_ascii=False, indent=2)

ok = sum(1 for x in results if x['status'] == 200)
print(f'Updated OK: {ok}/{len(results)}')
print(f'Skipped (no img or already had title): {skip_ids}')
