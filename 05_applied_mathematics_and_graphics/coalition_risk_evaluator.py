# ==============================================================================
# COALITION GAME THEORY & RISK ANALYSIS MODEL
# Evaluates objective functions and expected losses for competing coalitions 
# under uncertainty. Calculates guaranteed (minimax) outcomes and worst-case 
# risk scenarios using linearly interpolated probability matrices.
# ==============================================================================

import numpy as np
import itertools
import pandas as pd

# ==============================================================================
# PHASE 1: SEARCH SPACE & OBJECTIVE FUNCTIONS
# ==============================================================================

# Define the decision space domain (Grid with a step of 0.5)
x_vals = np.arange(0, 3.5, 0.5)
y_vals = np.arange(0, 2.5, 0.5)
xy_combinations = list(itertools.product(x_vals, y_vals))

# Objective (Payoff) Functions for Coalition 1 and Coalition 2
def F12(x, y):
    return (8.3 * x - 7.6 * x * y - 12 * y + 25.2) / 98.6

def F21(x, y):
    return (-3.9 * x + 12.5 * x * y + 13.9 * y + 12.6) / 76.4

# ==============================================================================
# PHASE 2: LOSS FUNCTIONS UNDER VARIOUS RISK STATES
# ==============================================================================

# Loss Functions for Coalition 1 (States: ns, fm, in)
def J12_ns(x, y): return (2.3 * y - 3.8 * x * y + 0.63 * x - 0.6) / 9.2
def J12_fm(x, y): return (2.9 * y - 6.9 * x * y + 1.7 * x - 2.9) / 3.9
def J12_in(x, y): return (1.6 * y - 3.6 * x * y - 4.3 * x - 7.4) / 2.5

# Loss Functions for Coalition 2 (States: ns, fm, in)
def J21_ns(x, y): return (-4.7 * y + 9.1 * x * y + 5.2 * x + 1.3) / 11.6
def J21_fm(x, y): return (-14.4 * y + 9.2 * x * y + 7.1 * x - 2.8) / 7.2
def J21_in(x, y): return (-6.5 * y + 8.2 * x * y + 3.5 * x + 5.8) / 3.2

# ==============================================================================
# PHASE 3: PROBABILITY MATRICES & INTERPOLATION
# ==============================================================================

# Initial Risk Probability Matrices
R1 = np.array([
    [0.01, 0.13, 0.08],
    [0.07, 0.10, 0.12],
    [0.15, 0.01, 0.03]
])

R2 = np.array([
    [0.11, 0.08, 0.06, 0.19],
    [0.02, 0.07, 0.15, 0.03],
    [0.09, 0.09, 0.01, 0.02]
])

def expand_matrix(prob_matrix, target_size):
    """
    Expands a probability matrix to match the target decision space size 
    using 1D linear interpolation across the columns.
    """
    expanded = np.zeros((prob_matrix.shape[0], target_size))
    for i in range(prob_matrix.shape[0]):
        original_indices = np.arange(prob_matrix.shape[1])
        target_indices = np.linspace(0, prob_matrix.shape[1] - 1, target_size)
        expanded[i] = np.interp(target_indices, original_indices, prob_matrix[i])
    return expanded

# Expand risk matrices to match the number of (x, y) combinations (35 items)
R1_exp = expand_matrix(R1, len(xy_combinations))
R2_exp = expand_matrix(R2, len(xy_combinations))

# ==============================================================================
# PHASE 4: EXECUTION & EXPECTED VALUE CALCULATIONS
# ==============================================================================

def main():
    print("=" * 60)
    print(" COALITION GAME THEORY & RISK ANALYSIS ")
    print("=" * 60)

    F12_vals, F21_vals = [], []
    I12_vals, I21_vals = [], []

    for idx, (x, y) in enumerate(xy_combinations):
        # Calculate base payoffs
        f12 = F12(x, y)
        f21 = F21(x, y)
        F12_vals.append(f12)
        F21_vals.append(f21)

        # Calculate Expected Losses based on interpolated probabilities
        J1_expected = (
            J12_ns(x, y) * R1_exp[0, idx] +
            J12_fm(x, y) * R1_exp[1, idx] +
            J12_in(x, y) * R1_exp[2, idx]
        )
        J2_expected = (
            J21_ns(x, y) * R2_exp[0, idx] +
            J21_fm(x, y) * R2_exp[1, idx] +
            J21_in(x, y) * R2_exp[2, idx]
        )

        # Calculate Net Integral Outcomes (Payoff - Expected Loss)
        I12_vals.append(f12 - J1_expected)
        I21_vals.append(f21 - J2_expected)

    # Compile results into a DataFrame
    df = pd.DataFrame({
        'X': [x for x, y in xy_combinations],
        'Y': [y for x, y in xy_combinations],
        'F12_Base': F12_vals,
        'F21_Base': F21_vals,
        'I12_Net': I12_vals,
        'I21_Net': I21_vals
    })

    print("\n[+] System Evaluation Table (First 10 rows):")
    print(df.head(10).to_string(index=False))

    # ==========================================================================
    # PHASE 5: GUARANTEED OUTCOMES & WORST-CASE ANALYSIS
    # ==========================================================================

    # Find minimums (Guaranteed pessimistic outcomes)
    idx_F12_min, idx_F21_min = np.argmin(F12_vals), np.argmin(F21_vals)
    idx_I12_min, idx_I21_min = np.argmin(I12_vals), np.argmin(I21_vals)

    print("\n" + "-" * 60)
    print("[+] GUARANTEED (MINIMUM) OUTCOMES")
    print("-" * 60)
    print(f"F12 Guaranteed Base: {min(F12_vals):.4f} at (x={xy_combinations[idx_F12_min][0]}, y={xy_combinations[idx_F12_min][1]})")
    print(f"F21 Guaranteed Base: {min(F21_vals):.4f} at (x={xy_combinations[idx_F21_min][0]}, y={xy_combinations[idx_F21_min][1]})")
    print(f"I12 Guaranteed Net:  {min(I12_vals):.4f} at (x={xy_combinations[idx_I12_min][0]}, y={xy_combinations[idx_I12_min][1]})")
    print(f"I21 Guaranteed Net:  {min(I21_vals):.4f} at (x={xy_combinations[idx_I21_min][0]}, y={xy_combinations[idx_I21_min][1]})")

    # Worst-case risk determination (Max cumulative probability peak)
    worst_risk1_idx = np.argmax(np.sum(R1_exp, axis=0))
    worst_risk2_idx = np.argmax(np.sum(R2_exp, axis=0))
    
    x1, y1 = xy_combinations[worst_risk1_idx]
    x2, y2 = xy_combinations[worst_risk2_idx]

    worst_f12 = F12(x1, y1)
    worst_f21 = F21(x2, y2)

    worst_I12 = worst_f12 - (
        J12_ns(x1, y1) * R1_exp[0, worst_risk1_idx] +
        J12_fm(x1, y1) * R1_exp[1, worst_risk1_idx] +
        J12_in(x1, y1) * R1_exp[2, worst_risk1_idx]
    )
    
    worst_I21 = worst_f21 - (
        J21_ns(x2, y2) * R2_exp[0, worst_risk2_idx] +
        J21_fm(x2, y2) * R2_exp[1, worst_risk2_idx] +
        J21_in(x2, y2) * R2_exp[2, worst_risk2_idx]
    )

    print("\n" + "-" * 60)
    print("[!] WORST-CASE RISK SCENARIOS")
    print("-" * 60)
    print("Coalition 1 (F12) Maximum Risk Exposure:")
    print(f"  Coordinates:    (x={x1}, y={y1})")
    print(f"  Base Payoff:    {worst_f12:.4f}")
    print(f"  Net w/ Risk:    {worst_I12:.4f}")
    print(f"  Pessimistic:    {worst_f12 - J12_ns(x1, y1):.4f} (Assuming baseline loss)")

    print("\nCoalition 2 (F21) Maximum Risk Exposure:")
    print(f"  Coordinates:    (x={x2}, y={y2})")
    print(f"  Base Payoff:    {worst_f21:.4f}")
    print(f"  Net w/ Risk:    {worst_I21:.4f}")
    print(f"  Pessimistic:    {worst_f21 - J21_ns(x2, y2):.4f} (Assuming baseline loss)")
    print("=" * 60)


if __name__ == "__main__":
    main()