---
name: docx-color-fixer
description: Fixes specific text or numbering colors in Word documents (.docx files). Use this skill when users want to change all occurrences of a specific text color (like a blue hex code) to another color (like black/auto) across an entire Word document.
---

# Docx Color Fixer

This skill automates the process of unpacking a `.docx` file, sweeping through all internal XML files (like `word/document.xml`, `word/numbering.xml`, `word/styles.xml`, etc.) to find and replace a specific text color hex code, and repacking the document.

## When to use

Use this skill when a user asks to:
- "Change all the blue numbers to black in this Word document"
- "Fix the numbering color in this docx file"
- "Replace color X with color Y in a Word document"

## How to use

This skill provides a Python script that handles the entire extraction, modification, and repacking process safely.

Run the provided script `scripts/fix_docx_color.py`:

```bash
# Basic usage (replaces 3370FF with auto in-place)
python3 scripts/fix_docx_color.py "/path/to/document.docx"

# Specify a different output file
python3 scripts/fix_docx_color.py "/path/to/input.docx" --output "/path/to/output.docx"

# Specify custom colors to replace (e.g., replacing red FF0000 with black 000000)
python3 scripts/fix_docx_color.py "/path/to/document.docx" --old-color "FF0000" --new-color "000000"
```

### Script Arguments:
- `input`: The absolute path to the `.docx` file you want to process.
- `--output` (or `-o`): (Optional) The absolute path for the modified `.docx` file. If omitted, it overwrites the input file.
- `--old-color` (or `-c`): The hex color code to search for (default: `3370FF` - a common blue color). Do not include the `#` symbol.
- `--new-color` (or `-n`): The new color value to apply (default: `auto` which maps to the document's default text color, usually black).
