# ==============================================================================
# NUMERICAL MODELING & ORTHOGONAL POLYNOMIAL APPROXIMATION
# A mathematical framework for building multi-dimensional regression models 
# using Chebyshev polynomials. Includes custom Grid Search for hyperparameter 
# optimization (polynomial degrees) to minimize the Root Mean Square Error (RMSE).
# ==============================================================================

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# ==============================================================================
# PHASE 1: DATA PREPROCESSING & SANITIZATION
# ==============================================================================

def load_data(file_path):
    """Loads numerical data, handling European comma-decimals and encodings."""
    df = pd.read_csv(file_path, header=None, delim_whitespace=True, encoding='ISO-8859-1')
    df = df.replace({',': '.'}, regex=True)
    return df.values.astype(float)

def handle_missing_values(data):
    """Imputes NaN values with the column mean (Mean Imputation)."""
    col_means = np.nanmean(data, axis=0)
    inds = np.where(np.isnan(data))
    data[inds] = np.take(col_means, inds[1])
    return data

def normalize_data(data, method='standardization'):
    """Applies feature scaling (Min-Max or Z-Score Standardization)."""
    if method == 'min_max':
        min_vals = np.min(data, axis=0)
        max_vals = np.max(data, axis=0)
        # Add epsilon to prevent division by zero
        return (data - min_vals) / (max_vals - min_vals + 1e-8)
    else:
        mean_vals = np.mean(data, axis=0)
        std_vals = np.std(data, axis=0)
        return (data - mean_vals) / (std_vals + 1e-8)

# ==============================================================================
# PHASE 2: MATHEMATICAL KERNELS & ORTHOGONAL POLYNOMIALS
# ==============================================================================

def chebyshev_polynomial(x, n):
    """
    Computes the value of the Chebyshev polynomial of the first kind T_n(x)
    using the recursive continuous formula: T_{n+1}(x) = 2x*T_n(x) - T_{n-1}(x)
    """
    if n == 0:
        return 1
    elif n == 1:
        return x
    else:
        T_0, T_1 = 1, x
        for _ in range(2, n + 1):
            T_next = 2 * x * T_1 - T_0
            T_0, T_1 = T_1, T_next
        return T_1

def calculate_tz_matrix(X_norm, degrees, coeffs):
    """Constructs the TZ transformation matrix using Chebyshev base functions."""
    tz_matrix = []
    for i in range(len(X_norm)):
        tz_row = [chebyshev_polynomial(X_norm[i, j], degrees[j]) * coeffs[j] 
                  for j in range(len(X_norm[i]))]
        tz_matrix.append(tz_row)
    return np.array(tz_matrix)

def calculate_lambda_matrix(p1, p2, p3):
    """
    [SIMULATED] Computes the Lambda coefficient matrix.
    In a real scenario, this involves solving normal equations (X^T * X)^-1 * X^T * Y.
    """
    dim = p1 + p2 + p3
    matrix = np.zeros((dim, dim))
    for i in range(dim):
        for j in range(dim):
            matrix[i, j] = np.cos(np.pi * i * j / dim) * 10 
    return matrix

def split_lambdas(lambda_matrix, p1, p2, p3):
    """Partitions the global Lambda matrix into subsystem block matrices."""
    l1 = lambda_matrix[:p1, :p1]
    l2 = lambda_matrix[p1:p1 + p2, p1:p1 + p2]
    l3 = lambda_matrix[p1 + p2:p1 + p2 + p3, p1 + p2:p1 + p2 + p3]
    return l1, l2, l3

# ==============================================================================
# PHASE 3: LINEAR ALGEBRA & ERROR METRICS
# ==============================================================================

def calculate_a_and_c_matrices(l1, l2, l3):
    """Solves the linear subsystems by computing the inverse matrices."""
    a1 = np.linalg.inv(l1)
    a2 = np.linalg.inv(l2)
    a3 = np.linalg.inv(l3)
    c = a1 + a2 + a3 

    # Evaluate the simulated polynomial approximation
    evaluated = np.dot(a1, a2) + np.dot(a2, a3) 
    return a1, a2, a3, c, evaluated

def calculate_incoherence(idx, evaluated, real):
    """Computes the Root Mean Square Error (RMSE) to measure approximation incoherence."""
    m_samples = real.shape[0]
    return np.sqrt(np.sum(np.power(evaluated[:, idx] - real[:, idx], 2)) / m_samples)

# ==============================================================================
# PHASE 4: OPTIMIZATION (GRID SEARCH) & VISUALIZATION
# ==============================================================================

def find_minimal_incoherence(y_real):
    """
    Performs a grid search over polynomial degrees (p1, p2, p3) to find the 
    architecture that minimizes the global RMSE (incoherence).
    """
    m_features = y_real.shape[1]
    best_incoherence = float('inf')
    best_params = (0, 0, 0)
    best_evaluation = None

    print("[*] Initiating Grid Search for optimal polynomial degrees...")
    
    for p1 in range(3, 7):
        for p2 in range(3, 7):
            for p3 in range(3, 7):
                lambda_coeffs = calculate_lambda_matrix(p1, p2, p3)
                l1, l2, l3 = split_lambdas(lambda_coeffs, p1, p2, p3)
                
                try:
                    a1, a2, a3, c, evaluated = calculate_a_and_c_matrices(l1, l2, l3)
                    
                    # Pad evaluation matrix if dimensions mismatch during simulation
                    if evaluated.shape != y_real.shape:
                        evaluated = np.resize(evaluated, y_real.shape)
                        
                    max_rmse = max(calculate_incoherence(idx, evaluated, y_real) for idx in range(m_features))
                    
                    if max_rmse < best_incoherence:
                        best_incoherence = max_rmse
                        best_params = (p1, p2, p3)
                        best_evaluation = evaluated
                except np.linalg.LinAlgError:
                    continue # Skip singular matrices

    return best_params, best_incoherence, best_evaluation

def plot_all(evaluated, real):
    """Renders a comparative plot of real vs. approximated values."""
    sample_size = evaluated.shape[0]
    m_features = real.shape[1]
    
    plt.figure(figsize=(10, 8))
    for i in range(m_features):
        plt.subplot(m_features, 1, i + 1)
        rmse = calculate_incoherence(i, evaluated, real)
        plt.title(f"Target Y{i + 1} Approximation | RMSE: {rmse:.6f}")
        plt.plot(range(1, sample_size + 1), real[:, i], color='blue', label=f"Real Y{i + 1}")
        plt.plot(range(1, sample_size + 1), evaluated[:, i], color='red', linestyle='dashed', label=f"Pred F{i + 1}")
        plt.legend(loc='upper right')
        plt.xlabel("Observation Index")
        plt.ylabel("Magnitude")
        plt.grid(True, alpha=0.3)
        
    plt.tight_layout()
    plt.show()

def generate_functional_equations(a1_matrix, a2_matrix, a3_matrix, l1, l2, l3):
    """Compiles the calculated matrix coefficients into human-readable algebraic equations."""
    m = a1_matrix.shape[1]
    all_functions = []

    def build_equation_string(subsystem_id, index, a_matrix, lambda_x):
        equation = f"F_{subsystem_id}_{index + 1}(x) = "
        terms = []
        for idx, row_val in enumerate(a_matrix[:, index]):
            term = " + ".join([f"({row_val * a_col:.4f} * T(x^{a_idx}))" for a_idx, a_col in enumerate(lambda_x[idx, :])])
            terms.append(term)
        return equation + " +\n    ".join(terms) + "\n\n"

    for sys_id, lam, a_mat in [(1, l1, a1_matrix), (2, l2, a2_matrix), (3, l3, a3_matrix)]:
        for i in range(m):
            all_functions.append(build_equation_string(sys_id, i, a_mat, lam))

    with open("recovered_functions.txt", "w", encoding="utf-8") as file:
        file.writelines(all_functions)
    
    print("[+] Algebraic equations successfully generated and saved to 'recovered_functions.txt'.")


# ==============================================================================
# MAIN EXECUTION
# ==============================================================================
if __name__ == "__main__":
    np.random.seed(42)

    # 1. Simulate data matrices for execution demonstration
    print("=" * 60)
    print(" CHEBYSHEV POLYNOMIAL APPROXIMATION PIPELINE ")
    print("=" * 60)
    
    m_samples = 10
    n_targets = 4
    real_y = np.random.rand(m_samples, n_targets) * 10 

    # 2. Hyperparameter Optimization
    best_pows, min_rmse, optimal_eval = find_minimal_incoherence(real_y)
    
    print(f"\n[+] Optimization Complete!")
    print(f"    Optimal Polynomial Degrees (p1, p2, p3): {best_pows}")
    print(f"    Minimum Global RMSE: {min_rmse:.6f}\n")

    # 3. Simulate matrices for equation generation based on optimal found sizes
    p1, p2, p3 = best_pows
    l1 = np.random.rand(p1, p1) * 10
    l2 = np.random.rand(p2, p2) * 10
    l3 = np.random.rand(p3, p3) * 10
    a1, a2, a3, _, _ = calculate_a_and_c_matrices(l1, l2, l3)

    # 4. Generate Equations and Plot
    generate_functional_equations(a1, a2, a3, l1, l2, l3)
    plot_all(optimal_eval, real_y)