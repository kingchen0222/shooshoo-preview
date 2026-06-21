# 場景參考圖系統

> 適用範圍：所有模組。場景皆為咻咻打包真實倉庫空間，可重複用於三方倉介紹、劇情式、卡通道具置入。

## 規則

劇情系列每集開始前，先列出本集所有場景 → 輸出場景參考圖 prompt → 等 King 回「場景圖好了」才開始 Shot 腳本。

## 場景參考圖輸出格式

每個場景出 **3 張角度**：
- **Wide（全景）**：建立空間感
- **Mid（中景）**：人物站立的構圖環境
- **Detail（細節）**：場景內關鍵道具/細節特寫

```
### @[場景代號]（場景中文名）

**Wide（wide.png）**
[prompt]

**Mid（mid.png）**
[prompt]

**Detail（detail.png）**
[prompt]

⚠️ 生成後命名：[場景代號]_wide / _mid / _detail.png
```

---

## 固定場景參考圖 Prompt 庫

**@倉庫主區（倉庫主作業區）**

Wide：
```
Modern Taiwan 3PL warehouse interior, daytime operation,
high ceiling 8 meters, industrial LED grid overhead warm white light,
concrete floor with worn yellow safety markings and aisle arrows,
metal shelving units 3 meters tall filled with brown cardboard boxes,
zone labels on hanging signs: 7-11區 / 全家區 / 蝦皮區 / MOMO區,
咻咻打包 orange logo on far wall signage large,
forklift path markings on floor, scattered tape dispensers and scanners,
NO people in frame — empty establishing shot,
wide angle 24mm, slight low angle looking across floor,
warm #FFE4B5 dominant color grade, industrial realism,
architectural photography style, 8K detail,
Maintain consistent filmic color grade, teal-amber LUT, 24fps cinematic.
```

Mid：
```
Taiwan 3PL warehouse interior, mid-shot framing,
two shelving units flanking empty aisle center frame,
cardboard boxes stacked varying heights creating natural depth,
warm overhead LED light with slight shadow under shelves,
concrete floor aisle stretching to background,
zone label 蝦皮區 visible on shelf end cap right side,
咻咻打包 small logo sticker on shelf post,
space for human subject to stand center frame,
35mm focal length perspective, natural depth of field,
warm #FFD59E color grade, slight atmospheric haze from dust,
8K detail, cinematic photography.
```

Detail：
```
Taiwan warehouse close-up details,
thermal label printer on metal shelf corner, stack of shipping labels,
barcode scanner holster hanging from shelf post,
brown tape dispenser with half-used roll,
handwritten zone marker on box corner,
warm side light from overhead LED,
macro detail shot, shallow depth of field,
warm amber tones, 8K detail, film texture.
```

---

**@辦公室（倉庫辦公室）**

Wide：
```
Small Taiwan warehouse office interior,
glass partition wall separating from warehouse floor — warehouse visible through glass,
2-3 desks with monitors, office chairs,
fluorescent ceiling light mixed with warm desk lamps,
whiteboard on wall with delivery schedule written in marker,
small 咻咻打包 framed logo on wall,
行政喵喵 small figurine on desk corner,
window blinds half open showing warehouse exterior,
NO people, establishing wide shot,
35mm, slightly cluttered but functional space,
warm #FFD59E interior, cooler blue tone from monitor screens,
architectural photography, 8K detail,
Maintain consistent filmic color grade, teal-amber LUT, 24fps cinematic.
```

Mid：
```
Taiwan warehouse office, desk area mid shot,
single desk with open laptop showing spreadsheet,
stack of shipping manifests paper, red pen, coffee cup half empty,
desk lamp warm light from left,
glass partition behind showing blurred warehouse,
empty chair pulled slightly out — someone just left,
35mm natural perspective,
warm desk light vs cool monitor glow contrast,
8K cinematic detail.
```

Detail：
```
Warehouse office desk detail close-up,
shipping manifest paper with printed delivery numbers,
red pen marking rows, coffee ring stain on corner of paper,
small sticky note with handwritten numbers,
keyboard edge and mouse partially visible,
shallow depth of field, sharp focus on paper numbers,
warm side lamp light, 8K film texture detail.
```

---

**@停車場（倉庫外停車場·夜）**

Wide：
```
Taiwan suburban warehouse parking lot, night scene,
single sodium vapor streetlamp center frame casting #FF8C00 cone of light,
wet asphalt reflecting lamp light in puddle,
warehouse building background, warm window light visible far right,
chain link fence left side, empty parking spaces marked,
no people, no moving vehicles,
wide 24mm, low angle showing sky and lamp post,
cold #4A6FA5 ambient night tone + warm #FF8C00 lamp accent,
noir cinematic style, 8K detail,
Maintain consistent filmic color grade, teal-amber LUT, 24fps cinematic.
```

Mid：
```
Taiwan parking lot night, mid establishing shot,
lamp post center-right, light cone on asphalt,
warehouse loading dock door background slightly ajar, warm light inside,
empty space center frame — person could stand here,
slight mist in air catching lamp light,
35mm, slightly low angle,
cold blue ambient + warm sodium lamp contrast,
8K cinematic noir detail.
```

Detail：
```
Parking lot night detail,
wet asphalt close-up showing lamp reflection distorted in puddle,
painted parking line partially visible,
cigarette butt near drain — someone waited here,
cold blue light from sky, warm orange from lamp edge,
macro, shallow depth of field, film grain texture.
```

---

**@廁所（倉庫廁所）**

Wide：
```
Taiwan industrial warehouse restroom interior,
white ceramic tile walls slightly worn, fluorescent overhead light harsh white,
2 sink basins with mirror above full width,
toilet stall doors left side — one slightly ajar,
mop bucket in corner, paper towel dispenser on wall,
cold flat institutional lighting — no warmth,
wide 24mm, slightly high angle,
cold #E8F4F8 desaturated color grade,
realistic worn institutional space — not clean not dirty, lived-in,
8K detail, cinematic photography,
Maintain consistent filmic color grade, teal-amber LUT, 24fps cinematic.
```

Mid：
```
Warehouse restroom mirror and sink area,
full-width mirror slightly foggy at edges,
2 ceramic sinks, soap dispenser, paper towels,
fluorescent light above mirror creating harsh downlight,
person-height framing — space to show reflection in mirror,
cold institutional white with slight yellow fluorescent cast,
35mm natural perspective, 8K detail.
```

Detail：
```
Restroom detail close-up,
mirror surface with slight water spots, reflection of fluorescent tube light,
sink drain with small water ring,
tap handle slightly dripping — one drop hanging,
cold white light, clinical feel,
shallow depth of field, macro detail, film grain.
```

---

**@走廊（倉庫內部走廊·過渡空間）**

Wide：
```
Taiwan warehouse interior corridor,
narrow passage between two shelving rows, 1.5 meters wide,
high shelves both sides creating tunnel perspective,
single LED strip light on ceiling casting top-down light,
concrete floor with center worn path,
far end: T-junction with yellow safety stripe visible,
no people, deep perspective focal pull,
24mm wide creating strong vanishing point,
warm top light with deep shadows on shelf sides,
cinematic corridor shot, 8K detail,
Maintain consistent filmic color grade, teal-amber LUT, 24fps cinematic.
```

Mid：
```
Warehouse corridor mid shot,
shelves both sides at 45-degree angle to camera,
cardboard box edges creating repeating pattern into background,
single overhead LED casting top-down pool of light,
shadow zones between lights,
35mm, natural depth of field,
warm center light, darker edges, tension framing.
```

Detail：
```
Warehouse corridor detail,
shelf post corner with worn paint and scrape marks,
cardboard box edge with barcode label partially peeled,
concrete floor crack running along base of shelf,
harsh top-down LED shadow under shelf,
micro detail, shallow depth of field, film texture.
```

---

**@貨架區（特定貨架·情節道具區）**

Wide：
```
Taiwan warehouse specific shelf section, daytime,
3-meter metal shelving unit, fully stocked with brown boxes,
each box has printed label — sizes vary,
wooden pallet on floor below bottom shelf,
aisle space in front 1.5 meters,
overhead LED warm light,
one box on second shelf slightly misaligned — sticking out 5cm,
wide shot showing full shelf unit front,
warm #FFE4B5 light, 8K detail, cinematic photography.
```

Mid / Detail：同規格，Mid 拍單排貨架中段，Detail 拍那個「歪掉的箱子」特寫。

---

## 場景 @ 代號速查表（Shot 標注用）

| 代號 | 場景 | 色調 | 敘事用途 |
|------|------|------|---------|
| @倉庫主區 | 主作業區 | warm #FFE4B5 | 日常作業、品牌介紹主場景 |
| @辦公室 | 倉庫辦公室 | warm+cool monitor | 文書/對話/查資料場景 |
| @停車場 | 戶外夜間 | cold #4A6FA5 + #FF8C00 | 夜戲、緊張對峙、告別場景 |
| @廁所 | 倉庫廁所 | cold institutional | 獨處、整理情緒場景 |
| @走廊 | 貨架走廊 | warm top-down | 過渡鏡、跟拍鏡 |
| @貨架區 | 特定道具貨架 | warm #FFE4B5 | 道具/線索特寫場景 |

> 「敘事用途」為建議方向，依當次企劃實際劇情調整，非固定指派。

---

## 場景色調系統

```
@倉庫主區 白天：warm #FFE4B5 dominant
@辦公室 日常：warm #FFD59E + cool monitor blue accent
@走廊 過渡：warm top-down + deep shelf shadows
@廁所 緊張：cold #E8F4F8 institutional flat
@停車場 夜間：cold #4A6FA5 ambient + warm #FF8C00 lamp
情緒轉折鏡：half warm half cold split
```
