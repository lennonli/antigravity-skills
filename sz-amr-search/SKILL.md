# Shenzhen AMR Administrative Penalty Search (深圳双公示查询)

Automates the search for administrative penalties on the Shenzhen Market Supervision and Administration Bureau website.

## V2 Version Status
- **Headless Default**: Runs in invisible mode for efficiency.
- **Header/Background**: PDFs include official-style headers and backgrounds.

## Usage

```bash
python3 ~/.gemini/antigravity/skills/sz-amr-search/scripts/sz_amr_search.py "公司名称"
```

### Options
- `--headful`: Run with visible browser window for debugging.
- `output_path`: Optional second argument to specify the PDF filename.

## Workflow
1. Navigates to `amr.sz.gov.cn` double-publicity list.
2. Clicks the "行政处罚公示" (Administrative Penalty Publicity) tab.
3. Inputs the company name and triggers an AJAX search.
4. Waits for the result table or "No results" indicator.
5. Prepends a custom header and exports the page as a formatted PDF.
