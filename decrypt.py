# -------------------------------
#   DECRYPT PANEL - Decrypt PDFs
# -------------------------------

import os
import customtkinter as ctk
from tkinter import filedialog
from pypdf import PdfReader, PdfWriter
from CTkMessagebox import CTkMessagebox


class DecryptPanel(ctk.CTkFrame):
    def __init__(self, master, go_back):
        super().__init__(master)

        self.go_back_callback = go_back
        self.selected_pdf = None

        # Title
        ctk.CTkLabel(self, text="Decrypt PDF", font=ctk.CTkFont(size=16, weight="bold")).pack(pady=10)

        # Selected file label
        self.file_label = ctk.CTkLabel(self, text="No PDF selected", anchor="center")
        self.file_label.pack(pady=10)

        # Password
        ctk.CTkLabel(self, text="Enter password:").pack(pady=(15, 2))
        self.password_entry = ctk.CTkEntry(self, placeholder_text="Password")
        self.password_entry.pack(pady=5, ipadx=30)

        # Buttons
        button_frame = ctk.CTkFrame(self, fg_color="transparent")
        button_frame.pack(pady=20)

        ctk.CTkButton(button_frame, text="Back", width=120, command=self.go_back_callback).grid(row=0, column=0, padx=10)
        ctk.CTkButton(button_frame, text="Select PDF", width=120, command=self.select_pdf).grid(row=0, column=1, padx=10)
        ctk.CTkButton(button_frame, text="Decrypt", width=120, command=self.decrypt_pdf).grid(row=0, column=2, padx=10)


    # -------------------------------
    # Select encrypted PDF
    # -------------------------------
    def select_pdf(self):
        pdf = filedialog.askopenfilename(filetypes=[("PDF files", "*.pdf")])
        if pdf:
            self.selected_pdf = pdf
            self.file_label.configure(text=os.path.basename(pdf))


    # -------------------------------
    # Decrypt the PDF
    # -------------------------------
    def decrypt_pdf(self):
        if not self.selected_pdf:
            CTkMessagebox(title="Error", message="Please select a PDF file.", icon="cancel")
            return

        password = self.password_entry.get().strip()

        if not password:
            CTkMessagebox(title="Error", message="Password cannot be empty.", icon="cancel")
            return

        try:
            reader = PdfReader(self.selected_pdf)

            # Try to decrypt
            if reader.is_encrypted:
                if reader.decrypt(password) != 1:
                    CTkMessagebox(title="Error", message="Incorrect password!", icon="cancel")
                    return
            else:
                CTkMessagebox(title="Info", message="This PDF is not encrypted.", icon="info")
                return

            # Ask where to save
            save_path = filedialog.asksaveasfilename(
                defaultextension=".pdf",
                filetypes=[("PDF file", "*.pdf")],
                initialfile="decrypted.pdf"
            )

            if not save_path:
                return

            writer = PdfWriter()

            for page in reader.pages:
                writer.add_page(page)

            # Write decrypted version (no password)
            with open(save_path, "wb") as f:
                writer.write(f)

            CTkMessagebox(title="Success", message="PDF decrypted successfully!", icon="check")

        except Exception as e:
            CTkMessagebox(title="Error", message=str(e), icon="cancel")

