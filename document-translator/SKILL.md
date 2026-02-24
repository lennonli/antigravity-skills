---
name: document-translator
description: This skill should be used when a user wants to translate a document (PDF, Word, or Text) into a Word file (.docx) using either Google Gemini or Zhipu AI (GLM).
---

# Document Translator

This skill uses LLM APIs (Gemini or Zhipu AI) to translate documents while preserving a simple paragraph structure in the output Word file.

## Setup

The skill requires at least one of the following environment variables to be set:
- `GOOGLE_API_KEY`: Required for Gemini translation.
- `ZHIPU_API_KEY`: Required for Zhipu AI (ChatGLM) translation.

## Usage

To translate a document, call the `scripts/translator.py` script.

### Command Format

```bash
python3 scripts/translator.py <input_file> [--output <output_file>] [--api <gemini|zhipu>] [--lang <target_language>]
```

### Parameters

- `input_file`: Path to the source document (.pdf, .docx, .txt).
- `--output`: (Optional) Path for the output file. Defaults to `<input_name>.translated.docx`.
- `--api`: (Optional) AI engine to use. Defaults to `gemini`.
- `--lang`: (Optional) Target language for translation. Defaults to `Chinese`.

## Examples

### Using Gemini (Default)
To translate a PDF to Chinese using Gemini:
```bash
python3 scripts/translator.py my_doc.pdf
```

### Using Zhipu AI
To translate a Word document to English using Zhipu AI:
```bash
python3 scripts/translator.py report.docx --api zhipu --lang English
```

### Specifying Output Path
```bash
python3 scripts/translator.py manual.txt --output translated_manual.docx --lang Japanese
```

## How it Works

1. **Extraction**: The script extracts plain text from the provided file using `pypdf` (for PDF), `python-docx` (for DOCX), or native file reading (for TXT).
2. **Translation**: The extracted text is sent to the chosen AI API with a prompt to translate into the target language while maintaining tone.
3. **Generation**: The translated text is written into a new Word document using `python-docx`, with basic paragraph preservation.
4. **Auto-Open**: Once saved, the script will automatically open the generated `.docx` file using the system's default application.
