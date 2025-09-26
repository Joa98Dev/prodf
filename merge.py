# Libraries
import customtkinter as ctk
from tkinter import filedialog
from pypdf import PdfWriter
from CTkMessagebox import CTkMessagebox

# Create the frame to show the merge screen
class MergePanel(ctk.CTkFrame):
    def __init__(self, master, go_back):
        super().__init__(master)

        # Store the selected PDF files
        self.pdf_files = []

        # Return to the App menu
        self.go_back_callback = go_back

        # Title
        ctk.CTkLabel(self, text="Merge PDFs", font=ctk.CTkFont(size=16, weight="bold")).pack(pady=10)

        # Textbox that shows the selected files
        self.file_listbox = ctk.CTkTextbox(self, height=120, width=400, state="disabled")
        self.file_listbox.pack(pady=5, padx=20, fill="both", expand=True)

        # Buttons
        button_frame = ctk.CTkFrame(self, fg_color="transparent")
        button_frame.pack(side="bottom", pady=15)

        ctk.CTkButton(button_frame, text="Back", width=120, command=self.go_back).grid(row=0, column=0, padx=10)
        ctk.CTkButton(button_frame, text="Add PDFs", width=120, command=self.select_pdf).grid(row=0, column=2, padx=10)
        ctk.CTkButton(button_frame, text="Merge PDFs", width=120, command=self.merge_pdfs).grid(row=0, column=1, padx=10)

    # Return to the App menu function
    def go_back(self):
        self.go_back_callback()

    # Select and load the PDF files
    def select_pdf(self):
        files = filedialog.askopenfilenames(filetypes=[("PDF files", "*.pdf")])
        if files:
            self.pdf_files.extend(files)
            self.update_listbox()

    # Show the selected files
    def update_listbox(self):
        self.file_listbox.configure(state="normal")
        self.file_listbox.delete("1.0", "end")
        for f in self.pdf_files:
            self.file_listbox.insert("end", f + "\n")
        self.file_listbox.configure(state="disabled")

    # Merge function
    def merge_pdfs(self):
        # Verifies if there is at least one pdf loaded
        if not self.pdf_files:
            CTkMessagebox(title="Error", message="Please select at least one PDF file.", icon="cancel")
            return

        # Let the user select where to save the merged PDF
        save_path = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF file", "*.pdf")])
        if not save_path:
            return

        try:
            merger = PdfWriter()
            for pdf in self.pdf_files:
                merger.append(pdf)
            merger.write(save_path)
            merger.close()

            CTkMessagebox(title="Success", message="PDFs merged successfully!", icon="check")
        except Exception as e:
            CTkMessagebox(title="Error", message=str(e), icon="cancel")

