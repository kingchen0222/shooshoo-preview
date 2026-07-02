"""
生成超商代寄 + 超商收件兩篇文章的封面圖
使用 Gemini Nano Banana 2 (gemini-3.1-flash-image-preview)
"""
import base64, json, urllib.request, time
from pathlib import Path
from dotenv import load_dotenv
import os

load_dotenv(dotenv_path='D:/咻咻打包CLAUDE/.env')
KEY = os.getenv('GOOGLE_AI_API_KEY')
OUT = Path('D:/咻咻打包CLAUDE/social-cards/文章配圖')
OUT.mkdir(parents=True, exist_ok=True)

MODEL = 'gemini-3.1-flash-image-preview'
API = f'https://generativelanguage.googleapis.com/v1beta/models/{MODEL}:generateContent?key={KEY}'

PROMPTS = [
    {
        'filename': 'convenience-store-shipping-cover.png',
        'prompt': (
            "A split-panel 3D clay Pixar-style editorial illustration for a Taiwanese e-commerce logistics brand. "
            "Warm peach and amber color palette overall. "
            "LEFT PANEL (cool blue-white fluorescent lighting, tired mood): A chubby round-faced cartoon Taiwanese boss character "
            "wearing a casual shirt, hunched forward with sweat drops, struggling under a towering wobbling stack of brown cardboard "
            "shipping boxes, standing in a long queue line at a convenience store entrance. Exhausted droopy eyes, stress lines on face. "
            "RIGHT PANEL (warm amber home lighting, happy mood): The same boss character sitting relaxed at a cozy wooden home desk "
            "with a laptop and a steaming coffee mug, smiling broadly and giving a thumbs up. "
            "Beside him, an adorable chubby brown tabby cat mascot character with pink blush cheeks, squinting happy eyes and stubby "
            "limbs is cheerfully striding away carrying a neat stack of cardboard boxes. "
            "A clear vertical dividing line separates the two panels. "
            "3D clay toy rounded soft edges, subsurface scattering, playful brand mascot illustration style. "
            "Wide 16:9 landscape composition. No text in image."
        )
    },
    {
        'filename': 'convenience-store-pickup-cover.png',
        'prompt': (
            "A cheerful 3D clay Pixar-style illustration for a Taiwanese e-commerce logistics brand. "
            "Warm amber and cream color palette. "
            "MAIN SCENE: Inside a bright modern warehouse. Two adorable clay toy mascot characters are happily working together: "
            "Character 1 is a cute chubby beige tape-roll character with tiny arms and a big smile (咚咚膠帶), "
            "sealing a cardboard box with tape. "
            "Character 2 is an adorable chubby brown tabby cat with pink blush cheeks and squinting happy eyes (揀貨喵喵), "
            "loading neatly stacked packages onto a small cart. "
            "BACKGROUND: Organized warehouse shelving with colorful packages. On the right side, three glowing portals or "
            "doorways in green, blue, and orange colors hint at the three convenience store chains "
            "without using any real logos — just warm colored light beams. "
            "BOTTOM RIGHT: Small orange brand badge area (留白 for brand mark). "
            "3D clay toy rounded edges, soft studio lighting, cheerful and trustworthy brand feel. "
            "Wide 16:9 landscape composition. No text in image."
        )
    }
]

def generate(prompt, filename):
    body = json.dumps({
        'contents': [{'parts': [{'text': prompt}]}],
        'generationConfig': {
            'responseModalities': ['IMAGE'],
            'imageConfig': {'aspectRatio': '16:9', 'imageSize': '2K'}
        }
    }).encode()

    req = urllib.request.Request(API, data=body,
        headers={'Content-Type': 'application/json'}, method='POST')

    for attempt in range(3):
        try:
            with urllib.request.urlopen(req, timeout=120) as r:
                data = json.loads(r.read())
            break
        except urllib.error.HTTPError as e:
            err = e.read().decode()
            if e.code == 429:
                wait = 30 * (attempt + 1)
                print(f'  429 rate limit, waiting {wait}s...')
                time.sleep(wait)
                req = urllib.request.Request(API, data=body,
                    headers={'Content-Type': 'application/json'}, method='POST')
                continue
            print(f'  HTTP {e.code}: {err[:200]}')
            return None
    else:
        print('  Max retries exceeded')
        return None

    parts = data.get('candidates', [{}])[0].get('content', {}).get('parts', [])
    img_parts = [p for p in parts if 'inlineData' in p]

    if not img_parts:
        reason = data.get('candidates', [{}])[0].get('finishReason', 'unknown')
        print(f'  No image, finishReason: {reason}')
        return None

    img_bytes = base64.b64decode(img_parts[0]['inlineData']['data'])
    out_path = OUT / filename
    out_path.write_bytes(img_bytes)
    print(f'  Saved: {out_path} ({len(img_bytes):,} bytes)')
    return str(out_path)

if __name__ == '__main__':
    print(f'Using key: {KEY[:8]}...{KEY[-4:] if KEY else "NONE"}')
    for i, item in enumerate(PROMPTS):
        print(f'\n[{i+1}/{len(PROMPTS)}] Generating: {item["filename"]}')
        result = generate(item['prompt'], item['filename'])
        if result:
            print(f'  OK: {result}')
        if i < len(PROMPTS) - 1:
            print('  Waiting 15s between requests...')
            time.sleep(15)

    print('\nDone.')
