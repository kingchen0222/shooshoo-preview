"""
楚然 → 熱巴 交接：角色去背
1. 從 Google Drive 下載 IP 角色原圖
2. rembg 去背
3. 存到 D:\咻咻打包claude\影片素材\角色去背\
熱巴 在 ChatArt 全能模式上傳這些 PNG 作為 @素材
"""
import sys, requests
from pathlib import Path
from PIL import Image
from io import BytesIO

try:
    from rembg import remove
    HAS_REMBG = True
except ImportError:
    HAS_REMBG = False
    print('[警告] rembg 未安裝，將只下載原圖')

# characters.py 角色 Google Drive URL
sys.path.insert(0, str(Path(__file__).parent))
from characters import CHARACTERS

OUT_DIR = Path('D:/咻咻打包claude/影片素材/角色去背')
OUT_DIR.mkdir(parents=True, exist_ok=True)
RAW_DIR = Path('D:/咻咻打包claude/影片素材/角色原圖')
RAW_DIR.mkdir(parents=True, exist_ok=True)


def download_and_rembg(name: str, url: str) -> str:
    out_path = OUT_DIR / f'{name}_去背.png'
    if out_path.exists():
        print(f'  已存在：{out_path.name}')
        return str(out_path)

    print(f'\n處理：{name}...')
    r = requests.get(url, timeout=30, allow_redirects=True)
    if r.status_code != 200:
        print(f'  下載失敗：{r.status_code}')
        return ''

    raw_path = RAW_DIR / f'{name}_原圖.png'
    raw_path.write_bytes(r.content)
    print(f'  原圖存：{raw_path.name}')

    if HAS_REMBG:
        img = Image.open(BytesIO(r.content))
        result = remove(img)
        result.save(out_path)
        print(f'  去背存：{out_path.name}')
    else:
        out_path.write_bytes(r.content)
        print(f'  [無rembg] 原圖直接複製：{out_path.name}')

    return str(out_path)


if __name__ == '__main__':
    # 可指定角色名：python prepare_characters.py 倉倉老闆 電商老闆
    targets = sys.argv[1:] if len(sys.argv) > 1 else list(CHARACTERS.keys())

    results = {}
    for name in targets:
        if name not in CHARACTERS:
            print(f'  找不到角色：{name}')
            continue
        results[name] = download_and_rembg(name, CHARACTERS[name])

    print('\n=== 楚然交接熱巴 角色去背素材 ===')
    for name, path in results.items():
        status = 'OK' if path else 'FAIL'
        print(f'  [{status}] {name} -> {path}')
    print(f'\n素材放置：{OUT_DIR}')
    print('熱巴：上傳以上 PNG 到 ChatArt 全能模式，prompt 中用 @角色名_去背 引用')
