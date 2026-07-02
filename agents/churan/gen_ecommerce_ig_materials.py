"""
楚然 — 電商 IG 素材批量生圖
15 張 4:5 圖片，分兩大主題：
  A. 電商賣家痛苦點（8張）
  B. 三方倉儲專業形象（7張）
輸出至: 影片素材/IG素材/電商主題/
"""

import os, time, json, requests
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()
KIE_KEY = os.getenv("KIE_API_KEY")
KIE_H   = {"Authorization": f"Bearer {KIE_KEY}", "Content-Type": "application/json"}
OUT_DIR = Path("D:/咻咻打包claude/影片素材/IG素材/電商主題")
OUT_DIR.mkdir(parents=True, exist_ok=True)

IMAGES = [
    # ── A. 電商賣家痛苦點 ──────────────────────────────────────────
    {
        "filename": "A01-開車寄貨.png",
        "prompt": (
            "Tired young Taiwanese man loading many cardboard boxes into the car trunk, "
            "parking lot background, evening warm light, sweating, stressed expression, "
            "realistic candid photography style, e-commerce seller daily life, "
            "warm orange tones, no text in image, 4:5 portrait"
        ),
    },
    {
        "filename": "A02-超商排隊-711.png",
        "prompt": (
            "Long queue inside a 7-Eleven convenience store Taiwan, "
            "young woman holding a tall stack of packages struggling to wait in line, "
            "other customers behind her, bright fluorescent interior lighting, "
            "realistic candid photography, no brand logos visible, no text in image, 4:5 portrait"
        ),
    },
    {
        "filename": "A03-超商排隊-全家.png",
        "prompt": (
            "Busy FamilyMart convenience store Taiwan, "
            "young man holding multiple courier packages trying to reach the counter, "
            "cramped space, frustrated tired expression, people waiting, "
            "realistic photography, warm interior, no text in image, 4:5 portrait"
        ),
    },
    {
        "filename": "A04-超商排隊-萊爾富.png",
        "prompt": (
            "HiLife convenience store Taiwan, e-commerce seller young woman "
            "balancing a tower of packages about to fall, awkward struggle, "
            "queue behind her, realistic candid photography, "
            "no brand logos, no text in image, 4:5 portrait"
        ),
    },
    {
        "filename": "A05-家裡變倉庫.png",
        "prompt": (
            "Small Taiwanese apartment living room completely taken over by cardboard boxes "
            "stacked ceiling high, sofa buried under packages, packing tape rolls everywhere, "
            "only a narrow path to walk through, cozy warm home lighting, "
            "realistic photography, no text in image, 4:5 portrait"
        ),
    },
    {
        "filename": "A06-家人吵架.png",
        "prompt": (
            "Stressed young Taiwanese couple arguing at home, boxes and packing materials "
            "scattered everywhere around them, one person frustrated pointing at the mess, "
            "other person on laptop managing orders, tense atmosphere, "
            "warm indoor lighting, realistic photography, no text in image, 4:5 portrait"
        ),
    },
    {
        "filename": "A07-爆單人手不夠.png",
        "prompt": (
            "Small e-commerce team of two people overwhelmed with orders, "
            "order printouts covering the table, boxes piling up faster than they can pack, "
            "exhausted expressions, frantic hands trying to keep up, late night, "
            "realistic photography, no text in image, 4:5 portrait"
        ),
    },
    {
        "filename": "A08-熬夜打包.png",
        "prompt": (
            "Lone e-commerce seller sitting alone at night surrounded by packing tape, "
            "bubble wrap, cardboard boxes, laptop showing order management screen, "
            "dark room with only desk lamp on, exhausted eyes, empty coffee cup, "
            "realistic photography, no text in image, 4:5 portrait"
        ),
    },
    # ── B. 三方倉儲專業形象 ────────────────────────────────────────
    {
        "filename": "B01-倉庫全景.png",
        "prompt": (
            "Modern professional 3PL fulfillment warehouse interior Taiwan, "
            "high ceiling with organized metal shelving racks filled with products, "
            "clean wide aisles, efficient layout, warm industrial overhead lighting, "
            "establishing wide shot, professional logistics facility, "
            "no text in image, 4:5 portrait"
        ),
    },
    {
        "filename": "B02-揀貨效率.png",
        "prompt": (
            "Professional warehouse worker confidently scanning product barcode "
            "with handheld scanner, organized shelving system in background, "
            "focused efficient expression, bright clean warehouse environment, "
            "logistics uniform, realistic photography, no text in image, 4:5 portrait"
        ),
    },
    {
        "filename": "B03-打包分工.png",
        "prompt": (
            "Professional warehouse assembly line team packing orders systematically, "
            "multiple workers each with clear station and role, boxes moving efficiently, "
            "organized workstations, teamwork and division of labor, "
            "clean professional environment, realistic photography, no text in image, 4:5 portrait"
        ),
    },
    {
        "filename": "B04-WMS系統.png",
        "prompt": (
            "Logistics manager at computer workstation monitoring inventory management system, "
            "multiple screens showing real-time data charts and order tracking, "
            "professional office area inside warehouse visible through glass, "
            "focused confident expression, modern tech setup, "
            "realistic photography, no text in image, 4:5 portrait"
        ),
    },
    {
        "filename": "B05-出貨整齊.png",
        "prompt": (
            "Rows of neatly labeled and sorted packages ready for shipment "
            "organized on conveyor belt and shelves in professional fulfillment center, "
            "clean systematic arrangement, courier bags and boxes perfectly sorted, "
            "bright clean warehouse, realistic photography, no text in image, 4:5 portrait"
        ),
    },
    {
        "filename": "B06-叉車作業.png",
        "prompt": (
            "Professional forklift operator moving pallets of stacked goods "
            "in a well-organized large warehouse, tall ceiling with industrial lighting, "
            "safety vest and helmet, efficient operations, organized storage in background, "
            "realistic photography, no text in image, 4:5 portrait"
        ),
    },
    {
        "filename": "B07-品質檢驗.png",
        "prompt": (
            "Quality control worker carefully inspecting and scanning packages "
            "before shipment in professional fulfillment center, "
            "clipboard checklist in hand, systematic organized process, "
            "shelves of completed orders in background, confident professional posture, "
            "realistic photography, no text in image, 4:5 portrait"
        ),
    },
]


def create_task(prompt):
    payload = {
        "model": "nano-banana-2",
        "input": {
            "prompt": prompt,
            "image_input": [],
            "aspect_ratio": "4:5",
            "resolution": "1K",
            "output_format": "png",
        }
    }
    r = requests.post("https://api.kie.ai/api/v1/jobs/createTask",
                      headers=KIE_H, json=payload, timeout=30)
    data = r.json()
    if data.get("code") != 200:
        raise Exception(f"建立任務失敗: {data.get('msg')}")
    return data["data"]["taskId"]


def poll_task(task_id, interval=8, timeout=300):
    elapsed = 0
    while elapsed < timeout:
        r = requests.get("https://api.kie.ai/api/v1/jobs/recordInfo",
                         headers=KIE_H, params={"taskId": task_id}, timeout=15)
        d = r.json().get("data", {})
        state = d.get("state")
        if state == "success":
            return json.loads(d["resultJson"])["resultUrls"][0]
        elif state == "fail":
            raise Exception(f"任務失敗: {d.get('failMsg')}")
        print(f"  [{elapsed}s] {state}...")
        time.sleep(interval)
        elapsed += interval
    raise TimeoutError("任務超時")


def download(url, path):
    r = requests.get(url, timeout=60)
    path.write_bytes(r.content)


def main():
    print(f"楚然：開始生成 {len(IMAGES)} 張電商 IG 素材\n{'='*50}")
    success, fail = 0, 0

    for i, img in enumerate(IMAGES, 1):
        fname = img["filename"]
        out_path = OUT_DIR / fname
        print(f"\n[{i:02d}/{len(IMAGES)}] {fname}")

        if out_path.exists():
            print(f"  已存在，跳過")
            success += 1
            continue

        try:
            task_id = create_task(img["prompt"])
            print(f"  task_id: {task_id}")
            url = poll_task(task_id)
            download(url, out_path)
            print(f"  OK 儲存至 {out_path}")
            success += 1
        except Exception as e:
            print(f"  FAIL 失敗: {e}")
            fail += 1

        # 避免 API rate limit
        if i < len(IMAGES):
            time.sleep(3)

    print(f"\n{'='*50}")
    print(f"完成：成功 {success} 張，失敗 {fail} 張")
    print(f"輸出資料夾：{OUT_DIR}")


if __name__ == "__main__":
    main()
