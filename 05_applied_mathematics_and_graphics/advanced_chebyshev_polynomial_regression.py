# ==============================================================================
# ADVANCED NUMERICAL MODELING & CHEBYSHEV APPROXIMATION PIPELINE
# Implements the Group Method of Data Handling (GMDH), Coordinate Descent 
# Optimization, Monte Carlo Boundary Simulation, and Algebraic Expansion.
# ==============================================================================

from math import comb
import numpy as np
import matplotlib.pyplot as plt
from tabulate import tabulate


def normalize(matrix):
    norm_mat = matrix.copy().astype(float)
    mins = norm_mat.min(axis=0)
    maxs = norm_mat.max(axis=0)
    for j in range(norm_mat.shape[1]):
        norm_mat[:, j] = (norm_mat[:, j] - mins[j]) / (maxs[j] - mins[j])
    return norm_mat, mins, maxs


def T(t, k):
    if k == 0:
        return np.ones_like(t)
    elif k == 1:
        return t
    else:
        return 2*t * T(t, k-1) - T(t, k-2)


def Tz(x, k):
    if k == 0:
        return 0.5*np.ones_like(x)
    else:
        return T(2*x - 1, k)


def build_tp_matrix(x_norm, p):
    n_samples, n_features = x_norm.shape
    cols = []
    for j in range(n_features):
        for k in range(p):
            col = Tz(x_norm[:, j], k).reshape(-1, 1)
            cols.append(col)
    return np.hstack(cols)


def coordinate_descent_single_output(Tp, b, max_iter=5000, tol=1e-6):
    n_samples, n_params = Tp.shape
    lam = np.zeros((n_params, 1))
    for iteration in range(max_iter):
        lam_old = lam.copy()
        for j in range(n_params):
            r = b - Tp @ lam + Tp[:, j:j+1] * lam[j]
            numerator = Tp[:, j:j+1].T @ r
            denominator = np.sum(Tp[:, j]**2) + 1e-12
            lam[j] = numerator / denominator
        if np.linalg.norm(lam - lam_old) < tol:
            # print(f"coordinate_descent_single_output: збіг на ітерації {iteration}")
            break
    return lam


# Якщо b має форму (n_samples, m), робимо цикл по стовпцях
def coordinate_descent_multi_output(Tp, Y, max_iter=5000, tol=1e-6):
    n_samples, n_params = Tp.shape
    m = Y.shape[1]
    lam_full = np.zeros((n_params, m))
    for i in range(m):
        b_col = Y[:, i:i+1]  # (n_samples,1)
        lam_i = coordinate_descent_single_output(Tp, b_col, max_iter, tol)
        lam_full[:, i:i+1] = lam_i
    return lam_full


def psi(lambda_mat, x_norm, Tz_v):
    n_samples, n_features = x_norm.shape
    p_val = lambda_mat.shape[1]
    psi_mat = np.zeros((n_samples, n_features))
    for j in range(n_features):
        psi_col = np.zeros(n_samples)
        for pk in range(p_val):
            psi_col += lambda_mat[j, pk] * Tz_v(x_norm[:, j], pk)
        psi_mat[:, j] = psi_col
    return psi_mat


def compute_a(psi_mat, Y_norm):
    n_samples, m = Y_norm.shape
    n_params = psi_mat.shape[1]
    a_full = np.zeros((n_params, m))
    for i in range(m):
        # беремо один вихід (нормалізований)
        y_col = Y_norm[:, i:i+1]  # (n_samples,1)
        # розв'язуємо ψ_mat (n_samples,n_params) * a (n_params,1) ≈ y_col
        a_i = coordinate_descent_single_output(psi_mat, y_col, max_iter=10000, tol=1e-8)
        a_full[:, i:i+1] = a_i
    return a_full


def compute_phi(psi_mat, a_matrix):
    return psi_mat @ a_matrix


def compute_c(phi1, phi2, phi3, Y_norm):
    n_samples, m = Y_norm.shape
    c_matrix = np.zeros((3, m))
    for j in range(m):
        M_j = np.hstack([phi1[:, j:j+1], phi2[:, j:j+1], phi3[:, j:j+1]])  # (n_samples,3)
        y_col = Y_norm[:, j:j+1]
        c_j = coordinate_descent_single_output(M_j, y_col, max_iter=10000, tol=1e-8)
        c_matrix[:, j:j+1] = c_j
    return c_matrix


def recalc_y(phi1, phi2, phi3, c_matrix):
    n_samples, m = phi1.shape
    y_recalc_norm = np.zeros((n_samples, m))
    for i in range(n_samples):
        for j in range(m):
            y_recalc_norm[i, j] = (phi1[i, j]*c_matrix[0, j]
                                   + phi2[i, j]*c_matrix[1, j]
                                   + phi3[i, j]*c_matrix[2, j])
    return y_recalc_norm


def rmse(a, b):
    return np.sqrt(np.mean((a - b)**2))


def plot_all_norm(evaluated, real):
    m_val = real.shape[1]
    for i in range(m_val):
        e = rmse(evaluated[:, i], real[:, i])
        plt.figure()
        plt.title(f"Ф{i+1} (нормалізовано): RMSE = {e:.4f}")
        plt.plot(range(1, evaluated.shape[0]+1), real[:, i], 'b-', label=f"Y{i+1} (реальне)")
        plt.plot(range(1, evaluated.shape[0]+1), evaluated[:, i], 'r--', label=f"Ф{i+1} (апроксимоване)")
        plt.legend()
        plt.show()


def denormalize_y(y_norm, y_min, y_max):
    y_denorm = y_norm.copy()
    for j in range(y_norm.shape[1]):
        y_denorm[:, j] = y_norm[:, j]*(y_max[j]-y_min[j]) + y_min[j]
    return y_denorm


def plot_all_denorm(evaluated, real):
    m_val = real.shape[1]
    for i in range(m_val):
        e = rmse(evaluated[:, i], real[:, i])
        plt.figure()
        plt.title(f"Ф{i+1} (денормалізовано): RMSE = {e:.4f}")
        plt.plot(range(1, evaluated.shape[0]+1), real[:, i], 'b-', label=f"Y{i+1} (реальне)")
        plt.plot(range(1, evaluated.shape[0]+1), evaluated[:, i], 'r--', label=f"Ф{i+1} (апроксимоване)")
        plt.legend()
        plt.show()


def print_matrix_tab(matrix, title="Matrix", row_names=None, col_names=None):
    n_rows, n_cols = matrix.shape

    if col_names is None:
        col_names = [f"col{j}" for j in range(n_cols)]
    if row_names is None:
        row_names = [f"row{i}" for i in range(n_rows)]

    headers = [""] + col_names

    table_data = []
    for i in range(n_rows):
        row_i = [row_names[i]] + [f"{matrix[i,j]:.5f}" for j in range(n_cols)]
        table_data.append(row_i)

    print(f"\n=== {title} (shape={n_rows}×{n_cols}) ===")
    print(tabulate(table_data, headers=headers, tablefmt="pretty"))


def print_psi_functions(lambda_matrix, group_index=1, T_label="T*"):
    n_features, p_val = lambda_matrix.shape
    for f in range(n_features):
        terms = []
        for k in range(p_val):
            coeff = lambda_matrix[f, k]
            terms.append(f"{coeff:+.6f}*{T_label}(x^{k})")
        formula = " ".join(terms)
        if formula.startswith("+"):
            formula = formula[1:].strip()
        print(f"Ψ{group_index}{f+1}(x) = {formula}")


def print_phi_function(group_index, output_index, a_matrix, lambda_matrix, T_label="T*", phi_label="Φ"):
    n_features, p_val = lambda_matrix.shape
    terms = []
    counter = 0
    for f in range(n_features):
        a_fi = a_matrix[f, output_index]
        for k in range(p_val):
            coeff = a_fi * lambda_matrix[f, k]
            if counter == 5:
                terms.append("\n\t")
                counter = 0
            terms.append(f"{coeff:+.8f} {T_label}(x^{k})")
            counter += 1

    name = f"{phi_label}{group_index}{output_index+1}(x)"

    formula = " ".join(terms)
    if formula.startswith("+"):
        formula = formula[1:].strip()

    print(f"{name} = {formula}")


def print_all_phi_for_group(group_index, a_matrix, lambda_matrix, m_outputs):
    for i in range(m_outputs):
        print_phi_function(group_index, i, a_matrix, lambda_matrix)


def print_F_functions_short(c_matrix, group_count=3, F_label="F"):
    _, m = c_matrix.shape
    for i in range(m):
        parts = []
        for j in range(group_count):
            c_val = c_matrix[j, i]
            parts.append(f"{c_val:+.6f}*Φ{j+1}{i+1}(x)")
        formula = " ".join(parts)
        if formula.startswith("+"):
            formula = formula[1:].strip()
        print(f"{F_label}{i+1}(x) = {formula}")


def print_F_functions_expanded(c_matrix, a_list, lambda_list, output_index, T_label="T*", F_label="F"):
    group_count = len(a_list)
    terms = []
    counter = 0
    for j in range(group_count):
        c_val = c_matrix[j, output_index]
        a_mat = a_list[j]
        lam_mat = lambda_list[j]
        n_features, p_val = lam_mat.shape

        for f in range(n_features):
            a_fi = a_mat[f, output_index]
            for k in range(p_val):
                lam_fk = lam_mat[f, k]
                coeff = c_val * a_fi * lam_fk
                if counter == 5:
                    terms.append("\n\t")
                    counter = 0
                terms.append(f"{coeff:+.6f}*{T_label}(x^{k})")
                counter += 1

    formula = " ".join(terms)
    if formula.startswith("+"):
        formula = formula[1:].strip()
    print(f"{F_label}{output_index+1}(x) = {formula}")


def print_all_F_expanded(c_matrix, a_list, lambda_list, T_label="T*", F_label="F"):
    _, m = c_matrix.shape
    for i in range(m):
        print_F_functions_expanded(c_matrix, a_list, lambda_list, i, T_label, F_label)


def print_Fi_additive_polynomial_norm(i, c_matrix, a_list, lam_list):
    group_count = len(a_list)
    x_mins_list = []
    x_maxs_list = []
    for j in range(group_count):
        n_features = lam_list[j].shape[0]
        x_mins_list.append(np.zeros(n_features))
        x_maxs_list.append(np.ones(n_features))
    print_Fi_additive_polynomial_denorm(i, c_matrix, a_list, lam_list, x_mins_list, x_maxs_list)


def expand_Tstar_polynomial(k):
    if k == 0:
        return {0: 0.5}
    elif k == 1:
        return {1: 2.0, 0: -1.0}
    elif k == 2:
        return {2: 4.0, 1: -2.0, 0: -0.5}
    elif k == 3:
        return {3: 8.0, 2: -4.0, 1: -3.0, 0: 1.0}
    elif k == 4:
        return {4: 16.0, 3: -8.0, 2: -10.0, 1: 4.0, 0: 0.5}
    elif k == 5:
        return {5: 32.0, 4: -16.0, 3: -28.0, 2: 12.0, 1: 4.0, 0: -1.0}
    else:
        raise NotImplementedError("Expansion for k > 5 is not implemented.")


def polynomial_shifted_to_original(poly_dict, x_min, x_max):
    delta = x_max - x_min
    result = {}
    for n, coeff in poly_dict.items():
        factor = coeff / (delta ** n)
        for r in range(n + 1):
            term_coeff = factor * comb(n, r) * ((-x_min) ** (n - r))
            result[r] = result.get(r, 0.0) + term_coeff
    return result


def expand_one_feature_poly(a_fi, lam_f, x_min, x_max, c_val=1.0):
    from collections import defaultdict
    poly_sum = defaultdict(float)
    p_val = len(lam_f)
    for k in range(p_val):
        c = c_val * a_fi * lam_f[k]
        base_poly = expand_Tstar_polynomial(k)
        for power in base_poly:
            base_poly[power] *= c
        poly_original = polynomial_shifted_to_original(base_poly, x_min, x_max)
        for power, coeff in poly_original.items():
            poly_sum[power] += coeff
    return dict(poly_sum)


def print_Fi_additive_polynomial_denorm(i, c_matrix, a_list, lam_list, x_mins_list, x_maxs_list):
    from collections import defaultdict
    total_poly = defaultdict(float)  # keys: (var_label, power), values: coefficient

    group_count = len(a_list)
    for j in range(group_count):
        c_val = c_matrix[j, i]
        a_mat = a_list[j]
        lam_mat = lam_list[j]
        x_mins = x_mins_list[j]
        x_maxs = x_maxs_list[j]
        n_features, p_val = lam_mat.shape
        for f in range(n_features):
            var_label = f"x{j + 1}_{f + 1}"
            a_fi = a_mat[f, i]
            sub_poly = expand_one_feature_poly(a_fi, lam_mat[f, :], x_mins[f], x_maxs[f], c_val)
            for power, coeff in sub_poly.items():
                total_poly[(var_label, power)] += coeff

    sorted_terms = sorted(total_poly.items(), key=lambda item: (item[0][0], item[0][1]))
    terms_str = []
    counter = 0
    for (var_label, power), coeff in sorted_terms:
        if abs(coeff) < 1e-14:
            continue
        if power == 0:
            term_str = f"{coeff:+.6f}"
        elif power == 1:
            term_str = f"{coeff:+.6f}*{var_label}"
        else:
            term_str = f"{coeff:+.6f}*{var_label}^{power}"
        if counter == 5:
            terms_str.append("\n\t")
            counter = 0
        terms_str.append(term_str)
        counter += 1
    formula = " ".join(terms_str)
    if formula.startswith("+"):
        formula = formula[1:].strip()
    print(f"F{i + 1}(x1,x2,x3) = {formula}")


def pipeline():
    # -------------------------------------------------
    # 1. Дані та розбиття на групи
    # -------------------------------------------------
    data = [
        [1, 2.050, 22.015, 1.050, 4.015, 5.000, 1.000, 8.100, 154.621, 158.145, 219.406, 227.683],
        [2, 5.150, 16.100, 1.150, 9.105, 9.100, 2.100, 2.308, 193.163, 173.368, 192.651, 190.123],
        [3, 8.200, 10.125, 1.192, 12.945, 12.200, 2.500, 3.500, 587.841, 271.084, 187.691, 183.576],
        [4, 11.250, 4.175, 1.205, 19.175, 28.700, 3.500, 3.500, 767.197, 383.567, 78.793, 74.189],
        [5, 14.355, 1.200, 4.405, 21.875, 30.000, 2.500, 9.457, 381.935, 493.378, 154.316, 183.576],
        [6, 17.350, 2.050, 8.350, 29.251, 39.000, 5.200, 1.000, 1153.789, 601.378, 177.082, 132.817],
        [7, 20.450, 4.900, 12.411, 34.495, 46.700, 8.500, 1.500, 1210.296, 855.579, 267.858, 257.425],
        [8, 23.698, 10.500, 16.508, 38.698, 53.800, 10.700, 2.700, 1581.381, 960.432, 391.956, 289.519],
        [9, 26.900, 15.000, 20.795, 42.598, 60.800, 12.500, 3.200, 1987.364, 1176.283, 491.262, 319.231],
        [10, 24.250, 20.700, 24.695, 16.999, 62.800, 14.000, 15.536, 1293.657, 1293.657, 512.859, 349.173],
        [11, 27.250, 25.750, 21.750, 9.748, 48.100, 16.700, 2.500, 2292.341, 1578.624, 653.717, 744.136],
        [12, 28.800, 30.775, 18.804, 4.775, 102.800, 18.500, 1.760, 1988.324, 2354.324, 717.965, 879.152],
        [13, 24.950, 35.800, 15.850, 2.798, 117.800, 21.000, 2.300, 1326.939, 3478.926, 955.991, 901.239],
        [14, 20.840, 40.950, 12.050, 2.798, 127.900, 29.900, 6.010, 658.407, 4588.675, 1169.392, 1250.482],
        [15, 36.500, 32.865, 9.910, 18.355, 82.600, 10.600, 4.386, 3686.567, 5499.367, 1292.924, 1340.976],
        [16, 4.929, 8.915, 5.031, 35.875, 75.900, 28.700, 2.100, 218.973, 6468.567, 1318.549, 1875.846],
        [17, 4.929, 8.915, 9.011, 25.375, 71.500, 28.700, 2.100, 195.737, 7335.932, 1257.355, 916.124],
        [18, 9.935, 4.815, 9.935, 31.899, 57.900, 18.700, 2.100, 186.746, 9335.124, 984.167, 863.928],
        [19, 9.935, 4.815, 19.875, 29.800, 69.800, 7.400, 1.800, 193.568, 11261.946, 716.375, 703.153],
        [20, 9.935, 4.815, 19.875, 29.800, 69.800, 7.400, 1.800, 193.568, 12151.387, 541.325, 291.578],
        [21, 12.750, 24.975, 28.108, 27.975, 12.500, 23.560, 13.530, 1323.784, 13910.519, 475.651, 571.588],
        [22, 21.350, 36.805, 38.204, 19.915, 6.900, 3.500, 3.600, 2381.825, 15485.124, 448.344, 341.842],
        [23, 24.150, 38.208, 30.248, 21.915, 8.600, 8.500, 4.850, 2381.945, 17688.125, 644.716, 239.425],
        [24, 21.350, 36.875, 28.375, 8.675, 3.401, 3.510, 6.450, 2881.321, 19883.453, 829.942, 129.412],
        [25, 27.375, 40.855, 23.331, 8.565, 1.300, 34.700, 9.520, 3529.958, 9080.562, 949.316, 95.954],
        [26, 30.600, 36.875, 25.895, 1.300, 2.340, 40.700, 4.230, 3120.356, 7887.987, 1148.231, 150.492],
        [27, 34.500, 47.775, 13.495, 14.775, 11.200, 23.700, 12.950, 5917.152, 5685.951, 1347.987, 254.897],
        [28, 30.700, 31.800, 5.029, 5.027, 7.800, 10.400, 1.500, 2812.143, 3455.494, 1542.967, 458.289],
        [29, 24.700, 13.700, 3.697, 25.677, 17.800, 10.400, 1.500, 2212.145, 1211.209, 1732.856, 672.164],
        [30, 12.750, 32.603, 15.927, 10.400, 13.340, 2.360, 12.243, 677.325, 1493.132, 453.168, 833.356],
        [31, 8.925, 27.345, 8.500, 44.415, 60.200, 9.900, 2.130, 10632.876, 364.615, 1177.224, 206.123],
        [32, 4.950, 12.392, 9.805, 19.175, 9.600, 6.750, 2.100, 4984.243, 152.534, 963.453, 82.659],
        [33, 9.950, 12.925, 12.919, 18.275, 101.100, 6.360, 3.600, 126.376, 45.178, 779.167, 93.884],
        [34, 18.010, 1.105, 27.933, 3.091, 128.300, 3.650, 13.120, 1616.829, 36.176, 580.362, 71.345],
        [35, 20.943, 3.010, 21.935, 9.355, 94.300, 3.520, 15.360, 473.329, 20.364, 287.192, 66.841],
        [36, 19.950, 13.110, 15.950, 4.115, 57.600, 2.720, 12.850, 449.421, 10.428, 185.834, 93.952],
        [37, 4.935, 2.135, 19.735, 12.529, 3.920, 1.760, 32.456, 96.324, 8.475, 301.985, 109.463],
        [38, 4.950, 12.128, 17.935, 12.160, 15.260, 2.160, 16.578, 176.478, 528.591, 233.415, 427.168],
        [39, 4.935, 2.135, 17.935, 12.529, 3.920, 1.760, 14.320, 170.948, 54.183, 602.861, 308.613],
        [40, 12.929, 2.135, 25.925, 29.135, 4.800, 1.480, 16.334, 204.549, 705.817, 407.319, 407.319],
        [41, 18.010, 1.105, 27.933, 3.091, 128.300, 3.650, 13.120, 1616.829, 676.578, 176.457, 282.263],
        [42, 14.943, 18.115, 6.029, 5.027, 97.800, 10.400, 1.500, 973.143, 16.494, 642.967, 433.281],
        [43, 9.050, 13.110, 17.970, 4.115, 57.600, 2.720, 12.850, 249.421, 10.428, 185.834, 241.122],
        [44, 20.943, 3.010, 21.935, 9.355, 94.300, 3.520, 15.360, 473.329, 195.814, 108.417, 184.132],
        [45, 19.950, 13.110, 15.950, 4.115, 57.600, 2.720, 12.850, 449.421, 204.549, 1178.653, 61.953],
    ]
    data = np.array(data)
    data = data[:, 1:]  # відкидаємо індексний стовпець

    data_raw = data.copy()

    x1 = data[:, 0:2]
    x2 = data[:, 2:4]
    x3 = data[:, 4:7]
    y = data[:, 7:11]

    # -------------------------------------------------
    # 2. Нормалізація
    # -------------------------------------------------
    x1_norm, x1_min, x1_max = normalize(x1)
    x2_norm, x2_min, x2_max = normalize(x2)
    x3_norm, x3_min, x3_max = normalize(x3)
    y_norm, y_min, y_max = normalize(y)

    # -------------------------------------------------
    # 3. b як середнє між мінімумом і максимумом у кожному рядку y_norm
    # -------------------------------------------------
    b = np.array([(row.min() + row.max()) / 2 for row in y_norm]).reshape(-1, 1)

    # -------------------------------------------------
    # 4. Зміщені поліноми Чебишева
    # -------------------------------------------------
    Tz_v = np.vectorize(Tz)

    # -------------------------------------------------
    # 5. Побудова матриці Tp (з нормалізованих x)
    # -------------------------------------------------
    p1, p2, p3 = 4, 4, 5
    # p1, p2, p3 = 5, 5, 6
    # p1, p2, p3 = 2, 2, 2

    Tp1 = build_tp_matrix(x1_norm, p1)
    Tp2 = build_tp_matrix(x2_norm, p2)
    Tp3 = build_tp_matrix(x3_norm, p3)
    Tp = np.hstack([Tp1, Tp2, Tp3])  # (n_samples, p1*dim(x1) + p2*dim(x2) + p3*dim(x3))

    # -------------------------------------------------
    # 6. Метод покоординатного спуску для одновихідних задач
    # -------------------------------------------------
    # 6.1. Обчислення λ (p1+p2+p3) для b
    # -------------------------------------------------
    _lambda = coordinate_descent_multi_output(Tp, b, max_iter=10000, tol=1e-8)
    # lam1 = coordinate_descent_multi_output(A1, b, max_iter=10000, tol=1e-8)
    # lam2 = coordinate_descent_multi_output(A2, b, max_iter=10000, tol=1e-8)
    # lam3 = coordinate_descent_multi_output(A3, b, max_iter=10000, tol=1e-8)

    # Розбиваємо lam на групи
    n_lambda_x1 = x1.shape[1] * p1
    n_lambda_x2 = x2.shape[1] * p2
    n_lambda_x3 = x3.shape[1] * p3

    lambda_x1 = _lambda[:n_lambda_x1].reshape((x1.shape[1], p1))
    lambda_x2 = _lambda[n_lambda_x1:n_lambda_x1 + n_lambda_x2].reshape((x2.shape[1], p2))
    lambda_x3 = _lambda[n_lambda_x1 + n_lambda_x2:].reshape((x3.shape[1], p3))

    col_names = [str(num) for num in range(1, 6)]
    print_matrix_tab(lambda_x1, "lambda_x1", row_names=["X11", "X12", "X13"], col_names=col_names)  # виводимо таблицю λ1
    print_matrix_tab(lambda_x2, "lambda_x2", row_names=["X21", "X22", "X23"], col_names=col_names)  # виводимо таблицю λ2
    print_matrix_tab(lambda_x3, "lambda_x3", row_names=["X31", "X32", "X33"], col_names=col_names)  # виводимо таблицю λ3

    # -------------------------------------------------
    # 7.1. Обчислення ψ
    # -------------------------------------------------
    psi1 = psi(lambda_x1, x1_norm, Tz_v)
    psi2 = psi(lambda_x2, x2_norm, Tz_v)
    psi3 = psi(lambda_x3, x3_norm, Tz_v)
    print()
    print_psi_functions(lambda_matrix=lambda_x1, group_index=1)
    print_psi_functions(lambda_matrix=lambda_x2, group_index=2)
    print_psi_functions(lambda_matrix=lambda_x3, group_index=3)

    # -------------------------------------------------
    # 7.2. compute_a: розв'язуємо ψ * a ≈ y_norm
    # -------------------------------------------------
    # a (для y_norm)
    a1_matrix = compute_a(psi1, y_norm)
    a2_matrix = compute_a(psi2, y_norm)
    a3_matrix = compute_a(psi3, y_norm)

    col_names = ["Y1", "Y2", "Y3", "Y4"]
    print_matrix_tab(a1_matrix, "a1_matrix", row_names=["X11", "X12", "X13"], col_names=col_names)
    print_matrix_tab(a2_matrix, "a2_matrix", row_names=["X21", "X22", "X23"], col_names=col_names)
    print_matrix_tab(a3_matrix, "a3_matrix", row_names=["X31", "X32", "X33"], col_names=col_names)
    print()

    # -------------------------------------------------
    # 7.3. compute_phi: φ = ψ * a
    # -------------------------------------------------
    # φ
    phi1 = compute_phi(psi1, a1_matrix)
    phi2 = compute_phi(psi2, a2_matrix)
    phi3 = compute_phi(psi3, a3_matrix)

    # Потім друкуємо формули:
    m = y.shape[1]   # кількість виходів
    print_all_phi_for_group(1, a1_matrix, lambda_x1, m)
    print_all_phi_for_group(2, a2_matrix, lambda_x2, m)
    print_all_phi_for_group(3, a3_matrix, lambda_x3, m)

    # -------------------------------------------------
    # 7.4. compute_c: [φ1 φ2 φ3]*c ≈ y_norm
    # -------------------------------------------------
    c_matrix = compute_c(phi1, phi2, phi3, y_norm)
    col_names = ["Y1", "Y2", "Y3", "Y4"]
    print_matrix_tab(c_matrix, "c_matrix", row_names=["X1", "X2", "X3"], col_names=col_names)
    print()

    # -------------------------------------------------
    # 7.5. recalc_y: відновлюємо y_norm
    # -------------------------------------------------
    # реконструкція y_norm
    y_recalc_norm = recalc_y(phi1, phi2, phi3, c_matrix)
    print_F_functions_short(c_matrix, group_count=3, F_label="F")
    print()
    print("\n=== F у формі поліномів Чебишева ===")
    a_list = [a1_matrix, a2_matrix, a3_matrix]
    lambda_list = [lambda_x1, lambda_x2, lambda_x3]
    print_all_F_expanded(c_matrix, a_list, lambda_list, T_label="T*", F_label="F")
    print()

    print("\n=== F у формі звичайних багаточленів (нормалізовано) ===")
    # Prepare lists of mins and maxs for each group:
    x_mins_list = [x1_min, x2_min, x3_min]
    x_maxs_list = [x1_max, x2_max, x3_max]
    for i in range(m):
        print_Fi_additive_polynomial_denorm(
            i,
            c_matrix,
            [a1_matrix, a2_matrix, a3_matrix],
            [lambda_x1, lambda_x2, lambda_x3],
            x_mins_list,
            x_maxs_list
        )

    print("\n=== F у формі звичайних багаточленів (денормалізованому)  ===")
    for i in range(m):  # m outputs
        print_Fi_additive_polynomial_norm(
            i,
            c_matrix,
            [a1_matrix, a2_matrix, a3_matrix],
            [lambda_x1, lambda_x2, lambda_x3]
        )

    # print()
    # for i in range(y_norm.shape[1]):  # нев'язка (нормалізовано)
    #     err = rmse(y_recalc_norm[:, i], y_norm[:, i])
    #     print(f"RMSE (нормалізовано) для Y{i+1}: {err:.4f}")
    #
    # plot_all_norm(y_recalc_norm, y_norm)

    y_recalc_denorm = denormalize_y(y_recalc_norm, y_min, y_max)

    # print()
    # for i in range(y.shape[1]):  # нев'язка (денормалізовано)
    #     err = rmse(y_recalc_denorm[:, i], y[:, i])
    #     print(f"RMSE (денормалізовано) для Y{i+1}: {err:.4f}")
    #
    # plot_all_denorm(y_recalc_denorm, y)

    # ------------------------------------------------------------
    # 8. Початкові межі B-,B+, D2-,D2+
    # ------------------------------------------------------------
    x1 = data_raw[:, 0:2]
    x2 = data_raw[:, 2:4]
    x3 = data_raw[:, 4:7]
    y = data_raw[:, 7:11]
    x1_min, x1_max = x1.min(axis=0), x1.max(axis=0)  # min and max from x1
    x2_min, x2_max = x2.min(axis=0), x2.max(axis=0)  # min and max from x2
    x3_min, x3_max = x3.min(axis=0), x3.max(axis=0)  # min and max from x3
    y_min, y_max = y.min(axis=0), y.max(axis=0)  # min and max from y

    b_minus, b_plus = 1.0 * y_min, 1.0 * y_max
    d2_minus, d2_plus = 1.0 * x2_min, 1.0 * x2_max
    # d1 та d3 не чіпаємо, бо згідно варіанту 16 вони незмінні
    d1_minus, d1_plus = 1.0 * x1_min, 1.0 * x1_max
    d3_minus, d3_plus = 1.0 * x3_min, 1.0 * x3_max

    STEP_B = 0.3  # 30 % розширення B
    STEP_D = 0.3  # 30 % розширення D2

    def grow(low, high, step):
        """симетрично розширює [low, high] на step частки ширини"""
        half = 0.5 * step * (high - low)
        return low - half, high + half

    def adjust_B_bounds(y_minus, y_plus):
        """
        Перевіряє умову (5.13). Якщо межі порушено — розширює відповідні b±.
        Повертає True, якщо межі змінено.
        """
        y_minus = y_minus.ravel()  # ← перетворюємо на 1-D
        y_plus = y_plus.ravel()

        need = (y_minus < b_minus) | (y_plus > b_plus)
        if np.any(need):
            b_minus[need], b_plus[need] = grow(b_minus[need],
                                               b_plus[need],
                                               STEP_B)
            return True
        return False

    def adjust_D2_bounds(x2_minus, x2_plus):
        """
        Перевіряє умову (5.19). Якщо межі порушено — розширює відповідні d2±.
        Повертає True, якщо межі змінено.
        """
        x2_minus = x2_minus.ravel()  # ← так само “сплющуємо”
        x2_plus = x2_plus.ravel()

        # need = (x2_minus < d2_minus) | (x2_plus > d2_plus)
        need = (d2_minus < x2_minus) | (d2_plus > x2_plus)
        if np.any(need):
            d2_minus[need], d2_plus[need] = grow(d2_minus[need],
                                                 d2_plus[need],
                                                 STEP_D)
            return True
        return False

    def op1_pareto_test(sample_sz=50_000):
        """Монте-Карло для оцінки y_i⁻,y_i⁺  (формули 5.11–5.12)."""
        rx1 = np.random.uniform(0, 1, size=(sample_sz, x1.shape[1]))
        rx2 = np.random.uniform(0, 1, size=(sample_sz, x2.shape[1]))
        rx3 = np.random.uniform(0, 1, size=(sample_sz, x3.shape[1]))

        p1 = psi(lambda_x1, rx1, Tz_v) @ a1_matrix
        p2 = psi(lambda_x2, rx2, Tz_v) @ a2_matrix
        p3 = psi(lambda_x3, rx3, Tz_v) @ a3_matrix
        y_mc = recalc_y(p1, p2, p3, c_matrix)

        y_mc = denormalize_y(y_mc, y_min, y_max)

        y_minus = y_mc.min(axis=0)[:, None]
        y_plus = y_mc.max(axis=0)[:, None]

        print_matrix_tab(
            np.hstack([y_minus, y_plus]),
            title="B*",
            row_names=[f"Y{i + 1}" for i in range(y.shape[1])],
            col_names=["y⁻", "y⁺"]
        )
        return y_minus, y_plus

    def adjust_D1_bounds(x1_minus, x1_plus):
        """Перевіряє умову (5.19) для x1 та розширює межі d1± при потребі"""
        x1_minus = x1_minus.ravel()
        x1_plus = x1_plus.ravel()
        need = (d1_minus < x1_minus) | (d1_plus > x1_plus)
        if np.any(need):
            d1_minus[need], d1_plus[need] = grow(d1_minus[need], d1_plus[need], STEP_D)
            return True
        return False

    # ------------------------------------------------------------
    # Основний цикл узгодження для x1 та x2
    # ------------------------------------------------------------
    MAX_ITERS = 20
    for it in range(MAX_ITERS):
        print(f"\n\n========== Ітерація {it + 1} ==========", end="")

        # Вивід меж D± для x1 та x2
        print_matrix_tab(
            np.vstack([
                np.hstack([d1_minus.reshape(-1, 1), d1_plus.reshape(-1, 1)]),
                np.hstack([d2_minus.reshape(-1, 1), d2_plus.reshape(-1, 1)])
            ]),
            title="D± (x1, x2)",
            row_names=[f"x1_{i + 1}" for i in range(x1.shape[1])] + [f"x2_{i + 1}" for i in range(x2.shape[1])],
            col_names=["d⁻", "d⁺"]
        )

        # Обчислення фактичних меж D* для x1
        x1_minus = x1.min(axis=0)
        x1_plus = x1.max(axis=0)
        print_matrix_tab(
            np.hstack([x1_minus.reshape(-1, 1), x1_plus.reshape(-1, 1)]),
            title="D* (x1)",
            row_names=[f"x1_{i + 1}" for i in range(x1.shape[1])],
            col_names=["x⁻", "x⁺"]
        )

        # Обчислення фактичних меж D* для x2
        x2_minus = x2.min(axis=0)
        x2_plus = x2.max(axis=0)
        print_matrix_tab(
            np.hstack([x2_minus.reshape(-1, 1), x2_plus.reshape(-1, 1)]),
            title="D* (x2)",
            row_names=[f"x2_{i + 1}" for i in range(x2.shape[1])],
            col_names=["x⁻", "x⁺"]
        )

        # Перевірка потреби розширення меж для x1
        if adjust_D1_bounds(x1_minus, x1_plus):
            print("D1 розширено, знову OP-1")
            continue

        # Перевірка потреби розширення меж для x2
        if adjust_D2_bounds(x2_minus, x2_plus):
            print("D2 розширено, знову OP-1")
            continue

        print("Сумісність досягнута: (5.19) виконується.")
        break
    else:
        print(f"Не вдалося узгодити межі за {MAX_ITERS} ітерацій.")


# --- запуск усього конвеєра ---------------------------------------------
pipeline()
