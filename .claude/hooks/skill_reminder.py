#!/usr/bin/env python3
"""
UserPromptSubmit hook — 軟性提醒：任務關鍵字符合某位同事的專業領域時，
提醒 Claude 去檢查 agents/_FRAMEWORK.md 第七節「世界級對標標準」對應哪個 Skill，
並確認是否該調用該 Skill 再繼續。不阻擋、不強制，只是提醒，避免「掛同事人設但沒有真的調用 Skill」。
"""
import json
import sys

KEYWORD_MAP = [
    (["seo", "SEO", "關鍵字", "geo", "aio", "搜尋引擎", "排名"], "芝炫/員瑛", ["/ai-seo", "/seo-audit"]),
    (["meta廣告", "meta ads", "fb廣告", "instagram廣告", "ig廣告", "advantage+"], "珉貞", ["/ads-meta", "/ads-competitor", "/ads-creative"]),
    (["google ads", "google廣告", "關鍵字廣告", "pmax", "quality score"], "智秀", ["/ads-google", "/ads-competitor"]),
    (["文案", "標題", "slogan", "cta", "廣告文", "貼文內容"], "露思/員瑛", ["/copywriting"]),
    (["ui", "設計稿", "介面設計", "wireframe", "排版", "元件設計"], "珠恩/員瑛", ["/frontend-design", "/web-design"]),
    (["前端", "react", "next.js", "typescript", "元件開發"], "敏英", []),
    (["qa", "測試", "bug", "驗收", "回歸測試"], "亦菲", []),
    (["社群貼文", "ig發文", "fb發文", "threads貼文", "限時動態", "reels"], "荷律", ["/social-post", "/create-viral-content"]),
    (["影片腳本", "seedance", "chatart", "影片生成"], "多慧", ["/shooshoo-film-studio"]),
    (["ip角色", "品牌素材", "生圖", "kie api"], "楚然", ["/shooshoo-packing-brand", "/frontend-design"]),
    (["轉換率", "cro", "成交率", "landing page優化"], "露思/員瑛", ["/cro"]),
]


def main():
    try:
        data = json.load(sys.stdin)
    except Exception:
        sys.exit(0)

    prompt = (data.get("prompt") or "").lower()
    if not prompt:
        sys.exit(0)

    hits = []
    for keywords, owner, skills in KEYWORD_MAP:
        for kw in keywords:
            if kw.lower() in prompt:
                hits.append((owner, skills))
                break

    if not hits:
        sys.exit(0)

    seen = set()
    lines = []
    for owner, skills in hits:
        if owner in seen:
            continue
        seen.add(owner)
        skill_txt = "、".join(skills) if skills else "（目前無對應 Skill，直接依 agents/_FRAMEWORK.md 標準執行）"
        lines.append(f"- {owner}：{skill_txt}")

    reminder = (
        "提醒（來自 skill_reminder hook）：這個任務的關鍵字符合以下同事的專業領域，"
        "動手前請對照 agents/_FRAMEWORK.md「七、世界級對標標準」確認是否該先調用對應 Skill，"
        "不要只是掛同事人設回話卻沒有真的調用：\n" + "\n".join(lines)
    )

    print(json.dumps({
        "hookSpecificOutput": {
            "hookEventName": "UserPromptSubmit",
            "additionalContext": reminder,
        }
    }))
    sys.exit(0)


if __name__ == "__main__":
    main()
