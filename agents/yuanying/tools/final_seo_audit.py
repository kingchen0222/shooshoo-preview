import json, re, requests, os
from requests.auth import HTTPBasicAuth
from dotenv import load_dotenv

load_dotenv()
WP_URL = os.getenv('WP_SITE_URL')
AUTH = HTTPBasicAuth(os.getenv('WP_USERNAME'), os.getenv('WP_APP_PASSWORD'))

# Refetch all posts (updated content)
all_posts = []
page = 1
while True:
    r = requests.get(f'{WP_URL}/wp-json/wp/v2/posts', auth=AUTH,
        params={'per_page': 100, 'page': page, 'status': 'publish'}, timeout=20)
    batch = r.json()
    if not batch: break
    all_posts.extend(batch)
    if len(batch) < 100: break
    page += 1

results = []
for p in all_posts:
    c = p['content']['rendered']
    text = re.sub(r'<[^>]+>', '', c)
    imgs = re.findall(r'<img[^>]+>', c)
    imgs_no_alt   = [i for i in imgs if 'alt=""' in i or 'alt=' not in i]
    imgs_no_title = [i for i in imgs if 'title=' not in i]
    h2s      = re.findall(r'<h2[^>]*>.*?</h2>', c, re.DOTALL)
    internal = re.findall(r'href="(https://www\.shooshoo\.com\.tw[^"#]+)"', c)
    external = [u for u in re.findall(r'href="(https://(?!www\.shooshoo\.com\.tw)[^"]+)"', c)
                if not any(x in u for x in ['wp-content', '#'])]
    cn_chars = len(re.findall(r'[一-鿿]', text))

    issues = []
    if not imgs:               issues.append('無圖片')
    if imgs_no_alt:            issues.append(f'圖片缺alt({len(imgs_no_alt)}張)')
    if imgs_no_title:          issues.append(f'圖片缺title({len(imgs_no_title)}張)')
    if not h2s:                issues.append('無H2')
    if not internal:           issues.append('無內部連結')
    if not external:           issues.append('無外部連結')
    if cn_chars < 300:         issues.append(f'字數過少({cn_chars}字)')

    results.append({
        'id': p['id'], 'slug': p['slug'],
        'imgs': len(imgs), 'imgs_no_alt': len(imgs_no_alt), 'imgs_no_title': len(imgs_no_title),
        'h2': len(h2s), 'internal': len(internal), 'external': len(external),
        'chars': cn_chars, 'issues': issues
    })

results.sort(key=lambda x: len(x['issues']), reverse=True)
with open('tmp_final_audit.json', 'w', encoding='utf-8') as f:
    json.dump(results, f, ensure_ascii=False, indent=2)

print(f'{"ID":<6} {"Slug":<45} {"Img":>4} {"Alt":>4} {"Ttl":>4} {"H2":>3} {"Int":>4} {"Ext":>4} {"Chars":>6}  Issues')
print('-'*120)
for r in results:
    issues_str = ' | '.join(r['issues']) if r['issues'] else 'OK'
    print(f'{r["id"]:<6} {r["slug"][:44]:<45} {r["imgs"]:>4} {r["imgs_no_alt"]:>4} {r["imgs_no_title"]:>4} {r["h2"]:>3} {r["internal"]:>4} {r["external"]:>4} {r["chars"]:>6}  {issues_str}')
