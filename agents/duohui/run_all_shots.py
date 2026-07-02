"""
熱巴 — 三方倉介紹 30秒 全 Shot 生成
6 Shots x 5秒 = 30秒
素材來自：D:\咻咻打包claude\影片素材\
"""
import asyncio, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from chatart import generate_video

MAT = Path('D:/咻咻打包claude/影片素材')
CHAR = MAT / '角色去背'
SCENE = MAT / '場景'

SHOTS = [
    {
        'name': 'shot01_痛點開場',
        'duration': 5,
        'images': [
            CHAR / '電商老闆_去背.png',   # 不存在就略過
            SCENE / '辦公室Mid.png',
        ],
        'prompt': (
            'Chaotic Taiwan e-commerce home workspace, '
            'cardboard boxes piled everywhere, shipping tape and bubble wrap scattered on floor, '
            'sticky notes on wall with messy schedule, frustrated atmosphere, '
            'slow push-in from wide to mid, harsh fluorescent overhead light casting hard shadows, '
            'warm #CC8800 tint on boxes, chaotic realism documentary style, '
            '9:16 vertical frame, 8K detail, film grain. '
            'Maintain consistent filmic color grade, teal-amber LUT, 24fps cinematic.'
        ),
    },
    {
        'name': 'shot02_痛點刺深',
        'duration': 5,
        'images': [
            SCENE / '辦公室Mid.png',
            CHAR / '倉倉老闆_去背.png',
        ],
        'prompt': (
            'Taiwan warehouse office desk covered in shipping manifests, '
            'stack of return forms with red pen error markings clearly visible, '
            'half-empty coffee cup, monitor with spreadsheet open, sticky notes everywhere, '
            'static shot slight 3 degree tilt, desk lamp warm light from left, monitor blue glow from right, '
            'focus pull from papers to background, shallow depth of field, '
            '9:16 vertical frame, 8K cinematic detail. '
            'Maintain consistent filmic color grade, teal-amber LUT, 24fps cinematic.'
        ),
    },
    {
        'name': 'shot03_咻咻登場',
        'duration': 5,
        'images': [
            SCENE / '倉庫主區Wide.png',
            SCENE / '咻咻LOGO.png',
            CHAR / '倉倉老闆_去背.png',
        ],
        'prompt': (
            'Clean organized modern 3PL warehouse interior Taiwan, '
            'high metal shelving units filled with boxes, yellow safety floor markings, '
            'large orange brand logo sign glowing on far wall, zone hanging signs visible, '
            'dramatic reveal dolly slowly forward from wide, '
            'warm industrial LED overhead light flooding space, '
            'no people, cinematic empty-space reveal, orange logo as accent focal point, '
            '9:16 vertical frame, low angle 24mm wide, 8K architectural style. '
            'Maintain consistent filmic color grade, teal-amber LUT, 24fps cinematic.'
        ),
    },
    {
        'name': 'shot04_服務展示',
        'duration': 5,
        'images': [
            SCENE / '走廊Mid.png',
        ],
        'prompt': (
            'Taiwan warehouse interior corridor between tall shelving rows, '
            'fast tracking shot forward through narrow passage, '
            'zone labels on shelf ends: 蝦皮 MOMO 7-11 全家, '
            'LED strip ceiling light top-down, deep shadows on both sides, '
            'motion blur on shelves, sharp center aisle, strong vanishing point perspective, '
            'forward movement energy speed ramp, '
            '9:16 vertical frame, 24mm wide, 8K detail, film grain. '
            'Maintain consistent filmic color grade, teal-amber LUT, 24fps cinematic.'
        ),
    },
    {
        'name': 'shot05_品牌信任',
        'duration': 5,
        'images': [
            SCENE / '倉庫主區Wide.png',
            SCENE / '咻咻LOGO.png',
            CHAR / '倉倉老闆_去背.png',
            CHAR / '電商老闆_去背.png',
        ],
        'prompt': (
            'Dramatic Taiwan warehouse brand moment, night atmosphere, '
            'single ceiling spotlight on large orange brand logo sign far wall, '
            'rest of warehouse in deep shadow, two IP character standees in foreground sharp, '
            'deep shadow #1A1A1A with warm orange #F5A623 spotlight accent, '
            'slow camera rise from standees up to logo, cinematic brand reveal, '
            '9:16 vertical frame, low angle, 8K detail. '
            'Maintain consistent filmic color grade, teal-amber LUT, 24fps cinematic.'
        ),
    },
    {
        'name': 'shot06_CTA',
        'duration': 5,
        'images': [
            SCENE / '倉庫主區Wide.png',
            SCENE / '咻咻LOGO.png',
            CHAR / '倉倉老闆_去背.png',
        ],
        'prompt': (
            'Inviting warm Taiwan 3PL warehouse space, orange brand dominant atmosphere, '
            'large orange logo sign glowing on far wall, '
            'QR code display board in mid-ground foreground right side, '
            'IP character standee beside QR board, '
            'slight push-in towards QR board at end, commercial brand atmosphere, '
            '9:16 vertical frame, warm orange #F5A623, 8K cinematic. '
            'Maintain consistent filmic color grade, teal-amber LUT, 24fps cinematic.'
        ),
    },
]


async def run_all():
    total = len(SHOTS)
    results = []
    for i, shot in enumerate(SHOTS, 1):
        name = shot['name']
        print(f'\n{"="*50}')
        print(f'[{i}/{total}] 生成 {name} ({shot["duration"]}秒)...')
        print(f'{"="*50}')

        # 過濾存在的圖片
        images = [str(p) for p in shot['images'] if p.exists()]
        missing = [p.name for p in shot['images'] if not p.exists()]
        if missing:
            print(f'  [警告] 找不到素材：{missing}，略過這些')
        print(f'  素材：{[Path(p).name for p in images]}')

        try:
            result = await generate_video(
                prompt=shot['prompt'],
                images=images,
                output_name=name,
                duration=shot['duration'],
            )
            results.append({'shot': name, 'file': result, 'ok': bool(result)})
            if result:
                print(f'  [{i}/{total}] 完成：{result}')
            else:
                print(f'  [{i}/{total}] 失敗或逾時')
        except Exception as e:
            print(f'  [{i}/{total}] 錯誤：{e}')
            results.append({'shot': name, 'file': None, 'ok': False})

        # Shot 之間暫停，讓 ChatArt 回到初始狀態
        if i < total:
            print(f'  等待 5 秒後繼續下一個 Shot...')
            await asyncio.sleep(5)

    print(f'\n{"="*50}')
    print('=== 全部 Shot 生成結果 ===')
    for r in results:
        status = 'OK' if r['ok'] else 'FAIL'
        print(f'  [{status}] {r["shot"]}: {r["file"] or "-"}')
    print(f'影片存放：D:\\咻咻打包claude\\行銷影片\\')


if __name__ == '__main__':
    # 可指定只跑特定 shot：python run_all_shots.py 3 4 5
    if len(sys.argv) > 1:
        indices = [int(x) - 1 for x in sys.argv[1:] if x.isdigit()]
        SHOTS = [SHOTS[i] for i in indices if 0 <= i < len(SHOTS)]
        print(f'只跑指定 Shot：{[s["name"] for s in SHOTS]}')

    asyncio.run(run_all())
