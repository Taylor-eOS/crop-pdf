import fitz  # PyMuPDF
import os
from PIL import Image

def pdf_to_images(pdf_path, output_folder, dpi=200, fmt='PNG', crop_margins=False):
    """
    Convert PDF pages to images with:
    - Configurable DPI (for Tolino optimization)
    - Optional margin cropping
    - Multiple output formats
    """
    doc = fitz.open(pdf_path)
    
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        
        # Calculate zoom factor from DPI (72 PDF points = 1 inch)
        zoom = dpi / 72
        matrix = fitz.Matrix(zoom, zoom)
        
        # Render page to pixmap
        pix = page.get_pixmap(matrix=matrix, alpha=False)
        
        # Convert to PIL Image
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
        
        if crop_margins:
            img = auto_crop_image(img)
        
        # Save with page number padding
        img.save(os.path.join(output_folder, f"page_{page_num+1:04d}.{fmt.lower()}"), fmt)
        
    print(f"Converted {len(doc)} pages to {fmt} images in {output_folder}")

def auto_crop_image(img, border=0):
    """Automatically crop white margins from image"""
    bg = Image.new(img.mode, img.size, img.getpixel((0,0)))
    diff = ImageChops.difference(img, bg)
    bbox = diff.getbbox()
    if bbox:
        return img.crop((bbox[0]-border, bbox[1]-border, 
                        bbox[2]+border, bbox[3]+border))
    return img

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Convert PDF pages to images')
    parser.add_argument('input_pdf', help='Path to input PDF file')
    parser.add_argument('-o', '--output', default='pdf_pages', 
                       help='Output folder (default: pdf_pages)')
    parser.add_argument('--dpi', type=int, default=200,
                       help='Resolution for Tolino optimization (default: 200)')
    parser.add_argument('--format', choices=['PNG', 'JPEG'], default='PNG',
                       help='Output format (default: PNG)')
    parser.add_argument('--crop', action='store_true',
                       help='Auto-crop page margins')
    
    args = parser.parse_args()
    
    pdf_to_images(
        args.input_pdf,
        args.output,
        dpi=args.dpi,
        fmt=args.format,
        crop_margins=args.crop
    )
