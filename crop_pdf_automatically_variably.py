import fitz  # PyMuPDF
import numpy as np

def extract_main_text_bbox(page, margin=3):
    """
    Extracts the bounding box of the main text on the page, excluding headers, footers, and footnotes,
    and adds a margin around the text.
    """
    words = page.get_text("words")  # Extract words as a list of (x0, y0, x1, y1, word, block_no, line_no, word_no)
    if not words:
        return None

    # Define margins for headers and footers (percentage of page height)
    top_margin = 0.1  # 10% of the page height for header
    bottom_margin = 0.1  # 10% of the page height for footer
    page_height = page.rect.height

    # Determine the average font height by calculating the median y1 - y0
    heights = [y1 - y0 for x0, y0, x1, y1, *rest in words]
    if not heights:
        return None  # Return if no text was detected

    median_height = np.median(heights)

    # Initialize bounding box for the main text area
    main_text_bbox = None

    for word in words:
        x0, y0, x1, y1 = word[:4]
        # Only include words within the main text area and exclude small fonts (likely footnotes)
        if y0 > page_height * top_margin and y1 < page_height * (1 - bottom_margin) and (y1 - y0) >= median_height * 0.8:
            word_rect = fitz.Rect(x0, y0, x1, y1)
            if main_text_bbox is None:
                main_text_bbox = word_rect
            else:
                main_text_bbox |= word_rect  # Expand the bounding box to include the word

    if main_text_bbox:
        # Add a margin to the bounding box
        main_text_bbox.x0 -= margin
        main_text_bbox.y0 -= margin
        main_text_bbox.x1 += margin
        main_text_bbox.y1 += margin

    return main_text_bbox

def crop_page_to_text_area(page, crop_rect):
    """
    Crop the page to the specified rectangle area, ensuring it stays within the MediaBox.
    """
    media_box = page.rect

    # Ensure the crop rectangle stays within the bounds of the MediaBox
    crop_rect = crop_rect.intersect(media_box)

    if not crop_rect.is_empty:
        page.set_cropbox(crop_rect)

def crop_pdf_to_text_area(pdf_path, output_path, margin=3):
    """
    Processes the PDF to crop all pages to the central text area, excluding headers, footers, and footnotes.
    A margin is added around the cropped area.
    """
    doc = fitz.open(pdf_path)

    for page_num in range(doc.page_count):
        page = doc[page_num]
        main_text_bbox = extract_main_text_bbox(page, margin=margin)

        if main_text_bbox:
            # Crop page to the detected main text area with margin
            crop_page_to_text_area(page, main_text_bbox)

    doc.save(output_path)
    doc.close()

# Usage example
pdf_path = 'input.pdf'
output_path = 'cropped_output.pdf'
crop_pdf_to_text_area(pdf_path, output_path, margin=3)
