# Credit China Full Automation (V2 - Headless Default)

This skill provides a fully automated workflow for obtaining official Credit Reports from `creditchina.gov.cn`. 

**V2 Update**: This skill now includes a standalone Python script `scripts/creditchina_search.py` that handles navigation, searching, and native PDF file downloading automatically. It defaults to **Headless Mode**.

## Overview

This skill simplifies the process of obtaining official Credit Reports from `creditchina.gov.cn`. It focuses on navigating the search interface, handling notoriously unstable captcha services, and retrieving downloaded PDF files natively produced by the site rather than relying on browser screenshots.

## Usage Instructions

To execute the skill, use the bundled Python script:

```bash
python3 ~/.gemini/antigravity/skills/creditchina-search/scripts/creditchina_search.py "<Company Name>" "<Optional_Output_PDF_Path>" [--headful]
```

**Options**:
- `--headful`: (Optional) Open the browser window. **Required if a complex captcha appears** that requires manual interaction.

## Workflow Execution
- **Initial Load**: Navigate to `https://www.creditchina.gov.cn/`.
- **Search Input**: Due to bot detection mechanisms, avoid direct immediate `type` commands. Instead, consider using `execute_browser_javascript` to populate the input box, or introduce human-like delays.
- **Trigger**: Click the search button.
- **Results**: The search results usually open in a new tab. Ensure the subagent focuses the correct tab for the company detail page.

### 2. Captcha Handling & Download Trigger (Critical)
When clicking the `下载信用信息报告` (Download Credit Report) button:
- **Constraint (Preventing Duplicates)**: **DO NOT** click the download button more than once. The site may freeze or open a captcha modal silently. Clicking multiple times will queue multiple identical PDF downloads in the background. Click ONCE and wait.
- **The Captcha Issue**: The captcha image is frequently broken, invisible, or fails to load initially.
- **The Solution**: If the captcha text is not visible, locate the `看不清？换一张` (Can't see? Change one) link or click directly on the broken image area.
- **Retry Logic**: Instruct the subagent to click the refresh link **multiple times** if necessary until a clear image appears.

### 3. File Retrieval & Renaming
Unlike sites where you print to PDF, Credit China provides a direct PDF file download.
- **Action**: After successfully submitting the captcha, the site triggers a native file download.
- **Playwright Behavior**: In Playwright automation, downloaded files are temporarily saved in a hidden system directory with a UUID name and no extension (e.g., `/var/folders/.../playwright-artifacts-XXX/UUID`).
- **Extraction**: 
    1. Search the temporary `/tmp` or `/var/folders/` directories for recently created files matching a UUID pattern.
    2. Use the `file` command to verify it is a `PDF document`.
    3. Copy the verified file to the user's `~/Downloads/` directory and rename it using the requested format (e.g., `{CompanyName}-信用中国报告-{Date}.pdf`).
    4. Clean up the temporary Playwright directory to avoid clutter.

## Example File Retrieval Command
```bash
# Locate the UUID file in Playwright temp directory, confirm it's a PDF, and rename it.
cp /var/folders/.../playwright-artifacts-.../d91d2feb-193d... ~/Downloads/公司名-信用中国报告-20260314.pdf
```
