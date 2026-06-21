# 角色設定系統（三視圖 + 角色定裝聖經模板）

> 適用範圍：劇情式模組、三方倉介紹（如有真人入鏡）。
> 本檔為**空白模板**，依當次企劃的角色填入，不可預設特定角色姓名。

---

## STEP 0｜角色三視圖 Prompt（腳本開始前必輸出）

**規則：腳本生成前，先列出本集會出現的所有真人角色的三視圖 prompt。**
讓 King 先去 GPT Image 2 生成靜態參考圖，確認臉對了再做影片。

### 輸出格式

```
## 🎭 本集登場角色 — GPT Image 2 三視圖 Prompt

### [角色名稱]

**正面（Front View）**
[prompt]

**側面（Side View — 右側）**
[prompt]

**半側面（3/4 View）**
[prompt]

⚠️ 生成後請命名為：[角色名_front / side / 34view].png
完成後回報「圖好了」，我再開始出 Shot 腳本。
```

### 三視圖 Prompt 規範

每張圖 prompt 結構：
```
[角色外觀完整描述],
[服裝完整描述],
[視角描述],
portrait photography style,
cinematic lighting, single motivated key light from [方向],
shallow depth of field, bokeh background,
8K detail, film photography texture,
realistic skin texture with visible pores,
subsurface scattering on skin,
catch light in both eyes,
NOT illustration, NOT cartoon, NOT CGI,
NOT plastic skin, NOT smooth porcelain.
```

視角描述：
- 正面：`front-facing portrait, subject looks directly at camera, centered frame`
- 側面：`strict profile view from right side, subject faces 90 degrees right, full head visible`
- 半側面：`3/4 view, subject faces slight right, classic portrait angle`

---

## 角色定裝聖經模板

> ⚠️ 主角描述為電影明星等級高規格，每個 Shot prompt 必須完整重述，不可省略或說「同上」。
> 依下列欄位填入每個角色的設定，填好後此表即為本次企劃的「角色定裝聖經」。

```
**[角色名稱]｜[身份]**

@image_[角色名]參考圖

【外觀錨點 — 每個 Shot 必帶完整版】
[年齡/族裔/身形/身高],
[臉型/五官/膚色],
[髮型髮色 — 若有固定識別特徵（如：必為低馬尾、必有疤痕）需明確標註,
 每次重述不可省略],
[配件 — 若有固定識別配件（如：右耳單耳環）需明確標註],
face reference: [可選：參考臉型描述，避免使用真實公開人物姓名].

服裝（[情境名稱]）：
[完整服裝描述，含顏色/版型/品牌徽章標註位置]

⚠️ 每次重述重點：
[列出 2-3 個此角色最容易被 AI 漂移掉的識別特徵]

聲音錨點：
Voice: [性別/年齡/語言腔調],
[音域/語速/說話習慣描述]
```

**多角色場景規則：**
- 服裝必須明確區分，避免撞色或撞款
- 每個角色至少 2 個「識別特徵」需在每個 shot 重述（髮型、配件、疤痕、徽章位置等）
- 非主要角色（如：一次性出現的聯絡人/路人）可簡化只寫聲音錨點 + 外觀一句話

**特殊角色（不露臉/聲音處理）：**
```
聲音錨點：
Voice: gender ambiguous, heavy digital processing filter,
pitch shifted -15%, cold transactional, no emotion,
reads lines like a list, not a conversation,
no breath sounds, no hesitation.
```
（此範本可套用於「神秘人/未揭露身份角色」，依劇情需要調整語氣描述）
