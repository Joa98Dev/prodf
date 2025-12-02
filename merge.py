# Libraries
import os
import customtkinter as ctk
from tkinter import filedialog, Listbox
from pypdf import PdfWriter
from CTkMessagebox import CTkMessagebox
from pdf2image import convert_from_path
from PIL import Image, ImageTk
from customtkinter import CTkImage

# Create PDF thumbnails
def pdf_to_thumbnail(pdf_path, size=(100, 100)):
    pages = convert_from_path(pdf_path, first_page=1, last_page=1)
    thumbnail = pages[0]
    thumbnail.thumbnail(size)
    return CTkImage(thumbnail, size=size)
    #return ImageTk.PhotoImage(thumbnail)

# Create the frame to show the merge screen
class MergePanel(ctk.CTkScrollableFrame):
    def __init__(self, master, go_back):
        super().__init__(master, width=600)

        # Store the selected PDF files
        self.pdf_files = []

        # Return to the App menu
        self.go_back_callback = go_back

        # Title
        ctk.CTkLabel(self, text="Merge PDFs", font=ctk.CTkFont(size=16, weight="bold")).pack(pady=10)

        # Textbox that shows the selected files
        #self.file_listbox = ctk.CTkTextbox(self, height=120, width=400, state="disabled")
        #self.file_listbox.pack(pady=5, padx=20, fill="both", expand=True)

        self.scroll_frame = ctk.CTkScrollableFrame(self, width=400, height=200)
        self.scroll_frame.pack(pady=10, padx=20, fill="both", expand=True)

        self.thumbnails = []

    
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
        for widget in self.scroll_frame.winfo_children():
            widget.destroy()
        self.thumbnails = []

        max_columns = 4
        row = 0
        column = 0

        #self.file_listbox.configure(state="normal")
        #self.file_listbox.delete("1.0", "end")
        #for f in self.pdf_files:
            #self.file_listbox.insert("end", f + "\n")
        #self.file_listbox.configure(state="disabled")

        for i, f in enumerate(self.pdf_files):
            thumb = pdf_to_thumbnail(f)
            self.thumbnails.append(thumb)

            thumb_label = ctk.CTkLabel(
                    self.scroll_frame,
                    image=thumb,
                    text=os.path.basename(f),
                    compound="top",
                    corner_radius=8,
                    fg_color="#333333",
                    width=120,
                    height=140
            )

            thumb_label.grid(row=0, column=i, padx=5, pady=5)

            thumb_label.bind("<Button-1>", lambda e, l=thumb_label, f=f: self.on_thumbnail_click(f,l))  
            thumb_label.bind("<Enter>", lambda e, f=f: self.hover_on(f))
            thumb_label.bind("<Leave>", self.hover_off)

            column += 1
            if column >= max_columns:
                column = 0
                row += 1

    # Select the PDF file inside the merge panel
    def on_thumbnail_click(self, pdf_path, label_widget):
        if getattr(label_widget, "selected", False):
            label_widget.configure(fg_color=None)
            label_widget.selected = False
        else:
            label_widget.configure(fg_color="#aa2e25")
            label_widget.selected = True

    def hover_on(self, pdf_path):
        top = ctk.CTkToplevel(self)
        top.geometry("300x400")
        top.overrideredirect(True)
        thumb = pdf_to_thumbnail(pdf_path, size=(300, 400))
        label = ctk.CTkLabel(top, image=thumb)
        label.image = thumb
        label.pack()
        self.hover_preview = top

    def hover_off(self, event):
        if hasattr(self, "hover_preview"):
            self.hover_preview.destroy()

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

