import fitz  # PyMuPDF

def main():
    pdf_path = input("Enter the full path to the PDF file: ")
    doc = fitz.open(pdf_path)

    # Store the original crop boxes for each page to ensure base adjustments are accurate
    original_rects = [page.rect for page in doc]

    # Initialize adjustments
    adjustments = {'l': 0, 'r': 0, 't': 0, 'b': 0}

    # Track additional offset for odd pages
    odd_offset = 0

    while True:
        command = input("Enter margin adjustment (format: side value), 'o value' for odd pages shift, or 'exit': ")
        if command == 'exit':
            break

        parts = command.split()
        if len(parts) != 2:
            print("Invalid command format. Use 'side value' or 'o value'.")
            continue

        side_or_offset, value = parts[0], float(parts[1])

        if side_or_offset in ['l', 'r', 't', 'b']:
            # Apply the adjustment cumulatively only to the specified side
            adjustments[side_or_offset] += value
        elif side_or_offset == 'o':
            # Adjust the offset for odd pages
            odd_offset += value
        else:
            print("Invalid command. Use 'l', 'r', 't', 'b', or 'o'.")
            continue

        for i, page in enumerate(doc):
            original_rect = original_rects[i]
            # Get the media box for the current page
            media_box = page.mediabox

            # Apply the offset for odd pages and ensure the new crop box stays within the MediaBox
            if i % 2 != 0:  # Odd page index in zero-based indexing
                new_rect = fitz.Rect(
                    max(media_box.x0, original_rect.x0 + adjustments['l'] + odd_offset),
                    max(media_box.y0, original_rect.y0 + adjustments['t']),
                    min(media_box.x1, original_rect.x1 - adjustments['r'] + odd_offset),
                    min(media_box.y1, original_rect.y1 - adjustments['b'])
                )
            else:
                new_rect = fitz.Rect(
                    max(media_box.x0, original_rect.x0 + adjustments['l']),
                    max(media_box.y0, original_rect.y0 + adjustments['t']),
                    min(media_box.x1, original_rect.x1 - adjustments['r']),
                    min(media_box.y1, original_rect.y1 - adjustments['b'])
                )

            # Set the new crop box
            page.set_cropbox(new_rect)

        # Save changes to a new file
        new_file_path = pdf_path.replace('.pdf', '_cropped.pdf')
        doc.save(new_file_path)
        print(f"Changes saved to {new_file_path}")

    doc.close()

if __name__ == "__main__":
    main()

