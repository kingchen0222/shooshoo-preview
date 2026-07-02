"""
熱巴 — ChatArt 瀏覽器自動化影片生成
Seedance 2.0 Fast + 全能模式 + 圖生影片
"""
import os, asyncio, random, json
from pathlib import Path
from dotenv import load_dotenv
from playwright.async_api import async_playwright

load_dotenv()

EMAIL        = os.getenv('CHATART_EMAIL')
PASSWORD     = os.getenv('CHATART_PASSWORD')
DOWNLOAD_DIR = Path('D:/咻咻打包claude/行銷影片')
VIDEO_URL    = 'https://app.chatartpro.com/video/image-to-video'
STATE_FILE   = Path(__file__).parent / 'storage_state.json'


async def generate_video(
    prompt: str,
    images: list = None,      # 圖片路徑清單（可多張）
    videos: list = None,      # 參考影片路徑清單（可多個）
    output_name: str = 'shooshoo_video',
    resolution: str = '720p',
    aspect: str = '9:16',
    duration: int = 5,        # 秒數：5 / 10 / 15（依腳本 Shot 需求）
):
    DOWNLOAD_DIR.mkdir(parents=True, exist_ok=True)

    async with async_playwright() as p:
        # 優先連接真實 Chrome（需先執行 start_chrome.ps1）
        using_real_chrome = False
        try:
            browser = await p.chromium.connect_over_cdp('http://localhost:9222')
            ctx = browser.contexts[0] if browser.contexts else await browser.new_context(accept_downloads=True)
            page = await ctx.new_page()
            print('  已連接真實 Chrome（使用現有登入狀態）')
            using_real_chrome = True
        except Exception:
            print('  提示：執行 agents/helv/start_chrome.ps1 可直接使用已登入的 Chrome')
            print('  改用內建瀏覽器...')
            browser = await p.chromium.launch(
                headless=False, slow_mo=350,
                args=['--lang=zh-TW', '--disable-blink-features=AutomationControlled']
            )
            ctx_kwargs = dict(
                viewport={'width': 1280, 'height': 900},
                locale='zh-TW', accept_downloads=True,
            )
            if STATE_FILE.exists():
                ctx_kwargs['storage_state'] = str(STATE_FILE)
                print('  讀取已儲存登入狀態')
            ctx = await browser.new_context(**ctx_kwargs)
            page = await ctx.new_page()

        # ── 1. 開啟影片頁 ────────────────────────────
        print('[1] 開啟 ChatArt 影片頁...')
        await page.goto(VIDEO_URL, wait_until='domcontentloaded', timeout=30000)
        await _delay(3, 4)
        await _close_popups(page)
        await _delay(1.5, 2.5)

        # ── 2. 確認登入狀態 ───────────────────────────
        login_btn = await page.query_selector('button:has-text("登入"), a:has-text("登入")')
        if login_btn and await login_btn.is_visible():
            if using_real_chrome:
                print('[2] Chrome 尚未登入 ChatArt，請在瀏覽器手動登入後按 Enter...')
                input()
            else:
                print('[2] 執行自動登入...')
                await _do_login(page, login_btn)
                await ctx.storage_state(path=str(STATE_FILE))
                print('   登入狀態已儲存')
            await _close_popups(page)
            await _delay(1, 2)
        else:
            print('[2] 已登入')

        # ── 3. 切換到「圖生影片」tab（若需要）────────
        if 'image-to-video' not in page.url:
            img_tab = await page.query_selector('text=圖生影片')
            if img_tab:
                await img_tab.click()
                await _delay(1, 1.5)

        # ── 4. 選擇 Seedance 2.0 Fast 模型 ──────────
        print('[4] 選擇 Seedance 2.0 Fast...')
        await _select_seedance_fast(page)

        # ── 5. 確認全能模式（預設即為全能模式）──────
        mode_el = await page.query_selector('text=全能模式')
        if mode_el:
            is_active = await page.eval_on_selector(
                ':text("全能模式")',
                'el => el.classList.toString() + el.closest("[class]")?.classList.toString()'
            )
            print(f'[5] 全能模式狀態: {str(is_active)[:80]}')
            if 'active' not in str(is_active).lower() and 'select' not in str(is_active).lower():
                await mode_el.click()
                await _delay(0.5, 1)

        # ── 6. 上傳素材（圖片 + 影片）────────────────
        all_files = []
        if images:
            all_files += [p for p in images if Path(p).exists()]
        if videos:
            all_files += [p for p in videos if Path(p).exists()]

        if all_files:
            print(f'[6] 上傳素材：{len(all_files)} 個檔案...')
            await _upload_files(page, all_files)
        else:
            print('[6] 無素材，略過上傳')

        # ── 7. 輸入 Prompt ────────────────────────────
        print('[7] 輸入影片描述...')
        await _input_prompt(page, prompt)

        # ── 8. 捲到設定區，設定畫質、比例、秒數 ──────
        await _scroll_to_settings(page)
        await _set_resolution(page, resolution)
        await _set_aspect(page, aspect)
        await _set_duration(page, duration)

        # ── 9. 點擊「產生」（處理 OAuth popup）──────────
        print('[9] 點擊產生...')
        await _click_generate(page, ctx)

        # ── 10. 等待生成 + 下載 ───────────────────────
        result = await _wait_and_download(page, output_name)
        await browser.close()
        return result


# ─── 登入流程 ──────────────────────────────────────────

async def _do_login(page, login_btn):
    # 點登入 → 可能跳轉到登入頁或彈出選項
    try:
        async with page.context.expect_page(timeout=5000) as popup_info:
            await login_btn.click()
        popup = await popup_info.value
        await popup.wait_for_load_state('networkidle')
        await _handle_login_page(popup)
        await popup.wait_for_close(timeout=60000)
    except Exception:
        await login_btn.click()
        await _delay(2, 3)
        await _handle_login_page(page)

    # 等待回到 ChatArt
    try:
        await page.wait_for_url('**chatartpro.com**', timeout=30000)
        print('   登入成功')
    except Exception:
        print('   等待登入回調...')


async def _handle_login_page(page):
    """在登入頁處理 Google 登入"""
    await page.wait_for_load_state('networkidle', timeout=10000)

    # 若在 Google OAuth 頁
    if 'accounts.google.com' in page.url:
        await _google_oauth(page)
        return

    # 找 Google 登入按鈕
    google_selectors = [
        'button:has-text("Google")', 'a:has-text("Google")',
        'text=使用 Google 登入', 'text=Sign in with Google',
        '[data-provider="google"]', '.google-btn'
    ]
    for sel in google_selectors:
        try:
            btn = await page.query_selector(sel)
            if btn and await btn.is_visible():
                try:
                    async with page.context.expect_page(timeout=5000) as p_info:
                        await btn.click()
                    gpage = await p_info.value
                    await gpage.wait_for_load_state('networkidle')
                    await _google_oauth(gpage)
                    await gpage.wait_for_close(timeout=60000)
                except Exception:
                    await btn.click()
                    await _delay(2, 3)
                    if 'accounts.google.com' in page.url:
                        await _google_oauth(page)
                return
        except Exception:
            pass

    await page.screenshot(path='tmp_login_page.png')
    print('   無法找到 Google 登入按鈕（截圖：tmp_login_page.png）')


async def _google_oauth(page):
    """Google 帳號密碼登入"""
    try:
        print('   [Google] 輸入 Email...')
        email_input = await page.wait_for_selector('input[type="email"]', timeout=10000)
        await _type_human(email_input, EMAIL)
        await _delay(0.5, 1)
        next_btn = await page.query_selector('#identifierNext, button:has-text("下一步"), button:has-text("Next")')
        if next_btn:
            await next_btn.click()
        else:
            await page.keyboard.press('Enter')
        await _delay(2, 3)

        print('   [Google] 輸入密碼...')
        pwd_input = await page.wait_for_selector('input[type="password"]', timeout=10000)
        await _type_human(pwd_input, PASSWORD)
        await _delay(0.5, 1)
        pw_next = await page.query_selector('#passwordNext, button:has-text("下一步"), button:has-text("Next")')
        if pw_next:
            await pw_next.click()
        else:
            await page.keyboard.press('Enter')
        await _delay(3, 5)
        print('   [Google] 登入送出')
    except Exception as e:
        print(f'   [Google] 錯誤: {e}')
        await page.screenshot(path='tmp_google_error.png')


# ─── 模型選擇 ──────────────────────────────────────────

async def _select_seedance_fast(page):
    """選擇 Seedance 2.0 Fast 模型：用 URL param 觸發選單 → 點 Fast 按鈕"""
    # 方法1：URL 參數開啟模型選擇面板
    await page.goto(
        VIDEO_URL + '?model_type=seedance-2.0-fast',
        wait_until='domcontentloaded', timeout=20000
    )
    await _delay(1.5, 2.5)
    await _close_popups(page)

    # 找到 "Seedance 2.0 Fast" 按鈕並點擊
    fast_selectors = [
        'button:has-text("Seedance 2.0 Fast")',
        'div:has-text("Seedance 2.0 Fast") >> button',
        ':text-is("Seedance 2.0 Fast")',
        'text=Seedance 2.0 Fast',
    ]
    for sel in fast_selectors:
        try:
            el = await page.wait_for_selector(sel, timeout=5000)
            if el and await el.is_visible():
                await el.click()
                await _delay(1, 1.5)
                print('   Seedance 2.0 Fast 已選擇')
                # 等頁面回到生成介面
                await page.wait_for_load_state('networkidle', timeout=10000)
                await _delay(1, 1.5)
                return
        except Exception:
            pass

    # 截圖確認
    await page.screenshot(path='tmp_model_selection.png')
    print('   截圖確認模型選擇（tmp_model_selection.png）')


# ─── 上傳素材 ──────────────────────────────────────────

async def _upload_files(page, file_paths: list):
    """上傳多個圖片/影片素材"""
    file_inputs = await page.query_selector_all('input[type="file"]')
    if file_inputs:
        # 有 file input，直接設定
        await file_inputs[0].set_input_files([str(f) for f in file_paths])
        await _delay(2, 4)
        print(f'   已上傳 {len(file_paths)} 個檔案')
    else:
        # 點擊上傳區域
        upload_area = await page.query_selector(
            '[class*="upload"], div:has-text("上傳參考圖"), .upload-btn, [class*="drag"]'
        )
        if upload_area:
            await upload_area.click()
            await _delay(1, 2)
            # 等待 file input 出現
            try:
                fi = await page.wait_for_selector('input[type="file"]', timeout=5000)
                await fi.set_input_files([str(f) for f in file_paths])
                await _delay(2, 4)
                print(f'   已上傳 {len(file_paths)} 個檔案')
            except Exception:
                print('   上傳失敗，截圖確認')
                await page.screenshot(path='tmp_upload_fail.png')


# ─── Prompt 輸入 ───────────────────────────────────────

async def _input_prompt(page, prompt: str):
    # ChatArt 使用 ProseMirror 富文字編輯器（div.tiptap.ProseMirror）
    pm_selectors = [
        'div.tiptap.ProseMirror',
        'div.ProseMirror',
        '.tiptap',
        'div[contenteditable="true"]',
    ]
    for sel in pm_selectors:
        try:
            el = await page.wait_for_selector(sel, timeout=5000)
            if el and await el.is_visible():
                await el.click()
                await _delay(0.3, 0.6)
                # 清空現有內容
                await page.keyboard.press('Control+a')
                await asyncio.sleep(0.2)
                await page.keyboard.press('Delete')
                await asyncio.sleep(0.2)
                # 仿真人輸入
                await _type_human(el, prompt)
                await _delay(0.5, 1)
                print(f'   Prompt 輸入完成（{len(prompt)} 字）')
                return
        except Exception:
            pass
    # fallback: textarea
    try:
        ta = await page.wait_for_selector('textarea', timeout=3000)
        if ta and await ta.is_visible():
            await ta.click()
            await ta.fill(prompt)
            print(f'   Prompt 輸入（textarea fallback）')
            return
    except Exception:
        pass
    print('   找不到 prompt 輸入框')
    await page.screenshot(path='tmp_no_prompt.png')


# ─── 畫質 / 比例設定 ───────────────────────────────────

async def _scroll_to_settings(page):
    """捲動左側面板到底，讓影片質量/時長/尺寸設定出現"""
    try:
        await page.evaluate("""
        () => {
            const wrap = document.querySelector('.el-scrollbar__wrap');
            if (wrap) wrap.scrollTop = wrap.scrollHeight;
        }
        """)
        await _delay(0.5, 0.8)
        print('   已捲到設定區')
    except Exception as e:
        print(f'   捲動失敗：{e}')


async def _click_setting_btn(page, text: str, label: str):
    """點選設定按鈕（用 locator 確保可見後點擊）"""
    try:
        loc = page.locator(f'button:has-text("{text}")')
        count = await loc.count()
        if count == 0:
            print(f'   [{label}] 找不到按鈕：{text}')
            return False
        btn = loc.first
        await btn.scroll_into_view_if_needed()
        await btn.click()
        await _delay(0.3, 0.6)
        print(f'   [{label}] 已選：{text}')
        return True
    except Exception as e:
        print(f'   [{label}] 點擊失敗：{e}')
        return False


async def _set_resolution(page, resolution: str):
    """設定影片質量：480p / 720p / 1080p"""
    await _click_setting_btn(page, resolution, '影片質量')


async def _set_aspect(page, aspect: str):
    """設定影片尺寸：9:16 / 16:9 / 1:1 / 3:4 / 4:3
    ChatArt 預設 16:9，需主動點 9:16
    """
    await _click_setting_btn(page, aspect, '影片尺寸')


async def _set_duration(page, duration: int):
    """設定影片時長：5s / 10s / 15s（ChatArt 用英文 s，不是秒）"""
    if duration not in (5, 10, 15):
        print(f'   秒數 {duration} 不合法，使用 5s')
        duration = 5
    # 先試 "5s"，再試 "5秒"
    ok = await _click_setting_btn(page, f'{duration}s', '影片時長')
    if not ok:
        await _click_setting_btn(page, f'{duration}秒', '影片時長')


async def _click_generate(page, ctx):
    """點擊「產生」並處理可能出現的 Google OAuth popup"""
    gen_btn = await page.query_selector('button:has-text("產生")')
    if not gen_btn or not await gen_btn.is_visible():
        await page.screenshot(path='tmp_no_gen_btn.png')
        print('   找不到「產生」按鈕（截圖：tmp_no_gen_btn.png）')
        return

    # 監聽 OAuth popup
    oauth_popup = None
    async def on_page(new_page):
        nonlocal oauth_popup
        if 'accounts.google.com' in new_page.url or 'google' in new_page.url.lower():
            oauth_popup = new_page
    ctx.on('page', on_page)

    try:
        await gen_btn.click()
        print('   「產生」已點擊')
    except Exception as e:
        print(f'   點擊錯誤：{e}')

    await _delay(2, 3)

    # 若有 OAuth popup，等它關閉
    if oauth_popup:
        print('   偵測到 Google OAuth，等待完成...')
        try:
            await oauth_popup.wait_for_close(timeout=30000)
            print('   OAuth 完成')
        except Exception:
            pass
        await _delay(2, 4)
        await page.wait_for_load_state('domcontentloaded', timeout=15000)

        # OAuth 完成後回影片頁再點一次「產生」
        if 'video' not in page.url:
            await page.goto(VIDEO_URL, wait_until='domcontentloaded', timeout=20000)
            await _delay(2, 3)
        try:
            gen_btn2 = await page.wait_for_selector('button:has-text("產生")', timeout=8000)
            if gen_btn2 and await gen_btn2.is_visible():
                await gen_btn2.click()
                print('   OAuth 後再次點擊「產生」')
                await _delay(2, 3)
        except Exception:
            pass

    print('   送出完成')


# ─── 等待下載 ──────────────────────────────────────────

async def _wait_and_download(page, output_name: str, timeout_sec: int = 360):
    print('[10] 等待生成完成（最多6分鐘）...')
    dl_selectors = [
        'button:has-text("下載")', 'a[download]',
        'button:has-text("Download")', 'a:has-text("下載")',
        '[class*="download"]:visible', 'button:has-text("保存")',
    ]
    for i in range(timeout_sec // 5):
        await asyncio.sleep(5)
        elapsed = (i + 1) * 5
        for sel in dl_selectors:
            try:
                btn = await page.query_selector(sel)
                if btn and await btn.is_visible():
                    print(f'   完成！({elapsed}s) 下載中...')
                    async with page.expect_download(timeout=30000) as dl_info:
                        await btn.click()
                    dl = await dl_info.value
                    save_path = DOWNLOAD_DIR / f'{output_name}.mp4'
                    await dl.save_as(str(save_path))
                    print(f'   儲存：{save_path}')
                    return str(save_path)
            except Exception:
                pass
        if elapsed % 60 == 0:
            print(f'   [{elapsed}s] 生成中...')
            await page.screenshot(path=f'tmp_progress_{elapsed}s.png')

    print('   逾時，截圖確認')
    await page.screenshot(path='tmp_chatart_timeout.png')
    return None


# ─── 工具函式 ──────────────────────────────────────────

async def _close_popups(page):
    for sel in [
        '.activity-dialog .close', '.activity-dialog-daily-sale .close',
        '[class*="dialog"] [class*="close"]', '[class*="modal"] [class*="close"]',
        '[aria-label="Close"]', 'button.close',
    ]:
        try:
            btn = await page.query_selector(sel)
            if btn and await btn.is_visible():
                await btn.click()
                await _delay(0.3, 0.6)
        except Exception:
            pass
    try:
        await page.keyboard.press('Escape')
        await _delay(0.3, 0.5)
    except Exception:
        pass


async def _type_human(element, text: str):
    for char in text:
        await element.type(char)
        await asyncio.sleep(random.uniform(0.04, 0.12))


async def _delay(min_s=0.5, max_s=1.5):
    await asyncio.sleep(random.uniform(min_s, max_s))


# ─── 直接執行 ──────────────────────────────────────────

if __name__ == '__main__':
    import sys
    prompt   = sys.argv[1] if len(sys.argv) > 1 else '咻咻打包 台南電商倉儲代出貨 3PL物流 橘色品牌 專業電商服務'
    img_arg  = sys.argv[2] if len(sys.argv) > 2 else None
    name     = sys.argv[3] if len(sys.argv) > 3 else 'shooshoo_video_01'
    dur_arg  = int(sys.argv[4]) if len(sys.argv) > 4 else 5   # 5 / 10 / 15 秒

    images = [img_arg] if img_arg else []
    asyncio.run(generate_video(prompt, images=images, output_name=name, duration=dur_arg))
