"""
楚然 — 生成影片素材
為熱巴的 ChatArt 全能模式提供 @素材 參考圖
"""
import os, requests, time
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()
KIE_KEY = os.getenv('KIE_API_KEY')
OUT_DIR = Path('D:/咻咻打包claude/影片素材')
OUT_DIR.mkdir(parents=True, exist_ok=True)

BASE_URL = 'https://api.kie.ai'

MATERIALS = {
    '倉庫主區Wide': """
Modern Taiwan 3PL warehouse interior, daytime operation,
high ceiling 8 meters, industrial LED grid overhead warm white light,
concrete floor with worn yellow safety markings and aisle arrows,
metal shelving units 3 meters tall filled with brown cardboard boxes,
zone labels on hanging signs: 7-11區 全家區 蝦皮區 MOMO區,
large orange 咻咻打包 logo sign on far wall glowing brightly,
forklift path markings on floor, clean organized space,
wide angle 24mm, slight low angle looking across floor,
warm #FFE4B5 dominant color grade, industrial realism,
9:16 vertical frame, architectural photography style, 8K detail,
Maintain consistent filmic color grade, teal-amber LUT, 24fps cinematic.
""".strip(),

    '辦公室Mid': """
Small Taiwan warehouse office interior,
glass partition wall separating from warehouse floor,
single desk with open laptop showing spreadsheet,
stack of shipping manifests paper with red pen markings,
coffee cup half empty, sticky notes on monitor,
small orange 咻咻打包 framed logo on wall,
warm desk lamp light from left, cool monitor glow,
9:16 vertical frame, 35mm natural perspective,
warm #FFD59E interior tone, 8K cinematic detail,
Maintain consistent filmic color grade, teal-amber LUT, 24fps cinematic.
""".strip(),

    '走廊Mid': """
Taiwan warehouse interior corridor,
narrow passage between two shelving rows 1.5 meters wide,
high shelves both sides creating tunnel perspective,
single LED strip light on ceiling casting top-down light,
concrete floor with center worn path,
zone labels visible on shelf ends: 蝦皮 MOMO 7-11,
small 咻咻打包 orange sticker on shelf post,
9:16 vertical frame, 24mm wide creating strong vanishing point,
warm top light with deep shadows on shelf sides,
cinematic corridor shot, 8K detail,
Maintain consistent filmic color grade, teal-amber LUT, 24fps cinematic.
""".strip(),

    '咻咻LOGO': """
Minimalist orange brand logo design,
咻咻打包 text in bold modern Chinese typography,
orange color #F5A623 on clean white background,
simple clean vector style,
package/box icon integrated into logo design,
high contrast, sharp edges, professional brand identity,
9:16 vertical frame centered, 8K sharp detail,
no shadows, flat design, pure white background.
""".strip(),
}


def _create_webhook() -> tuple[str, str]:
    """建立 webhook.site 臨時端點，回傳 (uuid, url)"""
    r = requests.post('https://webhook.site/token',
                      json={'default_status': 200, 'default_content': 'ok'},
                      timeout=10)
    uuid = r.json()['uuid']
    return uuid, f'https://webhook.site/{uuid}'


def _wait_for_callback(uuid: str, timeout: int = 300) -> dict:
    """輪詢 webhook.site，等待 KIE callback 到達"""
    deadline = time.time() + timeout
    while time.time() < deadline:
        time.sleep(5)
        r = requests.get(
            f'https://webhook.site/token/{uuid}/requests?sorting=newest&per_page=1',
            timeout=10)
        items = r.json().get('data', [])
        if items:
            import json as _json
            body = items[0].get('content', '{}')
            try:
                return _json.loads(body)
            except Exception:
                return {}
    return {}


def generate_image(name: str, prompt: str) -> str:
    out_path = OUT_DIR / f'{name}.png'
    if out_path.exists():
        print(f'  已存在：{out_path.name}，跳過')
        return str(out_path)

    print(f'\n生成：{name}...')

    # 建立 webhook 接收 callback
    webhook_uuid, callback_url = _create_webhook()
    print(f'  Webhook：{callback_url}')

    r = requests.post(
        f'{BASE_URL}/api/v1/jobs/createTask',
        headers={'Authorization': f'Bearer {KIE_KEY}'},
        json={
            'model': 'gpt-image-2-text-to-image',
            'callBackUrl': callback_url,
            'input': {
                'prompt': prompt,
                'aspect_ratio': '9:16'
            }
        },
        timeout=30
    )
    data = r.json()
    task_id = data.get('data', {}).get('taskId', '')
    if not task_id:
        print(f'  建立失敗：{data}')
        return ''
    print(f'  Task ID：{task_id}，等待 callback...')

    cb = _wait_for_callback(webhook_uuid, timeout=300)
    if not cb:
        print('  逾時，未收到 callback')
        return ''

    print(f'  Callback 收到')

    # callback 結構：data.resultJson 是 JSON 字串，內含 resultUrls 陣列
    import json as _json
    inner = cb.get('data') or {}
    result_json_str = inner.get('resultJson', '')
    img_url = ''
    if result_json_str:
        try:
            result_obj = _json.loads(result_json_str)
            urls = result_obj.get('resultUrls', [])
            img_url = urls[0] if urls else ''
        except Exception:
            pass

    # fallback: 直接找常見欄位
    if not img_url:
        img_url = (inner.get('imageUrl') or inner.get('url') or
                   inner.get('image_url') or '')

    if not img_url:
        print(f'  找不到圖片 URL，完整 callback：{cb}')
        return ''

    img_r = requests.get(img_url, timeout=60)
    out_path.write_bytes(img_r.content)
    print(f'  儲存：{out_path}')
    return str(out_path)


if __name__ == '__main__':
    import sys
    # 可指定只生成特定素材：python gen_video_materials.py 倉庫主區Wide
    targets = sys.argv[1:] if len(sys.argv) > 1 else list(MATERIALS.keys())
    results = {}
    for name in targets:
        if name in MATERIALS:
            results[name] = generate_image(name, MATERIALS[name])
        else:
            print(f'找不到素材：{name}，可用：{list(MATERIALS.keys())}')

    print('\n=== 素材生成完成 ===')
    for name, path in results.items():
        status = 'OK' if path else 'FAIL'
        print(f'  [{status}] {name}: {path}')
