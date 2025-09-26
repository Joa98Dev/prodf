# Libraries
import os
import base64
import customtkinter as ctk
from tkinter import filedialog
from CTkMessagebox import CTkMessagebox
import fitz

class PDF_to_HTML_Panel(ctk.CTkFrame):
    def __init__(self, master, go_back_callback):
        super().__init__(master)
        self.go_back_callback = go_back_callback
        self.selected_file = None

        ctk.CTkLabel(self, text="Convert PDF to HTML", font=ctk.CTkFont(size=16, weight="bold")).pack(pady=10)

        # File selection
        self.file_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.file_frame.pack(pady=5, padx=20, fill="x")

        self.file_select_button = ctk.CTkButton(
            self.file_frame,
            text="Select PDF File",
            command=self.select_pdf_file
        )
        self.file_select_button.pack(pady=5)

        self.file_label = ctk.CTkLabel(self.file_frame, text="No file selected")
        self.file_label.pack(pady=5)

        # Buttons
        button_frame = ctk.CTkFrame(self, fg_color="transparent")
        button_frame.pack(pady=15)

        ctk.CTkButton(button_frame, text="Back", width=120, command=self.go_back_callback).grid(row=0, column=0, padx=10)
        ctk.CTkButton(button_frame, text="Convert to HTML", width=120, command=self.convert_to_html).grid(row=0, column=1, padx=10)

    def select_pdf_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("PDF Files", "*.pdf")])
        if file_path:
            self.selected_file = file_path
            self.file_label.configure(text=os.path.basename(file_path))

    def convert_to_html(self):
        if not self.selected_file:
            CTkMessagebox(title="Error", message="No PDF file selected", icon="cancel")
            return

        output_file = filedialog.asksaveasfilename(
            defaultextension=".html",
            filetypes=[("HTML files", "*.html")],
            initialfile="output.html"
        )
        if not output_file:
            return

        try:
            doc = fitz.open(self.selected_file)
            html_content = "<html><body>\n"

            for page_num, page in enumerate(doc, start=1):
                # Page text as HTML
                html_content += page.get_text("html")

                # Extract images
                for img_index, img in enumerate(page.get_images(full=True), start=1):
                    xref = img[0]
                    base_image = doc.extract_image(xref)
                    image_bytes = base_image["image"]
                    image_ext = base_image["ext"]

                    # Encode to Base64
                    b64_img = base64.b64encode(image_bytes).decode("utf-8")

                    # Insert image into the HTML file
                    html_content += f'<div><img src="data:image/{image_ext};base64,{b64_img}" alt="page{page_num}_img{img_index}"></div>\n'

            html_content += "</body></html>"
            doc.close()

            # Save HTML
            with open(output_file, "w", encoding="utf-8") as f:
                f.write(html_content)

            CTkMessagebox(title="Success", message=f"HTML saved at:\n{output_file}", icon="check")

        except Exception as e:
            CTkMessagebox(title="Error", message=f"Conversion failed:\n{str(e)}", icon="cancel")

