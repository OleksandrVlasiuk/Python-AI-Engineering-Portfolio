# ==============================================================================
# FILE ENCODING CONVERTER & VIEWER
# A Tkinter-based GUI utility for detecting, viewing, and converting text file 
# encodings (UTF-8, UTF-16, ANSI, Windows-1251) using the chardet library.
# ==============================================================================

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import codecs
import chardet
import os
import time

# ==============================================================================
# PHASE 1: GUI INITIALIZATION & LAYOUT CONFIGURATION
# ==============================================================================
def create_main_window():
    global root, text_box, message_box, file_info_label, current_file, encoding_var, line_numbers

    root = tk.Tk()
    root.title('Universal File Encoding Utility')
    root.geometry("900x500")

    main_frame = ttk.Frame(root)
    main_frame.pack(fill=tk.BOTH, expand=1)

    # --- Header: File Metadata & Encoding Display ---
    top_frame = ttk.Frame(main_frame)
    top_frame.pack(fill=tk.X)

    file_info_label = ttk.Label(top_frame, text="Active File: None | Encoding: utf-8")
    file_info_label.pack(fill=tk.X)

    content_frame = ttk.Frame(main_frame)
    content_frame.pack(fill=tk.BOTH, expand=1)

    # --- Main Editor Area (with synchronized line numbers) ---
    text_box_frame = ttk.Frame(content_frame)
    text_box_frame.pack(fill=tk.BOTH, expand=1)

    line_numbers = tk.Text(text_box_frame, width=4, padx=5, state=tk.DISABLED, bg="#f0f0f0")
    line_numbers.pack(side=tk.LEFT, fill=tk.Y)

    text_box = tk.Text(text_box_frame, wrap=tk.NONE)
    text_box.pack(side=tk.LEFT, fill=tk.BOTH, expand=1)
    
    # Bind events for dynamic line number synchronization
    text_box.bind("<KeyRelease>", update_line_numbers)
    text_box.bind("<MouseWheel>", sync_scroll)

    scroll_y_text = ttk.Scrollbar(text_box_frame, orient=tk.VERTICAL, command=sync_scroll)
    scroll_y_text.pack(side=tk.RIGHT, fill=tk.Y)
    text_box.config(yscrollcommand=scroll_y_text.set)

    # --- Footer: Operation Logs Console ---
    message_box_frame = ttk.Frame(content_frame)
    message_box_frame.pack(fill=tk.X)

    message_box = tk.Text(message_box_frame, wrap=tk.NONE, height=5, bg="#f8f9fa")
    message_box.pack(fill=tk.BOTH, expand=1)

    encoding_var = tk.StringVar(value="utf-8")
    current_file = None

def create_menu():
    """Constructs the application navigation menu bar."""
    menubar = tk.Menu(root)
    root.config(menu=menubar)

    # File Control Menu
    file_menu = tk.Menu(menubar, tearoff=0)
    menubar.add_cascade(label="File", menu=file_menu)
    file_menu.add_command(label="Open File", command=open_file)
    file_menu.add_command(label="Save", command=save_file)
    file_menu.add_command(label="Save As...", command=save_file_as)
    file_menu.add_command(label="Clear Editor", command=clear_text)
    file_menu.add_separator()
    file_menu.add_command(label="Exit", command=root.quit)

    # Encoding Translation & Conversion Menu
    encoding_menu = tk.Menu(menubar, tearoff=0)
    menubar.add_cascade(label="Encoding Operations", menu=encoding_menu)
    
    # View Modes
    encoding_menu.add_command(label="Reload as UTF-8", command=lambda: change_view_encoding("utf-8"))
    encoding_menu.add_command(label="Reload as UTF-16", command=lambda: change_view_encoding("utf-16"))
    encoding_menu.add_command(label="Reload as ANSI", command=lambda: change_view_encoding("ansi"))
    encoding_menu.add_command(label="Reload as Windows-1251", command=lambda: change_view_encoding("windows-1251"))
    encoding_menu.add_separator()
    
    # Conversion Operations
    encoding_menu.add_command(label="Convert to UTF-8", command=lambda: convert_encoding("utf-8"))
    encoding_menu.add_command(label="Convert to UTF-16", command=lambda: convert_encoding("utf-16"))
    encoding_menu.add_command(label="Convert to ANSI", command=lambda: convert_encoding("ansi"))
    encoding_menu.add_command(label="Convert to Windows-1251", command=lambda: convert_encoding("windows-1251"))

# ==============================================================================
# PHASE 2: CORE ENCODING LOGIC & FILE I/O
# ==============================================================================
def try_open_file_with_encoding(filename):
    """
    Attempts to read a file by heuristically detecting its encoding via chardet.
    Falls back to a predefined list of common encodings if strict detection fails.
    """
    # Phase A: Heuristic Detection
    with open(filename, 'rb') as f:
        raw_data = f.read(10000)  # Sample the first 10KB
        detected = chardet.detect(raw_data)
        detected_encoding = detected['encoding']

    # Phase B: Fallback Array
    encodings_to_try = [detected_encoding, 'utf-8', 'utf-16', 'windows-1251', 'ansi']
    encodings_to_try = [enc for enc in encodings_to_try if enc]  # Filter out None types

    for enc in encodings_to_try:
        try:
            with codecs.open(filename, 'r', encoding=enc) as file:
                content = file.read()
            return content, enc
        except (UnicodeDecodeError, LookupError):
            continue  # Catch decode failures and attempt the next format

    raise Exception("Unsupported or corrupted file encoding.")

def open_file():
    global current_file
    filename = filedialog.askopenfilename()
    if filename:
        try:
            content, detected_encoding = try_open_file_with_encoding(filename)

            text_box.delete(1.0, tk.END)
            text_box.insert(tk.END, content)

            update_file_info(filename, detected_encoding)
            update_message_box(f"Successfully opened: {os.path.basename(filename)} (Detected: {detected_encoding})")
            
            current_file = filename
            encoding_var.set(detected_encoding)  
            update_line_numbers()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to parse file: {e}")

def save_file():
    global current_file
    if current_file:
        with open(current_file, 'w', encoding=encoding_var.get()) as file:
            content = text_box.get(1.0, tk.END)
            file.write(content)
        update_message_box(f"Changes saved securely to: {os.path.basename(current_file)}")
    else:
        save_file_as()

def save_file_as():
    global current_file
    filename = filedialog.asksaveasfilename(defaultextension=".txt",
                                            filetypes=[("Text Documents", "*.txt"), ("All Files", "*.*")])
    if filename:
        with open(filename, 'w', encoding=encoding_var.get()) as file:
            content = text_box.get(1.0, tk.END)
            file.write(content)
        update_file_info(filename)
        update_message_box(f"File successfully saved as: {os.path.basename(filename)}")
        current_file = filename

def clear_text():
    text_box.delete(1.0, tk.END)
    update_message_box("Editor buffer cleared.")
    update_file_info(None)

# ==============================================================================
# PHASE 3: ENCODING TRANSLATION OPERATIONS
# ==============================================================================
def change_view_encoding(encoding_type):
    """Reloads the active file using a user-specified encoding format."""
    global current_file
    if current_file:
        try:
            with open(current_file, 'r', encoding=encoding_type) as file:
                content = file.read()
            text_box.delete(1.0, tk.END)
            text_box.insert(tk.END, content)
            encoding_var.set(encoding_type)
            update_file_info(current_file)
            update_message_box(f"Buffer reloaded. Currently viewing as: {encoding_type.upper()}.")
        except Exception:
            update_message_box(f"Decode Error: Cannot view file in {encoding_type.upper()}. Formats are incompatible.")

def convert_encoding(encoding_type):
    """Destructively converts and saves the active file into a new target encoding."""
    global current_file
    if not current_file:
        update_message_box("Operation Failed: No active file loaded for conversion.")
        return
        
    try:
        # Read payload using the active stable encoding
        with open(current_file, 'r', encoding=encoding_var.get()) as file:
            content = file.read()

        # Overwrite payload using the target encoding ('replace' handles malformed bytes)
        with open(current_file, 'w', encoding=encoding_type, errors='replace') as file:
            file.write(content)

        encoding_var.set(encoding_type)
        update_file_info(current_file)
        update_message_box(f"Success: File encoding permanently converted to {encoding_type.upper()}.")
    except Exception as e:
        update_message_box(f"Conversion to {encoding_type.upper()} failed. Reason: {str(e)}")

# ==============================================================================
# PHASE 4: GUI UTILITIES & EVENT HANDLERS
# ==============================================================================
def update_message_box(message):
    """Appends operational logs to the bottom text console."""
    message_box.insert(tk.END, f" [LOG] {message}\n")
    message_box.yview(tk.END)  

def update_line_numbers(event=None):
    """Synchronizes the left-hand line numbering pane with the active editor text."""
    line_numbers.config(state=tk.NORMAL)
    line_numbers.delete(1.0, tk.END)
    lines = text_box.get(1.0, tk.END).split('\n')
    for i in range(1, len(lines)):
        line_numbers.insert(tk.END, f"{i}\n")
    line_numbers.config(state=tk.DISABLED)

def sync_scroll(*args):
    """Binds the vertical scrollbar to both the text editor and the line numbers pane."""
    text_box.yview(*args)
    line_numbers.yview(*args)

def update_file_info(filename, encoding_type=None):
    """Refreshes the top metadata header."""
    file_name_display = os.path.basename(filename) if filename else 'None'
    enc_display = encoding_type if encoding_type else encoding_var.get()
    file_info_label.config(text=f"Active File: {file_name_display} | Encoding: {enc_display.upper()}")

# === Execution Trigger ===
if __name__ == "__main__":
    create_main_window()
    create_menu()
    root.mainloop()