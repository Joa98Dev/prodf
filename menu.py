# Libraries and modules
import os
import customtkinter as ctk
from merge import MergePanel
from split import SplitPanel
from compress import CompressPanel
from html_to_pdf import ConvertPanel
from pdf_to_html import PDF_to_HTML_Panel
from rotate import RotatePanel
from sign import SignPanel
from watermark import WatermarkPanel
from encrypt import EncryptPanel
from decrypt import DecryptPanel
from imagetopdf import ImageToPDFPanel
from pdftoimage import PDFToImagePanel
from CTkMessagebox import CTkMessagebox
from PIL import Image


class PDFMenu(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("ProDF v1.6.0") # App title
        self.geometry("800x650")
        self.resizable(False, False) # Non-resizable

        # light/dark theme
        self.theme_mode = "dark"

        # Add navigation buttons
        self.current_page = 0
        self.buttons_per_page = 6


        # menu bar always on top
        self.create_menu_bar()

        # Dynamic screen
        self.container = ctk.CTkFrame(self)
        self.container.pack(expand=True, fill="both")


        # --------------------------
        #  LIGHT/DARK MODE TOGGLE
        # --------------------------
        self.theme_button = ctk.CTkButton(
            self,
            text="🌙",           # default (dark theme)
            width=40,
            height=30,
            fg_color="transparent",
            hover_color=("gray70", "gray30"),
            command=self.toggle_theme
        )
        self.theme_button.place(relx=0.98, rely=0.02, anchor="ne")



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

        # Set button grids to 3x2 (6 buttons per page)
        for r in range(2):
            main_frame.grid_rowconfigure(r, weight=1)
        for c in range(3):
            main_frame.grid_columnconfigure(c, weight=1)

        # --- NEW DEFINEND BUTTON LIST ---
        all_buttons = [
            ("Merge PDF", "icons/merge_icon.png", self.show_merge_panel),
            ("Split PDF", "icons/split_icon.png", self.show_split_panel),
            ("Compress PDF", "icons/compress_icon.png", self.show_compress_panel),
            ("Rotate PDF", "icons/rotate_icon.png", self.show_rotate_panel),
            ("HTML to PDF", "icons/html_icon.png", self.show_html_panel),
            ("PDF to HTML", "icons/pdf_html_icon.png", self.show_pdfhtml_panel),
            ("Sign PDF", "icons/sign_icon.png", self.show_sign_panel),
            ("Watermark", "icons/watermark_icon.png", self.show_watermark_panel),
            ("Encrypt", "icons/encrypt_icon.png", self.show_encrypt_panel),
            ("Decrypt", "icons/decrypt_icon.png", self.show_decrypt_panel),
            ("JPG to PDF", "icons/imagetopdf_icon.png", self.show_image_to_pdf_panel),
            ("PDF to JPG", "icons/pdftoimage_icon.png", self.show_pdf_to_image_panel),
        ]

        total_pages = (len(all_buttons) - 1) // self.buttons_per_page + 1
        
        # Get buttons of current panel
        start = self.current_page * self.buttons_per_page
        end = start + self.buttons_per_page
        page_buttons = all_buttons[start:end]

        # Render buttons
        for index, (label, icon_file, action) in enumerate(page_buttons):
            row = index // 3
            col = index % 3

            icon = ctk.CTkImage(
                Image.open(os.path.join(os.path.dirname(__file__), icon_file)),
                size=(80, 80)
            )

            btn = ctk.CTkButton(
                main_frame,
                text=label,
                font=("Roboto", 18),
                image=icon,
                compound="top",
                width=120,
                height=120,
                command=action
            )
            btn.grid(row=row, column=col, padx=10, pady=10, sticky="nsew")

        # --- PREVIOUS BUTTON ---
        prev_btn = ctk.CTkButton(
            main_frame,
            text="◀",
            width=40,
            height=40,
            corner_radius=14,
            font=("Roboto", 22),
            fg_color="transparent",
            hover_color="#2b2b2b",
            border_color="#3a3a3a",
            #border_width=2,
            command=lambda: self.change_page(-1)
        )
        prev_btn.place(x=10, rely=0.5, anchor="w")

        # --- NEXT BUTTON ---
        next_btn = ctk.CTkButton(
            main_frame,
            text="▶",
            width=40,
            height=40,
            corner_radius=14,
            font=("Roboto", 22),
            fg_color="transparent",
            hover_color="#2b2b2b",
            border_color="#3a3a3a",
            #border_width=2,
            command=lambda: self.change_page(1)
        )
        next_btn.place(relx=1.0, x=-10, rely=0.5, anchor="e")

    def change_page(self, direction):
        # Total of buttons
        total = 12
        total_pages = (total - 1) // self.buttons_per_page + 1

        self.current_page = (self.current_page + direction) % total_pages
        self.show_main_area()


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

    def show_sign_panel(self):
        self.clear_container()
        sign_screen = SignPanel(self.container, go_back=self.show_main_area)
        sign_screen.pack(fill="both", expand=True)

    def show_watermark_panel(self):
        self.clear_container()
        watermark_screen = WatermarkPanel(self.container, go_back=self.show_main_area)
        watermark_screen.pack(fill="both", expand=True)

    def show_encrypt_panel(self):
        self.clear_container()
        encrypt_screen = EncryptPanel(self.container, go_back=self.show_main_area)
        encrypt_screen.pack(fill="both", expand=True)

    def show_decrypt_panel(self):
        self.clear_container()
        decrypt_screen = DecryptPanel(self.container, go_back=self.show_main_area)
        decrypt_screen.pack(fill="both", expand=True)

    def show_image_to_pdf_panel(self):
        self.clear_container()
        imgtopdf_screen = ImageToPDFPanel(self.container, go_back=self.show_main_area)
        imgtopdf_screen.pack(fill="both", expand=True)

    def show_pdf_to_image_panel(self):
        self.clear_container()
        pdftoimg_screen = PDFToImagePanel(self.container, go_back=self.show_main_area)
        pdftoimg_screen.pack(fill="both", expand=True)


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
            message="ProDF v1.6.0\nDeveloped by Joa98\njoadev98@gmail.com\n\nLicense: GPL v3.0\nSource code available at:\nhttps://github.com/Joa98Dev/prodf\n",
            icon="info",
            option_1="OK"
        )


    def toggle_theme(self):
        if not hasattr(self, "theme_mode"):
            self.theme_mode = "dark"

        if self.theme_mode == "dark":
            ctk.set_appearance_mode("light")
            self.theme_mode = "light"
            self.theme_button.configure(text="🌙")
        else:
            ctk.set_appearance_mode("dark")
            self.theme_mode = "dark"
            self.theme_button.configure(text="☀️")


    def clear_container(self):
        for widget in self.container.winfo_children():
            widget.destroy()

