import fitz  # PyMuPDF
import os
import re

# Store adjustments per page in a dictionary
page_adjustments = {}

def apply_adjustments(doc, original_rects):
    for i, page in enumerate(doc):
        original_rect = original_rects[i]
        media_box = page.mediabox

        # Get the specific adjustments for the current page
        adjustments = page_adjustments.get(i, {'l': 0, 'r': 0, 't': 0, 'b': 0})

        try:
            # Apply the left, right, top, and bottom adjustments
            new_rect = fitz.Rect(
                max(media_box.x0, original_rect.x0 + adjustments['l']),
                max(media_box.y0, original_rect.y0 + adjustments['t']),
                min(media_box.x1, original_rect.x1 - adjustments['r']),
                min(media_box.y1, original_rect.y1 - adjustments['b'])
            )

            # Apply the new crop box, ensuring the values stay within MediaBox limits
            page.set_cropbox(new_rect)
        except ValueError as e:
            print(f"Warning: Could not apply adjustments to page {i+1}. Error: {e}")

def process_input(command):
    # Match the input command structure (e.g., '5r4' where 5 is page, r is right margin, 4 is adjustment)
    match = re.match(r"(\d+)([lrtb])([-+]?\d*\.?\d+)", command)
    if not match:
        print("Invalid command format. Use '5r4' for page 5, right margin +4.")
        return

    page_num = int(match.group(1)) - 1  # Page numbers are 0-indexed
    margin_side = match.group(2)
    value = float(match.group(3))

    if page_num < 0:
        print("Invalid page number.")
        return

    # Update adjustments for the specific page
    if page_num not in page_adjustments:
        page_adjustments[page_num] = {'l': 0, 'r': 0, 't': 0, 'b': 0}

    page_adjustments[page_num][margin_side] += value

def main():
    while True:
        pdf_path = input("Enter the full path to the PDF file (default: input.pdf): ") or "input.pdf"
        
        if not os.path.exists(pdf_path):
            print(f"File '{pdf_path}' does not exist. Please enter a valid file path.")
            continue
        
        doc = fitz.open(pdf_path)
        break

    original_rects = [page.rect for page in doc]

    while True:
        command = input("Enter margin adjustment (e.g., '5r4' for page 5, right +4), or 'exit': ")
        if command == 'exit':
            break

        process_input(command)
        apply_adjustments(doc, original_rects)

        # Save changes to a new file
        new_file_path = pdf_path.replace('.pdf', '_cropped.pdf')
        doc.save(new_file_path)
        print(f"Changes saved to {new_file_path}")

    doc.close()

if __name__ == "__main__":
    main()