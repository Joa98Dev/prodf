# Libraries and modules
import os
import sys
from PIL import Image, ImageTk
from menu import PDFMenu
import customtkinter as ctk



# Helper: get path for resources
def resource_path(path):
    """Get absolute path to resource, works for PyInstaller."""
    if hasattr(sys, "_MEIPASS"):
        return os.path.join(sys._MEIPASS, path)
    return os.path.join(os.path.abspath("."), path)

# Helper: set window icon cross-platform
def set_window_icon(window, icon_path):
    """Sets window icon on Windows (.ico) or Linux/macOS (.png)."""
    if sys.platform.startswith("win"):
        try:
            window.iconbitmap(icon_path)
        except Exception as e:
            print("Failed to load icon.ico:", e)
    else:
        try:
            img = Image.open(icon_path)
            photo = ImageTk.PhotoImage(img)
            window.iconphoto(True, photo)
        except Exception as e:
            print("Failed to load icon.png:", e)


# Main application
if __name__ == "__main__":

    # Set appearance and theme
    ctk.set_appearance_mode("System")
    ctk.set_default_color_theme(resource_path("themes/dark_rose.json"))
    #ctk.set_default_color_theme(resource_path("themes/frutiger.json"))

    # Create the main window
    app = PDFMenu()

    # Load icon (Windows: .ico, Linux/macOS: .png)
    icon_path = resource_path("icon.png")
    set_window_icon(app, icon_path)

    # Start the app
    app.mainloop()

