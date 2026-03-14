import asyncio
import os
import sys
import datetime
import re
import shutil
from playwright.async_api import async_playwright

async def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("company_name", nargs='?', default="测试主体名称")
    parser.add_argument("output", nargs='?', default=None)
    parser.add_argument("--headful", action="store_true", help="Run in headful mode")
    args = parser.parse_args()
    
    company_name = args.company_name
    date_str = datetime.datetime.now().strftime("%Y%m%d")
    
    if args.output:
        output_pdf = os.path.expanduser(args.output)
    else:
        output_pdf = os.path.expanduser(f"~/Downloads/{company_name}-信用中国报告-{date_str}.pdf")
        
    headless = not args.headful
    print(f"Searching for: {company_name} in {'headless' if headless else 'headful'} mode")
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=headless,
            args=['--disable-blink-features=AutomationControlled']
        )
        context = await browser.new_context(
            viewport={'width': 1280, 'height': 800},
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            accept_downloads=True
        )
        
        page = await context.new_page()
        print("Navigating to Credit China...")
        await page.goto("https://www.creditchina.gov.cn/", wait_until="networkidle")
        
        # Step 1: Perform Search
        print("Filling search term...")
        try:
            # Strategy A: Target by common placeholder (most robust)
            search_input = page.get_by_placeholder("请输入主体名称或统一社会信用代码")
            if await search_input.count() == 0:
                # Strategy B: Target by ID
                search_input = page.locator('input#home-search-text')
            
            if await search_input.count() == 0:
                # Strategy C: Target by generic type (brute force)
                search_input = page.locator('input[type="text"]').first
                
            await search_input.wait_for(state="visible", timeout=15000)
            await search_input.fill(company_name)
        except Exception as e:
            print(f"Failed all search input strategies: {e}")
            # Final attempt via direct JS eval if possible
            try:
                await page.evaluate(f"document.querySelector('input').value = '{company_name}'")
            except:
                pass
            
        await asyncio.sleep(1)
        
        print("Clicking search and waiting for result tab...")
        async with context.expect_page(timeout=15000) as new_page_info:
            await page.locator('.search-button').click()
        
        result_page = await new_page_info.value
        await result_page.wait_for_load_state("networkidle")
        print(f"Result page loaded: {result_page.url}")
        
        # Step 2: Navigate to specific company (first result)
        print("Navigating to the first company result...")
        async with context.expect_page(timeout=15000) as detail_page_info:
            first_result = result_page.locator(".search-result-name a").first
            await first_result.click()
            
        detail_page = await detail_page_info.value
        await detail_page.wait_for_load_state("networkidle")
        print(f"Detail page loaded: {detail_page.url}")
        
        # Step 3: Trigger Download and Handle Captcha
        print("Looking for '下载信用信息报告' button...")
        download_btn = detail_page.get_by_text("下载信用信息报告")
        await download_btn.scroll_into_view_if_needed()
        
        # Catch the download event before clicking
        try:
            async with detail_page.expect_download(timeout=60000) as download_info:
                print("Clicking download button...")
                await download_btn.click()
                
                # Check for captcha modal
                await asyncio.sleep(2)
                if await detail_page.is_visible(".verify-img-panel") or await detail_page.is_visible("#captchaImg"):
                     print("Captcha detected! Please check headless mode limitations or solve in headful mode.")
                     if headless:
                          await detail_page.screenshot(path="creditchina_captcha_needed.png")
                          print("Saved creditchina_captcha_needed.png. Solving requires manual intervention or headful mode.")
                     else:
                          print("Please solve the captcha in the browser...")
                          # Captcha logic would go here if automated, but for V2 we wait or prompt.
                
                download = await download_info.value
                path = await download.path()
                print(f"Download complete: {path}")
                
                # Copy to final destination
                shutil.copy(path, output_pdf)
                print(f"Successfully saved and renamed to: {output_pdf}")
                
        except Exception as e:
            print(f"Download flow interrupted or failed: {e}")
            if headless:
                 await detail_page.screenshot(path="creditchina_error.png")

        print("Done!")
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
