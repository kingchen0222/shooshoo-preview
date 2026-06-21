# 真人感技術系統（刺猬星球級）

> 適用範圍：所有模組（劇情式、三方倉介紹、卡通除外）。每個有真人角色的 Shot 生成前必讀。

## 根本原理：他們做對了三件事

```
普通 AI 影片：純文字生成，臉是 AI 自己發揮，
              嘴巴空洞半開，眼神虛飄，身體像木頭

刺猬星球級別：
  ① 臉有「皮膚感」— 毛孔細節，非塑膠感
  ② 眼神「有去處」— 看具體目標，非空視
  ③ 肢體「有聯動」— 全身動態鏈，非局部動
```

---

## 真人感必加句庫（每個有人物的 shot 都必須選用）

### A｜皮膚質感（對抗塑膠臉）

```
realistic skin texture with visible pores,
subsurface scattering on skin —
light penetrates slightly at cheeks and ears,
micro skin detail: fine lines, natural skin tone variation,
NOT smooth plastic or porcelain skin,
skin has lived-in quality
```

### B｜眼神方向（對抗虛飄眼）

```
根據場景選一個具體目標：

對著另一個角色說話：
gaze directed at other character's eyes,
focused eye contact at 1.5 meter distance

思考/回憶：
gaze directed slightly upward-left,
unfocused soft gaze at middle distance,
eyes not looking at camera or any person

看文件/手機：
gaze downward at 30-degree angle,
eyes focused on object in hands,
small eye movement as if reading

警覺掃視：
rapid gaze shift: left → right → settle forward,
eyes sharp focus, pupils slightly contracted

愛情/心動時：
gaze holds on target 0.5 second longer than normal,
eyes soften at corners,
pupils dilate slightly
```

### C｜肢體聯動（對抗木頭身）

```
full body kinetic chain movement:
head turn initiates shoulder follow,
breath visible as chest rises and falls,
weight distribution shifts naturally when moving,
micro-movements throughout:
  subtle finger adjustments,
  slight postural sway,
  natural asymmetry in stance
NOT frozen or posed body language
```

### D｜嘴巴狀態（對抗空洞半開）

```
說話時：
mouth opens naturally for speech,
lips form words with realistic muscle movement,
jaw movement matches speech rhythm

不說話時：
lips relaxed and closed,
mouth corners in neutral position,
NO perpetually slightly open mouth,
jaw naturally resting, not clenched

吃東西時：
mouth opens only when taking food,
chewing with closed mouth,
realistic swallow motion
```

### E｜微表情系統（讓臉「會說話」）

```
情緒不用抽象詞——用身體反應描述：

「緊張」：
jaw tightened 2mm, shoulders 3mm higher,
brow slightly furrowed, breathing rate increased,
micro-tension visible at eye corners

「心動（隱藏）」：
0.3 second pause in current action,
gaze holds 0.5 seconds longer,
slight lip press before returning to neutral

「懷疑」：
one brow rises 3mm, head tilts 8 degrees,
eyes narrow slightly, gaze sharpens

「疲憊」：
eyes 70% open, shoulders dropped 5mm,
movements 20% slower,
occasional blink slightly slower

「決心」：
jaw sets, gaze forward and level,
stillness before action — held breath then release

「假笑（掩飾）」：
mouth corners rise but eye corners do NOT crinkle,
no cheek lift, smile doesn't reach upper face,
controlled jaw
```

---

## 反 AI 感生成前檢查清單

```
每個 shot 生成前確認：
□ @image 有帶正確參考圖
□ 皮膚質感句有寫（A類）
□ 眼神方向有指定具體目標（B類）
□ 肢體聯動有描述（C類）
□ 嘴巴狀態有指定（D類）
□ 情緒用身體反應描述，不用抽象詞（E類）
□ 多人場景服裝有明確區分
□ 角色識別特徵（髮型/配件/疤痕等）有依角色定裝聖經重述
□ negative prompt 針對這個 shot 最怕的問題
□ 色調鎖定句在結尾
```

---

## 光影技術（刺猬星球「雕琢光影」技法）

```
人物臉部光線（最影響質感）：
single motivated light source —
name the source: window / desk lamp / phone screen / street lamp
light direction: from [angle] creating [shadow pattern]
fill ratio: 2:1 (dramatic) / 4:1 (cinematic) / 8:1 (noir)

讓光線說故事：
溫暖燈光在臉上 = 安全感/家
冷藍光在臉上 = 孤獨/數位/任務
光從下方 = 威脅/不安
背光輪廓 = 神秘/未知身份

皮膚光線反應：
subsurface scattering at ear edges and nose tip,
warm bounce light from below fills shadow side,
catch light in both eyes = 2 small white highlights
```
