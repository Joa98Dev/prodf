# -------------------------------
#   PDF → IMAGE PANEL
# -------------------------------

import os
import customtkinter as ctk
from tkinter import filedialog
from pdf2image import convert_from_path
from CTkMessagebox import CTkMessagebox


class PDFToImagePanel(ctk.CTkFrame):
    def __init__(self, master, go_back):
        super().__init__(master)

        self.go_back_callback = go_back
        self.selected_pdf = None

        ctk.CTkLabel(self, text="PDF to Images", font=ctk.CTkFont(size=16, weight="bold")).pack(pady=10)

        self.file_label = ctk.CTkLabel(self, text="No PDF selected")
        self.file_label.pack(pady=10)

        button_frame = ctk.CTkFrame(self, fg_color="transparent")
        button_frame.pack(pady=20)

        ctk.CTkButton(button_frame, text="Back", width=120, command=self.go_back_callback).grid(row=0, column=0, padx=10)
        ctk.CTkButton(button_frame, text="Select PDF", width=120, command=self.select_pdf).grid(row=0, column=1, padx=10)
        ctk.CTkButton(button_frame, text="Convert", width=120, command=self.convert_pdf).grid(row=0, column=2, padx=10)


    # Select a PDF
    def select_pdf(self):
        pdf = filedialog.askopenfilename(filetypes=[("PDF files", "*.pdf")])
        if pdf:
            self.selected_pdf = pdf
            self.file_label.configure(text=os.path.basename(pdf))


    # Convert PDF -> JPG
    def convert_pdf(self):
        if not self.selected_pdf:
            CTkMessagebox(title="Error", message="Please select a PDF file.", icon="cancel")
            return

        output_dir = filedialog.askdirectory()

        if not output_dir:
            return

        try:
            images = convert_from_path(self.selected_pdf, dpi=200)

            for i, img in enumerate(images):
                img_path = os.path.join(output_dir, f"page_{i+1}.jpg")
                img.save(img_path, "JPEG")

            CTkMessagebox(title="Success", message="PDF converted to images!", icon="check")

        except Exception as e:
            CTkMessagebox(title="Error", message=str(e), icon="cancel")

