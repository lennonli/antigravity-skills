import asyncio
import os
import sys
import datetime
import random
from playwright.async_api import async_playwright

async def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("name", nargs='?', default="测试主体名称")
    parser.add_argument("id_num", nargs='?', default="")
    parser.add_argument("output", nargs='?', default=None)
    parser.add_argument("--headless", action="store_true", help="Run in headless mode")
    args = parser.parse_args()
    
    name = args.name
    id_num = args.id_num
    date_str = datetime.datetime.now().strftime("%Y%m%d")
    
    if args.output:
        output_pdf = os.path.expanduser(args.output)
    else:
        output_pdf = os.path.expanduser(f"~/Downloads/{name}-中国执行信息公开网-{date_str}.pdf")
        
    headless = args.headless
    print(f"Searching for: {name} (ID: {id_num}) in {'headless' if headless else 'headful'} mode")
    if not headless:
        print("NOTE: Headful mode enabled by default to allow manual captcha entry.")
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=headless,
            args=['--disable-blink-features=AutomationControlled']
        )
        context = await browser.new_context(
            viewport={'width': 1280, 'height': 800},
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        
        page = await context.new_page()
        
        # Step 1: Initialize session via main portal
        print("Initializing session via main portal...")
        try:
            await page.goto("https://zxgk.court.gov.cn/", wait_until="networkidle", timeout=60000)
        except Exception as e:
            print(f"Main portal navigation failed/timed out: {e}")
            # Try to continue if page loaded partially
        await asyncio.sleep(3)
        
        # Click the comprehensive search button
        print("Navigating to comprehensive search...")
        try:
            # Based on SKILL.md, it's "综合查询被执行人"
            await page.get_by_text("综合查询被执行人").click()
            await asyncio.sleep(2)
        except:
            print("Direct navigation to search page...")
            await page.goto("https://zxgk.court.gov.cn/zhzxgk/", wait_until="networkidle")

        # Step 2: Information Input
        print("Handling declaration statement if present...")
        try:
            # The declaration modal often has a button to close it
            decl_btn = page.get_by_role("button", name="确定")
            if await decl_btn.count() > 0:
                await decl_btn.click()
                print("Closed declaration modal.")
                await asyncio.sleep(1)
        except:
            pass

        print("Filling search information...")
        await page.evaluate(f"document.querySelector('#pName').value = '{name}'")
        if id_num:
            await page.evaluate(f"document.querySelector('#pCardNum').value = '{id_num}'")
            
        # Step 3: Captcha handling
        # Since this script is newly automated, if it's headless, 
        # it might need a way to solve captcha. For now, we wait for user in headful 
        # or implement a simple screenshot-based retry if captcha is detected.
        # NOTE: If persistent captcha blocks automated headless, we might need OCR or manual intervention.
        # For V2, we try to reach the query button.
        
        print("Checking for captcha...")
        captcha_visible = await page.is_visible("#captchaImg")
        if captcha_visible:
            print("WARNING: Captcha detected. Headless automation might be blocked if not handled via OCR.")
            # If headful, user can solve. If headless, we capture a debug pic.
            if headless:
                 await page.screenshot(path="court_captcha_needed.png")
                 print("Captcha screenshot saved to court_captcha_needed.png. Please solve in headful mode if this fails.")
            else:
                 print("Please solve the captcha in the browser window.")
                 # Loop until the captcha is gone or search is performed
                 while await page.is_visible("#captchaImg"):
                     await asyncio.sleep(2)
        
        # Step 4: Search Execution
        print("Waiting randomized delay (3-5s) to mimic human...")
        await asyncio.sleep(random.uniform(3, 5))
        
        print("Executing search...")
        try:
            # Try to trigger the search button
            btn = page.locator("#zg-chaxun-btn")
            if await btn.count() > 0:
                await btn.click()
            else:
                print("Search button not found via ID, trying specific role...")
                await page.get_by_role("button", name="查询").click()
        except Exception as e:
            print(f"Search click failed: {e}")
            try:
                await page.evaluate("document.querySelector('#zg-chaxun-btn').click()")
            except:
                print("Failed all click methods.")
            
        print("Waiting for results...")
        # Step 5: Wait for AJAX results
        try:
            # Wait for either the result table OR the empty results indicator
            await page.wait_for_selector("#result-table, .context-block:has-text('验证码错误'), #result-block:has-text('未查询到记录')", timeout=30000)
            print("Results loaded or state settled.")
        except Exception as e:
            print(f"Wait for results timed out or failed: {e}")
            
        await asyncio.sleep(3) # Extra buffer for table rendering
        
        # Step 6: PDF Generation
        print("Preparing document headers...")
        try:
            await page.evaluate("""
                const header = document.createElement('div');
                header.innerText = '中国执行信息公开网 - 查询结果';
                header.style = 'text-align:center; font-size: 20px; padding: 10px; border-bottom: 2px solid red; color: red; position: relative; z-index: 1000; margin-bottom: 20px;';
                document.body.prepend(header);
            """)
        except:
            pass
        
        print(f"Generating PDF to {output_pdf}...")
        await page.emulate_media(media="screen")
        await page.pdf(
            path=output_pdf,
            format="A4",
            print_background=True,
            display_header_footer=True,
            margin={"top": "1cm", "right": "1cm", "bottom": "1cm", "left": "1cm"}
        )
        
        print("Done!")
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
