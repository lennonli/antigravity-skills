import asyncio
import os
import sys
import datetime
import re
from playwright.async_api import async_playwright
from pypdf import PdfWriter

async def solve_slider(page, selector=".dv_handler"):
    """
    Very basic slider solver for simple offsets. 
    If it fails, the user in headful mode can intervene.
    """
    try:
        handler = await page.wait_for_selector(selector, timeout=5000)
        if not handler:
            return
        
        box = await handler.bounding_box()
        if not box:
            return

        # Simple slide to the end (usually works for many basic sliders)
        await page.mouse.move(box["x"] + box["width"] / 2, box["y"] + box["height"] / 2)
        await page.mouse.down()
        # Track may be ~300px
        await page.mouse.move(box["x"] + 350, box["y"] + box["height"] / 2, steps=10)
        await page.mouse.up()
        await asyncio.sleep(1)
    except:
        pass

async def capture_tab(page, output_path, name):
    print(f"Capturing view: {name}...")
    # Hide possible overlaps
    await page.evaluate("""
        const headers = document.querySelectorAll('.header-wrapper, .footer-wrapper');
        headers.forEach(h => h.style.display = 'none');
    """)
    await page.pdf(
        path=output_path,
        format="A4",
        print_background=True,
        margin={"top": "1cm", "right": "1cm", "bottom": "1cm", "left": "1cm"}
    )

def extract_count(text):
    match = re.search(r'(\d+)', text)
    if match:
        return int(match.group(1))
    return 0

async def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("company_name", nargs='?', default="台山市精诚达电路有限公司")
    parser.add_argument("--headless", action="store_true", help="Run in headless mode")
    args = parser.parse_args()
    
    company_name = args.company_name
    date_str = datetime.datetime.now().strftime("%Y%m%d")
    final_output = os.path.expanduser(f"~/Downloads/{company_name}-环保信息网络核查-{date_str}.pdf")
    
    temp_dir = f"/tmp/ipe_{int(datetime.datetime.now().timestamp())}"
    os.makedirs(temp_dir, exist_ok=True)
    pdf_files = []

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=args.headless, args=['--disable-blink-features=AutomationControlled'])
        context = await browser.new_context(viewport={'width': 1280, 'height': 800})
        page = await context.new_page()
        
        # Step 1: Search
        print(f"Navigating to IPE search for {company_name}...")
        try:
            await page.goto("http://www.lvwang.org.cn/search/", wait_until="commit", timeout=60000)
            await asyncio.sleep(3)
            # Check if we are on the search version with hash
            if "/#/" not in page.url and "/search" in page.url:
                 await page.goto("http://www.lvwang.org.cn/search/#/", wait_until="networkidle")
        except:
            pass

        print("Entering company name...")
        await page.wait_for_selector("input.el-input__inner", state="visible", timeout=30000)
        await page.fill("input.el-input__inner", company_name)
        await page.click("button.search-form__input__append")
        
        # Handle search-time captcha
        print("Handling captcha (if any)...")
        await asyncio.sleep(2)
        if await page.is_visible(".dv_handler"):
            await solve_slider(page)
        
        # Wait for results
        print("Waiting for search results...")
        result_selector = "a.el-link--primary, .search-result__item"
        try:
            # Wait for results to be at least attached (might be hidden briefly)
            await page.wait_for_selector(result_selector, state="attached", timeout=60000)
            print("Results found in DOM.")
        except Exception as e:
            if args.headless:
                print(f"Results not found: {e}")
                await browser.close()
                return
            else:
                print("Please ensure captcha is solved and results are visible.")
                await page.wait_for_selector(result_selector, state="visible", timeout=60000)

        # Step 2: Navigate to details page
        print("Finding details link...")
        href = None
        # Permissive search for any link that looks like a company detail
        try:
            # Wait longer for the search results to settle
            await page.wait_for_selector(".search-result__item, a", timeout=30000)
            await asyncio.sleep(5)
            
            # Extract href using multiple strategies
            href = await page.evaluate(f"""() => {{
                // Strategy 1: Look for el-link--primary inside a result item
                let link = document.querySelector('a.el-link--primary');
                if (link && link.href) return link.href;
                
                // Strategy 2: Look for any link containing the company name
                let allLinks = Array.from(document.querySelectorAll('a'));
                let target = allLinks.find(a => a.innerText.includes("{company_name}") && a.href && a.href.includes("id="));
                if (target) return target.href;

                // Strategy 3: Look for any link with 'id=' and 'module='
                target = allLinks.find(a => a.href && a.href.includes("id=") && a.href.includes("eriCompanyDetails"));
                if (target) return target.href;

                return null;
            }}""")
        except Exception as e:
             print(f"Error during link detection: {e}")
        
        if not href:
            print("Link not found. Inspecting DOM...")
            await page.screenshot(path="ipe_search_no_link_debug.png")
            # Last ditch: try to just click the first el-link--primary if it exists but evaluate failed
            l = await page.query_selector("a.el-link--primary")
            if l:
                href = await l.get_attribute("href")
                if href and not href.startswith("http"):
                    href = "http://www.lvwang.org.cn" + (href if href.startswith("/") else "/" + href)

        if href:
            print(f"Navigating directly to: {href}")
            await page.goto(href, wait_until="networkidle")
        else:
            print("Could not resolve details URL. Aborting.")
            await browser.close()
            return

        details_page = page

        await details_page.wait_for_load_state("networkidle")
        
        # Step 3: Iterate Tabs and Capture
        print("Processing details tabs...")
        
        # Wait for tabs to render
        try:
            await details_page.wait_for_selector(".el-tabs__item", timeout=30000)
        except:
            print("Tabs not found, attempting screenshot debug...")
            await details_page.screenshot(path="ipe_tabs_not_found.png")
        
        # Capture main/overview first
        p1 = f"{temp_dir}/00_main.pdf"
        await capture_tab(details_page, p1, "Main Details")
        pdf_files.append(p1)
        
        # Collect all unique tabs and sub-tabs with counts
        # We perform a two-stage discovery to avoid misses
        targets = [] # List of {'title': str, 'selector': str, 'parent': str or None}
        
        top_tabs = await details_page.query_selector_all(".el-tabs__item")
        for tab in top_tabs:
            title = (await tab.inner_text()).replace('\n', ' ').strip()
            if extract_count(title) > 0 or "环境违法" in title:
                targets.append({'title': title, 'type': 'top'})

        processed_subtabs = set()
        
        for target in targets:
            title = target['title']
            print(f"Processing target: {title}")
            
            # Click top tab
            try:
                await details_page.get_by_role("tab").filter(has_text=title).first.click()
            except:
                # Fallback to evaluate
                all_at = await details_page.query_selector_all(".el-tabs__item")
                for at in all_at:
                    if title in (await at.inner_text()).replace('\n', ' ').strip():
                        await at.evaluate("(e) => e.click()")
                        break
            
            await asyncio.sleep(2)
            
            # Handle possible captcha
            if await details_page.is_visible(".dv_handler"):
                print("Captcha detected. Solving...")
                await solve_slider(details_page)
                if not args.headless:
                    while await details_page.is_visible(".dv_handler"):
                        await asyncio.sleep(2)

            # Check for sub-tabs inside this top tab
            sub_tabs = await details_page.query_selector_all(".el-tabs__header.is-top .el-tabs__item")
            sub_targets = []
            for st in sub_tabs:
                st_title = (await st.inner_text()).replace('\n', ' ').strip()
                if extract_count(st_title) > 0 and st_title not in processed_subtabs:
                    sub_targets.append(st_title)
                    processed_subtabs.add(st_title)
            
            if sub_targets:
                for st_title in sub_targets:
                    print(f"  Capture sub-tab: {st_title}")
                    try:
                        await details_page.get_by_role("tab").filter(has_text=st_title).first.click()
                    except:
                        # Fallback
                        st_all = await details_page.query_selector_all(".el-tabs__header.is-top .el-tabs__item")
                        for s_at in st_all:
                            if st_title in (await s_at.inner_text()).replace('\n', ' ').strip():
                                await s_at.evaluate("(e) => e.click()")
                                break
                    await asyncio.sleep(1)
                    file_path = f"{temp_dir}/tab_{title}_{st_title}.pdf".replace("/", "_")
                    file_path = f"{temp_dir}/" + os.path.basename(file_path)
                    await capture_tab(details_page, file_path, f"{title} - {st_title}")
                    pdf_files.append(file_path)
            else:
                # No specific sub-tabs identified with counts, capture the current view
                file_path = f"{temp_dir}/tab_{title}.pdf".replace("/", "_")
                file_path = f"{temp_dir}/" + os.path.basename(file_path)
                await capture_tab(details_page, file_path, title)
                pdf_files.append(file_path)
        # Merge PDFs
        print(f"Merging {len(pdf_files)} PDF components...")
        merger = PdfWriter()
        for pdf in pdf_files:
            merger.append(pdf)
        
        with open(final_output, "wb") as f:
            merger.write(f)
            
        print(f"Success! Final report: {final_output}")
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
