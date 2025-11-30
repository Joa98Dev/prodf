# -------------------------------
#   ENCRYPT PANEL - Encrypt PDFs
# -------------------------------

import os
import customtkinter as ctk
from tkinter import filedialog
from pypdf import PdfReader, PdfWriter
from CTkMessagebox import CTkMessagebox


class EncryptPanel(ctk.CTkFrame):
    def __init__(self, master, go_back):
        super().__init__(master)

        # Store callback to return to main menu
        self.go_back_callback = go_back

        # Store selected PDF
        self.selected_pdf = None

        # Title
        ctk.CTkLabel(self, text="Encrypt PDF", font=ctk.CTkFont(size=16, weight="bold")).pack(pady=10)

        # Label that shows selected file
        self.file_label = ctk.CTkLabel(self, text="No PDF selected", anchor="center")
        self.file_label.pack(pady=10)

        # Password entry field
        ctk.CTkLabel(self, text="Enter password:").pack(pady=(15, 2))
        self.password_entry = ctk.CTkEntry(self, placeholder_text="Password")
        self.password_entry.pack(pady=5, ipadx=30)

        # Re-enter password field
        ctk.CTkLabel(self, text="Confirm password:").pack(pady=(15, 2))
        self.confirm_entry = ctk.CTkEntry(self, placeholder_text="Re-enter password")
        self.confirm_entry.pack(pady=5, ipadx=30)

        # Buttons
        button_frame = ctk.CTkFrame(self, fg_color="transparent")
        button_frame.pack(pady=20)

        ctk.CTkButton(button_frame, text="Back", width=120, command=self.go_back_callback).grid(row=0, column=0, padx=10)
        ctk.CTkButton(button_frame, text="Select PDF", width=120, command=self.select_pdf).grid(row=0, column=1, padx=10)
        ctk.CTkButton(button_frame, text="Encrypt", width=120, command=self.encrypt_pdf).grid(row=0, column=2, padx=10)


    # -----------------------------------------
    # Select a single PDF file
    # -----------------------------------------
    def select_pdf(self):
        pdf = filedialog.askopenfilename(filetypes=[("PDF files", "*.pdf")])
        if pdf:
            self.selected_pdf = pdf
            self.file_label.configure(text=os.path.basename(pdf))


    # -----------------------------------------
    # Encrypt the selected PDF
    # -----------------------------------------
    def encrypt_pdf(self):
        # Validate if a PDF was selected
        if not self.selected_pdf:
            CTkMessagebox(title="Error", message="Please select a PDF file.", icon="cancel")
            return

        # Read passwords
        password = self.password_entry.get().strip()
        confirm = self.confirm_entry.get().strip()

        # Validate passwords
        if not password:
            CTkMessagebox(title="Error", message="Password cannot be empty.", icon="cancel")
            return

        if password != confirm:
            CTkMessagebox(title="Error", message="Passwords do not match.", icon="cancel")
            return

        # Ask user where to save encrypted file
        save_path = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("PDF file", "*.pdf")],
            initialfile="encrypted.pdf"
        )

        if not save_path:
            return

        try:
            reader = PdfReader(self.selected_pdf)
            writer = PdfWriter()

            # Copy all pages from the original to the writer
            for page in reader.pages:
                writer.add_page(page)

            # Encrypt using the user's password
            # By default, owner password = user password
            writer.encrypt(password)

            # Write encrypted PDF to disk
            with open(save_path, "wb") as f:
                writer.write(f)

            CTkMessagebox(title="Success", message="PDF encrypted successfully!", icon="check")

        except Exception as e:
            CTkMessagebox(title="Error", message=str(e), icon="cancel")

