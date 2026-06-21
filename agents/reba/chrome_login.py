"""
連接真實 Chrome → 開啟 ChatArt → Google 登入 554hilife@gmail.com
執行前請先開 Chrome：powershell -File agents/yifei/start_chrome.ps1
"""
import asyncio, os, random
from pathlib import Path
from dotenv import load_dotenv
from playwright.async_api import async_playwright

load_dotenv()
EMAIL    = os.getenv('CHATART_EMAIL')
PASSWORD = os.getenv('CHATART_PASSWORD')
VIDEO_URL = 'https://app.chatartpro.com/video/image-to-video'
STATE_FILE = Path(__file__).parent / 'storage_state.json'


async def type_slow(el, text):
    for c in text:
        await el.type(c)
        await asyncio.sleep(random.uniform(0.05, 0.12))


async def main():
    async with async_playwright() as p:
        # 連接真實 Chrome
        print('連接 Chrome (port 9222)...')
        for attempt in range(6):
            try:
                browser = await p.chromium.connect_over_cdp('http://localhost:9222')
                print('  連接成功')
                break
            except Exception as e:
                print(f'  等待 Chrome... ({attempt+1}/6)')
                await asyncio.sleep(2)
        else:
            print('ERROR: 無法連接 Chrome，請先執行 start_chrome.ps1')
            return

        ctx = browser.contexts[0] if browser.contexts else await browser.new_context()
        page = await ctx.new_page()

        # 開啟 ChatArt 影片頁
        print('開啟 ChatArt...')
        await page.goto(VIDEO_URL, wait_until='domcontentloaded', timeout=30000)
        await asyncio.sleep(3)

        # 關閉彈窗
        for sel in ['button.close', '[aria-label="Close"]', '[aria-label="close"]']:
            try:
                b = await page.query_selector(sel)
                if b and await b.is_visible():
                    await b.click()
                    await asyncio.sleep(0.5)
            except Exception:
                pass
        try:
            await page.keyboard.press('Escape')
        except Exception:
            pass
        await asyncio.sleep(1)

        # 截圖確認當前狀態
        await page.screenshot(path='tmp_before_login.png')
        print(f'目前 URL: {page.url[:80]}')

        # 檢查是否已登入
        login_btn = await page.query_selector('button:has-text("登入"), a:has-text("登入")')
        if not login_btn or not await login_btn.is_visible():
            print('已登入 ChatArt！無需重新登入。')
            await page.screenshot(path='tmp_chrome_chatart.png')
            return

        # 點擊登入
        print('點擊「登入」...')
        try:
            async with ctx.expect_page(timeout=5000) as pp:
                await login_btn.click()
            login_page = await pp.value
            await login_page.wait_for_load_state('domcontentloaded')
            print(f'  新頁面: {login_page.url[:60]}')
        except Exception:
            login_page = page
            await login_btn.click()
            await asyncio.sleep(2)

        await asyncio.sleep(2)

        # 找 Google 登入按鈕
        google_clicked = False
        for sel in ['button:has-text("Google")', 'a:has-text("Google")', '[data-provider="google"]']:
            try:
                gb = await login_page.query_selector(sel)
                if gb and await gb.is_visible():
                    print(f'點擊 Google 登入 ({sel})...')
                    try:
                        async with ctx.expect_page(timeout=6000) as gpp:
                            await gb.click()
                        gpage = await gpp.value
                        await gpage.wait_for_load_state('domcontentloaded')
                    except Exception:
                        gpage = login_page
                        await gb.click()
                        await asyncio.sleep(2)
                    google_clicked = True
                    break
            except Exception:
                pass

        if not google_clicked:
            await login_page.screenshot(path='tmp_login_page.png')
            print('找不到 Google 按鈕，截圖：tmp_login_page.png')
            return

        await asyncio.sleep(2)
        print(f'Google 頁面: {gpage.url[:80]}')

        # Google OAuth 登入
        if 'accounts.google.com' in gpage.url:
            print(f'輸入 Email: {EMAIL}')
            email_inp = await gpage.wait_for_selector('input[type="email"]', timeout=10000)
            await type_slow(email_inp, EMAIL)
            await asyncio.sleep(0.5)
            nb = await gpage.query_selector('#identifierNext')
            if nb:
                await nb.click()
            else:
                await gpage.keyboard.press('Enter')
            await asyncio.sleep(2.5)

            print('輸入密碼...')
            pwd_inp = await gpage.wait_for_selector('input[type="password"]', timeout=10000)
            await type_slow(pwd_inp, PASSWORD)
            await asyncio.sleep(0.5)
            pb = await gpage.query_selector('#passwordNext')
            if pb:
                await pb.click()
            else:
                await gpage.keyboard.press('Enter')

            print('等待登入完成（如有手機驗證請手動完成）...')
            await asyncio.sleep(5)

        # 等待回到 ChatArt（最多 60 秒）
        for _ in range(30):
            await asyncio.sleep(2)
            try:
                if 'chatartpro.com' in page.url and 'login' not in page.url:
                    break
            except Exception:
                pass

        await asyncio.sleep(2)
        await page.screenshot(path='tmp_chrome_chatart.png')
        print(f'登入後 URL: {page.url[:80]}')
        print('截圖：tmp_chrome_chatart.png')
        print('完成！Chrome 保持開啟。')


if __name__ == '__main__':
    asyncio.run(main())
