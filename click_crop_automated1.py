import tkinter as tk
from PIL import Image, ImageTk, ImageDraw
from pdf2image import convert_from_path
import cv2
import numpy as np
import PyPDF2

class PDFCutter(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title('PDF Cutter')
        self.geometry('600x800')
        self.pdf_path = 'input.pdf'
        self.pdf_file = PyPDF2.PdfReader(self.pdf_path)
        self.total_pages = len(self.pdf_file.pages)
        self.current_page = 0
        self.images = self.prepare_images()
        self.label = tk.Label(self)
        self.label.pack()
        self.crop_ratios = []
        self.template_image = None
        self.average_click_position = 0
        self.selected_pages = 12
        self.prediction_phase = False
        self.display_page()
    def prepare_images(self):
        images = convert_from_path(self.pdf_path, dpi=200)
        return [img.resize((600, 800), Image.LANCZOS) for img in images]
    def display_page(self):
        if self.current_page < self.total_pages:
            img = self.images[self.current_page].copy()
            if self.prediction_phase and self.template_image is not None:
                match_y = self.perform_template_matching(img)
                draw = ImageDraw.Draw(img)
                draw.rectangle([(0, match_y), (img.width, img.height)], outline="red", width=3)
            photo = ImageTk.PhotoImage(img)
            self.label.config(image=photo)
            self.label.image = photo
            if self.prediction_phase:
                self.bind('<Return>', self.confirm_crop)
                self.label.bind('<Button-1>', self.adjust_crop)
            else:
                self.label.bind('<Button-1>', self.on_click)
        else:
            self.apply_crops()
    def on_click(self, event):
        ratio = event.y / 800
        self.crop_ratios.append(ratio)
        print(f"Training Click on Page {self.current_page + 1}: Ratio = {ratio:.4f}")
        if self.template_image is None:
            image = self.images[self.current_page]
            self.template_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
            template_y = int(ratio * image.height)
            self.template_image = self.template_image[template_y-15:template_y+15, :, :]
            print(f"Template Snapshot saved around click.")
        self.current_page += 1
        if self.current_page == self.selected_pages:
            self.calculate_model_average()
            self.prediction_phase = True
        self.display_page()
    def perform_template_matching(self, img):
        img_cv = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
        result = cv2.matchTemplate(img_cv, self.template_image, cv2.TM_CCOEFF_NORMED)
        _, max_val, _, max_loc = cv2.minMaxLoc(result)
        best_match_y = max_loc[1]
        print(f"Template matched at y={best_match_y}px with confidence {max_val:.4f}")
        return best_match_y
    def calculate_model_average(self):
        self.average_click_position = sum(self.crop_ratios) / len(self.crop_ratios)
        print(f"Average crop position (trained model): {self.average_click_position:.4f}")
    def adjust_crop(self, event):
        adjusted_ratio = event.y / 800
        print(f"Adjusted crop point on Page {self.current_page + 1}: Ratio = {adjusted_ratio:.4f}")
        self.average_click_position = (self.average_click_position + adjusted_ratio) / 2
        print(f"Updated average click position: {self.average_click_position:.4f}")
        self.confirm_crop()
    def confirm_crop(self, event=None):
        print(f"Confirmed crop for Page {self.current_page + 1}")
        self.crop_ratios.append(self.average_click_position)
        self.current_page += 1
        self.display_page()
    def apply_crops(self):
        output_pdf = PyPDF2.PdfWriter()
        for index, page in enumerate(self.pdf_file.pages):
            crop_ratio = self.crop_ratios[index]
            self.crop_bottom_part(page, crop_ratio)
            output_pdf.add_page(page)
        self.save_pdf(output_pdf)
    def crop_bottom_part(self, page, ratio):
        media_box = page.mediabox
        new_bottom = media_box[1] + (media_box[3] - media_box[1]) * ratio
        page.cropbox.lower_left = (media_box.lower_left[0], new_bottom)
        page.cropbox.upper_right = (media_box.upper_right[0], media_box.upper_right[1])
        print(f"Cropping bottom at {new_bottom:.4f} for Page {self.current_page + 1}")
    def save_pdf(self, output_pdf):
        output_filename = 'cropped_output.pdf'
        with open(output_filename, 'wb') as f:
            output_pdf.write(f)
        print(f"All pages cropped and saved as {output_filename}.")
        self.destroy()

if __name__ == '__main__':
    app = PDFCutter()
    app.mainloop()
