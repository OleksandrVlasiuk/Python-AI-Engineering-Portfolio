# ==============================================================================
# 3D PARAMETRIC SURFACE GENERATOR & PROJECTION ANALYZER
# A computational geometry tool that generates 3D parametric surfaces 
# (e.g., Coons patches, bilinear interpolation) from control points and 
# visualizes both the 3D mesh and its 2D planar projections.
# ==============================================================================

import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

# ==============================================================================
# PHASE 1: GEOMETRIC COMPUTATION CLASS
# ==============================================================================

class ParametricSurfaceGenerator:
    """Handles the mathematical generation of 3D surfaces from control points."""
    
    def __init__(self, resolution=30):
        self.resolution = resolution

    def compute_bilinear_surface(self, points, u_params, v_params):
        """
        Computes a surface using bilinear interpolation weighting across 
        a defined grid of u and v parameters.
        """
        # Initialize an empty array for the 3D surface coordinates (u, v, [x, y, z])
        surface = np.zeros((len(u_params), len(v_params), 3))

        for i in range(len(u_params)):
            for j in range(len(v_params)):
                # Calculate interpolation weights for current u and v
                w_u = np.array([1 - u_params[i], u_params[i]])
                w_v = np.array([1 - v_params[j], v_params[j]])

                # Apply weights to the control points for each spatial dimension (x, y, z)
                for k in range(3):
                    surface[i, j, k] = np.sum(w_u * np.sum(w_v * points[:, :, :, k]))
                    
        return surface

    def compute_coons_patch(self, u_params, w_params, control_points):
        """
        Computes a generalized Coons patch surface blending based on 
        a parameter grid and a specific control point matrix.
        """
        n, m, _ = control_points.shape
        surface = np.zeros((len(u_params), len(w_params), 3))

        for i in range(n):
            for j in range(m):
                # Apply blending functions to construct the parametric surface
                surface += (
                    ((1 - w_params) * (1 - u_params)).reshape(-1, 1) * control_points[i, j, 0] +
                    (w_params * (1 - u_params)).reshape(-1, 1) * control_points[i, j, 1] +
                    ((1 - w_params) * u_params).reshape(-1, 1) * control_points[i, j, 2]
                )
        return surface

# ==============================================================================
# PHASE 2: VISUALIZATION & PLOTTING UTILITIES
# ==============================================================================

def plot_surface_and_projections(u_grid, v_grid, surface, title_prefix="Surface"):
    """
    Renders a 1x3 Matplotlib figure containing the 3D surface plot 
    and two 2D heatmaps representing planar projections.
    """
    # Extract independent coordinate matrices
    projection_x = surface[:, :, 0]
    projection_y = surface[:, :, 1]
    projection_z = surface[:, :, 2]

    # Initialize plotting area
    fig = plt.figure(figsize=(18, 5))
    fig.canvas.manager.set_window_title(f"Computational Geometry - {title_prefix}")

    # --- Plot 1: Full 3D Surface ---
    ax1 = fig.add_subplot(131, projection='3d')
    ax1.plot_surface(u_grid, v_grid, projection_x, cmap='viridis', edgecolor='none', alpha=0.9)
    ax1.set_title("3D Parametric Surface")
    ax1.set_xlabel('U Axis')
    ax1.set_ylabel('V/W Axis')
    ax1.set_zlabel('Projection Magnitude')

    # --- Plot 2: 2D Projection (First Plane) ---
    ax2 = fig.add_subplot(132)
    im2 = ax2.imshow(projection_x, cmap='viridis', extent=(0, 1, 0, 1), origin='lower', aspect='auto')
    ax2.set_title("2D Projection (Primary Plane)")
    ax2.set_xlabel('U Axis')
    ax2.set_ylabel('V/W Axis')
    fig.colorbar(im2, ax=ax2, fraction=0.046, pad=0.04)

    # --- Plot 3: 2D Projection (Secondary Plane) ---
    ax3 = fig.add_subplot(133)
    # Using transposed projection or different coordinate component depending on the geometric logic
    im3 = ax3.imshow(projection_x.T, cmap='viridis', extent=(0, 1, 0, 1), origin='lower', aspect='auto')
    ax3.set_title("2D Projection (Transposed Plane)")
    ax3.set_xlabel('U Axis')
    ax3.set_ylabel('V/W Axis')
    fig.colorbar(im3, ax=ax3, fraction=0.046, pad=0.04)

    plt.tight_layout()
    plt.show()

# ==============================================================================
# PHASE 3: EXECUTION PIPELINE
# ==============================================================================

if __name__ == "__main__":
    generator = ParametricSurfaceGenerator(resolution=30)
    
    print("=" * 60)
    print(" 3D PARAMETRIC SURFACE GENERATOR ")
    print("=" * 60)

    # --------------------------------------------------------------------------
    # Experiment 1: Bilinear Interpolation over a Unit Cube
    # --------------------------------------------------------------------------
    print("[*] Generating Bilinear Interpolation Surface...")
    
    # 8 vertices of a standard unit cube shaped into a tensor
    cube_points = np.array([
        [0, 0, 0], [1, 0, 0],
        [0, 1, 0], [1, 1, 0],
        [0, 0, 1], [1, 0, 1],
        [0, 1, 1], [1, 1, 1]
    ]).reshape(2, 2, 2, 3)

    # Generate trigonometric parameter space
    u_params_1 = np.sin(np.linspace(0, 2 * np.pi, generator.resolution))
    v_params_1 = np.cos(np.linspace(0, 2 * np.pi, generator.resolution))

    surface_1 = generator.compute_bilinear_surface(cube_points, u_params_1, v_params_1)
    
    # Create meshgrid for 3D plotting
    U1, V1 = np.meshgrid(u_params_1, v_params_1)
    plot_surface_and_projections(U1, V1, surface_1, title_prefix="Bilinear")

    # --------------------------------------------------------------------------
    # Experiment 2: Generalized Coons Patch
    # --------------------------------------------------------------------------
    print("[*] Generating Coons Patch Surface...")

    # Define specialized control matrix for the patch
    coons_control_points = np.array([
        [[0, 0, 0], [1, 0, 0], [0, 1, 0], [1, 1, 0]],
        [[0, 0, 1], [1, 0, 1], [0, 1, 1], [1, 1, 1]]
    ])

    u_params_2 = np.sin(np.linspace(0, 2 * np.pi, generator.resolution))
    w_params_2 = np.sin(np.linspace(0, 2 * np.pi, generator.resolution))

    surface_2 = generator.compute_coons_patch(u_params_2, w_params_2, coons_control_points)

    # Create meshgrid for 3D plotting
    U2, W2 = np.meshgrid(u_params_2, w_params_2)
    plot_surface_and_projections(U2, W2, surface_2, title_prefix="Coons Patch")
    
    print("[+] Rendering complete.")