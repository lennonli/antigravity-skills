from docx import Document
from docx.oxml.ns import qn
import sys

def modify_numbering(docx_path):
    doc = Document(docx_path)
    try:
        numbering_part = doc.part.numbering_part
        if numbering_part is None:
            print("No numbering part found.")
            return
            
        numbering_xml = numbering_part._element
        
        # Look for w:lvlText and w:numFmt inside w:lvl
        lvls = numbering_xml.xpath('//w:lvl')
        for lvl in lvls:
            # Check numFmt
            numFmt = lvl.find(qn('w:numFmt'))
            if numFmt is not None:
                val = numFmt.get(qn('w:val'))
                print(f"Original numFmt: {val}")
                if val in ["chineseCounting", "chineseLegalCounting", "ideographTraditional", "ideographZodiac", "ideographZodiacTraditional", "taiwaneseCounting", "taiwaneseCountingThousand", "chineseCountingThousand"]:
                    numFmt.set(qn('w:val'), 'decimal')
                    print(f"  -> Changed to decimal")
            
            # Check lvlText
            lvlText = lvl.find(qn('w:lvlText'))
            if lvlText is not None:
                val = lvlText.get(qn('w:val'))
                print(f"Original lvlText: {val}")
                if val:
                    # Basic replacments for testing
                    new_val = val.replace("第", "Article ").replace("条", "").replace("章", "Chapter ").replace("节", "Section ")
                    # If it was entirely Chinese characters but now we replaced, we might just want to use Article %1 etc.
                    # but if it was just "%1", it stays "%1".
                    if new_val != val:
                        # Clean up formatting, e.g., "Article %1"
                        new_val = new_val.strip()
                        lvlText.set(qn('w:val'), new_val)
                        print(f"  -> Changed to {new_val}")
                        
        doc.save(docx_path + ".modified.docx")
        print("Done modifying numbering XML.")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        modify_numbering(sys.argv[1])
