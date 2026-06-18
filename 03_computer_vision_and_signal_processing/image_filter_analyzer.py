# ==============================================================================
# COMPUTER VISION & EDGE DETECTION ANALYZER
# A GUI application utilizing OpenCV to perform histogram equalization (via YCrCb)
# and mathematical morphological edge detection (Roberts, Prewitt, Sobel).
# ==============================================================================

import cv2
import numpy as np
import matplotlib.pyplot as plt
import os
from tkinter import Tk, filedialog, Button, Label, Frame, Canvas
from PIL import Image, ImageTk

# ==============================================================================
# PHASE 1: GLOBAL STATE & UI INITIALIZATION
# ==============================================================================
original_image = None
equalized_image = None
file_path = None

def open_image():
    """Handles file dialog and loads the image into OpenCV (BGR format)."""
    global original_image, equalized_image, file_path
    file_path = filedialog.askopenfilename(filetypes=[("Image Files", "*.bmp;*.jpg;*.jpeg;*.png;*.tif;*.tiff")])
    if not file_path:
        return

    try:
        img_pil = Image.open(file_path)
        original_image = np.array(img_pil)
        # Convert RGB to OpenCV's default BGR color space
        original_image = cv2.cvtColor(original_image, cv2.COLOR_RGB2BGR)  
        show_image(original_image, original_canvas)
    except Exception as e:
        print(f"Error loading image: {e}")

def show_image(image, canvas):
    """Renders an OpenCV BGR image onto a Tkinter Canvas."""
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    image = Image.fromarray(image)
    image.thumbnail((300, 300))
    img_tk = ImageTk.PhotoImage(image)
    canvas.create_image(150, 150, image=img_tk)
    canvas.image = img_tk

# ==============================================================================
# PHASE 2: IMAGE ENHANCEMENT & HISTOGRAM EQUALIZATION
# ==============================================================================
def equalize_image():
    """
    Applies Histogram Equalization to the luminance (Y) channel of the YCrCb 
    color space to enhance contrast without distorting color channels.
    """
    global equalized_image
    if original_image is None:
        print("Validation Error: Please load an image first.")
        return

    # Convert BGR to YCrCb
    ycrcb = cv2.cvtColor(original_image, cv2.COLOR_BGR2YCrCb)
    # Equalize only the Y (luminance) channel
    ycrcb[:, :, 0] = cv2.equalizeHist(ycrcb[:, :, 0])
    # Convert back to BGR
    equalized_image = cv2.cvtColor(ycrcb, cv2.COLOR_YCrCb2BGR)

    show_image(equalized_image, equalized_canvas)

# ==============================================================================
# PHASE 3: DATA VISUALIZATION (HISTOGRAMS)
# ==============================================================================
def plot_histogram_original():
    """Triggers global and per-channel histogram plots for the original image."""
    if original_image is None:
        print("Validation Error: Please load an image first.")
        return
    plot_histogram(original_image, "Global Histogram (Pre-Equalization)")
    plot_channel_histograms(original_image, "RGB Channel Histograms (Pre-Equalization)")

def plot_histogram_equalized():
    """Triggers global and per-channel histogram plots for the equalized image."""
    if equalized_image is None:
        print("Validation Error: Equalized image matrix not found.")
        return
    plot_histogram(equalized_image, "Global Histogram (Post-Equalization)")
    plot_channel_histograms(equalized_image, "RGB Channel Histograms (Post-Equalization)")

def plot_histogram(image, title):
    """Generates a superimposed RGB histogram bar chart."""
    plt.figure(figsize=(8, 4))
    colors = ('b', 'g', 'r')
    for i, col in enumerate(colors):
        hist = cv2.calcHist([image], [i], None, [256], [0, 256])
        plt.bar(np.arange(256), hist.flatten(), width=1, color=col, alpha=0.7)
    plt.title(title)
    plt.xlabel("Pixel Intensity")
    plt.ylabel("Pixel Count")
    plt.show()

def plot_channel_histograms(image, title):
    """Generates isolated side-by-side histogram charts for Red, Green, and Blue."""
    plt.figure(figsize=(12, 4))
    colors = ('b', 'g', 'r')
    channels = cv2.split(image)
    for i, (channel, col) in enumerate(zip(channels, colors)):
        plt.subplot(1, 3, i + 1)
        hist = cv2.calcHist([channel], [0], None, [256], [0, 256])
        plt.bar(np.arange(256), hist.flatten(), width=1, color=col)
        plt.title(f"Channel: {col.upper()}")
    plt.suptitle(title)
    plt.show()

# ==============================================================================
# PHASE 4: MATHEMATICAL EDGE DETECTION FILTERS
# ==============================================================================
def apply_filter(filter_type):
    """Applies specific edge-detection convolution kernels to the images."""
    if original_image is None:
        print("Validation Error: Please load an image first.")
        return

    # Dynamically inject filtered canvases into the GUI if they don't exist yet
    if not hasattr(apply_filter, 'filtered_label_original'):
        apply_filter.filtered_label_original = Label(frame, text="Filtered Output (Original Base)")
        apply_filter.filtered_label_original.grid(row=2, column=0)
        apply_filter.filtered_canvas_original = Canvas(frame, width=300, height=300)
        apply_filter.filtered_canvas_original.grid(row=3, column=0)

        apply_filter.filtered_label_equalized = Label(frame, text="Filtered Output (Equalized Base)")
        apply_filter.filtered_label_equalized.grid(row=2, column=1)
        apply_filter.filtered_canvas_equalized = Canvas(frame, width=300, height=300)
        apply_filter.filtered_canvas_equalized.grid(row=3, column=1)

        # Expand UI window height dynamically to accommodate new canvases
        root.geometry("700x950")

    # Define Morphological Kernels
    if filter_type == "roberts":
        kernel_x = np.array([[0, 1], [-1, 0]], dtype=np.float32)
        kernel_y = np.array([[1, 0], [0, -1]], dtype=np.float32)
    elif filter_type == "prewitt":
        kernel_x = np.array([[1, 1, 1], [0, 0, 0], [-1, -1, -1]], dtype=np.float32)
        kernel_y = np.array([[-1, 0, 1], [-1, 0, 1], [-1, 0, 1]], dtype=np.float32)
    elif filter_type == "sobel":
        kernel_x = np.array([[1, 2, 1], [0, 0, 0], [-1, -2, -1]], dtype=np.float32)
        kernel_y = np.array([[-1, 0, 1], [-2, 0, 2], [-1, 0, 1]], dtype=np.float32)

    # Apply convolution to both Original and Equalized image variants
    for img, canvas in [(original_image, apply_filter.filtered_canvas_original),
                        (equalized_image, apply_filter.filtered_canvas_equalized)]:
        if img is None:
            continue

        # Edge detection is typically performed on grayscale representations
        img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        filtered_x = cv2.filter2D(img_gray, -1, kernel_x)
        filtered_y = cv2.filter2D(img_gray, -1, kernel_y)
        
        # Merge X and Y gradient approximations
        filtered_img = cv2.addWeighted(filtered_x, 0.5, filtered_y, 0.5, 0)
        show_image(filtered_img, canvas)


# ==============================================================================
# PHASE 5: MAIN GUI APPLICATION LOOP
# ==============================================================================
root = Tk()
root.title("Computer Vision Analyzer")
root.geometry("700x600")

frame = Frame(root)
frame.pack()

# Top Image Display Row
original_label = Label(frame, text="Original Image")
original_label.grid(row=0, column=0)
original_canvas = Canvas(frame, width=300, height=300)
original_canvas.grid(row=1, column=0)

equalized_label = Label(frame, text="Contrast Equalized Image")
equalized_label.grid(row=0, column=1)
equalized_canvas = Canvas(frame, width=300, height=300)
equalized_canvas.grid(row=1, column=1)

# Control Buttons
btn_open = Button(root, text="Load Image", command=open_image)
btn_open.pack(pady=5)

btn_equalize = Button(root, text="Apply Histogram Equalization", command=equalize_image)
btn_equalize.pack(pady=5)

btn_hist_original = Button(root, text="Plot Original Histogram", command=plot_histogram_original)
btn_hist_original.pack(pady=5)

btn_hist_equalized = Button(root, text="Plot Equalized Histogram", command=plot_histogram_equalized)
btn_hist_equalized.pack(pady=5)

btn_roberts = Button(root, text="Apply Roberts Cross Operator", command=lambda: apply_filter("roberts"))
btn_roberts.pack(pady=5)

btn_prewitt = Button(root, text="Apply Prewitt Operator", command=lambda: apply_filter("prewitt"))
btn_prewitt.pack(pady=5)

btn_sobel = Button(root, text="Apply Sobel Operator", command=lambda: apply_filter("sobel"))
btn_sobel.pack(pady=5)

if __name__ == "__main__":
    root.mainloop()