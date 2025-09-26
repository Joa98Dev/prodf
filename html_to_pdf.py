# Libraries
import os
import shutil
import subprocess
import customtkinter as ctk
from tkinter import filedialog
from CTkMessagebox import CTkMessagebox

class ConvertPanel(ctk.CTkFrame):
    def __init__(self, master, go_back_callback):
        super().__init__(master)
        self.go_back_callback = go_back_callback
        self.selected_file = None  # Stores the path of the selected HTML file

        ctk.CTkLabel(self, text="Convert HTML to PDF", font=ctk.CTkFont(size=16, weight="bold")).pack(pady=10)

        # Conversion mode (URL or local file)
        self.mode = ctk.StringVar(value="url")
        mode_frame = ctk.CTkFrame(self, fg_color="transparent")
        mode_frame.pack(pady=5)
        
        ctk.CTkRadioButton(mode_frame, text="From URL", variable=self.mode, value="url").grid(row=0, column=0, padx=10)
        ctk.CTkRadioButton(mode_frame, text="From File", variable=self.mode, value="file").grid(row=0, column=1, padx=10)
        
        # URL field
        self.url_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.url_frame.pack(pady=5, padx=20, fill="x")
        ctk.CTkLabel(self.url_frame, text="Website URL:").pack(anchor="w")
        self.url_entry = ctk.CTkEntry(self.url_frame, placeholder_text="https://example.com", width=400)
        self.url_entry.pack(fill="x", pady=5)
        
        # Local file field
        self.file_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.file_select_button = ctk.CTkButton(
            self.file_frame, 
            text="Select HTML File", 
            command=self.select_html_file
        )
        self.file_select_button.pack(pady=5)
        self.file_label = ctk.CTkLabel(self.file_frame, text="No file selected")
        self.file_label.pack(pady=5)
        
        # Buttons
        button_frame = ctk.CTkFrame(self, fg_color="transparent")
        button_frame.pack(pady=15)

        ctk.CTkButton(button_frame, text="Back", width=120, command=self.go_back_callback).grid(row=0, column=0, padx=10)
        ctk.CTkButton(button_frame, text="Convert to PDF", width=120, command=self.convert_to_pdf).grid(row=0, column=1, padx=10)
        
        # Initialize visibility
        self.toggle_inputs()
        self.mode.trace_add("write", lambda *args: self.toggle_inputs())

    def toggle_inputs(self):
        # Show URL input or file input based on selected mode
        if self.mode.get() == "url":
            self.url_frame.pack(pady=5, padx=20, fill="x")
            self.file_frame.pack_forget()
        else:
            self.file_frame.pack(pady=5, padx=20, fill="x")
            self.url_frame.pack_forget()

    def select_html_file(self):
        # Open file dialog to select a local HTML file
        file_path = filedialog.askopenfilename(
            filetypes=[("HTML Files", "*.html *.htm")]
        )
        if file_path:
            self.selected_file = file_path # Save the selected file path
            self.file_label.configure(text=os.path.basename(file_path)) # Update label

    def get_wkhtmltopdf_path(self):
        # Check if wkhtmltopdf is in system Path
        path = shutil.which("wkhtmltopdf")
        if path:
            return path

        # Otherwise, check local bin folder
        base_dir = os.path.dirname(os.path.abspath(__file__))

        if os.name == "nt":
            local_bin = os.path.join(base_dir, "bin", "wkhtmltopdf.exe")
        else:
            local_bin = os.path.join(base_dir, "bin", "wkhtmltopdf")

        if os.path.exists(local_bin):
            return os.path.abspath(local_bin)

        return None

    def convert_to_pdf(self):
        # Get path of wkhtmltopdf executable
        converter_path = self.get_wkhtmltopdf_path()
        if not converter_path:
            CTkMessagebox(title="Error", message="wkhtmltopdf not found in PATH or ./bin/", icon="cancel")
            return

        source = None
        mode = self.mode.get()
        
        # Determine the source: URL or local file
        if mode == "url":
            source = self.url_entry.get().strip()
            if not source:
                CTkMessagebox(title="Error", message="No URL entered.", icon="cancel")
                return
        else:
            if not self.selected_file:
                CTkMessagebox(title="Error", message="No HTML file selected.", icon="cancel")
                return
            source = self.selected_file

        # Ask user where to save the PDF
        output_file = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("PDF files", "*.pdf")],
            initialfile="output.pdf"
        )

        if not output_file:
            return

        try:
            # if is a local HTML file change to local path loader
            if mode == "file":
                original_dir = os.getcwd()
                os.chdir(os.path.dirname(source))
                source = os.path.basename(source)
            
            # Run wkhtmltopdf to convert HTML/URL to PDF
            subprocess.run([converter_path, source, output_file], check=True)
            
            # Restores to original working directory
            if mode == "file":
                os.chdir(original_dir)
                
            CTkMessagebox(title="Success", message=f"PDF saved at:\n{output_file}", icon="check")
        except subprocess.CalledProcessError as e:
            # Handle wkhtmltopdf errors
            CTkMessagebox(title="Error", message=f"Conversion failed:\n{e}", icon="cancel")
        except Exception as e:
            # Handle unexpected errors
            CTkMessagebox(title="Error", message=f"Unexpected error:\n{str(e)}", icon="cancel")
