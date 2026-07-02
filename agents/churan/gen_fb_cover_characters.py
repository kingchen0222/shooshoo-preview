"""
楚然 — FB封面 IP角色生圖
角色：咻咻 × 揀貨貓貓 × 咚咚膠帶（主角），福福叉車（背景）
輸出至: social-cards/FB封面/成品/
"""

import os, time, json, requests
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()
KIE_KEY = os.getenv("KIE_API_KEY")
KIE_H   = {"Authorization": f"Bearer {KIE_KEY}", "Content-Type": "application/json"}
OUT_DIR = Path("D:/咻咻打包CLAUDE/social-cards/FB封面/成品")
OUT_DIR.mkdir(parents=True, exist_ok=True)

PROMPT = (
    "3D clay toy characters, Pixar-adjacent style, soft subsurface scattering, "
    "rounded edges, warm saturated color palette. "

    "Three main characters working happily in a warehouse: "

    "Character 1 — ShooShoo: a cute chubby brown-yellow cardboard box character with legs, "
    "round dot eyes, rosy pink cheeks, holding a package ready to ship, "
    "speed motion lines around it showing energy and speed. "

    "Character 2 — Pick Cat: a chubby brown tabby cat character, "
    "pink blush cheeks, short stubby limbs, "
    "carrying and hugging a cardboard box, happy squinting eyes. "

    "Character 3 — Tape Tape: a cute beige tape roll character with tiny brown arms and legs, "
    "doing a peace sign V gesture with one hand, big happy smile, "
    "rolls of tape visible on its body. "

    "Background: a bright clean modern warehouse, "
    "chrome yellow toy forklift (smug raised-eyebrow expression) partially visible in background, "
    "organized shelving racks with cardboard boxes, warm orange industrial lighting, "
    "cozy and cheerful atmosphere. "

    "Group composition: all three characters standing together facing viewer, "
    "center frame, slight upward angle, "
    "full body visible, no text in image, square 1:1 format."
)

def create_task(prompt, aspect_ratio="1:1"):
    payload = {
        "model": "nano-banana-2",
        "input": {
            "prompt": prompt,
            "image_input": [],
            "aspect_ratio": aspect_ratio,
            "resolution": "1K",
            "output_format": "png",
        }
    }
    r = requests.post("https://api.kie.ai/api/v1/jobs/createTask",
                      headers=KIE_H, json=payload, timeout=30)
    data = r.json()
    if data.get("code") != 200:
        raise Exception(f"建立任務失敗: {data.get('msg')} | {data}")
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
        print(f"  [{elapsed}s] 生成中 ({state})...")
        time.sleep(interval)
        elapsed += interval
    raise TimeoutError("任務超時")


def download(url, path):
    r = requests.get(url, timeout=60)
    path.write_bytes(r.content)


if __name__ == "__main__":
    out_path = OUT_DIR / "ip-characters.png"
    print("楚然：開始生成 FB封面 IP角色圖")
    print(f"輸出：{out_path}\n")

    task_id = create_task(PROMPT)
    print(f"任務建立：{task_id}")
    url = poll_task(task_id)
    download(url, out_path)
    print(f"\nOK 儲存至 {out_path}")
