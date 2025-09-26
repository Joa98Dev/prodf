# Libraries
import customtkinter as ctk
from tkinter import filedialog
from pypdf import PdfWriter, PdfReader
from CTkMessagebox import CTkMessagebox

# Create the frame to show the split screen
class SplitPanel(ctk.CTkFrame):
    def __init__(self, master, go_back):
        super().__init__(master)
        
        # Store the selected PDF files
        self.pdf_files = []

        # Return to the App menu
        self.go_back_callback = go_back

        # Title
        ctk.CTkLabel(self, text="Split PDF", font=ctk.CTkFont(size=16, weight="bold")).pack(pady=10)

        # Textbox that shows the selected files
        self.file_listbox = ctk.CTkTextbox(self, height=120, width=400, state="disabled")
        self.file_listbox.pack(pady=5, padx=20, fill="both", expand=True)
 
       
        # Split mode selection
        self.mode_var = ctk.StringVar(value="custom")
        self.mode_dropdown = ctk.CTkOptionMenu(
                self,
                values=["custom", "fixed", "extract_all", "specific"],
                variable=self.mode_var,
                command=self.update_input_fields
        )
        self.mode_dropdown.pack(pady=5)

        # Dynamic input field
        self.input_field = ctk.CTkEntry(self, placeholder_text="Enter the ranges (e.g. 1-3,5)")
        self.input_field.pack(pady=5, padx=20)

        # Buttons
        button_frame = ctk.CTkFrame(self, fg_color="transparent")
        button_frame.pack(side="bottom", pady=15)

        ctk.CTkButton(button_frame, text="Back", width=120, command=self.go_back).grid(row=0, column=0, padx=10)
        ctk.CTkButton(button_frame, text="Add PDF", width=120, command=self.select_pdf).grid(row=0, column=2, padx=10)
        ctk.CTkButton(button_frame, text="Split PDF", width=120, command=self.split_pdf).grid(row=0, column=1, padx=10)

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
        self.file_listbox.configure(state="normal")
        self.file_listbox.delete("1.0", "end")
        for f in self.pdf_files:
            self.file_listbox.insert("end", f + "\n")
        self.file_listbox.configure(state="disabled")

    # Select mode
    def update_input_fields(self, selected_mode):
        if selected_mode in ("custom", "fixed", "specific"):
            self.input_field.configure(state="normal")
            placeholder = {
                "custom" : "e.g. 1-3,5,7-8",
                "fixed" : "e.g. (every 3 pages)",
                "specific" : "e.g. 1,4,6"
            }[selected_mode]
            self.input_field.configure(placeholder_text=placeholder)
        else:
            self.input_field.delete(0, "end")
            self.input_field.configure(state="disabled")

    # Split function
    def split_pdf(self):
        # Verifies if there is at least one pdf loaded
        if not self.pdf_files:
            CTkMessagebox(title="Error", message="No PDF file selected.", icon="cancel")
            return
        
        # Get the selected mode and input value
        mode = self.mode_var.get()
        input_value = self.input_field.get().strip()

        # Process each selected PDF
        for file_path in self.pdf_files:
            reader = PdfReader(file_path)
            
            # Custom ranges mode
            if mode == "custom":
                try:
                    ranges = self.parse_ranges(input_value, len(reader.pages))
                    for i, r in enumerate(ranges):
                        writer = PdfWriter()
                        for p in r:
                            writer.add_page(reader.pages[p])
                        with open(f"{file_path[:-4]}_part{i+1}.pdf", "wb") as f_out:
                                writer.write(f_out)
                except Exception as e:
                    CTkMessagebox(title="Error", message=f"Invalid ranges: {e}", icon="cancel")
            
            # Fixed step mode
            elif mode == "fixed":
                try:
                    step = int(input_value)
                    if step <= 0:
                        raise ValueError("Step must be greater than zero.")

                    for i in range(0, len(reader.pages), step):
                        writer = PdfWriter()
                        for p in range(i, min(i + step, len(reader.pages))):
                            writer.add_page(reader.pages[p])
                        with open(f"{file_path[:-4]}_part{i // step + 1}.pdf", "wb") as f_out:
                            writer.write(f_out)
                
                except Exception as e:
                    CTkMessagebox(title="Error", message=f"Invalid fixed value: {e}", icon="cancel")


            # Extract all pages
            elif mode == "extract_all":
                for i, page in enumerate(reader.pages):
                    writer = PdfWriter()
                    writer.add_page(page)
                    with open(f"{file_path[:-4]}_page{i+1}.pdf", "wb") as f_out:
                        writer.write(f_out)

            # Specific pages mode
            elif mode == "specific":
                try:
                    # Convert input string to list of page indices (0-based)
                    pages = [int(p.strip()) - 1 for p in input_value.split(",") if p.strip().isdigit()]
                    writer = PdfWriter()
                    for p in pages:
                        if 0 <= p < len(reader.pages):
                            writer.add_page(reader.pages[p])

                    # Save selected pages as a new PDF
                    with open(f"{file_path[:-4]}_extracted.pdf", "wb") as f_out:
                        writer.write(f_out)
                except Exception as e:
                    CTkMessagebox(title="Error", message=f"Invalid page numbers: {e}", icon="cancel")

            # Show success message after processing each file
            CTkMessagebox(title="Success", message="PDF successfully split.", icon="check")
    
    # Parse ranges like function
    def parse_ranges(self, input_str, max_pages):
        ranges = []
        parts = input_str.split(",")
        for part in parts:
            if "-" in part:
                start, end = map(int, part.split("-"))
                ranges.append(range(start - 1, end))
            else:
                ranges.append([int(part.strip()) - 1])

        # Convert ranges to lists
        return [list(r) if isinstance(r, range) else r for r in ranges]
