from reportlab.pdfgen import canvas
from PIL import Image
import os

def convert_png_to_pdf(png_path, pdf_path):
    img = Image.open(png_path)
    width, height = img.size
    c = canvas.Canvas(pdf_path, pagesize=(width, height))
    c.drawImage(png_path, 0, 0, width, height)
    c.save()

if __name__ == "__main__":
    src = '/Users/licheng/.gemini/antigravity/brain/7997ab82-5d16-4f1c-88e4-a4ee4629bcbf/court_search_report_licheng_report_1773421701166.png'
    dest = '/Users/licheng/.gemini/antigravity/brain/7997ab82-5d16-4f1c-88e4-a4ee4629bcbf/court_search_report_licheng.pdf'
    convert_png_to_pdf(src, dest)
    print(f"PDF saved to: {dest}")
