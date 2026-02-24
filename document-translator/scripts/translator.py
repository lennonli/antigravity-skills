import os
import sys
import argparse
import subprocess
import platform
from pathlib import Path
import docx
from pypdf import PdfReader
import google.generativeai as genai
from zhipuai import ZhipuAI
from typing import List, Optional

class DocumentTranslator:
    def __init__(self, api_type: str = "gemini", api_key: Optional[str] = None):
        self.api_type = api_type.lower()
        self.api_key = api_key or os.getenv("GOOGLE_API_KEY") if self.api_type == "gemini" else os.getenv("ZHIPU_API_KEY")
        
        if not self.api_key:
            raise ValueError(f"API key for {self.api_type} not found. Please set GOOGLE_API_KEY or ZHIPU_API_KEY environment variable.")
        
        if self.api_type == "gemini":
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel('gemini-1.5-pro')
        elif self.api_type == "zhipu":
            self.client = ZhipuAI(api_key=self.api_key)
        else:
            raise ValueError(f"Unsupported API type: {self.api_type}")

    def extract_text(self, file_path: str) -> str:
        suffix = Path(file_path).suffix.lower()
        if suffix in [".txt", ".md"]:
            with open(file_path, "r", encoding="utf-8") as f:
                return f.read()
        elif suffix == ".docx":
            doc = docx.Document(file_path)
            return "\n".join([p.text for p in doc.paragraphs])
        elif suffix == ".pdf":
            reader = PdfReader(file_path)
            text = ""
            for page in reader.pages:
                text += page.extract_text() + "\n"
            return text
        else:
            raise ValueError(f"Unsupported file format: {suffix}")

    def extract_docx_with_format(self, file_path: str) -> List[dict]:
        doc = docx.Document(file_path)
        data = []
        for p in doc.paragraphs:
            para_data = {
                "text": p.text,
                "alignment": p.alignment,
                "style": p.style.name if p.style else None,
                "paragraph_format": {
                    "line_spacing": p.paragraph_format.line_spacing,
                    "space_before": p.paragraph_format.space_before,
                    "space_after": p.paragraph_format.space_after,
                    "left_indent": p.paragraph_format.left_indent,
                },
                "runs": []
            }
            if p.runs:
                # We'll take the first run's formatting as a representative for the paragraph
                # because splitting translated text back into multiple formatted runs is unreliable.
                first_run = p.runs[0]
                para_data["font_format"] = {
                    "name": first_run.font.name,
                    "size": first_run.font.size,
                    "bold": first_run.bold,
                    "italic": first_run.italic,
                    "color": first_run.font.color.rgb if first_run.font.color else None
                }
            data.append(para_data)
        return data

    def translate_text(self, text: str, target_lang: str = "Chinese") -> str:
        if not text.strip():
            return ""
        prompt = f"Translate the following text into {target_lang}. Maintain the original tone and formatting as much as possible. Only return the translated text.\n\nText:\n{text}"
        
        if self.api_type == "gemini":
            response = self.model.generate_content(prompt)
            return response.text.strip()
        elif self.api_type == "zhipu":
            response = self.client.chat.completions.create(
                model="glm-4",
                messages=[
                    {"role": "user", "content": prompt}
                ],
            )
            return response.choices[0].message.content.strip()
        return ""

    def save_formatted_docx(self, formatted_data: List[dict], output_path: str):
        doc = docx.Document()
        for item in formatted_data:
            p = doc.add_paragraph(item["translated_text"])
            
            # Application of paragraph formatting
            if item["alignment"] is not None:
                p.alignment = item["alignment"]
            
            fmt = item["paragraph_format"]
            p.paragraph_format.line_spacing = fmt["line_spacing"]
            p.paragraph_format.space_before = fmt["space_before"]
            p.paragraph_format.space_after = fmt["space_after"]
            p.paragraph_format.left_indent = fmt["left_indent"]
            
            # Application of font formatting (to the whole translated paragraph for consistency)
            if "font_format" in item:
                run = p.runs[0]
                ff = item["font_format"]
                run.font.name = ff["name"]
                run.font.size = ff["size"]
                run.bold = ff["bold"]
                run.italic = ff["italic"]
                if ff["color"]:
                    run.font.color.rgb = ff["color"]
                    
        doc.save(output_path)

    def open_file(self, file_path: str):
        if platform.system() == "Darwin":  # macOS
            subprocess.run(["open", file_path])
        elif platform.system() == "Windows":  # Windows
            os.startfile(file_path)
        else:  # Linux
            subprocess.run(["xdg-open", file_path])

    def process(self, input_file: str, output_file: str, target_lang: str = "Chinese", skip_open: bool = False):
        suffix = Path(input_file).suffix.lower()
        
        if suffix == ".docx":
            print(f"Extracting formatted text from {input_file}...")
            paras = self.extract_docx_with_format(input_file)
            
            print(f"Translating paragraphs using {self.api_type} (this may take a while for large docs)...")
            for i, para in enumerate(paras):
                if para["text"].strip():
                    print(f"  Translating paragraph {i+1}/{len(paras)}...")
                    para["translated_text"] = self.translate_text(para["text"], target_lang)
                else:
                    para["translated_text"] = para["text"]
            
            print(f"Saving formatted translation to {output_file}...")
            self.save_formatted_docx(paras, output_file)
            
        else:
            print(f"Extracting raw text from {input_file}...")
            text = self.extract_text(input_file)
            
            print(f"Translating using {self.api_type}...")
            translated_text = self.translate_text(text, target_lang)
            
            print(f"Saving translation to {output_file}...")
            # For non-docx, we use a simple save
            doc = docx.Document()
            for p_text in translated_text.split("\n"):
                if p_text.strip():
                    doc.add_paragraph(p_text.strip())
            doc.save(output_file)
        
        if not skip_open:
            print(f"Opening {output_file}...")
            self.open_file(output_file)
        print("Done!")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Translate documents using Gemini or Zhipu AI.")
    parser.add_argument("input", help="Path to input file (txt, docx, pdf)")
    parser.add_argument("--output", help="Path to output docx file")
    parser.add_argument("--api", default="gemini", choices=["gemini", "zhipu"], help="AI API to use")
    parser.add_argument("--lang", default="Chinese", help="Target language")
    
    args = parser.parse_args()
    
    output_path = args.output or str(Path(args.input).with_suffix(".translated.docx"))
    
    try:
        translator = DocumentTranslator(api_type=args.api)
        translator.process(args.input, output_path, args.lang)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
