import tkinter as tk
from PIL import Image, ImageTk
from pdf2image import convert_from_path
from PyPDF2 import PdfReader, PdfWriter
import os
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

#This version seems to convert to raster images, or something, which loses quality
class PDFCutter(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title('PDF Cutter')
        self.geometry('600x800')
        self.pdf_path = 'input.pdf'
        self.pdf_file = PdfReader(self.pdf_path)
        self.total_pages = len(self.pdf_file.pages)
        self.current_page = 0
        self.images = self.prepare_images()
        self.label = tk.Label(self)
        self.label.pack()
        self.crop_ratios = []
        self.cut_bottom = False
        self.keep_top = False
        self.display_page()
    def prepare_images(self):
        images = convert_from_path(self.pdf_path, dpi=200)
        return [img.resize((600, 800), Image.LANCZOS) for img in images]
    def display_page(self):
        if self.current_page < self.total_pages:
            img = self.images[self.current_page]
            photo = ImageTk.PhotoImage(img)
            self.label.config(image=photo)
            self.label.image = photo
            self.label.bind('<Button-1>', self.on_click)
        else:
            self.apply_crops()
    def on_click(self, event):
        ratio = event.y / 800
        self.crop_ratios.append(ratio)
        self.current_page += 1
        self.display_page()
    def apply_crops(self):
        output_pdf_path = 'cropped_output.pdf'
        c = canvas.Canvas(output_pdf_path, pagesize=letter)
        for index, page in enumerate(self.pdf_file.pages):
            media_box = page.mediabox
            crop_ratio = self.crop_ratios[index]
            lower_y = media_box.lower_left[1] + (media_box.upper_right[1] - media_box.lower_left[1]) * crop_ratio
            upper_y = media_box.upper_right[1]
            if not self.keep_top:
                lower_y, upper_y = media_box.lower_left[1], lower_y
            c.setPageSize((media_box.upper_right[0] - media_box.lower_left[0], upper_y - lower_y))
            c.drawInlineImage(self.images[index], 0, -lower_y)
            c.showPage()
        c.save()
        print(f"All pages cropped and saved as {output_pdf_path}.")
        self.destroy()

if __name__ == '__main__':
    app = PDFCutter()
    app.mainloop()
