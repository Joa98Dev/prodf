# Libraries and modules
import os
import customtkinter as ctk
from merge import MergePanel
from split import SplitPanel
from compress import CompressPanel
from html_to_pdf import ConvertPanel
from pdf_to_html import PDF_to_HTML_Panel
from rotate import RotatePanel
from CTkMessagebox import CTkMessagebox
from PIL import Image


class PDFMenu(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("ProDF v1.0.0") # App title
        self.geometry("700x650") # Window size
        self.resizable(False, False) # Non-resizable

        # menu bar always on top
        self.create_menu_bar()

        # Dynamic screen
        self.container = ctk.CTkFrame(self)
        self.container.pack(expand=True, fill="both")

        self.show_main_area()

    # Create the menu bar
    def create_menu_bar(self):
        menu_frame = ctk.CTkFrame(self, height=40)
        menu_frame.pack(side="top", fill="x")

        # Menu bar buttons
        file_btn = ctk.CTkButton(menu_frame,
                                 text="File",
                                 width=80,
                                 height=30,
                                 corner_radius=5,
                                 command=self.show_file_menu
                                 )
        
        help_btn = ctk.CTkButton(menu_frame,
                                 text="Help",
                                 width=80,
                                 height=30,
                                 corner_radius=5,
                                 command=self.show_about
                                 )

        # Menu bar buttons features
        file_btn.pack(side="left", padx=10, pady=5)
        help_btn.pack(side="left", padx=10, pady=5)

    # Main Menu Area
    def show_main_area(self):
        self.clear_container()
        main_frame = ctk.CTkFrame(self.container)
        main_frame.pack(expand=True, fill="both", padx=20, pady=10)

        main_frame.grid_columnconfigure((0, 1, 2), weight=1, uniform="a")
        main_frame.grid_rowconfigure((0, 1), weight=1, uniform="a")

        # Button Icons
        merge_icon = ctk.CTkImage(
                Image.open(os.path.join(os.path.dirname(__file__), "icons/merge_icon.png")), size=(80, 80))

        split_icon = ctk.CTkImage(Image.open(os.path.join(os.path.dirname(__file__), "icons/split_icon.png")), size=(80, 80))

        compress_icon = ctk.CTkImage(Image.open(os.path.join(os.path.dirname(__file__), "icons/compress_icon.png")), size=(80, 80))

        html_icon = ctk.CTkImage(Image.open(os.path.join(os.path.dirname(__file__), "icons/html_icon.png")), size=(80, 80))

        pdf_html_icon = ctk.CTkImage(Image.open(os.path.join(os.path.dirname(__file__), "icons/pdf_html_icon.png")), size=(80, 80))

        rotate_icon = ctk.CTkImage(Image.open(os.path.join(os.path.dirname(__file__), "icons/rotate_icon.png")), size=(80, 80))

        # Buttons

        # Merge
        merge_btn = ctk.CTkButton(
                main_frame,
                text="Merge PDF",
                image=merge_icon,
                compound="top",
                width=150,
                height=80,
                command=self.show_merge_panel
        )

        # Split
        split_btn = ctk.CTkButton(
                main_frame,
                text="Split PDF",
                image=split_icon,
                compound="top",
                width=150,
                height=80,
                command=self.show_split_panel
        )

        # Compress
        compress_btn = ctk.CTkButton(
                main_frame,
                text="Compress PDF",
                image=compress_icon,
                compound="top",
                width=150,
                height=80,
                command=self.show_compress_panel
        )

        # Rotate
        rotate_btn = ctk.CTkButton(
                main_frame,
                text="Rotate PDF",
                image=rotate_icon,
                compound="top",
                width=150,
                height=80,
                command=self.show_rotate_panel
        )

        # HTML to PDF
        html_btn = ctk.CTkButton(
                main_frame,
                text="HTML to PDF",
                image=html_icon,
                compound="top",
                width=150,
                height=80,
                command=self.show_html_panel
        )

        # PDF to HTML
        convert_html_btn = ctk.CTkButton(
                main_frame,
                text="PDF to HTML",
                image=pdf_html_icon,
                compound="top",
                width=150,
                height=80,
                command=self.show_pdfhtml_panel
        )

        merge_btn.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

        split_btn.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")

        compress_btn.grid(row=0, column=2, padx=10, pady=10, sticky="nsew")

        rotate_btn.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")

        html_btn.grid(row=1, column=1, padx=10, pady=10, sticky="nsew")

        convert_html_btn.grid(row=1, column=2, padx=10, pady=10, sticky="nsew")

    # Button features
    def show_merge_panel(self):
        self.clear_container()
        merge_screen = MergePanel(self.container, go_back=self.show_main_area)
        merge_screen.pack(fill="both", expand=True)

    def show_split_panel(self):
        self.clear_container()
        split_screen = SplitPanel(self.container, go_back=self.show_main_area)
        split_screen.pack(fill="both", expand=True)

    def show_compress_panel(self):
        self.clear_container()
        compress_screen = CompressPanel(self.container, go_back=self.show_main_area)
        compress_screen.pack(fill="both", expand=True)

    def show_rotate_panel(self):
        self.clear_container()
        rotate_screen = RotatePanel(self.container, go_back=self.show_main_area)
        rotate_screen.pack(fill="both", expand=True)

    def show_html_panel(self):
        self.clear_container()
        html_screen = ConvertPanel(self.container, go_back_callback=self.show_main_area)
        html_screen.pack(fill="both", expand=True)

    def show_pdfhtml_panel(self):
        self.clear_container()
        pdfhtml_screen = PDF_to_HTML_Panel(self.container, go_back_callback=self.show_main_area)
        pdfhtml_screen.pack(fill="both", expand=True)

    def show_file_menu(self):
        win = ctk.CTkToplevel(self)
        win.title("File")
        win.geometry("220x120")
        win.resizable(False, False)

        ctk.CTkLabel(win, text="File options:", font=ctk.CTkFont(size=14, weight="bold")).pack(pady=10)
        ctk.CTkButton(win, text="Close", command=self.destroy).pack(pady=5)

    # About screen info
    def show_about(self):
        CTkMessagebox(
            title="About",
            message="ProDF v1.0.0\nDeveloped by Joa98\njoadev98@gmail.com\n\nLicense: GPL v3.0\nSource code available at:\nhttps://official-repo",
            icon="info",
            option_1="OK"
        )

    def clear_container(self):
        for widget in self.container.winfo_children():
            widget.destroy()

