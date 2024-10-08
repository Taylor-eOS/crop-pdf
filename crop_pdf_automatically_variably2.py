import fitz  # PyMuPDF

def extract_main_text_bbox(page, margin=3):
    words = page.get_text("words")  # Extract words as a list of rectangles
    if not words:
        return None
    # Define margins for headers and footers (percentage of page height)
    top_margin = 0.1  # 10% of the page height for header
    bottom_margin = 0.1  # 10% of the page height for footer
    page_height = page.rect.height

    # Filter out words that are likely part of the main text area
    main_text_words = [w for w in words if top_margin * page_height < w[1] and w[3] < (1 - bottom_margin) * page_height]
    if not main_text_words:
        return None

    # Calculate bounding box of the main text
    x0 = min(w[0] for w in main_text_words) - margin
    y0 = min(w[1] for w in main_text_words) - margin
    x1 = max(w[2] for w in main_text_words) + margin
    y1 = max(w[3] for w in main_text_words) + margin

    return fitz.Rect(x0, y0, x1, y1)

def recreate_page_with_crop(doc, page_index, crop_rect):
    source_page = doc.load_page(page_index)
    # Create a new blank page
    new_page = doc.new_page(width=crop_rect.width, height=crop_rect.height, pno=page_index)
    # Draw text from the original page to the new page
    text_instances = source_page.search_for(" ", clip=crop_rect)
    for inst in text_instances:
        words = source_page.get_text("words", clip=inst)
        for word in words:
            rect = fitz.Rect(word[:4]) - crop_rect.top_left
            new_page.insert_text(rect.bl, word[4], fontsize=word[3] - word[1])  # Adjust font size based on word height

    # Remove the original page
    doc.delete_page(page_index + 1)  # Remove the original page

def crop_pdf_to_text_area(pdf_path, output_path, margin=3):
    doc = fitz.open(pdf_path)
    for page_num in reversed(range(doc.page_count)):  # Start from the last page
        page = doc.load_page(page_num)
        main_text_bbox = extract_main_text_bbox(page, margin)
        if main_text_bbox:
            recreate_page_with_crop(doc, page_num, main_text_bbox)
    doc.save(output_path, garbage=4, deflate=True)
    doc.close()

# Usage example
pdf_path = 'input.pdf'
output_path = 'cropped_output.pdf'
crop_pdf_to_text_area(pdf_path, output_path, margin=3)

