# ==============================================================================
# ETL PANDAS DATA CLEANER
# A Tkinter GUI utility for Extracting, Transforming, and Loading datasets.
# Uses the Pandas library to seamlessly read CSV, JSON, and Excel files, 
# sanitize data (drop NaN and duplicates), and export to multiple formats.
# ==============================================================================

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import pandas as pd
import os

# ==============================================================================
# PHASE 1: GLOBAL STATE & UI INITIALIZATION
# ==============================================================================
current_df = None  # Global Pandas DataFrame to hold the active dataset

def create_main_window():
    global root, text_box, message_box, file_info_label, line_numbers

    root = tk.Tk()
    root.title('ETL Data Cleaner & Transformer')
    root.geometry("900x500")

    main_frame = ttk.Frame(root)
    main_frame.pack(fill=tk.BOTH, expand=1)

    # --- Top Header & Metadata ---
    top_frame = ttk.Frame(main_frame)
    top_frame.pack(fill=tk.X)

    file_info_label = ttk.Label(top_frame, text="Active Dataset: None", font=("Arial", 10, "bold"))
    file_info_label.pack(fill=tk.X, pady=5, padx=5)

    # --- Control Panel (Buttons) ---
    button_frame = ttk.Frame(top_frame)
    button_frame.pack(pady=5)

    # Ingestion Buttons
    ttk.Button(button_frame, text="Load CSV", command=lambda: load_file("csv")).grid(row=0, column=0, padx=5)
    ttk.Button(button_frame, text="Load JSON", command=lambda: load_file("json")).grid(row=0, column=1, padx=5)
    ttk.Button(button_frame, text="Load Excel", command=lambda: load_file("xlsx")).grid(row=0, column=2, padx=5)

    # Transformation Button
    btn_clean = ttk.Button(button_frame, text="Sanitize (Drop NaNs & Duplicates)", command=clean_data)
    btn_clean.grid(row=0, column=3, padx=15)

    # Extraction/Export Buttons
    ttk.Button(button_frame, text="Export CSV", command=lambda: save_file("csv")).grid(row=0, column=4, padx=5)
    ttk.Button(button_frame, text="Export JSON", command=lambda: save_file("json")).grid(row=0, column=5, padx=5)
    ttk.Button(button_frame, text="Export Excel", command=lambda: save_file("xlsx")).grid(row=0, column=6, padx=5)

    # --- Data Visualization Area ---
    content_frame = ttk.Frame(main_frame)
    content_frame.pack(fill=tk.BOTH, expand=1)

    text_box_frame = ttk.Frame(content_frame)
    text_box_frame.pack(fill=tk.BOTH, expand=1, pady=5)

    # Line Numbers
    line_numbers = tk.Text(text_box_frame, width=5, padx=5, state=tk.DISABLED, bg="#f0f0f0")
    line_numbers.pack(side=tk.LEFT, fill=tk.Y)

    # Main Text Buffer
    text_box = tk.Text(text_box_frame, wrap=tk.NONE)
    text_box.pack(side=tk.LEFT, fill=tk.BOTH, expand=1)
    
    text_box.bind("<KeyRelease>", update_line_numbers)
    text_box.bind("<MouseWheel>", sync_scroll)

    # Scrollbars
    scroll_y_text = ttk.Scrollbar(text_box_frame, orient=tk.VERTICAL, command=sync_scroll)
    scroll_y_text.pack(side=tk.RIGHT, fill=tk.Y)
    text_box.config(yscrollcommand=scroll_y_text.set)

    scroll_x_text = ttk.Scrollbar(content_frame, orient=tk.HORIZONTAL, command=text_box.xview)
    scroll_x_text.pack(fill=tk.X)
    text_box.config(xscrollcommand=scroll_x_text.set)

    # --- System Log Console ---
    message_box = tk.Text(content_frame, wrap=tk.WORD, height=5, bg="#f8f9fa")
    message_box.pack(fill=tk.X, pady=5)

    root.mainloop()

# ==============================================================================
# PHASE 2: ETL OPERATIONS (EXTRACT, TRANSFORM, LOAD)
# ==============================================================================

def load_file(file_type):
    """EXTRACT: Opens a file dialog and loads the dataset into a Pandas DataFrame."""
    global current_df
    
    file_path = filedialog.askopenfilename(filetypes=[(file_type.upper() + " Files", f"*.{file_type}")])
    if not file_path:
        return

    try:
        if file_type == "csv":
            current_df = pd.read_csv(file_path, low_memory=False)
        elif file_type == "json":
            current_df = pd.read_json(file_path)
        elif file_type == "xlsx":
            current_df = pd.read_excel(file_path)

        display_data(current_df)
        file_name = os.path.basename(file_path)
        
        file_info_label.config(text=f"Active Dataset: {file_name} | Shape: {current_df.shape[0]} rows, {current_df.shape[1]} cols")
        log_message(f"Successfully loaded {file_type.upper()} file: {file_name}")
        
    except Exception as e:
        messagebox.showerror("Ingestion Error", f"Failed to open {file_type.upper()} file:\n{e}")

def clean_data():
    """TRANSFORM: Sanitizes the active DataFrame by removing duplicates and missing values."""
    global current_df
    
    if current_df is None:
        messagebox.showwarning("Warning", "No dataset loaded. Please load a file first.")
        return

    try:
        initial_rows = current_df.shape[0]

        # Transformation pipeline
        current_df.drop_duplicates(inplace=True)
        current_df.dropna(how='any', inplace=True)

        final_rows = current_df.shape[0]
        rows_removed = initial_rows - final_rows

        display_data(current_df)
        
        file_info_label.config(text=f"Active Dataset (Cleaned) | Shape: {current_df.shape[0]} rows, {current_df.shape[1]} cols")
        log_message(f"Sanitization complete. Removed {rows_removed} invalid or duplicate rows.")
        messagebox.showinfo("Success", f"Data cleaned successfully!\nRows removed: {rows_removed}")
        
    except Exception as e:
        messagebox.showerror("Transformation Error", f"Failed to clean data:\n{e}")

def save_file(file_type):
    """LOAD: Exports the active DataFrame to the requested file format."""
    global current_df
    
    if current_df is None:
        messagebox.showwarning("Warning", "No dataset available to export.")
        return

    file_path = filedialog.asksaveasfilename(defaultextension=f".{file_type}",
                                             filetypes=[(file_type.upper() + " Files", f"*.{file_type}")])
    if not file_path:
        return

    try:
        if file_type == "csv":
            current_df.to_csv(file_path, index=False)
        elif file_type == "json":
            current_df.to_json(file_path, orient="records", indent=4, force_ascii=False)
        elif file_type == "xlsx":
            with pd.ExcelWriter(file_path, engine='xlsxwriter') as writer:
                current_df.to_excel(writer, index=False)

        file_name = os.path.basename(file_path)
        log_message(f"Successfully exported dataset to {file_type.upper()}: {file_name}")
        messagebox.showinfo("Success", f"File saved securely as {file_type.upper()}!")
        
    except Exception as e:
        messagebox.showerror("Export Error", f"Failed to save {file_type.upper()} file:\n{e}")

# ==============================================================================
# PHASE 3: GUI UTILITIES & EVENT HANDLERS
# ==============================================================================

def display_data(df):
    """Renders the DataFrame inside the Tkinter text buffer."""
    text_box.delete("1.0", tk.END)
    # Using to_string() for a clean tabular layout in standard text widgets
    text_box.insert(tk.END, df.to_string(index=False))
    update_line_numbers()

def log_message(message):
    """Appends system events to the log console."""
    message_box.insert(tk.END, f"[LOG] {message}\n")
    message_box.yview(tk.END)

def update_line_numbers(event=None):
    """Synchronizes the line number margin with the active text buffer."""
    line_numbers.config(state=tk.NORMAL)
    line_numbers.delete("1.0", tk.END)
    lines = text_box.get("1.0", tk.END).split("\n")
    for i in range(1, len(lines)):
        line_numbers.insert(tk.END, f"{i}\n")
    line_numbers.config(state=tk.DISABLED)

def sync_scroll(*args):
    """Binds vertical scrolling to both the text box and line numbers."""
    line_numbers.yview(*args)
    text_box.yview(*args)

# === Execution Trigger ===
if __name__ == "__main__":
    create_main_window()