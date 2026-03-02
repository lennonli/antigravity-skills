import os
import glob
import zipfile
import tempfile
import shutil
import argparse

def fix_docx_color(input_path, output_path=None, old_color="3370FF", new_color="auto"):
    if not output_path:
        output_path = input_path
        
    print(f"Fixing color {old_color} to {new_color} in: {input_path}")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        # Extract the docx
        with zipfile.ZipFile(input_path, 'r') as zip_ref:
            zip_ref.extractall(temp_dir)
            
        word_dir = os.path.join(temp_dir, "word")
        if not os.path.exists(word_dir):
            print("Error: Invalid DOCX file (no 'word' directory found).")
            return
            
        # Find all xml files
        xml_files = glob.glob(os.path.join(word_dir, "**/*.xml"), recursive=True)
        replaced_count = 0
        
        for xml_file in xml_files:
            try:
                with open(xml_file, "r", encoding="utf-8") as f:
                    content = f.read()
                
                target_str = f'w:color w:val="{old_color}"'
                replacement_str = f'w:color w:val="{new_color}"'
                
                if target_str in content:
                    print(f"  Replacing in {os.path.relpath(xml_file, temp_dir)}")
                    new_content = content.replace(target_str, replacement_str)
                    
                    with open(xml_file, "w", encoding="utf-8") as f:
                        f.write(new_content)
                    replaced_count += 1
            except Exception as e:
                print(f"  Error processing {xml_file}: {e}")
                
        if replaced_count > 0:
            print(f"Modifications complete in {replaced_count} files. Repacking...")
            # Repack docx
            # Save to a temporary file first if input == output
            with tempfile.NamedTemporaryFile(delete=False, suffix='.docx') as temp_out:
                temp_out_path = temp_out.name
                
            with zipfile.ZipFile(temp_out_path, 'w', zipfile.ZIP_DEFLATED) as zip_out:
                for root, _, files in os.walk(temp_dir):
                    for file in files:
                        file_path = os.path.join(root, file)
                        arcname = os.path.relpath(file_path, temp_dir)
                        zip_out.write(file_path, arcname)
                        
            # Move the temporary output to the final destination
            shutil.move(temp_out_path, output_path)
            print(f"Successfully saved to: {output_path}")
        else:
            print(f"No occurrences of color '{old_color}' found. Document unchanged.")
            # If output path is different, we should still copy the original
            if output_path != input_path:
                shutil.copy2(input_path, output_path)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Fix colors in a DOCX file (e.g., change blue numbering to black)")
    parser.add_argument("input", help="Path to input DOCX file")
    parser.add_argument("--output", "-o", help="Path to output DOCX file (modifies in-place if not provided)", default=None)
    parser.add_argument("--old-color", "-c", help="Hex color to replace (default: 3370FF)", default="3370FF")
    parser.add_argument("--new-color", "-n", help="New color value (default: auto)", default="auto")
    
    args = parser.parse_args()
    fix_docx_color(args.input, args.output, args.old_color, args.new_color)
