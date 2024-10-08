import fitz  #PyMuPDF
import numpy as np

#Assume consistent page positions and crop pages to the same box

def extract_main_text_bbox(page):
    """
    Extracts the bounding box of the main text on the page, taking into account indents and possible exclusions
    of the first line due to vertical spacing.
    """
    words = page.get_text("words")  # Extract words as a list of (x0, y0, x1, y1, word, block_no, line_no, word_no)
    if not words:
        return None

    # Lower the top margin to catch potentially skipped first lines
    top_margin = 0.05  # Reduced top margin to 5% of the page height
    bottom_margin = 0.1  # 10% of the page height for footer
    page_height = page.rect.height
    page_width = page.rect.width

    # Initialize bounding box for the main text area
    main_text_bbox = None

    # List to store x and y coordinates separately
    x_coords = []
    y_coords = []

    for word in words:
        x0, y0, x1, y1 = word[:4]
        # Check vertical boundaries with a relaxed top margin
        if y0 >= page_height * top_margin and y1 <= page_height * (1 - bottom_margin):
            x_coords.append(x0)
            y_coords.append(y0)
            word_rect = fitz.Rect(x0, y0, x1, y1)
            if main_text_bbox is None:
                main_text_bbox = word_rect
            else:
                main_text_bbox |= word_rect  # Expand the bounding box to include the word

    # Adjust the bounding box to include the furthest extents found
    if main_text_bbox:
        main_text_bbox.x0 = min(x_coords)
        main_text_bbox.y0 = min(y_coords)  # Ensure the topmost part of the text is included

    return main_text_bbox

def calculate_median_crop_box(boxes):
    """
    Calculate a median bounding box from a list of boxes.
    """
    x0s, y0s, x1s, y1s = zip(*[(box.x0, box.y0, box.x1, box.y1) for box in boxes])
    median_box = fitz.Rect(
        np.median(x0s), np.median(y0s), np.median(x1s), np.median(y1s)
    )
    return median_box

def calculate_consistent_crop_box(doc, sample_size=30):
    """
    Calculate a consistent cropping box from the first sample_size pages of each type (odd and even).
    """
    even_pages = []
    odd_pages = []
    
    for page_num in range(min(sample_size, doc.page_count)):
        page = doc[page_num]
        bbox = extract_main_text_bbox(page)
        if bbox:
            if page_num % 2 == 0:
                even_pages.append(bbox)
            else:
                odd_pages.append(bbox)

    # Calculate median boxes for even and odd pages to standardize the crop area
    even_crop_box = calculate_median_crop_box(even_pages) if even_pages else None
    odd_crop_box = calculate_median_crop_box(odd_pages) if odd_pages else None

    return even_crop_box, odd_crop_box

def crop_pdf_to_uniform_text_area(pdf_path, output_path):
    """
    Processes the PDF to crop all pages to a uniform central text area determined from the median of sample pages.
    """
    doc = fitz.open(pdf_path)
    even_crop_box, odd_crop_box = calculate_consistent_crop_box(doc)

    for page_num in range(doc.page_count):
        page = doc[page_num]
        crop_box = even_crop_box if page_num % 2 == 0 else odd_crop_box
        if crop_box:
            # Ensure the crop box is within the MediaBox
            media_box = page.rect
            crop_box.intersect(media_box)
            if crop_box.is_empty:
                continue  # Skip pages where the intersection is empty
            page.set_cropbox(crop_box)

    doc.save(output_path)
    doc.close()

# Usage example
pdf_path = 'input.pdf'
output_path = 'cropped_output.pdf'
crop_pdf_to_uniform_text_area(pdf_path, output_path)
