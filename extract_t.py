import pytesseract #pip install pytesseract #sudo apt-get install tesseract-ocr
import fitz  # PyMuPDF
from PIL import Image
import io
import re
import textwrap

# Ensure pytesseract is configured correctly (modify path if necessary)
# pytesseract.pytesseract.tesseract_cmd = r'/path/to/tesseract'

def pdf_to_images(pdf_path):
    """Convert PDF pages to images."""
    pdf_document = fitz.open(pdf_path)
    images = []
    
    for page_number in range(len(pdf_document)):
        page = pdf_document.load_page(page_number)
        pix = page.get_pixmap()
        img = Image.open(io.BytesIO(pix.tobytes("png")))
        images.append(img)
    
    return images

def extract_text_from_image(image):
    """Extract text from a given image using pytesseract with custom configurations."""
    # Set custom configurations: English language
    custom_config = r'--psm 3'  # Adjusting for single block of text, suitable for books. Tried: 3, 6, 1, 4
    text = pytesseract.image_to_string(image, lang='eng', config=custom_config)
    return text

def clean_text(text):
    """Remove unnecessary line breaks and tag headlines."""
    # Remove unnecessary line breaks but keep meaningful ones (e.g., paragraph breaks)
    cleaned_text = ' '.join(text.splitlines())
    
    # Detect potential headlines: assumption is that headlines are short lines with no more than 10 words
    headline_pattern = re.compile(r'(^.{1,80}$)', re.MULTILINE)
    
    # Add <headline> tags for the detected headlines
    cleaned_text = re.sub(headline_pattern, r'<headline>\1</headline>', cleaned_text)
    
    return cleaned_text

def save_text_to_file(text, output_file):
    """Save the cleaned text to a TXT file."""
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(text)

def pdf_to_text(pdf_path, txt_output_path):
    """Main function to convert PDF to text with headline tagging and cleaned line breaks."""
    images = pdf_to_images(pdf_path)
    all_text = ""

    for img in images:
        text = extract_text_from_image(img)
        cleaned_text = clean_text(text)
        all_text += cleaned_text + "\n\n"

    save_text_to_file(all_text, txt_output_path)

# Example usage
pdf_path = "cropped_output_individual.pdf"  # Replace with your PDF path
txt_output_path = "output_tesseract.txt"  # Replace with your desired TXT output path

pdf_to_text(pdf_path, txt_output_path)

