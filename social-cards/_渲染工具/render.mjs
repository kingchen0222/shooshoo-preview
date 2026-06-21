/**
 * 咻咻打包輪播渲染工具
 * 用法: node render.mjs <輪播資料夾路徑>
 * 範例: node render.mjs ../教育型/外包5訊號
 *
 * 自動偵測 index.html 內所有 .poster[id] 元素並截圖
 * 成品輸出至 <輪播資料夾>/成品/
 */

import { chromium } from 'playwright';
import path from 'path';
import { fileURLToPath } from 'url';
import fs from 'fs';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const arg = process.argv[2];

if (!arg) {
  console.error('用法: node render.mjs <輪播資料夾路徑>');
  console.error('範例: node render.mjs ../教育型/外包5訊號');
  process.exit(1);
}

const targetDir = path.resolve(__dirname, arg);
const htmlFile  = path.join(targetDir, 'index.html');
const outputDir = path.join(targetDir, '成品');

if (!fs.existsSync(htmlFile)) {
  console.error(`找不到 index.html：${htmlFile}`);
  process.exit(1);
}

fs.mkdirSync(outputDir, { recursive: true });

const htmlUrl = `file:///${htmlFile.replace(/\\/g, '/')}`;
const browser = await chromium.launch();
const page    = await browser.newPage();

await page.setViewportSize({ width: 1200, height: 900 });
await page.goto(htmlUrl, { waitUntil: 'networkidle' });
await page.waitForTimeout(2000); // 等 Google Fonts 載入

// 自動偵測所有 .poster[id]
const posterIds = await page.evaluate(() =>
  [...document.querySelectorAll('.poster[id]')].map(el => el.id)
);

if (posterIds.length === 0) {
  console.error('找不到任何 .poster[id] 元素');
  await browser.close();
  process.exit(1);
}

console.log(`\n偵測到 ${posterIds.length} 張輪播圖\n`);

for (const id of posterIds) {
  const outPath = path.join(outputDir, `${id}.png`);
  await page.locator(`#${id}`).screenshot({ path: outPath, type: 'png' });
  console.log(`OK  ${id}.png`);
}

await browser.close();
console.log(`\n完成 — ${posterIds.length} 張圖片存入 成品/`);
