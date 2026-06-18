# ==============================================================================
# TRANSIT ROUTING & NAVIGATION SYSTEM
# A Desktop GUI application using ttkbootstrap for computing direct and 
# multi-transfer tram routes, discovering reachable nodes, and analyzing 
# transit network junctions based on graph structures.
# ==============================================================================

import tkinter as tk
from tkinter import ttk
import ttkbootstrap as ttkb
from ttkbootstrap.constants import *

# ==============================================================================
# PHASE 1: DATA EXTRACTION & GRAPH INGESTION
# ==============================================================================

def load_stops_from_file(filename):
    """
    Parses and extracts unique transit stop names from a flat text file.
    """
    stops = []
    try:
        with open(filename, 'r', encoding='utf-8') as file:
            for line in file:
                stop = line.strip()
                if stop:
                    stops.append(stop)
    except FileNotFoundError:
        print(f"Error: The configuration file {filename} was not found!")
    return stops


def load_routes_from_file(filename):
    """
    Ingests and maps tram route topologies into a structured adjacency dictionary.
    Supports separate parsing for directional tracks (Forward and Backward).
    """
    routes = {}
    current_tram = None
    current_direction = None

    try:
        with open(filename, 'r', encoding='utf-8') as file:
            for line in file:
                line = line.strip()
                if not line:
                    continue

                if '–' in line and ('Forward:' in line or 'Backward:' in line):
                    # Parse header rows, e.g., "1 – Forward:"
                    parts = line.split('–')
                    current_tram = int(parts[0].strip())
                    current_direction = parts[1].strip().replace(':', '').lower()
                    if current_tram not in routes:
                        routes[current_tram] = {'forward': [], 'backward': []}
                else:
                    # Append sequential stops to the active route directional vector
                    if current_tram is not None and current_direction is not None:
                        routes[current_tram][current_direction].append(line)

    except FileNotFoundError:
        print(f"Error: The route configuration file {filename} was not found!")

    return routes

# ==============================================================================
# PHASE 2: GRAPH ROUTING & SEARCH ALGORITHMS
# ==============================================================================

def find_route(start_stop, end_stop, routes):
    """
    Performs a deterministic lookup to detect either a direct single-line connection
    or computes a valid multi-line path containing a single transfer point.
    """
    # 1. Direct Route Check
    for tram, directions in routes.items():
        for direction, stops in directions.items():
            if start_stop in stops and end_stop in stops:
                start_index = stops.index(start_stop)
                end_index = stops.index(end_stop)
                if start_index < end_index:
                    return f"Take Tram №{tram} from '{start_stop}' directly to '{end_stop}'."

    # 2. Single Transfer Route Pathfinding
    for tram1, directions1 in routes.items():
        for direction1, stops1 in directions1.items():
            if start_stop in stops1:
                for tram2, directions2 in routes.items():
                    if tram1 != tram2:
                        for direction2, stops2 in directions2.items():
                            common_stops = set(stops1).intersection(stops2)
                            if common_stops:
                                for transfer_stop in common_stops:
                                    if transfer_stop in stops1 and end_stop in stops2:
                                        return (
                                            f"Take Tram №{tram1} from '{start_stop}' to transfer node '{transfer_stop}'.\n"
                                            f"Switch to Tram №{tram2} from '{transfer_stop}' to arrive at '{end_stop}'."
                                        )

    return "No direct path or single-transfer route available within the current network data."


def reachable_stops_from(stop, routes):
    """
    Extracts all subsequent downstream stations reachable from a designated starting node.
    """
    reachable_stops = set()
    for tram, directions in routes.items():
        for direction, stops in directions.items():
            if stop in stops:
                index = stops.index(stop)
                # Capture all future stops along the active directional path vector
                reachable_stops.update(stops[index:])
    return reachable_stops


def trams_at_stop(stop, routes):
    """
    Identifies all tram lines intersecting or servicing a designated transit stop.
    """
    trams = []
    for tram, directions in routes.items():
        for direction, stops in directions.items():
            if stop in stops:
                trams.append(tram)
                break  # Prevent duplicate tracking across bidirectional records
    return trams

# ==============================================================================
# PHASE 3: MODERN GUI ARCHITECTURE (TTBBOOTSTRAP)
# ==============================================================================

def main():
    # Initialize the modern styled main window window using the 'flatly' theme
    root = ttkb.Window(themename="flatly")
    root.title("Transit Route Planner & Navigator")
    root.geometry("1000x600")

    # Ingest data assets from internal configuration files
    stops = load_stops_from_file('stops.txt')
    routes = load_routes_from_file('marshrut.txt')

    # --- Header Component ---
    titleLabel = ttkb.Label(root, text="Information & Reference System\nLviv Urban Tram Transit Network Navigator",
                            width=80, anchor="center", font=("Arial", 18, "bold"), bootstyle=INFO)
    titleLabel.grid(row=0, column=0, columnspan=2, pady=20)

    # --- Action Selection Label ---
    optionLabel = ttkb.Label(root, text="Select Navigation Metric:", width=60, anchor="center",
                             font=("Arial", 16), bootstyle=INFO)
    optionLabel.grid(row=1, column=0, columnspan=2, pady=10)

    # --- Mode Configuration Dropdown ---
    options = ["Shortest path between two stations",
               "Discover all reachable stations from a designated stop",
               "Identify all transit lines serving a stop"]
    optionCombo = ttkb.Combobox(root, values=options, width=50, font=("Arial", 12))
    optionCombo.grid(row=2, column=0, columnspan=2, padx=10, pady=10)
    optionCombo.current(0)

    # --- Departure Selection Elements ---
    labelFrom = ttkb.Label(root, text="Departure Stop:", width=20, anchor="w", font=("Arial", 12), bootstyle=INFO)
    labelFrom.grid(row=3, column=0, padx=10, pady=10, sticky='w')

    comboFrom = ttkb.Combobox(root, values=stops, width=50, font=("Arial", 12))
    comboFrom.grid(row=4, column=0, padx=10, pady=10, sticky='w')

    # --- Destination Selection Elements ---
    labelTo = ttkb.Label(root, text="Destination Stop:", width=20, anchor="w", font=("Arial", 12), bootstyle=INFO)
    labelTo.grid(row=3, column=1, padx=10, pady=10, sticky='w')

    comboTo = ttkb.Combobox(root, values=stops, width=50, font=("Arial", 12))
    comboTo.grid(row=4, column=1, padx=10, pady=10, sticky='w')

    # --- Dynamic Output Logger Box ---
    result = tk.Text(root, width=100, height=8, font=("Arial", 12), state='disabled')
    result.grid(row=5, column=0, columnspan=2, padx=10, pady=10)
    result.grid_remove()

    def on_option_change(event):
        """Reactive layout handler toggling form elements based on the navigation task."""
        selected_option = optionCombo.get()
        if selected_option == "Discover all reachable stations from a designated stop":
            labelTo.grid_remove()
            comboTo.grid_remove()
            labelFrom.grid(row=3, column=0, padx=10, pady=10, sticky='w')
            comboFrom.grid(row=4, column=0, padx=10, pady=10, sticky='w')
        elif selected_option == "Identify all transit lines serving a stop":
            labelFrom.grid_remove()
            comboFrom.grid_remove()
            labelTo.grid(row=3, column=0, padx=10, pady=10, sticky='w')
            comboTo.grid(row=4, column=0, padx=10, pady=10, sticky='w')
        else:
            labelTo.grid(row=3, column=1, padx=10, pady=10, sticky='w')
            comboTo.grid(row=4, column=1, padx=10, pady=10, sticky='w')
            labelFrom.grid(row=3, column=0, padx=10, pady=10, sticky='w')
            comboFrom.grid(row=4, column=0, padx=10, pady=10, sticky='w')

    optionCombo.bind("<<ComboboxSelected>>", on_option_change)

    def search_route():
        """Trigger button execution evaluating the inputs and outputting calculated paths."""
        selected_option = optionCombo.get()
        start_stop = comboFrom.get() if selected_option != "Identify all transit lines serving a stop" else comboTo.get()
        end_stop = comboTo.get() if selected_option != "Discover all reachable stations from a designated stop" else None

        result.config(state='normal')
        result.delete(1.0, tk.END)

        if selected_option == "Shortest path between two stations":
            if start_stop and end_stop:
                route_result = find_route(start_stop, end_stop, routes)
                result.insert(tk.END, route_result)
            else:
                result.insert(tk.END, "Validation Error: Please configure both departure and destination nodes.")

        elif selected_option == "Discover all reachable stations from a designated stop":
            if start_stop:
                reachable_stops = reachable_stops_from(start_stop, routes)
                result.insert(tk.END, "Reachable downstream stations from '{}': \n{}\n".format(
                    start_stop, ', '.join(reachable_stops)))
            else:
                result.insert(tk.END, "Validation Error: Please select a baseline starting stop.")

        elif selected_option == "Identify all transit lines serving a stop":
            if start_stop:
                trams = trams_at_stop(start_stop, routes)
                result.insert(tk.END, "Active tram lines servicing '{}': \n№{}\n".format(
                    start_stop, ', №'.join(map(str, trams))))
            else:
                result.insert(tk.END, "Validation Error: Please specify a target transit station.")

        result.config(state='disabled')
        result.grid()

    # --- Submit Action Button ---
    button = ttkb.Button(root, text="Execute Pathfinding", width=20, bootstyle=SUCCESS, command=search_route)
    button.grid(row=6, column=0, columnspan=2, padx=10, pady=10)

    root.mainloop()

if __name__ == "__main__":
    main()