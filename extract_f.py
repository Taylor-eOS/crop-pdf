import fitz
import sys
import os

def extract_text(pdf_file):
    # Open the PDF file
    doc = fitz.open(pdf_file)
    full_text = ""
    previous_block = None
    previous_line = None
    for page_num in range(doc.page_count):
        page = doc.load_page(page_num)
        blocks = page.get_text("dict")["blocks"]

        for block in blocks:
            if block['type'] == 0:  # Process only text blocks
                for line in block["lines"]:
                    current_line = ""
                    for span in line["spans"]:
                        text = span['text'].strip()  # Remove unnecessary spaces

                        # Check if the span is a headline (based on font size)
                        if span['size'] > 12:  # Adjust as needed for headline detection
                            full_text += f"\n<H1>{text}</H1>\n"
                        else:
                            # If we have a previous line, check for space handling
                            if previous_line:
                                # Ensure no double spaces between lines
                                if not previous_line.endswith("-"):
                                    current_line += " "
                            current_line += text
                    
                    # Add the processed line to the full text
                    full_text += current_line
                    previous_line = current_line  # Keep track of the last processed line

            full_text += "\n"  # Newline after each block for clean separation

    doc.close()
    return full_text

def save_to_file(text, output_file):
    # Write the extracted text to the output file
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(text)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python script.py <pdf_file>")
        sys.exit(1)
    
    pdf_file = sys.argv[1]
    
    if not os.path.exists(pdf_file):
        print(f"Error: File '{pdf_file}' not found!")
        sys.exit(1)

    output_file = f"{os.path.splitext(pdf_file)[0]}_output.txt"
    text = extract_text(pdf_file)
    save_to_file(text, output_file)
    
    print(f"Text extracted and saved to '{output_file}'")
