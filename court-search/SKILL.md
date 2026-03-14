# Court Search Automation (V2 - Full Automation)

This skill provides a fully automated workflow for navigating `zxgk.court.gov.cn`. 

**V2 Update**: Previously a manual workflow, this skill now includes a standalone Python script `scripts/court_search.py` that handles navigation, input, and PDF rendering automatically. It defaults to **Headless Mode**.

## Overview

This skill provides a robust workflow for navigating the technical complexities of government disclosure websites, specifically the China Executive Information Disclosure Network (zxgk.court.gov.cn). It covers session-aware captcha solving, human-like interaction patterns (randomized delays and mouse movements), and generating formatted PDF reports.

## Usage Instructions

To execute the skill, use the bundled Python script:

```bash
python3 ~/.gemini/antigravity/skills/court-search/scripts/court_search.py "<Name>" "<Optional_ID>" "<Optional_Output_PDF_Path>" [--headless]
```

**Options**:
- `--headless`: (Optional) Run in invisible mode (not recommended for this tool due to complex captchas).

## Search Workflow

### 1. Persistent Session Initialization
- **Action**: Do not navigate directly to the search sub-page. Instead, navigate to the root URL `https://zxgk.court.gov.cn/` and click the "综合查询被执行人" (Comprehensive Search) button.
- **Why**: This helps establish a stable session and ensures that all security scripts (setting the `lqWVdQzgOVyaP` cookie) are properly initialized. Wait for 3-5 seconds after page load.

### 2. Information Input
- **Tool**: Use `execute_browser_javascript` for inputs. Standard `browser_press_key` may fail with Chinese characters.
- **Selectors**: 
  - Name: `#pName`
  - ID/Org Code: `#pCardNum`
- **Example**: `document.querySelector('#pName').value = '姓名';`

### 3. Captcha Recognition & Validation
- **Detection**: Capture the captcha image (`#captchaImg`).
- **Recognition**: Read the 4-character code.
- **Handling Failures**: If the image is broken or blank, click the image directly to refresh it.

### 4. Search Execution (Optimized for Bot Avoidance)
- **Constraint**: To avoid being flagged as a bot, DO NOT click search immediately after input.
- **Randomized Delay**: Implement a randomized wait time between **3 and 5 seconds** before clicking. Testing shows this is long enough to look human but short enough to avoid session timeout.
- **Mouse Interaction**: Simulate a realistic mouse movement to the search button coordinates (`790, 457` on default desktop view) followed by a physical mouse down/up event, rather than just calling a JS `.click()`.
- **Trigger**: Target the search button `#zg-chaxun-btn`.

## PDF Report Generation

### 1. Injected Headers & Footers
Inject a header and footer into the DOM for a professional look:
```javascript
const header = document.createElement('div');
header.innerText = '中国执行信息公开网 - 查询结果';
header.style = 'text-align:center; font-size: 20px; padding: 10px; border-bottom: 2px solid red; color: red; position: relative; z-index: 1000;';
document.body.prepend(header);
```

### 2. Format
Convert search result screenshots to PDF using the `scripts/png_to_pdf.py` utility.

## Resources

### scripts/
- `png_to_pdf.py`: A utility to convert search result screenshots into standard PDF documents.

### references/
- `network_analysis.md`: Detailed logs of session cookies and anti-bot headers.
