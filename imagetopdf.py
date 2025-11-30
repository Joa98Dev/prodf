# -------------------------------
#   IMAGE → PDF PANEL
# -------------------------------

import os
import customtkinter as ctk
from tkinter import filedialog
from PIL import Image
from CTkMessagebox import CTkMessagebox


class ImageToPDFPanel(ctk.CTkFrame):
    def __init__(self, master, go_back):
        super().__init__(master)

        self.go_back_callback = go_back
        self.images = []

        ctk.CTkLabel(self, text="Images to PDF", font=ctk.CTkFont(size=16, weight="bold")).pack(pady=10)

        # File list
        self.files_label = ctk.CTkLabel(self, text="No images selected")
        self.files_label.pack(pady=10)

        # Buttons frame
        button_frame = ctk.CTkFrame(self, fg_color="transparent")
        button_frame.pack(pady=20)

        ctk.CTkButton(button_frame, text="Back", width=120, command=self.go_back_callback).grid(row=0, column=0, padx=10)
        ctk.CTkButton(button_frame, text="Select Images", width=120, command=self.select_images).grid(row=0, column=1, padx=10)
        ctk.CTkButton(button_frame, text="Convert", width=120, command=self.convert_to_pdf).grid(row=0, column=2, padx=10)


    # Select multiple images
    def select_images(self):
        files = filedialog.askopenfilenames(
            filetypes=[("Image files", "*.jpg *.jpeg *.png")]
        )
        if files:
            self.images = list(files)
            self.files_label.configure(text=f"{len(files)} images selected")


    # Convert to PDF
    def convert_to_pdf(self):
        if not self.images:
            CTkMessagebox(title="Error", message="Please select at least one image.", icon="cancel")
            return

        save_path = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("PDF file", "*.pdf")],
            initialfile="output.pdf"
        )

        if not save_path:
            return

        try:
            pil_images = []

            for img_path in self.images:
                img = Image.open(img_path).convert("RGB")  
                pil_images.append(img)

            # Save the first image, append the rest
            pil_images[0].save(save_path, save_all=True, append_images=pil_images[1:])

            CTkMessagebox(title="Success", message="Images converted to PDF!", icon="check")

        except Exception as e:
            CTkMessagebox(title="Error", message=str(e), icon="cancel")

