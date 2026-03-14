---
name: samr-search
description: Automates searching for penalty case documents on the SAMR (State Administration for Market Regulation) website (cfws.samr.gov.cn). Safely interacts with search inputs, catches results spawned in new browser tabs, and generates an exact PDF record.
---

# SAMR Penalty Document Search Skill (V2 - Headless Default)

This skill provides an automated flow to search the National Market Regulation Administration's penalty document platform (cfws.samr.gov.cn) for a specific company name or credit code. 

**V2 Update**: The skill now runs in **Headless Mode** (invisible browser) by default for silent operation.

## When to Use

Use this skill when the user explicitly requests to:
1. Search the SAMR (国家市场监督管理总局-行政处罚文书网) platform.
2. Query administrative penalty documents for a specific company name or ID on `cfws.samr.gov.cn`.
3. Generate an exact screenshot/PDF print of the search result for archiving.

## Execution Requirements

This skill relies on a standalone Python script located at `scripts/samr_search.py` because waiting for the proper `networkidle` states across dynamically opened browser context tabs requires low-level execution control via Playwright.

### Dependencies
Ensure the system has the standard python modules available in its active environment:
* `playwright`

## Usage Instructions

To execute the skill on behalf of the user, run the bundled python script using the `run_command` tool.

**Format:**
```bash
python3 ~/.gemini/antigravity/skills/samr-search/scripts/samr_search.py "<Company Name or ID>" "<Optional_Output_PDF_Path>"
```

**Example:**
If the user asks to search for "无锡威易发精密机械股份有限公司", you should execute:
```bash
python3 ~/.gemini/antigravity/skills/samr-search/scripts/samr_search.py "无锡威易发精密机械股份有限公司" "~/Downloads/无锡威易发精密机械股份有限公司-行政处罚文书网-20260314.pdf"
```

## How It Works Internally
1. The script browses to `https://cfws.samr.gov.cn/`.
2. It interacts with the complex Vue/JQuery inputs, specifically targeting the `#keyword` ID, injecting the search term and circumventing keystroke blocking mechanisms via `.evaluate()`.
3. It clicks the `.quickly-entry a` (magnifying glass) retrieve button.
4. Crucially, the SAMR platform forces results to open into an entirely new browser tab (`target="_blank"` equivalent framework routing). The script intercepts this using `context.expect_page()`.
5. It switches execution focus to the newly captured `result_page` and invokes a `networkidle` blocker to wait until all tables have fully rendered.
6. Automatically formats a `print_background=True` A4 PDF with exact standard headers and footers intact.
