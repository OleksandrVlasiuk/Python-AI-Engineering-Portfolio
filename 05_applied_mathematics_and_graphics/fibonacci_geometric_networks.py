# ==============================================================================
# GEOMETRIC NETWORK TOPOLOGY GENERATOR
# Generates discrete network graphs on a square boundary. Maps connections 
# deterministically using Fibonacci sequence step-offsets versus a stochastic 
# random baseline pairing model, integrated with centralized star-hubs.
# ==============================================================================

import random
import matplotlib.pyplot as plt
import numpy as np

class GeometricNetworkSimulator:
    """Simulates and visualizes structural topologies on a 2D geometric boundary."""
    def __init__(self, size=5.0, points_per_side=10):
        self.size = float(size)
        self.points_per_side = points_per_side
        self.boundary_points = []
        self._generate_square_boundary()

    def _generate_square_boundary(self):
        """Generates clockwise indexed sequential coordinates along the square perimeter."""
        r = self.size
        n = self.points_per_side
        
        # Append base vertices
        self.boundary_points.append((0.0, 0.0))
        self.boundary_points.append((r, 0.0))
        self.boundary_points.append((r, r))
        self.boundary_points.append((0.0, r))

        # Interpolate structured discrete segments along perimeter lines
        for i in range(1, n):
            offset = i * r / n
            self.boundary_points.append((offset, 0.0))    # Bottom side
            self.boundary_points.append((r, offset))       # Right side
            self.boundary_points.append((r - offset, r))   # Top side
            self.boundary_points.append((0.0, r - offset)) # Left side

    def compute_fibonacci_pairs(self):
        """Computes link indices where the path step delta matches a Fibonacci value."""
        pairs = []
        num_points = len(self.boundary_points)
        
        # Compute valid Fibonacci terms within index bounds
        fib_sequence = [0, 1]
        while fib_sequence[-1] < num_points:
            fib_sequence.append(fib_sequence[-1] + fib_sequence[-2])
            
        # Evaluate index deltas deterministically
        for i in range(num_points):
            for j in range(num_points):
                if (i - j) > 0 and (i - j) in fib_sequence:
                    pairs.append((i, j))
        return pairs

    def compute_random_pairs(self, count):
        """Generates a randomized baseline network pairing without self-loops or duplicates."""
        pairs = []
        num_points = len(self.boundary_points)
        
        while len(pairs) < count:
            p1, p2 = random.sample(range(num_points), 2)
            if p1 != p2 and (p1, p2) not in pairs and (p2, p1) not in pairs:
                pairs.append((p1, p2))
        return pairs

    def render_topology(self, random_baseline=False, show_hubs=True):
        """Visualizes the compiled network configuration via Matplotlib."""
        plt.figure(figsize=(7, 7))
        plt.axis('equal')
        
        title_string = "Stochastic Random Baseline Network" if random_baseline else "Deterministic Fibonacci Sequence Network"
        plt.title(title_string, fontsize=12, fontweight='bold', pad=15)

        # 1. Extract and plot boundary points
        x_coords = [p[0] for p in self.boundary_points]
        y_coords = [p[1] for p in self.boundary_points]
        plt.scatter(x_coords, y_coords, s=15, color='#e06666', zorder=4, label="Boundary Nodes")

        # 2. Compute and draw link paths
        if random_baseline:
            pairs = self.compute_random_pairs(count=len(self.boundary_points))
            line_color = '#6aa84f'  # Muted green for stochastic connections
        else:
            pairs = self.compute_fibonacci_pairs()
            line_color = '#4ea1d3'  # Soft blue for algorithmic connections

        for p1, p2 in pairs:
            x1, y1 = self.boundary_points[p1]
            x2, y2 = self.boundary_points[p2]
            plt.plot([x1, x2], [y1, y2], color=line_color, lw=0.6, alpha=0.8, zorder=2)

        # 3. Inject internal structural star-hubs if enabled
        if show_hubs:
            r = self.size
            hub_nodes = [
                (r / 2, r / 2), 
                (r / 3, r / 3), 
                (2 * r / 3, 2 * r / 3),
                (r / 3, 2 * r / 3),
                (2 * r / 3, r / 3)
            ]
            
            # Render hub nodes and interconnect them to all boundary vertices
            for idx, hub in enumerate(hub_nodes):
                hx, hy = hub
                label_node = "Internal Star-Hubs" if idx == 0 else ""
                plt.scatter(hx, hy, s=40, color='#8733af', zorder=5, label=label_node)
                
                for bp in self.boundary_points:
                    bx, by = bp
                    plt.plot([hx, bx], [hy, by], color='#8733af', lw=0.4, alpha=0.3, zorder=1)

        plt.grid(True, linestyle='--', alpha=0.5)
        plt.legend(loc="upper right")
        plt.tight_layout()
        plt.show()

# ==============================================================================
# PIPELINE EXECUTION
# ==============================================================================
if __name__ == "__main__":
    # Seed the PRNG to guarantee consistent generation outputs across executions
    random.seed(42)
    
    # Initialize simulator configuration parameters
    SQUARE_SIZE = 5.0
    POINTS_PER_SIDE = 12

    simulator = GeometricNetworkSimulator(size=SQUARE_SIZE, points_per_side=POINTS_PER_SIDE)
    
    # Pipeline Pass 1: Render Algorithmic Fibonacci Architecture
    simulator.render_topology(random_baseline=False, show_hubs=True)
    
    # Pipeline Pass 2: Render Comparative Stochastic Baseline Architecture
    simulator.render_topology(random_baseline=True, show_hubs=True)