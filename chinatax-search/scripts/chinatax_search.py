import asyncio
from playwright.async_api import async_playwright
import os
import sys
import datetime

# Province mapping logic based on company name prefixes
REGION_TO_PROVINCE = {
    "北京": "北京", "天津": "天津", "上海": "上海", "重庆": "重庆",
    "河北": "河北", "山西": "山西", "辽宁": "辽宁", "吉林": "吉林", "黑龙江": "黑龙江",
    "江苏": "江苏", "浙江": "浙江", "安徽": "安徽", "福建": "福建", "江西": "江西", "山东": "山东",
    "河南": "河南", "湖北": "湖北", "湖南": "湖南", "广东": "广东", "海南": "海南",
    "四川": "四川", "贵州": "贵州", "云南": "云南", "陕西": "陕西", "甘肃": "甘肃", "青海": "青海",
    "内蒙古": "内蒙古", "广西": "广西", "西藏": "西藏", "宁夏": "宁夏", "新疆": "新疆", "台湾": "台湾",
    "大连": "大连", "宁波": "宁波", "厦门": "厦门", "青岛": "青岛", "深圳": "深圳",
    
    # Common cities mapping to provinces
    "成都": "四川", "无锡": "江苏", "广州": "广东", "武汉": "湖北", "杭州": "浙江",
    "南京": "江苏", "济南": "山东", "郑州": "河南", "西安": "陕西", "福州": "福建",
    "合肥": "安徽", "长沙": "湖南", "南宁": "广西", "昆明": "云南", "南昌": "江西",
    "长春": "吉林", "哈尔滨": "黑龙江", "石家庄": "河北", "太原": "山西", "贵阳": "贵州"
}

def guess_province(company_name):
    for key, province in REGION_TO_PROVINCE.items():
        if company_name.startswith(key):
            return province
    return None # Fallback

async def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("company_name", nargs='?', default="成都睿源云启科技有限公司")
    parser.add_argument("output", nargs='?', default=None)
    parser.add_argument("--headful", action="store_true", help="Run in headful mode")
    args = parser.parse_args()
    
    company_name = args.company_name
    date_str = datetime.datetime.now().strftime("%Y%m%d")
    output_pdf = os.path.expanduser(args.output) if args.output else os.path.expanduser(f"~/Downloads/{company_name}-重大税收违法失信主体信息-{date_str}.pdf")
    
    province = guess_province(company_name)
    if not province:
        # Default to Sichuan for this test since the user requested it
        print(f"Could not determine province for '{company_name}', defaulting to 四川")
        province = "四川"
    else:
        print(f"Determined province: {province}")
        
    headless = not args.headful
    print(f"Searching in {'headless' if headless else 'headful'} mode...")
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=headless,
            args=['--disable-blink-features=AutomationControlled']
        )
        context = await browser.new_context(
            viewport={'width': 1366, 'height': 768},
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = await context.new_page()
        
        print("Navigating to China Tax National Index...")
        await page.goto("https://www.chinatax.gov.cn/chinatax/c101249/n2020011502/index.html", wait_until="networkidle")
        
        print(f"Clicking link for province: {province} and waiting for new tab...")
        try:
            async with context.expect_page(timeout=15000) as new_page_info:
                # Find the a tag in the lis with the exact province text
                await page.locator(f"ul.nsrmdgbl_box_list li a:text-is('{province}')").click()
                
            provincial_page = await new_page_info.value
            print(f"Successfully caught new provincial page! URL: {provincial_page.url}")
        except Exception as e:
            print(f"Failed to catch new page: {e}")
            await browser.close()
            return
            
        print("Waiting for provincial search page to load fully...")
        try:
            await provincial_page.wait_for_load_state("networkidle", timeout=15000)
        except:
            print("Networkidle wait timed out, continuing...")
        await asyncio.sleep(2)
        
        print("Taking debug screenshot of provincial platform...")
        await provincial_page.screenshot(path="chinatax_debug_provincial.png", full_page=True)
        
        print("Dumping provincial HTML for inspection...")
        html_content = await provincial_page.content()
        with open("chinatax_provincial_page.html", "w") as f:
            f.write(html_content)
            
        print("Filling search input...")
        try:
            # The name input uses `search-field="title"`
            await provincial_page.locator('input[search-field="title"]').fill(company_name)
        except Exception as e:
            print(f"Input fill error: {e}")
            
        print("Clicking submit button...")
        try:
            # The submit button has id `search`
            await provincial_page.locator('#search').click()
        except Exception as e:
            print(f"Search click error: {e}")
            
        print("Waiting for AJAX search results...")
        # The results are loaded via an AJAX call from dataSearch.js.
        # Wait for either networkidle or a specific element to appear.
        try:
            await provincial_page.wait_for_load_state("networkidle", timeout=15000)
        except:
             pass
        await asyncio.sleep(5) # Let animations or framework renders settle
        
        print("Taking result screenshot...")
        await provincial_page.screenshot(path="chinatax_debug_result.png", full_page=True)
        
        print(f"Generating PDF to {output_pdf}...")
        await provincial_page.emulate_media(media="screen")
        await provincial_page.pdf(
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
