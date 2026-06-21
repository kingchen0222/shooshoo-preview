"""
執行一次：登入 ChatArt 並儲存登入狀態
之後 chatart.py 會自動讀取，不需重新登入

執行方式：python agents/reba/login_once.py
"""
import asyncio, os
from pathlib import Path
from dotenv import load_dotenv
from playwright.async_api import async_playwright

load_dotenv()

EMAIL    = os.getenv('CHATART_EMAIL')
PASSWORD = os.getenv('CHATART_PASSWORD')
STATE_FILE = Path(__file__).parent / 'storage_state.json'


async def login_and_save():
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=False,
            slow_mo=400,
            args=['--lang=zh-TW']
        )
        ctx = await browser.new_context(
            viewport={'width': 1280, 'height': 900},
            locale='zh-TW'
        )
        page = await ctx.new_page()

        print('開啟 ChatArt 影片頁...')
        await page.goto(
            'https://app.chatartpro.com/video/image-to-video',
            wait_until='domcontentloaded', timeout=30000
        )
        await asyncio.sleep(3)

        # 找 Google 登入按鈕
        google_selectors = [
            'button:has-text("Google")', 'a:has-text("Google")',
            'text=使用 Google 登入', 'text=Sign in with Google',
            '[data-provider="google"]', '.google-login-btn'
        ]
        clicked = False
        for sel in google_selectors:
            try:
                btn = await page.query_selector(sel)
                if btn and await btn.is_visible():
                    print(f'點擊 Google 登入: {sel}')
                    try:
                        # Google 可能開新分頁
                        async with ctx.expect_page(timeout=5000) as popup_info:
                            await btn.click()
                        popup = await popup_info.value
                        await popup.wait_for_load_state('networkidle')
                        if 'accounts.google.com' in popup.url:
                            await _google_oauth(popup, EMAIL, PASSWORD)
                            print('等待 Google 完成...')
                            await popup.wait_for_close(timeout=60000)
                    except Exception:
                        await btn.click()
                        await asyncio.sleep(3)
                        if 'accounts.google.com' in page.url:
                            await _google_oauth(page, EMAIL, PASSWORD)
                    clicked = True
                    break
            except Exception:
                pass

        if not clicked:
            print('找不到 Google 登入按鈕，截圖確認...')
            await page.screenshot(path='tmp_login_not_found.png')
            print('請在瀏覽器手動完成登入，完成後按 Enter...')
            input()

        # 等待登入完成（回到 ChatArt）
        print('等待登入完成...')
        try:
            await page.wait_for_url('**app.chatartpro.com**', timeout=60000)
            # 確認不在登入頁
            for _ in range(10):
                if 'login' not in page.url and 'accounts.google' not in page.url:
                    break
                await asyncio.sleep(2)
        except Exception:
            print('手動確認：瀏覽器已登入後，請按 Enter 繼續...')
            input()

        # 儲存登入狀態
        await ctx.storage_state(path=str(STATE_FILE))
        print(f'登入狀態已儲存至：{STATE_FILE}')
        print('之後執行 chatart.py 將自動登入，不需手動操作。')

        await asyncio.sleep(2)
        await browser.close()


async def _google_oauth(page, email, password):
    import random
    async def type_slow(el, text):
        for c in text:
            await el.type(c)
            await asyncio.sleep(random.uniform(0.05, 0.12))

    try:
        print('  輸入 Email...')
        email_inp = await page.wait_for_selector('input[type="email"]', timeout=10000)
        await type_slow(email_inp, email)
        await asyncio.sleep(0.5)
        next_btn = await page.query_selector('#identifierNext, button:has-text("下一步"), button:has-text("Next")')
        if next_btn:
            await next_btn.click()
        else:
            await page.keyboard.press('Enter')
        await asyncio.sleep(2.5)

        print('  輸入密碼...')
        pwd_inp = await page.wait_for_selector('input[type="password"]', timeout=10000)
        await type_slow(pwd_inp, password)
        await asyncio.sleep(0.5)
        pw_next = await page.query_selector('#passwordNext, button:has-text("下一步"), button:has-text("Next")')
        if pw_next:
            await pw_next.click()
        else:
            await page.keyboard.press('Enter')
        await asyncio.sleep(4)
        print('  Google 登入完成')
    except Exception as e:
        print(f'  Google 登入錯誤：{e}')
        await page.screenshot(path='tmp_google_oauth_error.png')
        print('  請在瀏覽器手動完成，完成後按 Enter...')
        input()


if __name__ == '__main__':
    asyncio.run(login_and_save())
