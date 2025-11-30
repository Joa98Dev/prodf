import os
import customtkinter as ctk
from tkinter import filedialog, Canvas, IntVar
from tkinter import ttk
from reportlab.pdfgen import canvas as pdf_canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.utils import ImageReader
from pypdf import PdfReader, PdfWriter
from PIL import Image, ImageDraw, ImageTk
from pdf2image import convert_from_path


class SignPanel(ctk.CTkFrame):
    def __init__(self, master, go_back=None):
        super().__init__(master)
        self.go_back_callback = go_back

        # Signature drawing
        self.drawing = False
        self.signature_image = None
        self.signature_draw_image = Image.new("RGBA", (400, 150), (0, 0, 0, 0))
        self.draw_obj = ImageDraw.Draw(self.signature_draw_image)

        ctk.CTkLabel(self, text="Sign PDF", font=ctk.CTkFont(size=18, weight="bold")).pack(pady=10)

        # Canvas for drawing signature
        self.canvas_sig = Canvas(self, width=400, height=150, bg="white")
        self.canvas_sig.pack(pady=10)
        self.canvas_sig.bind("<Button-1>", self.start_draw)
        self.canvas_sig.bind("<B1-Motion>", self.draw)
        self.canvas_sig.bind("<ButtonRelease-1>", self.stop_draw)

        # Buttons for signature
        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(pady=10)
        ctk.CTkButton(btn_frame, text="Clear", command=self.clear_signature).grid(row=0, column=0, padx=5)
        ctk.CTkButton(btn_frame, text="Save Signature", command=self.save_signature).grid(row=0, column=1, padx=5)
        ctk.CTkButton(btn_frame, text="Load Image", command=self.load_signature_image).grid(row=0, column=2, padx=5)
        ctk.CTkButton(btn_frame, text="Load PDF", command=self.load_pdf).grid(row=0, column=3, padx=5)
        if self.go_back_callback:
            ctk.CTkButton(btn_frame, text="Back", command=self.go_back).grid(row=0, column=4, padx=5)

        # Page selection Combobox
        page_frame = ctk.CTkFrame(self, fg_color="transparent")
        page_frame.pack(pady=5)
        ctk.CTkLabel(page_frame, text="Page to sign:").grid(row=0, column=0, padx=5)
        self.page_var = IntVar(value=1)
        self.page_combo = ttk.Combobox(page_frame, textvariable=self.page_var, width=5, state="readonly")
        self.page_combo['values'] = [1]
        self.page_combo.bind("<<ComboboxSelected>>", lambda e: self.update_pdf_preview())
        self.page_combo.grid(row=0, column=1, padx=5)

        # PDF Preview
        self.pdf_canvas_widget = Canvas(self, width=400, height=500, bg="gray")
        self.pdf_canvas_widget.pack(pady=10)

        self.pdf_image = None
        self.pdf_path = None
        self.pdf_reader = None
        self.current_page = 0

        # Signature overlay position
        self.sig_pos = [50, 50]
        self.sig_preview_image = None
        self.dragging = False

        self.pdf_canvas_widget.bind("<Button-1>", self.start_drag)
        self.pdf_canvas_widget.bind("<B1-Motion>", self.drag_signature)
        self.pdf_canvas_widget.bind("<ButtonRelease-1>", self.stop_drag)

        # Button to apply signature
        ctk.CTkButton(self, text="Apply Signature", command=self.apply_signature).pack(pady=10)

    # Back callback
    def go_back(self):
        if self.go_back_callback:
            self.go_back_callback()

    # Drawing signature
    def start_draw(self, event):
        self.drawing = True
        self.last_x, self.last_y = event.x, event.y

    def draw(self, event):
        if self.drawing:
            self.canvas_sig.create_line(self.last_x, self.last_y, event.x, event.y, fill="black", width=2)
            self.draw_obj.line((self.last_x, self.last_y, event.x, event.y), fill="black", width=2)
            self.last_x, self.last_y = event.x, event.y

    def stop_draw(self, event):
        self.drawing = False

    def clear_signature(self):
        self.canvas_sig.delete("all")
        self.signature_draw_image = Image.new("RGBA", (400, 150), (0, 0, 0, 0))
        self.draw_obj = ImageDraw.Draw(self.signature_draw_image)
        self.signature_image = None
        self.sig_preview_image = None
        self.update_pdf_preview()

    def save_signature(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("PNG Files", "*.png")])
        if file_path:
            self.signature_draw_image.save(file_path)
            self.signature_image = file_path
            self.sig_preview_image = Image.open(file_path).convert("RGBA")
            self.update_pdf_preview()

    def load_signature_image(self):
        file_path = filedialog.askopenfilename(filetypes=[("Image Files", "*.png *.jpg *.jpeg")])
        if file_path:
            self.signature_image = file_path
            self.sig_preview_image = Image.open(file_path).convert("RGBA")
            if self.pdf_path:
                self.update_pdf_preview()

    # Load PDF
    def load_pdf(self):
        self.pdf_path = filedialog.askopenfilename(filetypes=[("PDF Files", "*.pdf")])
        if not self.pdf_path:
            return
        self.pdf_reader = PdfReader(self.pdf_path)
        total_pages = len(self.pdf_reader.pages)
        self.page_combo['values'] = [i + 1 for i in range(total_pages)]
        self.page_var.set(1)
        self.current_page = 0
        self.update_pdf_preview()

    # Update PDF preview
    def update_pdf_preview(self):
        if not self.pdf_reader or not self.pdf_path:
            return

        self.current_page = self.page_var.get() - 1

        try:
            pages = convert_from_path(
                self.pdf_path,
                first_page=self.current_page + 1,
                last_page=self.current_page + 1,
                size=(400, 500),
            )
        except Exception as e:
            print(f"Error converting PDF to image: {e}")
            return

        self.pdf_image = pages[0].convert("RGBA")

        if self.sig_preview_image:
            self.pdf_image.paste(self.sig_preview_image, tuple(self.sig_pos), self.sig_preview_image)

        self.tk_pdf_image = ImageTk.PhotoImage(self.pdf_image)
        self.pdf_canvas_widget.delete("all")
        self.pdf_canvas_widget.create_image(0, 0, anchor="nw", image=self.tk_pdf_image)

    # Drag signature
    def start_drag(self, event):
        if self.sig_preview_image:
            x, y = event.x, event.y
            sx, sy = self.sig_pos
            w, h = self.sig_preview_image.size
            if sx <= x <= sx + w and sy <= y <= sy + h:
                self.dragging = True
                self.drag_offset = (x - sx, y - sy)

    def drag_signature(self, event):
        if self.dragging:
            x, y = event.x - self.drag_offset[0], event.y - self.drag_offset[1]
            self.sig_pos = [x, y]
            self.update_pdf_preview()

    def stop_drag(self, event):
        self.dragging = False

    # Apply signature
    def apply_signature(self):
        if not self.pdf_path or not self.sig_preview_image:
            print("PDF or signature missing!")
            return

        output_path = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF Files", "*.pdf")])
        if not output_path:
            return

        reader = PdfReader(self.pdf_path)
        writer = PdfWriter()

        # Temporary PDF with signature
        temp_sig_pdf = "temp_sig.pdf"
        c = pdf_canvas.Canvas(temp_sig_pdf, pagesize=letter)
        x, y = self.sig_pos
        c.drawImage(ImageReader(self.sig_preview_image), x, 500 - y - 75, width=200, height=75, mask="auto")
        c.showPage()
        c.save()

        # Merge signature page with selected page
        with open(temp_sig_pdf, "rb") as f_sig:
            sig_reader = PdfReader(f_sig)
            selected_page = reader.pages[self.current_page]
            selected_page.merge_page(sig_reader.pages[0])
            writer.add_page(selected_page)

        # Add remaining pages
        for i, page in enumerate(reader.pages):
            if i != self.current_page:
                writer.add_page(page)

        with open(output_path, "wb") as out:
            writer.write(out)

        os.remove(temp_sig_pdf)
        print(f"PDF saved with signature at {output_path}")

