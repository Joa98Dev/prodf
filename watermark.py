import os
import tempfile
import customtkinter as ctk
from tkinter import filedialog, messagebox
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.colors import black, Color
from pypdf import PdfReader, PdfWriter
from pdf2image import convert_from_path
from PIL import Image
from customtkinter import CTkImage


class WatermarkPanel(ctk.CTkScrollableFrame):
    def __init__(self, master, go_back=None):
        super().__init__(master)
        self.go_back = go_back

        ctk.CTkLabel(self, text="Add Watermark", font=("Arial", 18, "bold")).pack(pady=10)

        # PDF selection
        self.pdf_path = None
        ctk.CTkButton(self, text="Select PDF", command=self.select_pdf).pack(pady=5)

        # Watermark type
        self.mode = ctk.StringVar(value="text")
        ctk.CTkRadioButton(self, text="Text Watermark", variable=self.mode, value="text", command=self.toggle_mode).pack()
        ctk.CTkRadioButton(self, text="Image Watermark", variable=self.mode, value="image", command=self.toggle_mode).pack()

        # Text watermark options
        self.text_frame = ctk.CTkFrame(self)
        self.text_entry = ctk.CTkEntry(self.text_frame, placeholder_text="Enter watermark text")
        self.text_entry.pack(pady=5, padx=5)
        self.size_entry = ctk.CTkEntry(self.text_frame, placeholder_text="Font size (e.g. 36)")
        self.size_entry.pack(pady=5, padx=5)
        self.opacity_slider = ctk.CTkSlider(self.text_frame, from_=0, to=1, number_of_steps=10)
        self.opacity_slider.set(1.0)
        self.opacity_slider.pack(pady=5, padx=5)
        self.text_frame.pack(pady=10, fill="x")

        # Image watermark options
        self.image_frame = ctk.CTkFrame(self)
        self.img_path = None
        ctk.CTkButton(self.image_frame, text="Select Image", command=self.select_image).pack(pady=5, padx=5)

        # Preview
        self.preview_label = ctk.CTkLabel(self, text="No preview available")
        self.preview_label.pack(pady=10)

        # Apply and Back buttons
        ctk.CTkButton(self, text="Apply Watermark", command=self.apply_watermark).pack(pady=10)
        if self.go_back:
            ctk.CTkButton(self, text="Back", command=self.go_back).pack(pady=5)

    def toggle_mode(self):
        if self.mode.get() == "text":
            self.text_frame.pack(pady=10, fill="x")
            self.image_frame.pack_forget()
        else:
            self.text_frame.pack_forget()
            self.image_frame.pack(pady=10, fill="x")

    def select_pdf(self):
        path = filedialog.askopenfilename(filetypes=[("PDF files", "*.pdf")])
        if path:
            self.pdf_path = path
            messagebox.showinfo("Selected", f"PDF: {os.path.basename(path)}")
            self.show_preview()

    def select_image(self):
        path = filedialog.askopenfilename(filetypes=[("Image files", "*.png *.jpg *.jpeg")])
        if path:
            self.img_path = path
            messagebox.showinfo("Selected", f"Image: {os.path.basename(path)}")
            self.show_preview()

    
    def build_watermark_pdf(self, page_size=None):
        """Create a temporary PDF watermark matching the given page size"""
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
    
        # Use page size of the original PDF if provided
        if page_size is None:
            page_width, page_height = letter
        else:
            page_width, page_height = page_size

        c = canvas.Canvas(temp_file.name, pagesize=(page_width, page_height))

        if self.mode.get() == "text":
            text = self.text_entry.get()
            if not text.strip():
                text = "WATERMARK"  # default text
            size = int(self.size_entry.get() or 36)
            c.setFont("Helvetica", size)
            c.setFillColorRGB(0, 0, 0)  # solid black
            c.drawCentredString(page_width / 2, page_height / 2, text)
        else:
            if not self.img_path:
                # If no image, fallback to blank PDF (no watermark)
                c.save()
                return temp_file.name

            img = Image.open(self.img_path)
            img_width, img_height = img.size
            max_w, max_h = page_width, page_height
            if img_width > max_w or img_height > max_h:
                img.thumbnail((max_w, max_h))
                img_width, img_height = img.size
            c.drawImage(self.img_path, (page_width - img_width) / 2, (page_height - img_height) / 2,
                        img_width, img_height, mask='auto')

        c.save()
        return temp_file.name

    def show_preview(self):
        """Show first page preview with watermark"""
        if not self.pdf_path:
            return
        try:
            reader = PdfReader(self.pdf_path)
            writer = PdfWriter()

            first_page = reader.pages[0]
            page_width = float(first_page.mediabox.width)
            page_height = float(first_page.mediabox.height)

            watermark_file = self.build_watermark_pdf(page_size=(page_width, page_height))
            watermark_reader = PdfReader(watermark_file)

            first_page.merge_page(watermark_reader.pages[0])
            writer.add_page(first_page)

            temp_out = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
            with open(temp_out.name, "wb") as f:
                writer.write(f)

            images = convert_from_path(temp_out.name, first_page=1, last_page=1)
            img = images[0]
            img.thumbnail((400, 500))
            ctk_img = CTkImage(light_image=img, dark_image=img, size=img.size)

            self.preview_label.configure(image=ctk_img, text="")
            self.preview_label.image = ctk_img

        except Exception as e:
            self.preview_label.configure(text=f"Preview error: {e}", image=None)


    def apply_watermark(self):
        if not self.pdf_path:
            messagebox.showerror("Error", "Please select a PDF file")
            return
        output_path = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF files", "*.pdf")])
        if not output_path:
            return
        try:
            reader = PdfReader(self.pdf_path)
            writer = PdfWriter()
            watermark_file = self.build_watermark_pdf()
            watermark_reader = PdfReader(watermark_file)

            for page in reader.pages:
                page.merge_page(watermark_reader.pages[0])
                writer.add_page(page)

            with open(output_path, "wb") as f:
                writer.write(f)

            messagebox.showinfo("Success", f"Watermarked PDF saved as {os.path.basename(output_path)}")
        except Exception as e:
            messagebox.showerror("Error", str(e))

