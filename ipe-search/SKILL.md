# IPE Environmental Search Automation (绿网核查)

Automates the collection of environmental information from the IPE (Institute of Public & Environmental Affairs) platform.

## Features
- **Slider Captcha Passive Support**: Attempts simple slider solving and supports manual override in headful mode.
- **Recursive Tab Discovery**: Automatically detects tabs with data counts and captures them individually.
- **PDF Merging**: Consolidates the overview and all relevant data tabs into a single PDF report.

## Usage

```bash
python3 ~/.gemini/antigravity/skills/ipe-search/scripts/ipe_search.py "公司名称"
```

### Options
- `--headless`: Run in invisible mode (not recommended due to slider captchas).

## Workflow
1. Navigates to `lvwang.org.cn/search/`.
2. Performs a search and handles the initial slider captcha.
3. Opens the first result in a new tab.
4. Scans the details page for tabs containing data (indicated by numbers in tab labels).
5. Methodically clicks each tab, solves any secondary captchas, and prints the content to a temporary PDF.
6. Merges all generated PDFs (Overview + Data Tabs) into the final report.
