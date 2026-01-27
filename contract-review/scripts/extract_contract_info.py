#!/usr/bin/env python3
"""
Extract key information from contract documents.

This script extracts essential contract information including parties, dates,
key terms, and creates a structured summary.

Usage:
    python extract_contract_info.py <contract_file_path>
"""

import sys
import os
from pathlib import Path
import re
from datetime import datetime


def extract_contract_info(file_path):
    """
    Extract key information from a contract document.
    
    Args:
        file_path: Path to the contract file (.txt, .docx, or .pdf)
    
    Returns:
        Dictionary containing extracted contract information
    """
    
    file_ext = Path(file_path).suffix.lower()
    
    # Read contract text based on file type
    if file_ext == '.txt':
        with open(file_path, 'r', encoding='utf-8') as f:
            text = f.read()
    elif file_ext == '.docx':
        try:
            from docx import Document
            doc = Document(file_path)
            text = '\n'.join([para.text for para in doc.paragraphs])
        except ImportError:
            print("Error: python-docx not installed. Install with: pip install python-docx")
            sys.exit(1)
    elif file_ext == '.pdf':
        try:
            import PyPDF2
            with open(file_path, 'rb') as f:
                reader = PyPDF2.PdfReader(f)
                text = ''
                for page in reader.pages:
                    text += page.extract_text()
        except ImportError:
            print("Error: PyPDF2 not installed. Install with: pip install PyPDF2")
            sys.exit(1)
    else:
        print(f"Error: Unsupported file type {file_ext}")
        sys.exit(1)
    
    # Extract information
    info = {
        'file_name': Path(file_path).name,
        'file_path': file_path,
        'extraction_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'contract_title': extract_title(text),
        'parties': extract_parties(text),
        'dates': extract_dates(text),
        'governing_law': extract_governing_law(text),
        'key_amounts': extract_amounts(text),
        'contract_type': identify_contract_type(text),
        'key_sections': extract_key_sections(text)
    }
    
    return info


def extract_title(text):
    """Extract contract title from the first few lines."""
    lines = text.strip().split('\n')
    # Usually contract title is in the first 5 lines
    for line in lines[:5]:
        line = line.strip()
        if len(line) > 10 and len(line) < 100:  # Reasonable title length
            # Remove common prefixes
            if any(keyword in line for keyword in ['协议', '合同', 'Agreement', 'Contract']):
                return line
    return "Unknown"


def extract_parties(text):
    """Extract contracting parties."""
    parties = []
    
    # Chinese patterns
    cn_patterns = [
        r'甲方[：:]\s*([^\n）)]+)',
        r'乙方[：:]\s*([^\n）)]+)',
        r'丙方[：:]\s*([^\n）)]+)',
        r'投资方[：:]\s*([^\n）)]+)',
        r'目标公司[：:]\s*([^\n）)]+)',
    ]
    
    # English patterns
    en_patterns = [
        r'Party A[:\s]+([^\n]+?)(?=\(|$)',
        r'Party B[:\s]+([^\n]+?)(?=\(|$)',
        r'between\s+([^"and]+?)\s+and\s+([^\n]+)',
    ]
    
    for pattern in cn_patterns + en_patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        for match in matches:
            if isinstance(match, tuple):
                parties.extend([m.strip() for m in match if m.strip()])
            else:
                parties.append(match.strip())
    
    # Remove duplicates while preserving order
    seen = set()
    unique_parties = []
    for party in parties:
        if party not in seen and len(party) > 2:
            seen.add(party)
            unique_parties.append(party)
    
    return unique_parties[:10]  # Limit to first 10


def extract_dates(text):
    """Extract important dates from contract."""
    dates = {}
    
    # Execution date patterns
    execution_patterns = [
        r'签署日期[：:]\s*(\d{4})\s*年\s*(\d{1,2})\s*月\s*(\d{1,2})\s*日',
        r'签订日期[：:]\s*(\d{4})\s*年\s*(\d{1,2})\s*月\s*(\d{1,2})\s*日',
        r'Date[:\s]+([A-Z][a-z]+\s+\d{1,2},\s*\d{4})',
        r'Dated[:\s]+([A-Z][a-z]+\s+\d{1,2},\s*\d{4})',
        r'(\d{4})\s*年\s*(\d{1,2})\s*月\s*(\d{1,2})\s*日',
    ]
    
    for pattern in execution_patterns:
        match = re.search(pattern, text)
        if match:
            dates['execution_date'] = match.group(0)
            break
    
    # Effective date
    effective_patterns = [
        r'生效日期[：:]\s*([^\n]+)',
        r'Effective\s+Date[:\s]+([^\n]+)',
    ]
    
    for pattern in effective_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            dates['effective_date'] = match.group(1).strip()
            break
    
    # Term/Duration
    term_patterns = [
        r'期限[：:]\s*([^\n]+)',
        r'Term[:\s]+([^\n]+)',
        r'有效期[：:]\s*([^\n]+)',
    ]
    
    for pattern in term_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            dates['term'] = match.group(1).strip()
            break
    
    return dates


def extract_governing_law(text):
    """Extract governing law clause."""
    patterns = [
        r'适用法律[：:]\s*([^\n]+)',
        r'准据法[：:]\s*([^\n]+)',
        r'本协议适用([^\n]*?法律)',
        r'Governing\s+Law[:\s]+([^\n]+)',
        r'governed\s+by\s+(?:the\s+)?laws?\s+of\s+([^\n,\.]+)',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return match.group(1).strip()
    
    return None


def extract_amounts(text):
    """Extract key monetary amounts."""
    amounts = []
    
    # RMB patterns
    rmb_patterns = [
        r'人民币\s*([\d,，]+(?:\.\d+)?)\s*(?:元|万元)',
        r'RMB\s*([\d,，]+(?:\.\d+)?)',
        r'¥\s*([\d,，]+(?:\.\d+)?)',
    ]
    
    # USD patterns
    usd_patterns = [
        r'\$\s*([\d,]+(?:\.\d+)?)',
        r'USD\s*([\d,]+(?:\.\d+)?)',
    ]
    
    for pattern in rmb_patterns + usd_patterns:
        matches = re.findall(pattern, text)
        amounts.extend(matches[:5])  # Limit to first 5
    
    return amounts


def identify_contract_type(text):
    """Identify the type of contract based on keywords."""
    contract_types = {
        '股东协议': ['股东协议', 'Shareholder Agreement', '股权协议'],
        '投资协议': ['投资协议', 'Investment Agreement', '融资协议', 'Financing Agreement'],
        '劳动合同': ['劳动合同', 'Employment Contract', 'Employment Agreement'],
        '保密协议': ['保密协议', 'Non-Disclosure Agreement', 'NDA', 'Confidentiality Agreement'],
        '服务协议': ['服务协议', 'Service Agreement', '咨询协议', 'Consulting Agreement'],
        '采购合同': ['采购合同', 'Purchase Agreement', '买卖合同', 'Sales Contract'],
        '租赁协议': ['租赁协议', 'Lease Agreement', '租赁合同'],
        '借款协议': ['借款协议', 'Loan Agreement', '贷款合同'],
    }
    
    text_lower = text.lower()
    
    for contract_type, keywords in contract_types.items():
        for keyword in keywords:
            if keyword.lower() in text_lower:
                return contract_type
    
    return "未分类 / Unclassified"


def extract_key_sections(text):
    """Extract key section headings from the contract."""
    sections = []
    
    # Common section patterns (both numbered and unnumbered)
    section_patterns = [
        r'^(?:第[一二三四五六七八九十百]+条|Article\s+\d+)[：:、\s]+(.+)$',
        r'^\d+[\.\、]\s*(.+)$',
        r'^[一二三四五六七八九十]+[\.\、]\s*(.+)$',
    ]
    
    lines = text.split('\n')
    for line in lines:
        line = line.strip()
        if len(line) > 5 and len(line) < 100:  # Reasonable section heading length
            for pattern in section_patterns:
                match = re.match(pattern, line)
                if match and not any(char.isdigit() for char in match.group(1)[:5]):
                    sections.append(match.group(1).strip())
                    break
    
    # Remove duplicates and limit
    seen = set()
    unique_sections = []
    for section in sections:
        if section not in seen:
            seen.add(section)
            unique_sections.append(section)
    
    return unique_sections[:20]  # Limit to first 20 sections


def format_output(info):
    """Format extracted information for display."""
    output = []
    output.append("=" * 80)
    output.append("合同信息提取报告 / Contract Information Extraction Report")
    output.append("=" * 80)
    output.append(f"\n文件名称 / File Name: {info['file_name']}")
    output.append(f"提取时间 / Extraction Time: {info['extraction_date']}")
    output.append(f"\n合同标题 / Contract Title:\n  {info['contract_title']}")
    output.append(f"\n合同类型 / Contract Type:\n  {info['contract_type']}")
    
    if info['parties']:
        output.append(f"\n合同各方 / Parties:")
        for i, party in enumerate(info['parties'], 1):
            output.append(f"  {i}. {party}")
    
    if info['dates']:
        output.append(f"\n重要日期 / Important Dates:")
        for key, value in info['dates'].items():
            output.append(f"  {key}: {value}")
    
    if info['governing_law']:
        output.append(f"\n适用法律 / Governing Law:\n  {info['governing_law']}")
    
    if info['key_amounts']:
        output.append(f"\n关键金额 / Key Amounts:")
        for amount in info['key_amounts']:
            output.append(f"  {amount}")
    
    if info['key_sections']:
        output.append(f"\n主要章节 / Key Sections:")
        for i, section in enumerate(info['key_sections'][:10], 1):
            output.append(f"  {i}. {section}")
    
    output.append("\n" + "=" * 80)
    
    return '\n'.join(output)


def main():
    if len(sys.argv) < 2:
        print("Usage: python extract_contract_info.py <contract_file_path>")
        sys.exit(1)
    
    file_path = sys.argv[1]
    
    if not os.path.exists(file_path):
        print(f"Error: File not found: {file_path}")
        sys.exit(1)
    
    print("Extracting contract information...")
    info = extract_contract_info(file_path)
    
    output = format_output(info)
    print(output)
    
    # Optionally save to file
    output_file = Path(file_path).stem + "_extracted_info.txt"
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(output)
    print(f"\nReport saved to: {output_file}")


if __name__ == '__main__':
    main()
