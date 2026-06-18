# ==============================================================================
# COHEN-SUTHERLAND LINE CLIPPING ALGORITHM
# A fundamental computer graphics algorithm to perform line clipping against 
# a rectangular viewing window using bitwise outcode logic.
# ==============================================================================

import matplotlib.pyplot as plt
import numpy as np

# Bitwise flags for the clipping region
INSIDE = 0  # 0000
LEFT   = 1  # 0001
RIGHT  = 2  # 0010
BOTTOM = 4  # 0100
TOP    = 8  # 1000

def calculate_outcode(x, y, xmin, ymin, xmax, ymax):
    """Computes the 4-bit outcode for a point (x, y) relative to a window."""
    code = INSIDE
    if x < xmin:   code |= LEFT
    elif x > xmax: code |= RIGHT
    if y < ymin:   code |= BOTTOM
    elif y > ymax: code |= TOP
    return code

def clip_line(x1, y1, x2, y2, xmin, ymin, xmax, ymax):
    """
    Clips a line segment [p1, p2] against a rectangular window [xmin, ymin, xmax, ymax]
    using the Cohen-Sutherland algorithm.
    """
    code1 = calculate_outcode(x1, y1, xmin, ymin, xmax, ymax)
    code2 = calculate_outcode(x2, y2, xmin, ymin, xmax, ymax)

    while (code1 | code2) != 0:
        # If both points are outside the same side, discard the line
        if (code1 & code2) != 0:
            return None, None, None, None

        # Choose an external point
        code_out = code1 if code1 != 0 else code2
        x, y = 0, 0

        # Find the intersection point
        if code_out & TOP:
            x = x1 + (x2 - x1) * (ymax - y1) / (y2 - y1)
            y = ymax
        elif code_out & BOTTOM:
            x = x1 + (x2 - x1) * (ymin - y1) / (y2 - y1)
            y = ymin
        elif code_out & RIGHT:
            y = y1 + (y2 - y1) * (xmax - x1) / (x2 - x1)
            x = xmax
        elif code_out & LEFT:
            y = y1 + (y2 - y1) * (xmin - x1) / (x2 - x1)
            x = xmin

        # Replace the external point with the intersection point
        if code_out == code1:
            x1, y1 = x, y
            code1 = calculate_outcode(x1, y1, xmin, ymin, xmax, ymax)
        else:
            x2, y2 = x, y
            code2 = calculate_outcode(x2, y2, xmin, ymin, xmax, ymax)

    return x1, y1, x2, y2

def visualize_clipping(x1, y1, x2, y2, xmin, ymin, xmax, ymax):
    """Visualizes the clipping process in three distinct stages."""
    result = clip_line(x1, y1, x2, y2, xmin, ymin, xmax, ymax)
    
    plt.figure(figsize=(15, 5))

    # Stage 1: Initial State
    plt.subplot(131)
    plt.plot([x1, x2], [y1, y2], label="Original Segment", color='blue', lw=2)
    plt.axvline(xmin, color='red', linestyle='--'); plt.axvline(xmax, color='red', linestyle='--')
    plt.axhline(ymin, color='red', linestyle='--'); plt.axhline(ymax, color='red', linestyle='--')
    plt.xlim(0, 100); plt.ylim(0, 100); plt.title('1. Original Segment & Window'); plt.legend()

    # Stage 2: Clipped State
    plt.subplot(132)
    if result[0] is not None:
        plt.plot([result[0], result[2]], [result[1], result[3]], label="Clipped Segment", color='red', lw=2)
    plt.axvline(xmin, color='red', linestyle='--'); plt.axvline(xmax, color='red', linestyle='--')
    plt.axhline(ymin, color='red', linestyle='--'); plt.axhline(ymax, color='red', linestyle='--')
    plt.xlim(0, 100); plt.ylim(0, 100); plt.title('2. Resulting Clipped Segment'); plt.legend()

    # Stage 3: Comparison
    plt.subplot(133)
    plt.plot([x1, x2], [y1, y2], label="Original Path", color='gray', linestyle='--')
    if result[0] is not None:
        plt.plot([result[0], result[2]], [result[1], result[3]], label="Visible Segment", color='green', lw=2)
    plt.xlim(0, 100); plt.ylim(0, 100); plt.title('3. Overlay Comparison'); plt.legend()

    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    visualize_clipping(x1=20, y1=30, x2=80, y2=90, xmin=30, ymin=40, xmax=60, ymax=80)