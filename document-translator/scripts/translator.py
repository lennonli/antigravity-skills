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

    def translate_text(self, text: str, target_lang: str = "Chinese") -> str:
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

    def save_to_docx(self, text: str, output_path: str):
        doc = docx.Document()
        # Simple splitting by double newline to preserve some structure
        paragraphs = text.split("\n")
        for p_text in paragraphs:
            if p_text.strip():
                doc.add_paragraph(p_text.strip())
        doc.save(output_path)

    def open_file(self, file_path: str):
        if platform.system() == "Darwin":  # macOS
            subprocess.run(["open", file_path])
        elif platform.system() == "Windows":  # Windows
            os.startfile(file_path)
        else:  # Linux
            subprocess.run(["xdg-open", file_path])

    def process(self, input_file: str, output_file: str, target_lang: str = "Chinese"):
        print(f"Extracting text from {input_file}...")
        text = self.extract_text(input_file)
        
        print(f"Translating using {self.api_type}...")
        translated_text = self.translate_text(text, target_lang)
        
        print(f"Saving translation to {output_file}...")
        self.save_to_docx(translated_text, output_file)
        
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
