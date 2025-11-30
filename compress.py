# Libraries
import os
import subprocess
import customtkinter as ctk
from tkinter import filedialog
from CTkMessagebox import CTkMessagebox
import numpy as np
from pdf2image import convert_from_path
from PIL import Image, ImageTk
from customtkinter import CTkImage
from fpdf import FPDF
import io
import traceback
import tempfile
import sys

# Create PDF thumbnails
def pdf_to_thumbnail(pdf_path, size=(100, 100)):
    pages = convert_from_path(pdf_path, first_page=1, last_page=1)
    thumbnail = pages[0]
    thumbnail.thumbnail(size)
    return CTkImage(thumbnail, size=size)


# Get the path of the QPDF executable
def get_qpdf_path():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    bin_dir = os.path.join(base_dir, "bin")
    if sys.platform.startswith("win"):
        return os.path.join(bin_dir, "qpdf.exe")
    else:
        return os.path.join(bin_dir, "qpdf")

# Compress a PDF using QPDF
def compress_pdf_file(input_path, output_path, compression_level):
    qpdf_path = get_qpdf_path()
    if not os.path.isfile(qpdf_path):
        CTkMessagebox(title="Error", message="qpdf not found in 'bin/' directory.", icon="cancel")
        return False

    # Compression level
    compression_args = {
        "low": ["--object-streams=preserve"],
        "medium": ["--object-streams=generate"],
        "high": ["--object-streams=generate", "--compress-streams=y", "--decode-level=specialized"],
        "extreme": ["--object-streams=generate", "--compress-streams=y", "--decode-level=specialized"]
    }

    if compression_level not in compression_args:
        return False

    # Build QPDF command
    cmd = [qpdf_path, "--stream-data=compress"] + compression_args[compression_level] + [input_path, output_path]

    try:
        # Run QPDF command
        subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        return True
    except subprocess.CalledProcessError as e:
        CTkMessagebox(title="Compression Error", message=e.stderr or str(e), icon="cancel")
        return False

# Convert the PDF to images and recomebine into a compressed PDF
def compress_pdf_as_images(input_pdf, output_pdf, quality=80, dpi=150):
    try:
        print("[*] Convirtiendo PDF a imágenes...")
        images = convert_from_path(input_pdf, dpi=dpi)

        print("[*] Reensamblando PDF...")
        pdf = FPDF(unit="pt")

        temp_files = []

        for idx, img in enumerate(images):
            width, height = img.size
            pdf.add_page(format=[width, height])

            # Save temporary JPEG to add into PDF
            temp_img = tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") 
            img.convert("RGB").save(temp_img.name, format="JPEG", quality=quality)
            temp_files.append(temp_img.name)

            pdf.image(temp_img.name, x=0, y=0, w=width, h=height)

        pdf.output(output_pdf)
        return True

        # Clean up temporary files
        for path in temp_files:
            os.remove(path)
    
        return True

    except Exception as e:
        print(f"[!] Error recomprimiendo como imágenes: {e}")
        traceback.print_exc()
        return False

# Checks if PDF contains images
def pdf_likely_has_images(pdf_path, dpi=100, threshold=500):
    try:
        # Convert first page to image
        images = convert_from_path(pdf_path, dpi=dpi, first_page=1, last_page=1)
        if not images:
            return False

        img = images[0].convert("RGB")
        data = np.array(img)
        unique_colors = len(np.unique(data.reshape(-1, data.shape[2]), axis=0))

        print(f"[i] Detected {unique_colors} unique colors on first page.")

        # If more than threshold unique colors, assume PDF has images
        return unique_colors > threshold
    except Exception as e:
        print(f"[i] Error analyzing image content: {e}")
        return False

# Compress feature (Front-End)
class CompressPanel(ctk.CTkFrame):
    def __init__(self, master, go_back):
        super().__init__(master)

        # Store the selected PDF files
        self.pdf_files = []

        # Return to the App Menu
        self.go_back_callback = go_back

        # Title
        ctk.CTkLabel(self, text="Compress PDF", font=ctk.CTkFont(size=16, weight="bold")).pack(pady=10)

        # Textbox that shows the selected files
        #self.file_listbox = ctk.CTkTextbox(self, height=120, width=400, state="disabled")
        #self.file_listbox.pack(pady=5, padx=20, fill="both", expand=True)
        
        self.scroll_frame = ctk.CTkScrollableFrame(self, width=400, height=200)
        self.scroll_frame.pack(pady=10, padx=20, fill="both", expand=True)

        self.thumbnails = []

        # Compression level selection
        self.mode_var = ctk.StringVar(value="Recommended Compression")
        self.mode_dropdown = ctk.CTkOptionMenu(
            self,
            variable=self.mode_var,
            values=["Less Compression", "Recommended Compression", "High Compression", "Extreme Compression"]
        )
        self.mode_dropdown.pack(pady=5)

        # Buttons
        button_frame = ctk.CTkFrame(self, fg_color="transparent")
        button_frame.pack(side="bottom", pady=15)

        ctk.CTkButton(button_frame, text="Back", width=120, command=self.go_back).grid(row=0, column=0, padx=0)
        ctk.CTkButton(button_frame, text="Add PDF", width=120, command=self.select_pdf).grid(row=0, column=2, padx=10)
        ctk.CTkButton(button_frame, text="Compress PDF", width=120, command=self.compress_pdf).grid(row=0, column=1, padx=10)

    # Return to the App menu function
    def go_back(self):
        self.go_back_callback()

    # Select and load the PDF files
    def select_pdf(self):
        files = filedialog.askopenfilenames(filetypes=[("PDF file", "*.pdf")])
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

    # Compress selected files
    def compress_pdf(self):
        if not self.pdf_files:
            CTkMessagebox(title="Error", message="No PDF file selected.", icon="cancel")
            return

        # Map readeable levels to QPDF compression levels
        compression_map = {
            "Less Compression": "low",
            "Recommended Compression": "medium",
            "High Compression": "high",
            "Extreme Compression": "extreme"
        }

        selected_mode = self.mode_var.get()
        compression_level = compression_map.get(selected_mode)

        if not compression_level:
            CTkMessagebox(title="Error", message="Please select a compression level", icon="cancel")
            return

        # Process each selected PDF
        for input_path in self.pdf_files:
            filename = os.path.basename(input_path)
            suggested_output = os.path.splitext(filename)[0] + "_compressed.pdf"

            # Ask user where to save the compressed PDF
            output_path = filedialog.asksaveasfilename(
                defaultextension=".pdf",
                initialfile=suggested_output,
                filetypes=[("PDF files", "*.pdf")]
            )

            if not output_path:
                continue

            try:
                # Detect if PDF contains images
                has_images = pdf_likely_has_images(input_path)
                print(f"[i] El PDF {'tiene' if has_images else 'NO tiene'} imágenes.")

                success = False

                # Compress with QPDF
                temp_qpdf = output_path + ".qpdf.pdf"
                success = compress_pdf_file(input_path, temp_qpdf, compression_level)

                if not success:
                    raise Exception("QPDF compression failed.")

                original_size = os.path.getsize(input_path)
                compressed_size = os.path.getsize(temp_qpdf)

                print(f"[i] Tamaño original: {original_size} bytes")
                print(f"[i] Tamaño tras qpdf: {compressed_size} bytes")

                
                # If small enough or no images, save compressed file
                if not has_images or compressed_size < original_size * 0.85:
                    os.rename(temp_qpdf, output_path)
                    CTkMessagebox(title="Success", message=f"Compressed PDF saved:\n{output_path}", icon="check")
                    continue
                else:
                    os.remove(temp_qpdf)

                # Rasterize PDF for better compression
                if compression_level == "extreme":
                    success = compress_pdf_as_images(input_path, output_path, quality=50, dpi=100)
                elif compression_level == "high":
                    success = compress_pdf_as_images(input_path, output_path, quality=70, dpi=150)
                elif compression_level == "medium":
                    success = compress_pdf_as_images(input_path, output_path, quality=85, dpi=200)
                else:
                    raise Exception("Rasterization not allowed at this level.")

                if not success:
                    raise Exception("Raster image compression failed.")

                CTkMessagebox(title="Success", message=f"Compressed PDF saved:\n{output_path}", icon="check")

            except subprocess.CalledProcessError as e:
                CTkMessagebox(title="Error", message=f"Compression failed:\n{e.stderr}", icon="cancel")

            except Exception as e:
                CTkMessagebox(title="Error", message=f"Error: {str(e)}", icon="cancel")

