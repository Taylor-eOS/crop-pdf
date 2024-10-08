import fitz  # PyMuPDF

def find_footnote_start(page):
    """Attempts to find the start of the footnotes based on text block positions or lines."""
    text_blocks = page.get_text("blocks")
    last_y = 0
    max_gap = 0
    footnote_y_start = page.rect.height

    # Find the largest vertical gap between successive text blocks, assuming it might indicate start of footnotes
    for block in text_blocks:
        rect = fitz.Rect(block[:4])
        if rect.y0 - last_y > max_gap:
            max_gap = rect.y0 - last_y
            footnote_y_start = rect.y0
        last_y = rect.y1

    # Optionally check for lines if no significant gap found
    if max_gap < 20:  # Threshold for deciding if a gap is 'significant'
        lines = page.get_drawings()
        for line in lines:
            if line['width'] > page.rect.width * 0.8 and line['items'][0]['rect'].y0 < footnote_y_start:  # Assumption that line width covers most of the page width
                footnote_y_start = line['items'][0]['rect'].y0

    return footnote_y_start

def remove_footnotes(pdf_path):
    doc = fitz.open(pdf_path)
    new_file_path = pdf_path.replace('.pdf', '_no_footnotes.pdf')

    for page in doc:
        # Find the y-coordinate to start cropping (remove footnotes)
        footnote_y_start = find_footnote_start(page)
        new_crop = fitz.Rect(0, 0, page.rect.width, footnote_y_start)
        page.set_cropbox(new_crop)

    doc.save(new_file_path)
    doc.close()
    print(f"Footnotes removed. New file saved as {new_file_path}")

if __name__ == "__main__":
    pdf_path = input("Enter the full path to the PDF file: ")
    remove_footnotes(pdf_path)
