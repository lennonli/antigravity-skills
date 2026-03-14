---
name: procuratorate-search
description: Automates searching for records on the China Procuratorate (中国检察网) website (12309.gov.cn). Safely interacts with the search input, handles new tab result spawning, and generates a properly formatted PDF of the results.
---

# China Procuratorate Search Skill (V2 - Headless Default)

This skill provides an automated flow to search the China Procuratorate (12309 中国检察网) platform for a specific company or individual name. 

**V2 Update**: The skill now runs in **Headless Mode** (invisible browser) by default. You can use the `--headful` flag to see the browser window.

## When to Use

Use this skill when the user explicitly requests to:
1. Search the China Procuratorate (中国检察网) platform.
2. Query legal documents, case information, or announcements on `12309.gov.cn`.
3. Generate an exact screenshot/PDF print of the search result for archiving.

## Execution Requirements

This skill relies on a standalone Python script located at `scripts/procuratorate_search.py` because handling new browser tabs (`target="_blank"`) and subsequent page loading requires Playwright's low-level context management.

### Dependencies
Ensure the system has the standard python modules available in its active environment:
* `playwright`

## Usage Instructions

To execute the skill on behalf of the user, run the bundled python script using the `run_command` tool.

**Format:**
```bash
python3 ~/.gemini/antigravity/skills/procuratorate-search/scripts/procuratorate_search.py "<Search Term>" "<Optional_Output_PDF_Path>" [--headful]
```

**Options**:
- `--headful`: (Optional) Open the browser window to see the interaction.

**Example:**
If the user asks to search for "成都睿源云启科技有限公司", you should execute:
```bash
python3 ~/.gemini/antigravity/skills/procuratorate-search/scripts/procuratorate_search.py "成都睿源云启科技有限公司" "~/Downloads/成都睿源云启科技有限公司-中国检察网-20260314.pdf"
```

## How It Works Internally
1. **Initial Access**: Navigates to the main portal at `https://www.12309.gov.cn/12309/index.html`.
2. **Search Action**: Locates the `input[name="text"]` field and fills it with the query term.
3. **Tab Capture**: Since the submit button has `target="_blank"`, the script uses `context.expect_page()` to intercept the search result tab.
4. **AJAX Wait & Render**: Waits for the asynchronous data on the result page to fully load via `networkidle` listeners, then generates a `print_background=True` A4 PDF with exact standard headers and footers.
