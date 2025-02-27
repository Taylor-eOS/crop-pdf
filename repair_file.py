import fitz  # PyMuPDF
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from io import BytesIO

def extract_images_from_pdf(pdf_path):
    """Extract images from a PDF file."""
    doc = fitz.open(pdf_path)
    images = []
    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        image_list = page.get_images(full=True)
        for img_index, img in enumerate(image_list):
            xref = img[0]
            base_image = doc.extract_image(xref)
            image_data = base_image["image"]
            images.append(image_data)
    return images

def create_pdf_from_images(images, output_pdf_path):
    """Create a new PDF from extracted images."""
    c = canvas.Canvas(output_pdf_path, pagesize=A4)
    width, height = A4

    for image_data in images:
        img_buffer = BytesIO(image_data)
        c.drawImage(img_buffer, 0, 0, width=width, height=height, preserveAspectRatio=True)
        c.showPage()  # Add a new page for the next image
    c.save()

def repair_pdf(input_pdf_path, output_pdf_path):
    """Repair a PDF by extracting images and creating a new PDF."""
    print("Extracting images from the PDF...")
    images = extract_images_from_pdf(input_pdf_path)
    if not images:
        print("No images found in the PDF.")
        return

    print(f"Found {len(images)} images. Creating a new PDF...")
    create_pdf_from_images(images, output_pdf_path)
    print(f"New PDF created successfully: {output_pdf_path}")

if __name__ == "__main__":
    input_pdf = "input.pdf"  # Replace with your input PDF file path
    output_pdf = "output.pdf"  # Replace with your desired output PDF file path
    repair_pdf(input_pdf, output_pdf)
