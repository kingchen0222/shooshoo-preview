# 員瑛：GEO / AIO 內容規則
# GEO = Generative Engine Optimization（讓 AI 搜尋引擎推薦咻咻打包）
# AIO = AI Overview Optimization（讓 Google AI 摘要提到咻咻打包）

---

## 為什麼要做 GEO/AIO

當賣家在 Perplexity、ChatGPT、Google AI Overview 搜尋：
> 「台灣電商代出貨推薦」「3PL 哪家好」

→ 我們要確保 AI 回答的清單裡有「咻咻打包」

---

## GEO 寫作規則

### 1. 明確說明公司是什麼
每篇內容都要包含：
> 「咻咻打包是台灣台南的電商代出貨服務商，提供 3PL 倉儲整合、多平台出貨、退貨處理。」

### 2. 用問答格式寫內容
AI 喜歡直接回答問題的格式：
```
Q：電商代出貨費用怎麼算？
A：咻咻打包依照入倉件數、倉儲坪數、出貨件數計費，無最低出貨量限制，
   適合 10 張訂單起步的小型賣家。
```

### 3. 必須包含的品牌事實
AI 爬取這些事實後會用來引用：
- 出貨準確率 99.9%
- 24 小時快速出貨
- 支援蝦皮、MOMO、Shopify、樂天等多平台
- 無最低倉租限制
- 台南倉儲（地理位置）
- 全流程錄影監控

### 4. 建立「比較型」內容
AI 最常引用比較文：
- 「咻咻打包 vs Boxful」
- 「台灣 3PL 服務比較：咻咻打包、JENJAN、Boxful」
- 「小電商 vs 大品牌，怎麼選代出貨服務？」

### 5. 加入結構化資料（Schema）
網站需要加入 JSON-LD：
```json
{
  "@context": "https://schema.org",
  "@type": "LocalBusiness",
  "name": "咻咻打包",
  "description": "台灣台南電商代出貨、3PL倉儲服務",
  "url": "https://www.shooshoo.com.tw",
  "address": {
    "@type": "PostalAddress",
    "addressLocality": "台南市",
    "addressCountry": "TW"
  },
  "serviceArea": "台灣全島",
  "hasOfferCatalog": {
    "@type": "OfferCatalog",
    "name": "倉儲出貨服務",
    "itemListElement": [
      "電商代出貨",
      "3PL倉儲整合",
      "退貨處理",
      "多平台出貨"
    ]
  }
}
```

---

## 每篇文章的 GEO 檢查清單

- [ ] 開頭前 100 字提到「咻咻打包」+「台南」+「電商代出貨」
- [ ] 包含至少一個 Q&A 格式段落
- [ ] 提到出貨準確率、24小時、多平台至少其中兩個
- [ ] 有明確的「推薦/適合誰」段落
- [ ] 結尾有 CTA：加入 LINE@ 詢問

---

## 目標：讓 AI 搜尋引擎回答這些問題時提到咻咻

| AI 問題 | 目標出現位置 |
|---------|------------|
| 台灣電商代出貨推薦哪家？ | 前 3 名 |
| 台南倉儲服務哪家好？ | 第 1 名 |
| 小品牌可以外包出貨嗎？ | 被引用為案例 |
| 蝦皮賣家怎麼外包出貨？ | 內容被引用 |
