import tkinter as tk
from tkinter import filedialog, ttk, messagebox
import fitz
from PIL import Image, ImageTk
import io

preview_pages = 25

class PDFCropperApp:
    def __init__(self, root):
        self.root = root
        self.root.title("PDF Cropper")
        self.canvas = tk.Canvas(self.root, width=800, height=600, bg='white')
        self.canvas.pack(fill=tk.BOTH, expand=True)
        self.button_frame = ttk.Frame(self.root)
        self.button_frame.pack(fill=tk.X, padx=5, pady=5)
        self.open_btn = ttk.Button(self.button_frame, text="Open PDF", command=self.open_pdf)
        self.open_btn.pack(side=tk.LEFT, padx=2)
        self.crop_btn = ttk.Button(self.button_frame, text="Crop PDF", command=self.crop_pdf, state=tk.DISABLED)
        self.crop_btn.pack(side=tk.RIGHT, padx=2)
        self.doc = None
        self.zoom = 1.0
        self.scale_factor = 1.0
        self.max_width = 0
        self.max_height = 0
        self.composite_img = None
        self.tk_image = None
        self.start_x = None
        self.start_y = None
        self.rect_id = None
        self.current_rect = None
        self.canvas.bind("<ButtonPress-1>", self.on_press)
        self.canvas.bind("<B1-Motion>", self.on_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_release)

    def open_pdf(self):
        file_path = filedialog.askopenfilename(filetypes=[("PDF Files", "*.pdf")])
        if not file_path:
            return
        self.doc = fitz.open(file_path)
        if len(self.doc) == 0:
            messagebox.showerror("Error", "The selected PDF has no pages.")
            return
        num_pages = min(preview_pages, len(self.doc))
        self.max_width = int(max(p.rect.width for p in self.doc[:num_pages]))
        self.max_height = int(max(p.rect.height for p in self.doc[:num_pages]))
        self.generate_composite()
        self.display_composite()
        self.crop_btn.config(state=tk.NORMAL)

    def generate_composite(self):
        num_pages = min(preview_pages, len(self.doc))
        base = None
        alpha_per_page = 100  #Increased from 30 for darker text
        for page_num in range(num_pages):
            page = self.doc[page_num]
            mat = fitz.Matrix(self.zoom, self.zoom)
            pix = page.get_pixmap(matrix=mat)
            img_data = pix.tobytes("ppm")
            img = Image.open(io.BytesIO(img_data)).convert("RGBA")
            page_base = Image.new("RGBA", (self.max_width, self.max_height), (255, 255, 255, 0))
            page_base.paste(img, (0, 0))
            datas = page_base.getdata()
            new_data = []
            threshold = 220  #Lower threshold to include more text
            for item in datas:
                if item[0] < threshold or item[1] < threshold or item[2] < threshold:
                    new_data.append((item[0], item[1], item[2], alpha_per_page))  #Less transparent
                else:
                    new_data.append((255, 255, 255, 0))
            page_base.putdata(new_data)
            if base is None:
                base = Image.new("RGBA", (self.max_width, self.max_height), (255, 255, 255, 255))
            base.alpha_composite(page_base)
        self.composite_img = base.convert("RGB")

    def display_composite(self):
        if self.composite_img is None:
            return
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        img_width, img_height = self.composite_img.size
        self.scale_factor = min(canvas_width / img_width, canvas_height / img_height)
        new_size = (int(img_width * self.scale_factor), int(img_height * self.scale_factor))
        resized_img = self.composite_img.resize(new_size, Image.LANCZOS)
        self.tk_image = ImageTk.PhotoImage(resized_img)
        self.canvas.create_image(0, 0, anchor=tk.NW, image=self.tk_image)

    def on_press(self, event):
        self.start_x = event.x
        self.start_y = event.y
        if self.rect_id:
            self.canvas.delete(self.rect_id)
        self.rect_id = self.canvas.create_rectangle(self.start_x, self.start_y, self.start_x, self.start_y, outline='red')

    def on_drag(self, event):
        if self.rect_id:
            self.canvas.coords(self.rect_id, self.start_x, self.start_y, event.x, event.y)

    def on_release(self, event):
        self.current_rect = (min(self.start_x, event.x), min(self.start_y, event.y), max(self.start_x, event.x), max(self.start_y, event.y))

    def crop_pdf(self):
        if not self.current_rect or not self.doc:
            return
        disp_x0, disp_y0, disp_x1, disp_y1 = self.current_rect
        comp_x0 = disp_x0 / self.scale_factor
        comp_y0 = disp_y0 / self.scale_factor
        comp_x1 = disp_x1 / self.scale_factor
        comp_y1 = disp_y1 / self.scale_factor
        pdf_x0 = comp_x0 / self.zoom
        pdf_x1 = comp_x1 / self.zoom
        pdf_y0 = self.max_height - (comp_y1 / self.zoom)
        pdf_y1 = self.max_height - (comp_y0 / self.zoom)
        crop_rect = fitz.Rect(pdf_x0, pdf_y0, pdf_x1, pdf_y1)
        crop_rect.normalize()
        output_path = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF Files", "*.pdf")])
        if not output_path:
            return
        for page in self.doc:
            media_box = page.rect
            adjusted_rect = crop_rect.intersect(media_box)
            if not adjusted_rect.is_empty:
                page.set_cropbox(adjusted_rect)
        self.doc.save(output_path)
        self.doc.close()
        messagebox.showinfo("Success", f"PDF saved to {output_path}")
        self.reset_app()

    def reset_app(self):
        self.doc = None
        self.canvas.delete("all")
        self.crop_btn.config(state=tk.DISABLED)
        self.current_rect = None
        self.start_x = None
        self.start_y = None

if __name__ == "__main__":
    root = tk.Tk()
    app = PDFCropperApp(root)
    root.mainloop()

