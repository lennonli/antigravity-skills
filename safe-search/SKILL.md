---
name: safe-search
description: Automates searching for foreign exchange penalty records on the State Administration of Foreign Exchange (SAFE) platform (safe.gov.cn). Safely interacts with search inputs wrapped in hidden iframes, enforces USCC validation, and generates an exact PDF record.
---

# SAFE Foreign Exchange Penalty Search Skill (V2 - Headless Default)

This skill provides an automated flow to search the State Administration of Foreign Exchange (国家外汇管理局 - 外汇行政处罚信息查询) platform for a specific entity. 

**V2 Update**: This skill now runs in **Headless Mode** (invisible browser) by default. You can use the `--headful` flag to see the browser window.

## When to Use

Use this skill when the user explicitly requests to:
1. Search the SAFE (外汇局/国家外汇管理局) platform for administrative penalties.
2. Query penalty information using a specific company's Unified Social Credit Code (USCC) on `safe.gov.cn`.
3. Generate an exact screenshot/PDF print of the search result for archiving.

## Execution Requirements

This skill relies on a standalone Python script located at `scripts/safe_search.py` because handling nested `iframe` interactions, Javascript execution triggers, and subsequent AJAX-based table rendering requires robust low-level Playwright execution.

### Dependencies
Ensure the system has the standard python modules available in its active environment:
* `playwright`

## Usage Instructions

To execute the skill on behalf of the user, run the bundled python script using the `run_command` tool.

**Format:**
```bash
python3 ~/.gemini/antigravity/skills/safe-search/scripts/safe_search.py "<USCC Code>" "<Company Name for PDF Labeling>" "<Optional_Output_PDF_Path>" [--headful]
```

**Options**:
- `--headful`: (Optional) Open the browser window to see the interaction (useful if the iframe fails to load).

**Note:** The first argument **MUST** be the Unified Social Credit Code (e.g., 914403007504806052). The platform will not accept Chinese character strings. The script has an internal safety check to prevent running if Chinese characters are detected in the USCC field.

**Example:**
If the user asks to search for "大疆创新" with the USCC `914403007504806052`, execute:
```bash
python3 ~/.gemini/antigravity/skills/safe-search/scripts/safe_search.py "914403007504806052" "大疆创新" "~/Downloads/大疆创新-外汇行政处罚信息-20260314.pdf"
```

## How It Works Internally
1. **Validation**: Script checks the input string against Unicode Chinese ranges `[\u4e00-\u9fff]` to ensure the user isn't mistakenly supplying a company name instead of a USCC.
2. **Iframe Penetration**: Browses to the national index at `https://www.safe.gov.cn/safe/whxzcfxxcx/index.html` and targets the embedded `/www/illegal` iframe by polling `page.frames`.
3. **Form Simulation**: Locates the `#irregularityno` field inside the iframe, fills it, and directly invokes the specific window-level `submitForm()` javascript function to bypass brittle UI clicks.
4. **AJAX Wait & Render**: Waits for the asynchronous data tables to load via `networkidle` blockers, then generates a `print_background=True` A4 PDF with exact standard headers and footers intact.
