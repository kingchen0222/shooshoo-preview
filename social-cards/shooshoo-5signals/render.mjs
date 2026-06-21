import { chromium } from 'playwright';
import path from 'path';
import { fileURLToPath } from 'url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const htmlPath = `file:///${__dirname.replace(/\\/g,'/')}/index.html`;
const outputDir = path.join(__dirname, 'output');

const posters = [
  { id: 'xhs-01', name: 'xhs-01-cover' },
  { id: 'xhs-02', name: 'xhs-02-signal01-order' },
  { id: 'xhs-03', name: 'xhs-03-signal02-error' },
  { id: 'xhs-04', name: 'xhs-04-signal03-space' },
  { id: 'xhs-05', name: 'xhs-05-signal04-multichannel' },
  { id: 'xhs-06', name: 'xhs-06-signal05-founder' },
  { id: 'xhs-07', name: 'xhs-07-cta' },
];

const browser = await chromium.launch();
const page = await browser.newPage();

// 1080 viewport so fonts load correctly; actual element sizes are fixed px
await page.setViewportSize({ width: 1200, height: 900 });
await page.goto(htmlPath, { waitUntil: 'networkidle' });

// Wait for Google Fonts to load
await page.waitForTimeout(2000);

for (const { id, name } of posters) {
  const el = page.locator(`#${id}`);
  const outPath = path.join(outputDir, `${name}.png`);
  await el.screenshot({ path: outPath, type: 'png' });
  console.log(`OK  ${name}.png`);
}

await browser.close();
console.log('\nDone — 7 images in output/');
