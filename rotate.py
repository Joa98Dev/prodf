# Libraries
import customtkinter as ctk
from tkinter import filedialog
from pypdf import PdfReader, PdfWriter
from CTkMessagebox import CTkMessagebox


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
        self.file_listbox = ctk.CTkTextbox(self, height=120, width=400, state="disabled")
        self.file_listbox.pack(pady=5, padx=20, fill="both", expand=True)

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
        self.file_listbox.configure(state="normal")
        self.file_listbox.delete("1.0", "end")
        for f in self.pdf_files:
            angle = self.rotations.get(f, 0)
            self.file_listbox.insert("end", f"{f}  (Rotation: {angle}°)\n")
        self.file_listbox.configure(state="disabled")

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

