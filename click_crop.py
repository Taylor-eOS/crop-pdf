import tkinter as tk
from PIL import Image, ImageTk
from pdf2image import convert_from_path
import PyPDF2
import os

class PDFCutter(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title('PDF Cutter')
        self.geometry('600x800')  # Set the size of the window

        # Load PDF
        self.pdf_path = 'input.pdf'
        self.pdf_file = PyPDF2.PdfReader(self.pdf_path)
        self.total_pages = len(self.pdf_file.pages)
        self.current_page = 0
        self.images = self.prepare_images()
        self.label = tk.Label(self)
        self.label.pack()
        self.crop_ratios = []  # To store crop ratios for each page

        # Flags to control the behavior
        self.cut_bottom = False  # Set True to cut the bottom part, False to cut the top part
        self.keep_top = False    # Set True to keep the top part, False to keep the bottom part
        self.display_page()

    def prepare_images(self):
        images = convert_from_path(self.pdf_path, dpi=200)
        return [img.resize((600, 800), Image.LANCZOS) for img in images]  # Resize images to fit window

    def display_page(self):
        if self.current_page < self.total_pages:
            img = self.images[self.current_page]
            photo = ImageTk.PhotoImage(img)
            self.label.config(image=photo)
            self.label.image = photo  # Keep a reference to avoid garbage collection
            self.label.bind('<Button-1>', self.on_click)
        else:
            self.apply_crops()

    def on_click(self, event):
        ratio = event.y / 800  # Calculate crop ratio based on the scaled image
        self.crop_ratios.append(ratio)  # Save the ratio to crop the selected part
        self.current_page += 1
        self.display_page()

    def apply_crops(self):
        output_pdf = PyPDF2.PdfWriter()
        for index, page in enumerate(self.pdf_file.pages):
            crop_ratio = self.crop_ratios[index]
            if self.cut_bottom:
                if self.keep_top:
                    self.crop_bottom_part(page, crop_ratio)
                else:
                    self.keep_bottom_part(page, crop_ratio)
            else:
                if self.keep_top:
                    self.crop_top_part(page, crop_ratio)
                else:
                    self.keep_top_part(page, crop_ratio)
            output_pdf.add_page(page)

        self.save_pdf(output_pdf)

    def crop_bottom_part(self, page, ratio):
        media_box = page.mediabox
        new_bottom = media_box[1] + (media_box[3] - media_box[1]) * ratio  # Calculate the new bottom based on the ratio
        page.cropbox.lower_left = (media_box.lower_left[0], new_bottom)
        page.cropbox.upper_right = (media_box.upper_right[0], media_box.upper_right[1])

    def keep_bottom_part(self, page, ratio):
        media_box = page.mediabox
        new_bottom = media_box[1] + (media_box[3] - media_box[1]) * ratio  # Calculate the new bottom based on the ratio
        page.cropbox.lower_left = (media_box.lower_left[0], media_box.lower_left[1])
        page.cropbox.upper_right = (media_box.upper_right[0], new_bottom)

    def crop_top_part(self, page, ratio):
        media_box = page.mediabox
        new_top = media_box[3] - (media_box[3] - media_box[1]) * ratio  # Calculate the new top based on the ratio
        page.cropbox.lower_left = (media_box.lower_left[0], media_box.lower_left[1])
        page.cropbox.upper_right = (media_box.upper_right[0], new_top)

    def keep_top_part(self, page, ratio):
        media_box = page.mediabox
        new_top = media_box[3] - (media_box[3] - media_box[1]) * ratio  # Calculate the new top based on the ratio
        page.cropbox.lower_left = (media_box.lower_left[0], new_top)
        page.cropbox.upper_right = (media_box.upper_right[0], media_box.upper_right[1])

    def save_pdf(self, output_pdf):
        output_filename = 'cropped_output.pdf'
        with open(output_filename, 'wb') as f:
            output_pdf.write(f)
        print(f"All pages cropped and saved as {output_filename}.")
        self.destroy()

if __name__ == '__main__':
    app = PDFCutter()
    app.mainloop()

