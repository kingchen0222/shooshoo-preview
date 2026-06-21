---
name: shooshoo-film-studio
description: 咻咻打包 AI 影片腳本生成系統。生成三種題材的完整 Seedance 2.0 製作腳本，含逐鏡 prompt、角色定裝聖經、場景參考圖、@image 標記、聲音錨點、IP道具標注、刺猬星球級真人感技術。劇情式為動態企劃流程，非固定劇本。觸發關鍵字：@影片、影片腳本、三方倉介紹、劇情式、卡通IP、EP腳本、咻咻影片、Seedance腳本。
metadata:
  author: King / 咻咻打包
  version: 4.0.0
---

# 咻咻打包 影片腳本生成系統 v4.0

## 觸發指令

```
@影片 三方倉 [主題]        → 寫實風三方倉介紹腳本
@影片 劇情 企劃 [主題/方向]  → 啟動新劇集企劃（角色/世界觀/大綱）
@影片 劇情 EP[集數]        → 製作指定集數 Shot 腳本
@影片 卡通 [主題]          → 卡通IP超展開腳本
```

---

## 模組總覽（依指令載入對應 reference）

| 模組 / 元件 | 何時讀取 | 檔案 |
|---|---|---|
| 三方倉介紹 | `@影片 三方倉` | `references/module-warehouse-intro.md` |
| 劇情式（企劃＋逐集製作） | `@影片 劇情` | `references/module-drama.md` |
| 卡通 IP | `@影片 卡通` | `references/module-cartoon.md` |
| 角色三視圖＋角色定裝聖經模板 | 任一模組需要真人角色時 | `references/character-bible-template.md` |
| 真人感技術句庫 | 任一模組的 shot 含真人角色時 | `references/realism-techniques.md` |
| 場景參考圖庫（倉庫六大場景） | 任一模組需要場景參考圖時 | `references/scene-library.md` |
| Seedance技術規範／音樂庫／發文文案 | 出 Shot 腳本或發文文案時 | `references/seedance-spec.md` |

> ⚠️ 劇情式模組不內建固定劇本與固定角色，每次企劃由使用者輸入決定。角色定裝聖經與場景庫為通用模板，套用到任何題材。

---

## 全域製作規格

```
工具：Seedance 2.0
分鏡秒數：只能是 5秒 / 10秒 / 15秒
色調鎖定句（每個 prompt 結尾必加）：
  Maintain consistent filmic color grade,
  teal-amber LUT, 24fps cinematic.
角色描述：每個 prompt 必帶角色外觀錨點
聲音：每個有對白的 shot 必帶聲音錨點
對白原則：一個 shot 最多一輪對話，長對話拆成多個 shot
```

---

## 三層製作流程（圖轉片，不純文字生成）

```
Layer 1｜GPT Image 2 先生成靜態參考圖
  → 每個主要角色生成「電影感肖像圖」
  → 要求：realistic, cinematic lighting,
           8K detail, film photography style
  → 這一步決定臉是否真實

Layer 2｜@image 帶入 Seedance（圖轉片）
  → Seedance 只負責讓圖「動起來」
  → 文字 prompt 補充：鏡頭、光線、動作、情緒
  → 不讓 Seedance 自己發明臉

Layer 3｜剪映/CapCut 後製
  → 多個 clip 串接
  → 字幕、音效、音樂後製加入
```

---

## 輸出格式（每個 Shot 固定格式）

```
### SHOT [編號]｜[秒數]｜[場景名稱]

地點：
@image：[場景代號]

出場角色：[角色名稱]
@image：[角色參考圖檔名]

IP道具：
@image_[IP名稱] → [出現位置說明]
（無則寫「無」）

聲音錨點：（有對白或聲音必填，無對白寫「無對白」）
[角色]聲音錨點：[完整聲音描述]
台詞：「[台詞內容]」[說話方式補充]

[Seedance prompt 區塊]
```

⚠️ 聲音錨點規則：
- 有對白的 Shot：必須帶該角色完整聲音錨點 + 當集台詞內容 + 說話方式
- 多角色對白：每個角色分開寫聲音錨點
- 不露臉/處理過聲音的角色：必帶聲音處理濾鏡描述（見 `character-bible-template.md` 特殊角色範本）
- 無對白 Shot：寫「無對白」，不可省略此欄位

---

## 跨模組規則

```
三方倉：有真人才出角色圖；有重複場景才出場景圖
劇情式：每次新角色/新場景皆需建立角色定裝聖經與場景庫，詳細流程見 module-drama.md
卡通：跳過所有前置，直接出腳本
```

【快速模式】King 說「直接出腳本」→ 跳過等待 King 確認角色圖/場景圖，@image 標「待補」直接繼續出 Shot 腳本。
