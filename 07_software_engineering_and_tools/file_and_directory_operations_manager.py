# ==============================================================================
# FILE SYSTEM & DIRECTORY MANAGER
# A Tkinter-based GUI utility for executing advanced file operations, 
# including duplication detection, chronological sorting, text editing, 
# and automated directory organization based on file extensions.
# ==============================================================================

import tkinter as tk
from tkinter import ttk
from tkinter import filedialog, simpledialog, messagebox
import os
import shutil
import time
from datetime import datetime

# ==============================================================================
# PHASE 1: GUI INITIALIZATION & LAYOUT CONFIGURATION
# ==============================================================================

def create_main_window():
    global root, text_box, result_box, message_box, file_info_label, current_file

    root = tk.Tk()
    root.title('File and Directory Operations Manager')
    root.geometry("900x500")

    main_frame = ttk.Frame(root)
    main_frame.pack(fill=tk.BOTH, expand=1)

    # --- Top Frame: File Metadata Display ---
    top_frame = ttk.Frame(main_frame)
    top_frame.pack(fill=tk.X)

    file_info_label = ttk.Label(top_frame, text="Active File Info: None")
    file_info_label.pack(fill=tk.X)

    content_frame = ttk.Frame(main_frame)
    content_frame.pack(fill=tk.BOTH, expand=1)

    # --- Left Pane: Primary Text Editor ---
    text_box_frame = ttk.Frame(content_frame)
    text_box_frame.grid(row=0, column=0, sticky="nsew")

    text_box = tk.Text(text_box_frame, wrap=tk.NONE)
    text_box.pack(fill=tk.BOTH, expand=1)

    scroll_y_text = ttk.Scrollbar(text_box_frame, orient=tk.VERTICAL, command=text_box.yview)
    scroll_y_text.pack(side=tk.RIGHT, fill=tk.Y)

    scroll_x_text = ttk.Scrollbar(text_box_frame, orient=tk.HORIZONTAL, command=text_box.xview)
    scroll_x_text.pack(side=tk.BOTTOM, fill=tk.X)

    text_box.config(yscrollcommand=scroll_y_text.set, xscrollcommand=scroll_x_text.set)

    # --- Right Pane: Operation Results Output ---
    result_box_frame = ttk.Frame(content_frame)
    result_box_frame.grid(row=0, column=1, sticky="nsew")

    result_box = tk.Text(result_box_frame, wrap=tk.NONE, height=5)
    result_box.pack(fill=tk.BOTH, expand=1)

    # Add internal padding for cleaner output rendering
    result_box.config(padx=10, pady=10) 

    scroll_y_result = ttk.Scrollbar(result_box_frame, orient=tk.VERTICAL, command=result_box.yview)
    scroll_y_result.pack(side=tk.RIGHT, fill=tk.Y)

    # --- Bottom Pane: System Notifications & Logs ---
    message_box_frame = ttk.Frame(content_frame)
    message_box_frame.grid(row=1, column=0, columnspan=2, sticky="nsew")

    message_box = tk.Text(message_box_frame, wrap=tk.NONE, height=5)
    message_box.pack(fill=tk.BOTH, expand=1)

    scroll_y_message = ttk.Scrollbar(message_box_frame, orient=tk.VERTICAL, command=message_box.yview)
    scroll_y_message.pack(side=tk.RIGHT, fill=tk.Y)

    message_box.config(yscrollcommand=scroll_y_message.set)
    result_box.config(yscrollcommand=scroll_y_result.set)

    # --- Grid Weight Configurations for Dynamic Resizing ---
    content_frame.grid_columnconfigure(0, weight=3)
    content_frame.grid_columnconfigure(1, weight=1)
    content_frame.grid_rowconfigure(0, weight=2)
    content_frame.grid_rowconfigure(1, weight=1)

    current_file = None  # Track the current active file session


def create_menu():
    """Constructs the application navigation menu bar."""
    menubar = tk.Menu(root)
    root.config(menu=menubar)

    # File Control Menu
    file_menu = tk.Menu(menubar, tearoff=0)
    menubar.add_cascade(label="File", menu=file_menu)
    file_menu.add_command(label="Open File", command=open_file)
    file_menu.add_command(label="Save", command=save_file)
    file_menu.add_command(label="Save As", command=save_file_as)
    file_menu.add_command(label="Clear Editor", command=clear_text)
    file_menu.add_separator()
    file_menu.add_command(label="Exit Application", command=root.quit)

    # File System Operations Menu
    operation_menu = tk.Menu(menubar, tearoff=0)
    menubar.add_cascade(label="FS Operations", menu=operation_menu)
    operation_menu.add_command(label="Analyze File Chronology (Task 1)", command=find_newest_oldest_files)
    operation_menu.add_command(label="Detect Duplicate Files (Task 2)", command=find_duplicates)
    operation_menu.add_command(label="Filter Files by Extension (Task 3)", command=list_files_by_type)
    operation_menu.add_command(label="Auto-Organize Directory (Task 4)", command=organize_files_by_type)
    operation_menu.add_command(label="List All Directory Contents", command=list_all_files)

    # System Info Menu
    help_menu = tk.Menu(menubar, tearoff=0)
    menubar.add_cascade(label="Help", menu=help_menu)
    help_menu.add_command(label="About", command=show_about_message)

# ==============================================================================
# PHASE 2: BASIC FILE I/O OPERATIONS (EDITOR)
# ==============================================================================

def open_file():
    global current_file
    filename = filedialog.askopenfilename()
    if filename:
        with open(filename, 'r', encoding='utf-8', errors='replace') as file:
            content = file.read()
        text_box.delete(1.0, tk.END)
        text_box.insert(tk.END, content)
        update_file_info(filename)
        message_box.insert(tk.END, f"Successfully opened file: {filename}\n")
        current_file = filename

def save_file():
    global current_file
    if current_file:
        with open(current_file, 'w', encoding='utf-8') as file:
            content = text_box.get(1.0, tk.END)
            file.write(content)
        message_box.insert(tk.END, f"Saved changes to file: {current_file}\n")
    else:
        save_file_as()

def save_file_as():
    global current_file
    filename = filedialog.asksaveasfilename(defaultextension=".txt",
                                            filetypes=[("Text Documents", "*.txt"), ("All Files", "*.*")])
    if filename:
        with open(filename, 'w', encoding='utf-8') as file:
            content = text_box.get(1.0, tk.END)
            file.write(content)
        update_file_info(filename)
        message_box.insert(tk.END, f"Saved new file as: {filename}\n")
        current_file = filename

def clear_text():
    text_box.delete(1.0, tk.END)
    message_box.insert(tk.END, "Editor buffer cleared.\n")
    update_file_info(None)

def update_file_info(filename):
    """Fetches and displays metadata (size, modification time) for the active file."""
    if filename:
        size = os.path.getsize(filename)
        mtime = os.path.getmtime(filename)
        sttm = time.localtime(mtime)
        info_text = (f"Target: {filename} | Buffer Size: {size} bytes | "
                     f"Last Modified: {sttm.tm_year}-{sttm.tm_mon}-{sttm.tm_mday} "
                     f"{sttm.tm_hour}:{sttm.tm_min}:{sttm.tm_sec}")
    else:
        info_text = "Active File Info: None"
    file_info_label.config(text=info_text)

def show_about_message():
    messagebox.showinfo("About", "File System & Directory Manager\nVersion 1.0 \nDeveloped by Oleksandr Vlasiuk\n")


# ==============================================================================
# PHASE 3: ADVANCED FILE SYSTEM OPERATIONS (ALGORITHMS)
# ==============================================================================

# Task 1: Chronological Directory Analysis
def find_newest_oldest_files():
    """Scans a directory and ranks files based on their last modification timestamp."""
    folder = filedialog.askdirectory()
    if folder:
        files = [os.path.join(folder, f) for f in os.listdir(folder) if os.path.isfile(os.path.join(folder, f))]
        # Sort files chronologically (Newest first)
        files.sort(key=os.path.getmtime, reverse=True)  

        newest_files = files[:2]
        oldest_files = files[-2:]  # Extract the last two files

        result_box.delete(1.0, tk.END)

        # Print Most Recently Modified
        result_box.insert(tk.END, "Recently Modified Files (Newest):\n")
        for file in newest_files:
            file_name = os.path.basename(file)
            result_box.insert(tk.END, f"{file_name} - {datetime.fromtimestamp(os.path.getmtime(file))}\n")

        # Print Oldest Files
        result_box.insert(tk.END, "\nOldest Files in Directory:\n")
        for file in oldest_files:
            file_name = os.path.basename(file)
            result_box.insert(tk.END, f"{file_name} - {datetime.fromtimestamp(os.path.getmtime(file))}\n")

        # Print Complete Chronological List
        result_box.insert(tk.END, "\nComplete Directory Chronology:\n")
        for file in files:
            file_name = os.path.basename(file)
            result_box.insert(tk.END, f"{file_name} - {datetime.fromtimestamp(os.path.getmtime(file))}\n")

# Task 2: Cross-Directory Duplication Detection
def find_duplicates():
    """Compares two directories and identifies files with identical names and byte sizes."""
    folder1 = filedialog.askdirectory(title="Select Primary Directory")
    folder2 = filedialog.askdirectory(title="Select Secondary Directory for Comparison")
    
    if folder1 and folder2:
        # Create hash maps based on filename and filesize
        files1 = {f: os.path.getsize(os.path.join(folder1, f)) for f in os.listdir(folder1) if
                  os.path.isfile(os.path.join(folder1, f))}
        files2 = {f: os.path.getsize(os.path.join(folder2, f)) for f in os.listdir(folder2) if
                  os.path.isfile(os.path.join(folder2, f))}
                  
        # Detect intersections (Duplicates)
        duplicates = set(files1.items()) & set(files2.items())

        result_box.delete(1.0, tk.END)
        result_box.insert(tk.END, f"Scanning Base Directory: {os.path.basename(folder1)}\n")
        result_box.insert(tk.END, f"Against Target Directory: {os.path.basename(folder2)}\n\n")
        result_box.insert(tk.END, "Identified Duplicate Files:\n")
        for file, size in duplicates:
            result_box.insert(tk.END, f"{file} - Size Allocation: {size} bytes\n")

# Task 3: Recursive Extension Filtering
def list_files_by_type():
    """Walks through a directory recursively and filters files based on specified extensions."""
    folder = filedialog.askdirectory()
    if folder:
        file_types = simpledialog.askstring("Input", "Enter desired file extensions (e.g., .txt, .py):")
        if file_types:
            file_types = [ft.strip() for ft in file_types.split(",")]
            matches = []
            
            # Recursive directory walk
            for root, dirs, files in os.walk(folder):
                for file in files:
                    if any(file.endswith(ft) for ft in file_types):
                        # Extract relative pathing for cleaner output
                        relative_path = os.path.relpath(os.path.join(root, file), folder)
                        matches.append(relative_path)

            result_box.delete(1.0, tk.END)
            result_box.insert(tk.END, f"Found files matching extensions {', '.join(file_types)}:\n")
            for match in matches:
                result_box.insert(tk.END, f"{match}\n")

# Task 4: Automated Directory Organizer
def organize_files_by_type():
    """Sorts all files in a directory into dynamic subfolders based on their file extension."""
    folder = filedialog.askdirectory()
    if folder:
        file_count = {}

        # Scan and aggregate file extension metrics
        for root, dirs, files in os.walk(folder):
            for file in files:
                file_extension = file.split('.')[-1] if '.' in file else None
                if file_extension: 
                    if file_extension not in file_count:
                        file_count[file_extension] = 0
                    file_count[file_extension] += 1

        # Provision dynamic subdirectories for each detected extension
        for file_type, count in file_count.items():
            if count > 0:
                os.makedirs(os.path.join(folder, file_type), exist_ok=True)

        # Relocate files into their respective subdirectories
        for root, dirs, files in os.walk(folder):
            for file in files:
                file_extension = file.split('.')[-1] if '.' in file else None
                if file_extension:
                    source_path = os.path.join(root, file)
                    destination_path = os.path.join(folder, file_extension, file)
                    # Prevent moving files that are already sorted
                    if source_path != destination_path:
                        shutil.move(source_path, destination_path)

        result_box.delete(1.0, tk.END)
        result_box.insert(tk.END, "Execution Complete: Directory successfully organized by file extensions.\n")

def list_all_files():
    """Utility function to output all root files within a target directory."""
    folder = filedialog.askdirectory()
    if folder:
        files = os.listdir(folder)
        result_box.delete(1.0, tk.END)
        result_box.insert(tk.END, "Directory Contents:\n")
        for file in files:
            result_box.insert(tk.END, file + "\n")

# ==============================================================================
# MAIN ENTRY POINT
# ==============================================================================
def main():
    create_main_window()
    create_menu()
    root.mainloop()

if __name__ == "__main__":
    main()