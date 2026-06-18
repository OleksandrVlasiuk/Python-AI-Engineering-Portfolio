# ==============================================================================
# HILL CIPHER IMPLEMENTATION
# A polygraphic substitution cipher based on linear algebra. 
# Implements matrix multiplication, determinants, adjugate matrices, and 
# modular inverses for secure text encryption and decryption.
# ==============================================================================

import sys

# Define standard alphabet and modulo space
alphabet = "abcdefghijklmnopqrstuvwxyz"
m = len(alphabet)

# ==============================================================================
# PHASE 1: LINEAR ALGEBRA & MATHEMATICAL UTILITIES
# ==============================================================================

def text_to_numbers(text):
    """Maps characters to their corresponding numerical indexes."""
    return [alphabet.index(c) for c in text]

def numbers_to_text(numbers):
    """Maps numerical indexes back to their character representation."""
    return ''.join([alphabet[i] for i in numbers])

def generate_key_matrix(key):
    """Constructs an NxN key matrix from a flat string keyword."""
    key_numbers = text_to_numbers(key)
    n = int(len(key_numbers) ** 0.5)
    key_matrix = []
    for i in range(n):
        row = key_numbers[i * n:(i + 1) * n]
        key_matrix.append(row)
    return key_matrix

def mod_inv(a, mod):
    """Calculates the modular inverse using the Extended Euclidean Algorithm."""
    t, new_t = 0, 1
    r, new_r = mod, a
    while new_r != 0:
        quotient = r // new_r
        t, new_t = new_t, t - quotient * new_t
        r, new_r = new_r, r - quotient * new_r
    if r > 1:
        raise ValueError(f"{a} has no modular inverse under modulo {mod}")
    if t < 0:
        t = t + mod
    return t

def determinant(matrix, mod):
    """Calculates the determinant of a matrix under a specific modulo."""
    n = len(matrix)
    if n == 1:
        return matrix[0][0] % mod
    if n == 2:
        return (matrix[0][0] * matrix[1][1] - matrix[0][1] * matrix[1][0]) % mod
    det = 0
    for c in range(n):
        det += ((-1) ** c) * matrix[0][c] * determinant(minor(matrix, 0, c), mod)
        det %= mod
    return det

def minor(matrix, i, j):
    """Returns the minor matrix after removing row 'i' and column 'j'."""
    return [row[:j] + row[j + 1:] for row in (matrix[:i] + matrix[i + 1:])]

def adjugate(matrix):
    """Calculates the adjugate (adjoint) matrix."""
    n = len(matrix)
    adj = [[0] * n for _ in range(n)]
    for i in range(n):
        for j in range(n):
            sign = (-1) ** (i + j)
            adj[j][i] = sign * determinant(minor(matrix, i, j), m)
    return adj

def mod_inv_matrix(matrix, mod):
    """Calculates the modular inverse of the entire key matrix."""
    n = len(matrix)
    det = determinant(matrix, mod)
    det_inv = mod_inv(det, mod)
    # Multiply adjugate by modular inverse of determinant
    matrix_mod_inv = [[(det_inv * adjugate(matrix)[i][j]) % mod for j in range(n)] for i in range(n)]
    return matrix_mod_inv

def gcd(a, b):
    """Calculates the Greatest Common Divisor."""
    while b:
        a, b = b, a % b
    return a

# ==============================================================================
# PHASE 2: ENCRYPTION & DECRYPTION LOGIC
# ==============================================================================

def encrypt_hill(plain_text, key):
    key_matrix = generate_key_matrix(key)
    n = len(key_matrix)

    # Pad text with 'x' to match matrix dimension block size
    while len(plain_text) % n != 0:
        plain_text += 'x'

    plain_numbers = text_to_numbers(plain_text)
    cipher_numbers = []

    for i in range(0, len(plain_numbers), n):
        block = plain_numbers[i:i + n]
        # Perform matrix multiplication block by block
        cipher_block = [sum(block[k] * key_matrix[k][j] for k in range(n)) % m for j in range(n)]
        cipher_numbers.extend(cipher_block)

    return numbers_to_text(cipher_numbers)

def decrypt_hill(cipher_text, key):
    key_matrix = generate_key_matrix(key)
    inv_key_matrix = mod_inv_matrix(key_matrix, m)
    n = len(key_matrix)

    cipher_numbers = text_to_numbers(cipher_text)
    plain_numbers = []

    for i in range(0, len(cipher_numbers), n):
        block = cipher_numbers[i:i + n]
        # Multiply ciphertext block by inverse key matrix
        plain_block = [sum(block[k] * inv_key_matrix[k][j] for k in range(n)) % m for j in range(n)]
        plain_numbers.extend(plain_block)

    return numbers_to_text(plain_numbers)

# ==============================================================================
# PHASE 3: FILE I/O AND CLI EXECUTION
# ==============================================================================

def encrypt_file(input_file, output_file, key):
    with open(input_file, 'r') as f:
        plain_text = f.read().strip().replace(' ', '').lower()

    key = key.lower()
    key_matrix = generate_key_matrix(key)
    det = determinant(key_matrix, m)

    # Validate key feasibility
    if det == 0:
        print("Error: Key matrix determinant is 0. Please provide a different key.")
        return
    if gcd(det, m) != 1:
        print("Error: Key matrix determinant is not coprime with alphabet modulus. Please provide a different key.")
        return

    cipher_text = encrypt_hill(plain_text, key)

    with open(output_file, 'w') as f:
        f.write(cipher_text)

    print(f"Encryption successful. Cipher text written to {output_file}")

def decrypt_file(input_file, output_file, key):
    with open(input_file, 'r') as f:
        cipher_text = f.read().strip().replace(' ', '').lower()

    key = key.lower()
    key_matrix = generate_key_matrix(key)
    det = determinant(key_matrix, m)

    # Validate key feasibility
    if det == 0:
        print("Error: Key matrix determinant is 0. Please provide a different key.")
        return
    if gcd(det, m) != 1:
        print("Error: Key matrix determinant is not coprime with alphabet modulus. Please provide a different key.")
        return

    plain_text = decrypt_hill(cipher_text, key)

    with open(output_file, 'w') as f:
        f.write(plain_text)

    print(f"Decryption successful. Plain text written to {output_file}")

if __name__ == "__main__":
    if len(sys.argv) < 5:
        print("Insufficient arguments provided. Initiating interactive mode.")
        mode = input("Select mode (encrypt/decrypt): ").strip().lower()
        input_file = input("Enter path to input file: ").strip()
        output_file = input("Enter path to output file: ").strip()
        key = input("Enter keyword (Must form an NxN perfect square matrix): ").strip()
    else:
        mode = sys.argv[1].lower()
        input_file = sys.argv[2]
        output_file = sys.argv[3]
        key = sys.argv[4]

    if mode == "encrypt":
        encrypt_file(input_file, output_file, key)
    elif mode == "decrypt":
        decrypt_file(input_file, output_file, key)
    else:
        print("Invalid mode. Please use 'encrypt' or 'decrypt'.")