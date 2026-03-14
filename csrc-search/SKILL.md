---
name: csrc-search
description: Automates searching and downloading dishonesty records from the CSRC (China Securities Regulatory Commission) platform (neris.csrc.gov.cn/shixinchaxun/). Bypasses specific sliding captchas using OpenCV and generates highly formatted PDF prints of the result page.
---

# CSRC Dishonest Records Search Skill (V2 - Headless Default)

This skill provides an automated flow to search the China Securities Regulatory Commission (CSRC) database for a specific individual or entity and generate a formatted PDF document containing the results. 

**V2 Update**: The skill now runs in **Headless Mode** by default. You can visually debug the captcha process by adding the `--headful` flag.

## When to Use

Use this skill when the user explicitly requests to:
1. Search the CSRC (证券期货市场失信记录查询平台) platform.
2. Look up dishonesty or penalty records for a specific name (姓名/名称) and ID (统一社会信用代码/身份证号码) on `neris.csrc.gov.cn`.
3. Generate an exact screenshot/PDF print of the search result for archiving.

## Execution Requirements

This skill is powered by a standalone Python script located at `scripts/csrc_search.py` because passing the slider captcha and generating an exact `print_background=True` PDF requires lower-level Playwright and computer vision integrations than a standard subagent.

### Dependencies
Ensure the system has the following python packages available in its active environment:
* `playwright`
* `opencv-python`
* `numpy`

## Usage Instructions

To execute the skill on behalf of the user, run the bundled python script using the `run_command` tool.

**Format:**
```bash
python3 ~/.gemini/antigravity/skills/csrc-search/scripts/csrc_search.py "<Name>" "<ID>" "<Optional_Output_PDF_Path>" [--headful]
```

**Options**:
- `--headful`: (Optional) Open the browser window to see the interaction.

**Example:**
If the user asks to search for "成都睿源云启科技有限公司" with ID "91510100MA6DF63234", you should execute:
```bash
python3 ~/.gemini/antigravity/skills/csrc-search/scripts/csrc_search.py "成都睿源云启科技有限公司" "91510100MA6DF63234" "~/Downloads/成都睿源云启科技有限公司-失信记录-20260314.pdf"
```

## How It Works Internally
1. The script browses to `https://neris.csrc.gov.cn/shixinchaxun/honestyObj/query.do`.
2. It uses `page.evaluate` to bypass potential keyboard encodings and directly modifies Vue element `value` attributes.
3. It clicks the `搜索` (Search) button.
4. If a generic sliding puzzle captcha appears, it pulls the `base64` versions of the background image and puzzle slice, uses `cv2.matchTemplate()` to find the exact gap coordinate, and utilizes human-mimicking randomized mouse moves (`page.mouse.move()` with overshoot/rebound logic) to slide the knob precisely.
5. It captures the newly spawned `BrowserContext` tab which contains the result datatable.
6. Once the page state reaches `networkidle`, the script uses `page.pdf()` to print a highly-formatted A4 background-rendered version directly to the disk without native OS dialog prompts.
