import fitz  # PyMuPDF
import os
import re

def apply_adjustments(doc, original_rects, adjustments, odd_offset):
    for i, page in enumerate(doc):
        original_rect = original_rects[i]
        media_box = page.mediabox

        try:
            # Apply the left, right, top, and bottom adjustments to both even and odd pages
            new_rect = fitz.Rect(
                max(media_box.x0, original_rect.x0 + adjustments['l']),
                max(media_box.y0, original_rect.y0 + adjustments['t']),
                min(media_box.x1, original_rect.x1 - adjustments['r']),
                min(media_box.y1, original_rect.y1 - adjustments['b'])
            )

            # If the page is odd, additionally apply the odd page offset, but stay within MediaBox
            if i % 2 != 0:  # Odd pages
                new_rect = fitz.Rect(
                    max(media_box.x0, new_rect.x0 + odd_offset),  # Ensure it doesn't go past the left boundary
                    new_rect.y0,
                    min(media_box.x1, new_rect.x1 + odd_offset),  # Ensure it doesn't go past the right boundary
                    new_rect.y1
                )

            # Apply the new crop box, but ensure the values stay within the MediaBox limits
            page.set_cropbox(new_rect)
        except ValueError as e:
            print(f"Warning: Could not apply adjustments to page {i+1}. Error: {e}")

def process_input(command, adjustments, odd_offset):
    match = re.match(r"([lrtbo])([-+]?\d*\.?\d+)", command)
    if not match:
        print("Invalid command format. Use 'l5', 'r-5', 'o10', etc.")
        return adjustments, odd_offset

    side_or_offset = match.group(1)
    value = float(match.group(2))

    if side_or_offset in ['l', 'r', 't', 'b']:
        adjustments[side_or_offset] += value
    elif side_or_offset == 'o':
        odd_offset += value
    else:
        print("Invalid command. Use 'l', 'r', 't', 'b', or 'o'.")

    return adjustments, odd_offset

def main():
    while True:
        pdf_path = input("Enter the full path to the PDF file (default: input.pdf): ") or "input.pdf"
        
        if not os.path.exists(pdf_path):
            print(f"File '{pdf_path}' does not exist. Please enter a valid file path.")
            continue
        
        doc = fitz.open(pdf_path)
        break

    original_rects = [page.rect for page in doc]
    adjustments = {'l': 0, 'r': 0, 't': 0, 'b': 0}
    odd_offset = 0

    while True:
        command = input("Enter margin adjustment (e.g., 'l5', 'r-10', 'o5'), or 'exit': ")
        if command == 'exit':
            break

        # Use the new process_input function to interpret and update adjustments
        adjustments, odd_offset = process_input(command, adjustments, odd_offset)

        # Apply the adjustments after every command
        apply_adjustments(doc, original_rects, adjustments, odd_offset)

        # Save changes to a new file
        new_file_path = pdf_path.replace('.pdf', '_cropped.pdf')
        doc.save(new_file_path)
        print(f"Changes saved to {new_file_path}")

    doc.close()

if __name__ == "__main__":
    main()
