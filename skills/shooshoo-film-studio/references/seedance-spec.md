# Seedance 2.0 技術規範 / 音樂系統 / 發文文案系統

## Seedance 2.0 技術規範

**語言混寫：**
```
場景/情緒/細節 → 中文
光線/鏡頭/風格 → 英文
```

**鏡頭語法（8點）：**
```
主體 / 情緒 / 光學規格 / 運動 / 光線 / 風格 / 音效 / 連續性
```

**漂移防護三錨點：**
```
① @image 參考圖（每個 shot 都帶）
② 角色外觀文字重述（不省略，不說「同上」）
③ 色調鎖定句（每個 prompt 結尾）
```

**Negative prompt 原則：**
```
針對這個 shot 最怕的問題，3-5個詞：

劇情式人物必帶：
no perpetually open mouth,
no vacant staring expression,
no plastic skin texture,
no frozen body language,
no matching uniforms on different characters

角色固定識別特徵必帶（依角色定裝聖經，例如固定髮型/固定配件）：
依該角色定裝聖經中標註的「每次重述重點」反向寫成 negative prompt
（例如某角色固定低馬尾 → no hair down, low ponytail only）

卡通必帶：
no human body for forklift,
no realistic style, no CGI realistic
```

---

## 音樂系統（情境通用 cue 庫）

| 情境 | 音樂指令 |
|------|---------|
| 開場懸念 | low electronic drone, single cello note, 40Hz bass |
| 日常建立 | soft ambient piano, warm texture, no percussion |
| 試探對話 | sparse strings barely audible, tension building slowly |
| 危機逼近 | staccato strings accelerating, percussion enters 90BPM |
| 緊張對峙 | full orchestra tension, brass low notes, silence between beats |
| 情感時刻 | single piano note → harmony builds, no rhythm |
| 反轉揭曉 | complete silence → single impact note → music cuts |
| 情感種子（曖昧/心動萌生） | piano C note, unexpected, soft, 3秒後 fade |
| 結尾懸念 | cello sustain → cut to silence → one note echo |
| 卡通喜劇 | upbeat electronic, cartoon SFX layered, 120BPM |

> 劇情式模組的「情感主題音樂錨點」（哪個角色/哪條情感線配哪個識別音、怎麼隨集數遞增）依每次企劃自訂，詳見 `module-drama.md`。

---

## 發文文案系統

每支影片產完腳本後，同步輸出：

```
【平台】FB / IG / Threads / YouTube Shorts
【開頭鉤子】（對應影片第一鏡情緒）
【主文】（台灣電商賣家語氣，親切務實）
【CTA】加 LINE @911ycmhl
【Hashtag】#台南代出貨 #電商出貨外包 #咻咻打包
```
