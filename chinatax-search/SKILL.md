---
name: chinatax-search
description: Automates searching for major tax violation cases on the State Taxation Administration (Chinatax) platform and its provincial sub-sites. Features intelligent provincial routing based on company names, complex multi-tab DOM interaction, and exact background PDF rendering.
---

# China Tax Major Violations Search Skill (V2 - Headless Default)

This skill provides an automated flow to search the National China Tax platform ("重大税收违法失信案件信息公布栏") for a specific company name. 

**V2 Update**: The skill now runs in **Headless Mode** by default. You can use the `--headful` flag to see the browser window.

## When to Use

Use this skill when the user explicitly requests to:
1. Search the China Tax (国家税务总局 - 重大税收违法查询) platform.
2. Query major tax violation entities for a specific company name on `chinatax.gov.cn` and its provincial sub-sites.
3. Generate an exact screenshot/PDF print of the search result for archiving.

## Execution Requirements

This skill relies on a standalone Python script located at `scripts/chinatax_search.py` because handling cross-origin tab spawning (`target="_blank"`) and subsequent AJAX-based table rendering requires Playwright's `context.expect_page()` and `networkidle` listeners.

### Dependencies
Ensure the system has the standard python modules available in its active environment:
* `playwright`

## Usage Instructions

To execute the skill on behalf of the user, run the bundled python script using the `run_command` tool.

**Format:**
```bash
python3 ~/.gemini/antigravity/skills/chinatax-search/scripts/chinatax_search.py "<Company Name>" "<Optional_Output_PDF_Path>" [--headful]
```

**Options**:
- `--headful`: (Optional) Open the browser window to see the interaction.

**Example:**
If the user asks to search for "成都睿源云启科技有限公司", you should execute:
```bash
python3 ~/.gemini/antigravity/skills/chinatax-search/scripts/chinatax_search.py "成都睿源云启科技有限公司" "~/Downloads/成都睿源云启科技有限公司-重大税收违法失信主体信息-20260314.pdf"
```

## How It Works Internally
1. **Intelligent Routing**: The script contains a mapping dictionary (`REGION_TO_PROVINCE`) that infers the target province based on the prefix of the company name (e.g., "成都..." -> "四川").
2. **National Portal**: It browses to the national index at `https://www.chinatax.gov.cn/chinatax/c101249/n2020011502/index.html`.
3. **Provincial Tab Capture**: It clicks the corresponding province link and intercepts the newly spawned browser tab using `context.expect_page()`.
4. **Form Interaction**: On the provincial page (e.g., Sichuan), it precisely targets custom attribute inputs like `input[search-field="title"]` to inject the company name and triggers the `#search` submit button.
5. **AJAX Wait & Render**: It waits for the asynchronous data tables to load via `networkidle` blockers, then generates a `print_background=True` A4 PDF with exact standard headers and footers intact.
