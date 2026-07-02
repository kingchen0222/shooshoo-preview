"""
Skill 稽核腳本 — 機械化驗證，不靠記憶。

用途：
1. 掃描本機實際安裝的所有 Skill（plugin + skills-dir）
2. 掃描 agents/*.md 裡「## Skills」區塊引用的 Skill 名稱
3. 比對兩邊，找出：
   (a) 同事檔案裡寫了、但本機沒真的裝的（= 假 Skill，今天發生過的問題）
   (b) 本機裝了、但沒有任何同事認領的（= 裝了沒人學）

用法：python agents/audit_skills.py
建議：每次 `claude plugin install` 或改 agents/*.md 的 Skills 區塊後都跑一次。
"""
import json
import re
import subprocess
import sys
from pathlib import Path

if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8")

REPO_ROOT = Path(__file__).resolve().parent.parent
AGENTS_DIR = REPO_ROOT / "agents"

# 已知不是「假 Skill」但腳本會誤判的例外：
# - Claude Code 內建 bundled skill（不在檔案系統的 .claude/skills 或 plugins 裡，是應用程式內建的）
# - 套件包名稱本身（裡面有子技能用 "套件名:子技能" 呼叫，同事檔案只寫了套件名）
KNOWN_NOT_FAKE = {
    "code-review", "verify", "simplify", "review", "security-review", "init", "run",
    "claude-wordpress-skills", "elementor-claude-skill", "claude-ads",
}


def get_real_installed_skills() -> set[str]:
    real = set()

    # 1) 透過 claude plugin list --json 找每個已裝 plugin 底下的 SKILL.md
    try:
        result = subprocess.run(
            ["claude", "plugin", "list", "--json"],
            capture_output=True, text=True, timeout=30, shell=True,
        )
        plugins = json.loads(result.stdout)
        for p in plugins:
            install_path = Path(p.get("installPath", ""))
            if install_path.exists():
                for skill_md in install_path.rglob("SKILL.md"):
                    real.add(skill_md.parent.name)
    except Exception as e:
        print(f"[警告] claude plugin list 執行失敗：{e}")

    # 2) 直接掃 ~/.claude/skills/（包含直接複製進去的，可能不在 plugin list 裡）
    skills_dir = Path.home() / ".claude" / "skills"
    if skills_dir.exists():
        for item in skills_dir.iterdir():
            if not item.is_dir():
                continue
            if (item / "SKILL.md").exists():
                real.add(item.name)
            else:
                for skill_md in item.rglob("SKILL.md"):
                    real.add(skill_md.parent.name)

    return real


def get_referenced_skills() -> dict[str, list[str]]:
    """回傳 {skill_name: [出現的檔案清單]}，只抓 ## Skills / ## 認領技能 區塊內的 backtick 名稱"""
    referenced: dict[str, list[str]] = {}
    section_re = re.compile(
        r"^##\s+(Skills|認領技能)", re.MULTILINE
    )
    token_re = re.compile(r"`/?([a-z][a-z0-9-]{2,})`")

    for md_file in AGENTS_DIR.rglob("*.md"):
        if md_file.name in ("README.md", "_FRAMEWORK.md", "audit_skills.py"):
            continue
        text = md_file.read_text(encoding="utf-8")
        matches = list(section_re.finditer(text))
        for i, m in enumerate(matches):
            start = m.end()
            end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
            # 遇到下一個 "---\n\n## " 大區塊就停（避免吃到後面不相干的區塊）
            section_text = text[start:end]
            next_h2 = re.search(r"\n## ", section_text)
            if next_h2:
                section_text = section_text[: next_h2.start()]
            for tok in token_re.finditer(section_text):
                name = tok.group(1)
                referenced.setdefault(name, []).append(str(md_file.relative_to(REPO_ROOT)))

    return referenced


def main():
    real = get_real_installed_skills()
    referenced = get_referenced_skills()

    fake = sorted(set(referenced) - real - KNOWN_NOT_FAKE)
    unclaimed = sorted(real - set(referenced))

    print(f"本機實際安裝 Skill 數：{len(real)}")
    print(f"同事檔案引用 Skill 數（去重）：{len(referenced)}")
    print()

    print("=" * 60)
    print(f"[FAKE] 假 Skill（同事檔案寫了，本機沒真的裝，共 {len(fake)} 個）")
    print("=" * 60)
    if not fake:
        print("  無，全部乾淨。")
    for name in fake:
        print(f"  - {name}")
        for f in referenced[name]:
            print(f"      引用於：{f}")

    print()
    print("=" * 60)
    print(f"[UNCLAIMED] 沒人認領的已裝 Skill（共 {len(unclaimed)} 個，非全部需要處理，僅供檢視）")
    print("=" * 60)
    if not unclaimed:
        print("  無，全部都有人認領。")
    for name in sorted(unclaimed):
        print(f"  - {name}")


if __name__ == "__main__":
    main()
