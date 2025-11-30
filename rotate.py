# Libraries
import os
import customtkinter as ctk
from tkinter import filedialog
from pypdf import PdfReader, PdfWriter
from CTkMessagebox import CTkMessagebox
from pdf2image import convert_from_path
from PIL import Image, ImageTk
from customtkinter import CTkImage

# Create PDF thumbnails
def pdf_to_thumbnail(pdf_path, rotation=0, size=(100, 100)):
    # Convert first page into an image
    pages = convert_from_path(pdf_path, first_page=1, last_page=1)
    thumbnail = pages[0]
    
    # Aply rotattion
    if rotation != 0:
        thumbnail = thumbnail.rotate(rotation, expand=True)

    thumbnail.thumbnail(size)
    return CTkImage(thumbnail, size=size)

class RotatePanel(ctk.CTkFrame):
    def __init__(self, master, go_back):
        super().__init__(master)
        
        # Store the selected PDF (Original)
        self.pdf_files = []
        # Store the selected PDF (rotated)
        self.rotations = {}
        # Return to the App menu
        self.go_back_callback = go_back

        ctk.CTkLabel(
            self, text="Rotate PDF", font=ctk.CTkFont(size=18, weight="bold")
        ).pack(pady=10)

        # Preview area
        self.scroll_frame = ctk.CTkScrollableFrame(self, width=400, height=200)
        self.scroll_frame.pack(pady=10, padx=20, fill="both", expand=True)

        self.thumbnails = [] 

        # Buttons Frame
        button_frame = ctk.CTkFrame(self, fg_color="transparent")
        button_frame.pack(side="bottom", pady=15)

        select_btn = ctk.CTkButton(button_frame, text="Add PDF(s)", width=120, command=self.select_file)
        rotate_left_btn = ctk.CTkButton(button_frame, text="Left", width=120, command=lambda: self.rotate("left"))
        rotate_right_btn = ctk.CTkButton(button_frame, text="Right", width=120, command=lambda: self.rotate("right"))
        save_btn = ctk.CTkButton(button_frame, text="Save", width=120, command=self.save_files)
        back_btn = ctk.CTkButton(button_frame, text="Back", width=120, command=self.go_back)

        # Place buttons
        select_btn.grid(row=0, column=1, padx=10)
        rotate_left_btn.grid(row=0, column=3, padx=10)
        rotate_right_btn.grid(row=0, column=4, padx=10)
        save_btn.grid(row=0, column=5, padx=10)
        back_btn.grid(row=0, column=0, padx=10)

    # Return to the App Menu function
    def go_back(self):
        self.go_back_callback()

    def select_file(self):
        files = filedialog.askopenfilenames(filetypes=[("PDF files", "*.pdf")])
        if files:
            for f in files:
                self.pdf_files.append(f)
                self.rotations[f] = 0  # start with 0° rotation
            self.update_listbox()

    # Show the selected PDF
    def update_listbox(self):

        for widget in self.scroll_frame.winfo_children():
            widget.destroy()
        self.thumbnails = []

        max_columns = 4
        row = 0
        column = 0

        for i, f in enumerate(self.pdf_files):
            rotation = self.rotations.get(f, 0)
            thumb = pdf_to_thumbnail(f, rotation=rotation)
            #thumb = pdf_to_thumbnail(f)
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
        rotation = self.rotations.get(pdf_path, 0)
        thumb = pdf_to_thumbnail(pdf_path, rotation=rotation, size=(300, 400))
        label = ctk.CTkLabel(top, image=thumb)
        label.image = thumb
        label.pack()
        self.hover_preview = top

    def hover_off(self, event):
        if hasattr(self, "hover_preview"):
            self.hover_preview.destroy()

    def rotate(self, direction):
        # Verifies that at leat one file have been selected
        if not self.pdf_files:
            CTkMessagebox(title="Error", message="Please select at least one PDF file.", icon="cancel")
            return

        # Apply rotation preview (not saving yet)
        for f in self.pdf_files:
            if direction == "right":
                self.rotations[f] = (self.rotations[f] + 90) % 360
            elif direction == "left":
                self.rotations[f] = (self.rotations[f] - 90) % 360

        self.update_listbox()  # Update preview

    def save_files(self):
        # Check if there are any PDF loaded
        if not self.pdf_files:
            CTkMessagebox(title="Error", message="No PDF selected.", icon="cancel")
            return
        
        # Iterate over all selected PDF files
        for f in self.pdf_files:
            # Ask user where to save the ouput PDF
            output_path = filedialog.asksaveasfilename(
                initialfile=f.split("/")[-1],
                defaultextension=".pdf",
                filetypes=[("PDF files", "*.pdf")]
            )

            # Skip this file if user cancels
            if not output_path:
                continue

            try:
                # Read original PDF
                reader = PdfReader(f)
                # Create a new PDF writer
                writer = PdfWriter()
                # Get the rotation angle for this file (default -> 0)
                angle = self.rotations.get(f, 0)

                # Apply rotation to each page and add to writer
                for page in reader.pages:
                    page.rotate(angle)
                    writer.add_page(page)

                # Save the new PDF to the chosen output
                with open(output_path, "wb") as out:
                    writer.write(out)

                # Show success message
                CTkMessagebox(title="Success", message=f"Saved {output_path}", icon="check")
            except Exception as e:
                # Show error message if something goes wrong
                CTkMessagebox(title="Error", message=str(e), icon="cancel")

