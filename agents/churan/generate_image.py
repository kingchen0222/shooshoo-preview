import os
import time
import json
import requests
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("KIE_API_KEY")
BASE_URL = "https://api.kie.ai"
HEADERS = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

# 模型選擇規則：
# FB / Threads → IMAGE2      (6 pts, 1K)
# IG           → BANANA2     (8 pts, 1K)
# 印刷          → BANANA PRO  (僅特殊需求)
PLATFORM_MODEL = {
    "fb":      "gpt-image-2-image-to-image",
    "threads": "gpt-image-2-image-to-image",
    "ig":      "nano-banana-2",
    "print":   "nano-banana-pro",
}

PLATFORM_ASPECT = {
    "fb":      "1:1",
    "threads": "1:1",
    "ig":      "4:5",
    "print":   "1:1",
}

# 各模型支援的參數不同
GPT_IMAGE2_MODEL = "gpt-image-2-image-to-image"


def build_input(model, prompt, aspect_ratio, resolution, output_format, image_input):
    if model == GPT_IMAGE2_MODEL:
        return {
            "prompt": prompt,
            "input_urls": image_input or [],
            "aspect_ratio": aspect_ratio,
        }
    else:
        return {
            "prompt": prompt,
            "image_input": image_input or [],
            "aspect_ratio": aspect_ratio,
            "resolution": resolution,
            "output_format": output_format,
        }


def create_task(prompt, model, aspect_ratio, resolution="1K", output_format="png", image_input=None):
    payload = {
        "model": model,
        "input": build_input(model, prompt, aspect_ratio, resolution, output_format, image_input)
    }
    res = requests.post(f"{BASE_URL}/api/v1/jobs/createTask", headers=HEADERS, json=payload)
    data = res.json()
    if data.get("code") != 200:
        raise Exception(f"建立任務失敗: {data.get('msg')}")
    return data["data"]["taskId"]


def poll_task(task_id, interval=5, timeout=300):
    elapsed = 0
    while elapsed < timeout:
        res = requests.get(f"{BASE_URL}/api/v1/jobs/recordInfo", headers=HEADERS, params={"taskId": task_id})
        data = res.json().get("data", {})
        state = data.get("state")

        if state == "success":
            result = json.loads(data["resultJson"])
            return result["resultUrls"]
        elif state == "fail":
            raise Exception(f"任務失敗: {data.get('failMsg')}")

        print(f"等待中... ({elapsed}s)")
        time.sleep(interval)
        elapsed += interval

    raise TimeoutError("任務超時")


def generate(prompt, platform="ig", resolution="1K", output_format="png", image_input=None,
             aspect_ratio=None, model=None):
    """
    platform: 'ig' | 'fb' | 'threads' | 'print'
    楚然會根據平台自動選擇模型與比例，預設解析度 1K。
    """
    platform = platform.lower()
    selected_model = model or PLATFORM_MODEL.get(platform, "nano-banana-2")
    selected_ratio = aspect_ratio or PLATFORM_ASPECT.get(platform, "1:1")

    print(f"楚然：生圖中\n平台: {platform} | 模型: {selected_model} | 比例: {selected_ratio}")

    task_id = create_task(prompt, selected_model, selected_ratio, resolution, output_format, image_input)
    print(f"任務 ID: {task_id}")

    urls = poll_task(task_id)
    print("完成！圖片網址：")
    for url in urls:
        print(f"  {url}")
    return urls


if __name__ == "__main__":
    # 測試：IG 貼文用 BANANA 2
    generate(
        prompt="咻咻打包倉庫日常，可愛貓咪角色揀貨打包，台灣電商風格，溫暖活潑色調",
        platform="ig"
    )
