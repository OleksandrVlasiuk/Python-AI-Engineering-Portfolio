# ==============================================================================
# IMAGE COMPRESSION ANALYSIS TOOL
# A Desktop GUI application for analyzing image compression algorithms 
# (BMP/RLE, TIFF/LZW, JPEG). Generates enhanced difference maps to visualize 
# encoding artifacts and calculates multi-channel pixel-loss metrics.
# ==============================================================================

import os
import time
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk, ImageChops
import numpy as np

# ==============================================================================
# PHASE 1: GLOBAL CONFIGURATION & SYSTEM UTILITIES
# ==============================================================================
active_image = None
input_file_path = ""
MAX_WIDTH, MAX_HEIGHT = 400, 400  # UI Render constraints

def resize_image_for_ui(img):
    """Scales down the image for UI rendering while preserving aspect ratio."""
    img.thumbnail((MAX_WIDTH, MAX_HEIGHT))
    return img

def ensure_directories():
    """Provisions output directories for processed images and difference maps."""
    os.makedirs("Formatted_images", exist_ok=True)
    os.makedirs("Differences", exist_ok=True)

def get_file_size_kb(filename):
    """Calculates file size in Kilobytes (KB)."""
    return os.path.getsize(filename) / 1024

def log_action(message):
    """Appends execution logs to the GUI message console."""
    message_box.insert(tk.END, message + "\n" + "-" * 50 + "\n")
    message_box.yview(tk.END)

# ==============================================================================
# PHASE 2: IMAGE ANALYSIS & DIFFERENCE MAPPING
# ==============================================================================
def analyze_loss_metrics(original, compressed):
    """Calculates pixel-wise mathematical loss metrics between original and compressed."""
    diff = ImageChops.difference(original, compressed)
    diff_array = np.array(diff)
    
    loss_r = np.sum(diff_array[:, :, 0])
    loss_g = np.sum(diff_array[:, :, 1])
    loss_b = np.sum(diff_array[:, :, 2])
    total_loss = np.sum(diff_array)
    
    avg_loss_r = np.mean(diff_array[:, :, 0])
    avg_loss_g = np.mean(diff_array[:, :, 1])
    avg_loss_b = np.mean(diff_array[:, :, 2])
    
    avg_loss_all = np.sum([avg_loss_r, avg_loss_g, avg_loss_b]) 
    
    return total_loss, loss_r, loss_g, loss_b, avg_loss_r, avg_loss_g, avg_loss_b, avg_loss_all

def generate_difference_maps(original, compressed, format_name):
    """Generates and saves contrast-enhanced difference maps for visual inspection."""
    ensure_directories()

    compressed = compressed.convert("RGB")  
    diff = ImageChops.difference(original, compressed)
    diff_array = np.array(diff, dtype=np.float32)

    # Amplify global contrast for visual clarity
    if diff_array.max() > 0:
        diff_array = (diff_array / diff_array.max()) * 255
    diff_array = diff_array.astype(np.uint8)

    enhanced_diff = Image.fromarray(diff_array)
    enhanced_diff.save(os.path.join("Differences", f"diff_{format_name}_enhanced.png"))

    # Isolate and save distinct RGB channels
    for i, color in enumerate(['Red', 'Green', 'Blue']):
        channel_diff = diff_array[:, :, i]

        if channel_diff.max() > 0:
            channel_diff = (channel_diff / channel_diff.max()) * 400 # High amplification
        channel_diff = channel_diff.astype(np.uint8)

        channel_image = Image.fromarray(channel_diff, mode='L')
        channel_image.save(os.path.join("Differences", f"diff_{format_name}_{color}_enhanced.png"))

# ==============================================================================
# PHASE 3: I/O OPERATIONS (LOAD & COMPRESS)
# ==============================================================================
def load_initial_image():
    """Handles file dialog and initializes the primary image buffer."""
    global active_image, input_file_path, img_tk_original
    file_path = filedialog.askopenfilename(filetypes=[("BMP files", "*.bmp"), ("All files", "*.*")])
    
    if file_path:
        input_file_path = file_path
        
        load_start = time.time()
        active_image = Image.open(input_file_path).convert("RGB")
        load_time = time.time() - load_start
        
        # Render on UI
        resized_img = resize_image_for_ui(active_image.copy())
        img_tk_original = ImageTk.PhotoImage(resized_img)
        original_label.config(image=img_tk_original)
        original_label.image = img_tk_original
        
        # Logging
        file_size = get_file_size_kb(input_file_path)
        log_action(f"[*] Loaded: {os.path.basename(input_file_path)}\n"
                   f"    Dimensions: {active_image.size}\n"
                   f"    Load Time: {load_time:.4f} sec\n"
                   f"    File Size: {file_size:.2f} KB")

def process_and_save_compression(format_name, params, output_name, quality_metric=None):
    """Executes encoding, benchmarks I/O, and logs compression artifacts."""
    ensure_directories()
    output_path = os.path.join("Formatted_images", output_name)
    global active_image, img_tk_modified

    if active_image:
        # Encode Benchmark
        encode_start_time = time.time()
        active_image.save(output_path, format=format_name, **params)
        encode_time = time.time() - encode_start_time

        # Decode Benchmark
        decode_start_time = time.time()
        compressed_image = Image.open(output_path)
        decode_time = time.time() - decode_start_time

        # Execute Difference Mapping
        generate_difference_maps(active_image, compressed_image, format_name)

        # File Size Metrics
        size_kb = get_file_size_kb(output_path)
        original_size_kb = get_file_size_kb(input_file_path)
        size_change = ((size_kb - original_size_kb) / original_size_kb) * 100

        # Loss Analysis Metrics
        metrics = analyze_loss_metrics(active_image, compressed_image)
        total_loss, loss_r, loss_g, loss_b, avg_r, avg_g, avg_b, avg_all = metrics

        # Construct Audit Log
        msg = f"[+] Exported Image: {output_name}\n"
        msg += f"    Format: {format_name} | Compression Time: {encode_time:.4f}s | Decode Time: {decode_time:.4f}s\n"
        msg += f"    File Size Delta: {size_change:.2f}% ({size_kb:.2f} KB)\n\n"
        msg += f"    Absolute Diff (RGB): R={loss_r}, G={loss_g}, B={loss_b}\n"
        msg += f"    Average Pixel Diff: R={avg_r:.4f}, G={avg_g:.4f}, B={avg_b:.4f}\n"
        msg += f"    Total Global Loss: {total_loss} | Avg Loss/Pixel: {avg_all:.4f}"

        if format_name == "JPEG" and quality_metric:
            msg += f"\n    [JPEG Quality={quality_metric} Target Metrics Applied]"

        log_action(msg)

        # Update UI with the compressed image
        resized_mod_img = resize_image_for_ui(compressed_image.copy())
        img_tk_modified = ImageTk.PhotoImage(resized_mod_img)
        modified_label.config(image=img_tk_modified)
        modified_label.image = img_tk_modified
    else:
        messagebox.showerror("Error", "Please load an initial BMP image first.")

def inspect_jpeg_artifacts():
    """Manual trigger to visually verify JPEG artifacts via system image viewer."""
    if active_image:
        jpeg_path = os.path.join("Formatted_images", "output.jpg")
        if os.path.exists(jpeg_path):
            compressed_image = Image.open(jpeg_path).convert("RGB")
            diff_image = ImageChops.difference(active_image, compressed_image)
            diff_image.show() 
        else:
            messagebox.showerror("Error", "Compressed JPEG artifact not found. Please run JPEG compression first.")
    else:
        messagebox.showerror("Error", "Please load an initial BMP image first.")

# ==============================================================================
# PHASE 4: GUI INITIALIZATION & MAIN LOOP
# ==============================================================================
root = tk.Tk()
root.title("Image Compression & Loss Analyzer")
root.geometry("900x650")

# --- Control Panel ---
menu_frame = ttk.Frame(root, padding=10)
menu_frame.pack(fill=tk.X)

btn_load = ttk.Button(menu_frame, text="1. Load Base Image", command=load_initial_image)
btn_load.pack(side=tk.LEFT, padx=5)

btn_rle = ttk.Button(menu_frame, text="Save BMP (RLE)",
                     command=lambda: process_and_save_compression("BMP", {"compress_level": 1}, "output_rle.bmp"))
btn_rle.pack(side=tk.LEFT, padx=5)

btn_lzw = ttk.Button(menu_frame, text="Save TIFF (LZW)",
                     command=lambda: process_and_save_compression("TIFF", {"compression": "tiff_lzw"}, "output_lzw.tiff"))
btn_lzw.pack(side=tk.LEFT, padx=5)

btn_jpeg = ttk.Button(menu_frame, text="Save JPEG (Lossy)",
                      command=lambda: process_and_save_compression("JPEG", {"quality": 10}, "output.jpg", quality_metric=10))
btn_jpeg.pack(side=tk.LEFT, padx=5)

btn_inspect = ttk.Button(menu_frame, text="Inspect JPEG Artifacts", command=inspect_jpeg_artifacts)
btn_inspect.pack(side=tk.RIGHT, padx=5)

# --- Canvas Render Area ---
image_frame = ttk.Frame(root, padding=10)
image_frame.pack(fill=tk.BOTH, expand=True)

original_label = tk.Label(image_frame, text="Original Image", bg="#e0e0e0", width=50, height=20)
original_label.pack(side=tk.LEFT, padx=10, pady=10, expand=True)

modified_label = tk.Label(image_frame, text="Compressed Image", bg="#e0e0e0", width=50, height=20)
modified_label.pack(side=tk.RIGHT, padx=10, pady=10, expand=True)

# --- Audit Log Console ---
log_frame = ttk.Frame(root, padding=10)
log_frame.pack(fill=tk.X)

tk.Label(log_frame, text="Execution Logs & Metrics:", font=("Arial", 10, "bold")).pack(anchor="w")
message_box = tk.Text(log_frame, wrap=tk.WORD, height=12, bg="#1e1e1e", fg="#00ff00", font=("Consolas", 10))
message_box.pack(fill=tk.X, pady=5)

if __name__ == "__main__":
    root.mainloop()