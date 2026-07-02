"""
咻咻打包 超商文章完整重做
1. KIE 生兩張對應風格封面圖（3D Pixar 暖橘色）
2. 用 inline HTML 格式重寫文章（對齊現有文章風格）
3. 上傳圖片 → 設 featured + OG → 確認 publish
"""
import requests, os, json, time
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(dotenv_path='D:/咻咻打包CLAUDE/.env')
WP   = os.getenv('WP_SITE_URL').rstrip('/')
USER = os.getenv('WP_USERNAME')
PASS = os.getenv('WP_APP_PASSWORD')
KIE  = os.getenv('KIE_API_KEY')
AUTH = (USER, PASS)
KIE_H = {"Authorization": f"Bearer {KIE}", "Content-Type": "application/json"}

OUT = Path('D:/咻咻打包CLAUDE/social-cards/文章配圖')

# ── KIE 生圖 ──────────────────────────────────────────────────────
IMAGES = [
    {
        'filename': 'shooshoo-convenience-store-shipping-hero.png',
        'prompt': (
            "A split-panel 3D Pixar-style clay toy commercial illustration for Taiwanese e-commerce "
            "logistics brand called ShooShoo Packing (咻咻打包). "
            "LEFT PANEL with cool blue-white tones and '自己出貨' label: "
            "Cute chubby 3D Pixar cartoon Taiwanese boss character with sweat drops, "
            "struggling under a huge wobbling tower of brown cardboard shipping boxes, "
            "standing exhausted in a long queue line at 7-ELEVEN convenience store entrance. "
            "Floating Chinese labels: '自己跑超商' and '耗時耗力'. Tired droopy expression. "
            "RIGHT PANEL with warm amber-orange tones and '交給咻咻' label: "
            "Same boss character sitting relaxed at a cozy wooden desk with laptop, "
            "smiling broadly giving thumbs up. An adorable chubby orange tabby 3D clay cat "
            "mascot with big round eyes happily carrying a neat stack of packages. "
            "Floating Chinese labels: '在家等上門' and '省時省力'. "
            "Center orange circle with 'VS' text. "
            "Top orange banner with Chinese text '咻咻打包・超商代寄服務'. "
            "Overall warm amber orange brand colors. "
            "3D clay toy rounded edges, soft subsurface scattering, Pixar quality. "
            "Wide 16:9 landscape. Infographic-style layout."
        ),
    },
    {
        'filename': 'shooshoo-convenience-store-pickup-hero.png',
        'prompt': (
            "A vibrant 3D Pixar-style clay toy commercial illustration for Taiwanese logistics brand "
            "ShooShoo Packing (咻咻打包). "
            "MAIN SCENE inside modern bright warehouse with warm amber-orange shelving racks. "
            "Two adorable chubby orange tabby 3D clay cat mascots working cheerfully: "
            "Left cat using barcode scanner picking packages from shelves with enthusiasm. "
            "Right cat sealing cardboard boxes with tape, happy squinting eyes. "
            "BACKGROUND: Organized warehouse shelves with packages and boxes. "
            "Right side has three glowing delivery portal gates: "
            "one in 7-ELEVEN green, one in FamilyMart blue, one in Hi-Life red, "
            "representing the three convenience store chains with packages flying through. "
            "Large orange Chinese banner at top: '超商收件完整說明'. "
            "Row of store name badges: '7-11' '全家' '萊爾富' '蝦皮' in matching brand colors. "
            "Bottom right corner has '咻咻打包' brand badge in orange. "
            "Overall warm amber-orange color palette, cozy professional warehouse feel. "
            "3D clay toy rounded edges, bright cheerful studio lighting, Pixar quality. "
            "Wide 16:9 landscape. Infographic-style layout with embedded Chinese text."
        ),
    },
]

def kie_create(prompt, aspect='16:9', res='2K'):
    r = requests.post('https://api.kie.ai/api/v1/jobs/createTask',
        headers=KIE_H,
        json={'model': 'nano-banana-2', 'input': {
            'prompt': prompt, 'image_input': [],
            'aspect_ratio': aspect, 'resolution': res, 'output_format': 'png'
        }}, timeout=30)
    d = r.json()
    if d.get('code') != 200:
        raise Exception(f'KIE createTask failed: {d.get("msg")}')
    return d['data']['taskId']

def kie_poll(task_id, interval=8, timeout=360):
    for _ in range(timeout // interval):
        r = requests.get('https://api.kie.ai/api/v1/jobs/recordInfo',
            headers=KIE_H, params={'taskId': task_id}, timeout=15)
        d = r.json().get('data', {})
        state = d.get('state', '')
        print(f'  [{state}]', end=' ', flush=True)
        if state == 'success':
            print()
            return json.loads(d['resultJson'])['resultUrls'][0]
        elif state == 'fail':
            raise Exception(f'Task failed: {d.get("failMsg")}')
        time.sleep(interval)
    raise TimeoutError('KIE task timeout')

def kie_download(url, path):
    r = requests.get(url, timeout=60)
    Path(path).write_bytes(r.content)
    print(f'  Saved {Path(path).name} ({len(r.content):,} bytes)')

# ── 文章 HTML（inline CSS 格式，對齊現有文章） ────────────────────

CONTENT_3264 = """<div style="max-width:860px;margin:0 auto;font-family:'Noto Sans TC',sans-serif;color:#333;line-height:1.8;">

<div style="text-align:center;margin-bottom:32px;">
  <img decoding="async" src="HERO_IMG_URL" alt="台南超商代寄服務｜自己跑超商 vs 委託咻咻上門收 時間比較" style="width:100%;border-radius:12px;" />
</div>

<div style="background:#fff8f0;border-left:5px solid #f5a623;padding:20px 24px;border-radius:8px;margin-bottom:36px;">
  <p style="font-size:1.1em;margin:0;">你上一次自己跑超商寄件，花了多久？<br>打包、扛箱、找停車位、排號碼牌——保守估計一趟至少 <strong>40 分鐘到 2 小時</strong>。如果每天出貨 30 單，一週有幾個小時消耗在排隊？</p>
</div>

<h2 style="font-size:1.6em;color:#c0580a;border-bottom:3px solid #f5a623;padding-bottom:8px;margin-top:48px;">超商代寄，原來可以不用自己去</h2>
<p>「超商代寄」不是只有你一個人能做。咻咻打包幫台南電商賣家做的事很簡單：<strong>你打包好，放著等，咻咻來收。</strong></p>

<div style="display:grid;grid-template-columns:1fr 1fr;gap:20px;margin:28px 0;">
  <div style="background:#f0f4ff;border-radius:10px;padding:20px;">
    <div style="font-size:1em;font-weight:700;color:#1a3a6b;margin-bottom:12px;">😮‍💨 以前：自己跑超商</div>
    <ul style="margin:0;padding-left:1.2em;font-size:0.95em;line-height:2.2;color:#555;">
      <li>自己打包、貼寄件單</li>
      <li>扛箱子出門，找停車位</li>
      <li>到 7-11 / 全家 / 萊爾富 排隊</li>
      <li>等店員掃描確認每一件</li>
      <li>回家，明天繼續重複</li>
    </ul>
  </div>
  <div style="background:#fff8f0;border-radius:10px;padding:20px;">
    <div style="font-size:1em;font-weight:700;color:#c0580a;margin-bottom:12px;">😌 現在：委託咻咻</div>
    <ul style="margin:0;padding-left:1.2em;font-size:0.95em;line-height:2.2;color:#555;">
      <li>庫存放進咻咻台南倉</li>
      <li>訂單進來，咻咻自動揀貨打包</li>
      <li>咻咻送件到 7-11 / 全家 / 萊爾富</li>
      <li>你：完全不用動</li>
      <li>省出來的時間⋯⋯繼續讀下去</li>
    </ul>
  </div>
</div>

<h2 style="font-size:1.6em;color:#c0580a;border-bottom:3px solid #f5a623;padding-bottom:8px;margin-top:48px;">省下來的時間，你打算拿來做什麼？</h2>
<p>這不是在賣廣告，是真的在問你：</p>

<div style="margin:24px 0;">
  <div style="display:flex;align-items:flex-start;gap:16px;margin-bottom:16px;background:#fff;border:1px solid #f0e0c8;border-radius:10px;padding:18px;">
    <div style="font-size:2em;line-height:1;">👨‍👩‍👧</div>
    <div><strong>陪家人吃晚餐</strong><br><span style="color:#777;font-size:0.95em;">有些老闆說，外包出貨之後，終於有時間陪家人，不用再趕著跑超商。</span></div>
  </div>
  <div style="display:flex;align-items:flex-start;gap:16px;margin-bottom:16px;background:#fff;border:1px solid #f0e0c8;border-radius:10px;padding:18px;">
    <div style="font-size:2em;line-height:1;">📈</div>
    <div><strong>選品、做行銷，業績翻倍</strong><br><span style="color:#777;font-size:0.95em;">空出來的時間拿去選新品、跑廣告，當月業績直接翻倍的案例不是沒有。</span></div>
  </div>
  <div style="display:flex;align-items:flex-start;gap:16px;margin-bottom:16px;background:#fff;border:1px solid #f0e0c8;border-radius:10px;padding:18px;">
    <div style="font-size:2em;line-height:1;">💆</div>
    <div><strong>腰不痠了，人輕鬆了</strong><br><span style="color:#777;font-size:0.95em;">也有人說，就只是不用再扛箱子了，這樣就夠了。</span></div>
  </div>
</div>

<div style="background:#fff3cd;border-left:5px solid #f5a623;padding:16px 20px;border-radius:8px;margin:32px 0;">
  <p style="margin:0;font-size:1.1em;font-weight:700;color:#7a5a00;">老闆的時間，不該花在排隊。</p>
</div>

<h2 style="font-size:1.6em;color:#c0580a;border-bottom:3px solid #f5a623;padding-bottom:8px;margin-top:48px;">咻咻支援哪些超商？</h2>
<p>7-ELEVEN、全家 FamilyMart、萊爾富 HiLife，三家全都支援。買家指定哪家，咻咻就送哪家，不用你操心。</p>

<div style="display:flex;gap:12px;flex-wrap:wrap;margin:20px 0;">
  <div style="background:#1c6a2e;color:#fff;padding:8px 20px;border-radius:20px;font-weight:700;font-size:0.95em;">7-ELEVEN</div>
  <div style="background:#1e4b8f;color:#fff;padding:8px 20px;border-radius:20px;font-weight:700;font-size:0.95em;">全家 FamilyMart</div>
  <div style="background:#c0392b;color:#fff;padding:8px 20px;border-radius:20px;font-weight:700;font-size:0.95em;">萊爾富 HiLife</div>
</div>

<h2 style="font-size:1.6em;color:#c0580a;border-bottom:3px solid #f5a623;padding-bottom:8px;margin-top:48px;">適合什麼樣的賣家？</h2>
<div style="margin:20px 0;">
  <div style="margin-bottom:12px;border:1px solid #f0e0c8;border-radius:10px;overflow:hidden;">
    <div style="background:#fff8f0;padding:12px 18px;font-weight:700;color:#c0580a;">🛒 蝦皮、MOMO 賣家</div>
    <div style="padding:12px 18px;font-size:0.95em;">每天訂單進來，出貨吃掉一半工時，外包是最有效的時間解法。</div>
  </div>
  <div style="margin-bottom:12px;border:1px solid #f0e0c8;border-radius:10px;overflow:hidden;">
    <div style="background:#fff8f0;padding:12px 18px;font-weight:700;color:#c0580a;">🎙 直播主</div>
    <div style="padding:12px 18px;font-size:0.95em;">播完一場就是幾十上百單，自己出根本出不完，咻咻當天收，隔天出。</div>
  </div>
  <div style="margin-bottom:12px;border:1px solid #f0e0c8;border-radius:10px;overflow:hidden;">
    <div style="background:#fff8f0;padding:12px 18px;font-weight:700;color:#c0580a;">🏷 個人品牌電商</div>
    <div style="padding:12px 18px;font-size:0.95em;">精力放在產品和行銷，不是物流。</div>
  </div>
  <div style="margin-bottom:12px;border:1px solid #f0e0c8;border-radius:10px;overflow:hidden;">
    <div style="background:#fff8f0;padding:12px 18px;font-weight:700;color:#c0580a;">📦 量少也 OK</div>
    <div style="padding:12px 18px;font-size:0.95em;">每天 10 單也歡迎，咻咻沒有最低出貨量限制。</div>
  </div>
</div>

<h2 style="font-size:1.6em;color:#c0580a;border-bottom:3px solid #f5a623;padding-bottom:8px;margin-top:48px;">超商代寄怎麼開始？</h2>
<div style="display:flex;gap:0;margin:24px 0;overflow:hidden;border-radius:10px;border:1px solid #f0e0c8;">
  <div style="flex:1;padding:18px;text-align:center;background:#fff8f0;">
    <div style="font-size:1.8em;margin-bottom:8px;">💬</div>
    <div style="font-weight:700;color:#c0580a;font-size:0.9em;">Step 1</div>
    <div style="font-size:0.9em;margin-top:4px;">加 LINE，聊一下現在每天出幾單</div>
  </div>
  <div style="width:1px;background:#f0e0c8;"></div>
  <div style="flex:1;padding:18px;text-align:center;background:#fff;">
    <div style="font-size:1.8em;margin-bottom:8px;">📦</div>
    <div style="font-weight:700;color:#c0580a;font-size:0.9em;">Step 2</div>
    <div style="font-size:0.9em;margin-top:4px;">庫存寄進咻咻台南倉庫</div>
  </div>
  <div style="width:1px;background:#f0e0c8;"></div>
  <div style="flex:1;padding:18px;text-align:center;background:#fff8f0;">
    <div style="font-size:1.8em;margin-bottom:8px;">🚀</div>
    <div style="font-weight:700;color:#c0580a;font-size:0.9em;">Step 3</div>
    <div style="font-size:0.9em;margin-top:4px;">之後的出貨，咻咻全包</div>
  </div>
</div>
<p style="text-align:center;color:#777;font-size:0.95em;">就這樣。</p>

<div style="text-align:center;margin:40px 0 20px;">
  <a href="https://lin.ee/L9HtuyF" style="display:inline-block;background:#f5a623;color:#fff;font-size:1.1em;font-weight:700;padding:16px 40px;border-radius:50px;text-decoration:none;box-shadow:0 4px 16px rgba(245,166,35,0.4);">加 LINE 詢問超商代寄 →</a>
  <p style="margin-top:10px;color:#999;font-size:0.85em;">LINE ID：@911ycmhl</p>
</div>

<hr style="border:none;border-top:1px solid #f0e0c8;margin:40px 0;" />
<p style="font-size:0.9em;color:#777;">延伸閱讀：<a href="https://www.shooshoo.com.tw/convenience-store-pickup-guide/" style="color:#c0580a;">超商收件完整說明</a> ・ <a href="https://www.shooshoo.com.tw/convenience-store-vs-home-delivery-comparison/" style="color:#c0580a;">超商寄件 vs 宅配到府比較</a></p>

</div>

<script type="application/ld+json">
{"@context":"https://schema.org","@type":"FAQPage","mainEntity":[{"@type":"Question","name":"台南超商代寄可以不用自己去超商嗎？","acceptedAnswer":{"@type":"Answer","text":"可以。咻咻打包提供超商代寄服務，賣家把貨放在咻咻台南倉庫，訂單由咻咻揀貨打包後直接送至7-11、全家或萊爾富，賣家完全不需要親自跑超商。"}},{"@type":"Question","name":"超商代寄支援哪些超商？","acceptedAnswer":{"@type":"Answer","text":"咻咻打包支援7-ELEVEN、全家FamilyMart、萊爾富HiLife三大超商代寄，買家指定哪家超商取件，咻咻就送到哪家。"}},{"@type":"Question","name":"出貨量少可以委託超商代寄嗎？","acceptedAnswer":{"@type":"Answer","text":"可以。咻咻打包無最低出貨量限制，每天10單也歡迎，適合蝦皮新手賣家、直播主或剛起步的個人品牌電商。"}},{"@type":"Question","name":"委託超商代寄後，自己要做什麼？","acceptedAnswer":{"@type":"Answer","text":"幾乎不需要做任何事。庫存寄入咻咻台南倉後，訂單進來由咻咻自動揀貨、打包、寄出，賣家只需要專注在接單和行銷。"}}]}
</script>"""

CONTENT_3268 = """<div style="max-width:860px;margin:0 auto;font-family:'Noto Sans TC',sans-serif;color:#333;line-height:1.8;">

<div style="text-align:center;margin-bottom:32px;">
  <img decoding="async" src="HERO_IMG_URL" alt="超商收件完整說明｜咻咻打包 7-11全家萊爾富蝦皮超商取件代寄服務" style="width:100%;border-radius:12px;" />
</div>

<div style="background:#fff8f0;border-left:5px solid #f5a623;padding:20px 24px;border-radius:8px;margin-bottom:36px;">
  <p style="font-size:1.1em;margin:0;">台灣電商有一個隱形問題：<strong>買家在家等宅配，等到天荒地老</strong>。上班族選超商取件，是因為方便——下班順路進 7-11 掃一下就帶走，沒有時間壓力。<br>對賣家來說，「超商收件」意思是你要把貨送到買家指定的超商。這件事，咻咻可以幫你搞定。</p>
</div>

<h2 style="font-size:1.6em;color:#c0580a;border-bottom:3px solid #f5a623;padding-bottom:8px;margin-top:48px;">超商收件是什麼？</h2>
<p>超商收件（又稱超商取件、超商取貨）是台灣電商最主流的配送方式之一，流程很簡單：</p>

<div style="display:flex;gap:0;margin:24px 0;overflow:hidden;border-radius:10px;border:1px solid #f0e0c8;">
  <div style="flex:1;padding:16px;text-align:center;background:#fff8f0;">
    <div style="font-size:1.6em;margin-bottom:6px;">🛒</div>
    <div style="font-weight:700;color:#c0580a;font-size:0.85em;">買家下單</div>
    <div style="font-size:0.82em;color:#777;margin-top:4px;">選擇超商取件門市</div>
  </div>
  <div style="width:1px;background:#f0e0c8;"></div>
  <div style="flex:1;padding:16px;text-align:center;background:#fff;">
    <div style="font-size:1.6em;margin-bottom:6px;">📦</div>
    <div style="font-weight:700;color:#c0580a;font-size:0.85em;">咻咻出貨</div>
    <div style="font-size:0.82em;color:#777;margin-top:4px;">揀貨打包送至超商總倉</div>
  </div>
  <div style="width:1px;background:#f0e0c8;"></div>
  <div style="flex:1;padding:16px;text-align:center;background:#fff8f0;">
    <div style="font-size:1.6em;margin-bottom:6px;">📲</div>
    <div style="font-weight:700;color:#c0580a;font-size:0.85em;">買家取件</div>
    <div style="font-size:0.82em;color:#777;margin-top:4px;">下班順路掃碼取貨</div>
  </div>
</div>

<p>買家不用在家等，賣家不用解釋配送進度，雙方都省事。</p>

<h2 style="font-size:1.6em;color:#c0580a;border-bottom:3px solid #f5a623;padding-bottom:8px;margin-top:48px;">咻咻支援哪些超商收件？</h2>

<div style="margin:20px 0;border:1px solid #f0e0c8;border-radius:10px;overflow:hidden;">
  <table style="width:100%;border-collapse:collapse;font-size:0.95em;">
    <thead>
      <tr style="background:#fff8f0;">
        <th style="padding:12px 16px;text-align:left;color:#c0580a;font-weight:700;">超商</th>
        <th style="padding:12px 16px;text-align:left;color:#c0580a;font-weight:700;">取件方式</th>
        <th style="padding:12px 16px;text-align:left;color:#c0580a;font-weight:700;">全台門市數</th>
      </tr>
    </thead>
    <tbody>
      <tr style="border-top:1px solid #f0e0c8;">
        <td style="padding:12px 16px;"><strong style="color:#1c6a2e;">7-ELEVEN</strong></td>
        <td style="padding:12px 16px;">ibon 機台掃描</td>
        <td style="padding:12px 16px;">約 6,700 間</td>
      </tr>
      <tr style="border-top:1px solid #f0e0c8;background:#fafafa;">
        <td style="padding:12px 16px;"><strong style="color:#1e4b8f;">全家 FamilyMart</strong></td>
        <td style="padding:12px 16px;">FamiPort 掃碼</td>
        <td style="padding:12px 16px;">約 4,200 間</td>
      </tr>
      <tr style="border-top:1px solid #f0e0c8;">
        <td style="padding:12px 16px;"><strong style="color:#c0392b;">萊爾富 HiLife</strong></td>
        <td style="padding:12px 16px;">Life-ET 機台</td>
        <td style="padding:12px 16px;">約 1,300 間</td>
      </tr>
      <tr style="border-top:1px solid #f0e0c8;background:#fafafa;">
        <td style="padding:12px 16px;"><strong style="color:#ee4d2d;">蝦皮超商取件</strong></td>
        <td style="padding:12px 16px;">蝦皮 App 取件碼</td>
        <td style="padding:12px 16px;">同以上三家</td>
      </tr>
    </tbody>
  </table>
</div>

<h2 style="font-size:1.6em;color:#c0580a;border-bottom:3px solid #f5a623;padding-bottom:8px;margin-top:48px;">超商收件 vs 宅配到府，賣家怎麼選？</h2>
<p>沒有哪個比哪個好，看商品和買家習慣：</p>
<div style="display:grid;grid-template-columns:1fr 1fr;gap:16px;margin:20px 0;">
  <div style="background:#fff8f0;border-radius:10px;padding:18px;">
    <div style="font-weight:700;color:#c0580a;margin-bottom:10px;">📮 選超商收件</div>
    <ul style="margin:0;padding-left:1.2em;font-size:0.93em;line-height:2;color:#555;">
      <li>輕小件（5kg 以內）</li>
      <li>上班族買家、不方便在家等</li>
      <li>蝦皮、MOMO 一般商品</li>
    </ul>
  </div>
  <div style="background:#f0f4ff;border-radius:10px;padding:18px;">
    <div style="font-weight:700;color:#1a3a6b;margin-bottom:10px;">🚚 選宅配到府</div>
    <ul style="margin:0;padding-left:1.2em;font-size:0.93em;line-height:2;color:#555;">
      <li>大型、重量品（5kg+）</li>
      <li>易碎品、需冷藏</li>
      <li>需要指定配送時段</li>
    </ul>
  </div>
</div>
<p>咻咻打包兩種都支援，同一批訂單可以混合出貨，不需要賣家自己分類。</p>

<h2 style="font-size:1.6em;color:#c0580a;border-bottom:3px solid #f5a623;padding-bottom:8px;margin-top:48px;">蝦皮超商取件，咻咻怎麼代操？</h2>
<div style="background:#fff8f0;border-radius:10px;padding:20px 24px;margin:20px 0;">
  <ol style="margin:0;padding-left:1.5em;line-height:2.4;font-size:0.95em;">
    <li>買家在蝦皮下單，選好取件門市</li>
    <li>訂單同步進咻咻系統</li>
    <li>咻咻倉庫揀貨、打包、代送至蝦皮指定超商總倉</li>
    <li>買家在超商掃碼取貨</li>
  </ol>
</div>
<p>賣家全程不需要碰任何出貨操作。</p>

<h2 style="font-size:1.6em;color:#c0580a;border-bottom:3px solid #f5a623;padding-bottom:8px;margin-top:48px;">超商收件包裹放多久？</h2>
<div style="background:#fff8f0;border-left:5px solid #f5a623;padding:16px 20px;border-radius:8px;margin:20px 0;">
  <p style="margin:0;">7-11 和全家超商收件包裹通常保存 <strong>7 天</strong>，逾期退回寄件方（咻咻倉庫）。建議出貨後主動提醒買家儘快取件，可以有效降低退貨率。</p>
</div>

<h2 style="font-size:1.6em;color:#c0580a;border-bottom:3px solid #f5a623;padding-bottom:8px;margin-top:48px;">把超商收件這件事，完全交給咻咻</h2>
<p>你不需要搞懂每家超商的寄件流程，不需要自己跑門市，不需要記取件碼。<strong>你只要賣東西，剩下的咻咻來。</strong></p>

<div style="text-align:center;margin:40px 0 20px;">
  <a href="https://lin.ee/L9HtuyF" style="display:inline-block;background:#f5a623;color:#fff;font-size:1.1em;font-weight:700;padding:16px 40px;border-radius:50px;text-decoration:none;box-shadow:0 4px 16px rgba(245,166,35,0.4);">加 LINE 詢問超商代寄 →</a>
  <p style="margin-top:10px;color:#999;font-size:0.85em;">LINE ID：@911ycmhl</p>
</div>

<hr style="border:none;border-top:1px solid #f0e0c8;margin:40px 0;" />
<p style="font-size:0.9em;color:#777;">延伸閱讀：<a href="https://www.shooshoo.com.tw/tainan-convenience-store-shipping/" style="color:#c0580a;">台南超商代寄推薦</a> ・ <a href="https://www.shooshoo.com.tw/convenience-store-vs-home-delivery-comparison/" style="color:#c0580a;">超商寄件 vs 宅配到府費用比較</a></p>

</div>

<script type="application/ld+json">
{"@context":"https://schema.org","@type":"FAQPage","mainEntity":[{"@type":"Question","name":"超商收件和宅配到府哪個比較好？","acceptedAnswer":{"@type":"Answer","text":"沒有絕對。輕小件（5kg以內）、上班族買家選超商收件更方便；大型、重量、易碎品選宅配到府更安全。咻咻打包兩種都支援，同批訂單可混合出貨。"}},{"@type":"Question","name":"蝦皮超商取件可以委託咻咻代寄嗎？","acceptedAnswer":{"@type":"Answer","text":"可以。咻咻打包支援蝦皮超商取件代操，訂單進系統後由咻咻代送至蝦皮指定超商總倉，賣家不需自行操作任何出貨步驟。"}},{"@type":"Question","name":"超商收件包裹放多久？","acceptedAnswer":{"@type":"Answer","text":"7-11和全家超商收件包裹保存約7天，逾期退回寄件方。建議出貨後提醒買家盡快取件以降低退貨率。"}},{"@type":"Question","name":"委託咻咻打包做超商收件，賣家需要做什麼？","acceptedAnswer":{"@type":"Answer","text":"把庫存寄入咻咻台南倉庫後，後續揀貨、打包、送件全由咻咻處理，賣家只需要專注接單和行銷，不需要碰任何出貨操作。"}}]}
</script>"""

POSTS = [
    {
        'id': 3264,
        'slug': 'tainan-convenience-store-shipping',
        'title': '台南超商代寄推薦｜委託咻咻，在家等上門收，不用自己跑超商',
        'img_key': 0,
        'img_filename': IMAGES[0]['filename'],
        'img_alt': '台南超商代寄服務｜自己跑超商 vs 委託咻咻上門收 時間對比圖',
        'focus_kw': '台南超商代寄',
        'meta_desc': '台南電商賣家不用自己跑超商寄件！咻咻打包超商代寄服務，在家等上門收貨，7-11、全家、萊爾富都支援，讓你省時間做老闆該做的事。',
        'og_title': '台南超商代寄推薦 2026｜在家等收，不用跑超商',
        'content': CONTENT_3264,
    },
    {
        'id': 3268,
        'slug': 'convenience-store-pickup-guide',
        'title': '超商收件完整說明｜7-11全家萊爾富蝦皮，咻咻幫你搞定',
        'img_key': 1,
        'img_filename': IMAGES[1]['filename'],
        'img_alt': '超商收件說明｜7-11全家萊爾富蝦皮超商取件，咻咻打包代寄服務',
        'focus_kw': '超商收件',
        'meta_desc': '超商收件完整說明：7-ELEVEN、全家、萊爾富、蝦皮超商取件全支援。委託咻咻打包代寄，不用自己送件，賣家只要接單，出貨咻咻包辦。',
        'og_title': '超商收件完整說明 2026｜7-11全家萊爾富蝦皮咻咻代寄',
        'content': CONTENT_3268,
    },
]

def upload_image(img_path, alt_text, title):
    img = Path(img_path)
    r = requests.post(f'{WP}/wp-json/wp/v2/media', auth=AUTH,
        headers={'Content-Disposition': f'attachment; filename="{img.name}"',
                 'Content-Type': 'image/png'},
        data=img.read_bytes(), timeout=60)
    if r.status_code not in (200, 201):
        raise Exception(f'Upload failed {r.status_code}: {r.text[:200]}')
    media = r.json()
    media_id = media['id']
    media_url = media['source_url']
    requests.post(f'{WP}/wp-json/wp/v2/media/{media_id}', auth=AUTH,
        json={'alt_text': alt_text, 'title': title}, timeout=15)
    print(f'  Uploaded media_id={media_id}')
    return media_id, media_url

def update_post(post_id, media_id, media_url, p):
    content = p['content'].replace('HERO_IMG_URL', media_url)
    r = requests.post(f'{WP}/wp-json/wp/v2/posts/{post_id}', auth=AUTH,
        json={'title': p['title'], 'content': content,
              'featured_media': media_id, 'status': 'publish'}, timeout=20)
    print(f'  Post update: {r.status_code}')
    r2 = requests.post(f'{WP}/wp-json/rankmath/v1/updateMeta', auth=AUTH,
        json={'objectID': post_id, 'objectType': 'post', 'meta': {
            'rank_math_focus_keyword': p['focus_kw'],
            'rank_math_description':  p['meta_desc'],
            'rank_math_og_title':     p['og_title'],
            'rank_math_og_description': p['meta_desc'],
            'rank_math_og_image_id':  str(media_id),
            'rank_math_twitter_title': p['og_title'],
            'rank_math_twitter_description': p['meta_desc'],
            'rank_math_twitter_image_id': str(media_id),
        }}, timeout=15)
    print(f'  RankMath: {r2.status_code}')

# ── MAIN ──────────────────────────────────────────────────────────
generated_paths = {}

# Phase 1: 生圖
print('=== Phase 1: KIE Image Generation ===')
task_ids = {}
for img in IMAGES:
    out_path = OUT / img['filename']
    if out_path.exists():
        print(f'Skip (exists): {img["filename"]}')
        generated_paths[img['filename']] = str(out_path)
        continue
    print(f'Creating task: {img["filename"]}')
    tid = kie_create(img['prompt'])
    task_ids[img['filename']] = tid
    print(f'  task_id={tid}')
    time.sleep(3)

for fname, tid in task_ids.items():
    print(f'Polling: {fname}')
    url = kie_poll(tid)
    out_path = OUT / fname
    kie_download(url, out_path)
    generated_paths[fname] = str(out_path)
    time.sleep(5)

# Phase 2: 上傳 + 更新
print('\n=== Phase 2: Upload + Update Posts ===')
for p in POSTS:
    fname = p['img_filename']
    img_path = generated_paths.get(fname)
    if not img_path or not Path(img_path).exists():
        print(f'ERROR: image not found for post {p["id"]}')
        continue
    print(f'\n[Post {p["id"]}] {p["slug"]}')
    media_id, media_url = upload_image(img_path, p['img_alt'], p['title'])
    update_post(p['id'], media_id, media_url, p)

print('\n=== DONE ===')
for p in POSTS:
    print(f'  https://www.shooshoo.com.tw/{p["slug"]}/')
