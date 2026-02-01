import os
from pathlib import Path
from pypdf import PdfReader, PdfWriter, Transformation, PageObject

def split_double_pages(input_path, output_path):
    reader = PdfReader(input_path)
    writer = PdfWriter()
    for page in reader.pages:
        mediabox = page.mediabox
        width = mediabox.width
        height = mediabox.height
        mid = float(width) / 2
        left_page = PageObject.create_blank_page(None, mid, height)
        left_page.merge_page(page)
        left_page.add_transformation(Transformation().translate(tx=-0, ty=0))
        right_page = PageObject.create_blank_page(None, mid, height)
        right_page.merge_page(page)
        right_page.add_transformation(Transformation().translate(tx=-mid, ty=0))
        writer.add_page(left_page)
        writer.add_page(right_page)
    with open(output_path, "wb") as f:
        writer.write(f)
    print(f"Created {output_path}")
    print(f"Original pages: {len(reader.pages)}, New pages: {len(writer.pages)}")

if __name__ == "__main__":
    print("Split double-page PDF into single pages in reading order")
    input_str = input("Input file: ") or 'input.pdf'
    output_str = os.path.splitext(input_str)[0] + '_split.pdf'
    if not input_str:
        print("No input file given")
        exit(1)
    input_file = Path(input_str)
    if not input_file.is_file():
        print(f"File not found: {input_file}")
        exit(1)
    if not output_str:
        output_str = input_file.stem + "_split.pdf"
    output_file = Path(output_str)
    if output_file.suffix.lower() != ".pdf":
        output_file = output_file.with_suffix(".pdf")
    split_double_pages(input_file, output_file)
    print(f"Saved as: {output_file}")

