import sys
import pymupdf
from collections import Counter
from pathlib import Path

def normalize_pdf(input_path, output_path, target_format="A4", jpeg_quality=90):
    doc = pymupdf.open(input_path)
    sizes = []
    for page in doc:
        r = page.rect
        sizes.append((round(r.width, 2), round(r.height, 2)))
    if sizes:
        most_common = Counter(sizes).most_common(1)
        common_w, common_h = most_common[0][0]
        print(f"Most common size detected: {common_w:.0f} × {common_h:.0f} pt")
        target_width_pt = common_w
        target_height_pt = common_h
    else:
        target_width_pt, target_height_pt = pymupdf.paper_size(target_format)
        print(f"Fallback to {target_format}: {target_width_pt:.0f} × {target_height_pt:.0f} pt")
    new_doc = pymupdf.open()
    for i, page in enumerate(doc):
        old_rect = page.rect
        scale_x = target_width_pt / old_rect.width
        scale_y = target_height_pt / old_rect.height
        scale = min(scale_x, scale_y)
        mat = pymupdf.Matrix(scale, scale)
        pix = page.get_pixmap(matrix=mat, alpha=False)
        new_page = new_doc.new_page(width=target_width_pt, height=target_height_pt)
        img_rect = pymupdf.Rect(0, 0, pix.width, pix.height)
        target_rect = pymupdf.Rect(0, 0, target_width_pt, target_height_pt)
        new_page.insert_image(target_rect, pixmap=pix)
    new_doc.save(output_path, deflate=True, garbage=4, linear=False)
    new_doc.close()
    doc.close()
    print(f"Written to {output_path}")

if __name__ == "__main__":
    input_file = input('Full input file name: ')
    output_file = input_file.rsplit('.', 1)[0] + '_streamlined.pdf'
    fmt = "A4"
    normalize_pdf(input_file, output_file, target_format=fmt)
