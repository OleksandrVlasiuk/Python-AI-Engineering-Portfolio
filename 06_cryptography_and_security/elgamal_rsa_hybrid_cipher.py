# ==============================================================================
# HYBRID ASYMMETRIC CRYPTOGRAPHY & DIGITAL SIGNATURES
# A comprehensive Public Key Infrastructure (PKI) simulation.
# Implements ElGamal for secure message encryption and RSA combined with 
# SHA-256 hashing for cryptographic non-repudiation (Digital Signatures).
# ==============================================================================

import random
from sympy import isprime, mod_inverse, randprime
from hashlib import sha256
import os

# ==============================================================================
# PHASE 1: DISCRETE MATHEMATICS & PRIME UTILITIES
# ==============================================================================

def generate_large_prime(bits=256):
    """Generates a cryptographically secure random prime of specified bit length."""
    return randprime(2 ** (bits - 1), 2 ** bits)

def find_primitive_root(p):
    """Calculates the primitive root modulo p for the cyclic group."""
    for g in range(2, p):
        if pow(g, (p - 1) // 2, p) != 1:
            return g
    return None

# ==============================================================================
# PHASE 2: ELGAMAL ENCRYPTION ALGORITHM
# ==============================================================================

def generate_elgamal_keys(bits=256):
    """
    Generates ElGamal key pairs.
    Returns: p (prime modulus), g (generator), a (private key), h (public key)
    """
    p = generate_large_prime(bits)
    g = find_primitive_root(p)
    a = random.randint(1, p - 1)  # Private Key
    h = pow(g, a, p)              # Public Key
    return p, g, a, h

def encrypt_message_elgamal(p, g, h, message):
    """Encrypts an ASCII string using the ElGamal public key system."""
    r = random.randint(1, p - 1)  # Ephemeral key (randomized per session)
    c1 = pow(g, r, p)
    # Mask each character using the shared secret
    c2 = [(ord(char) * pow(h, r, p)) % p for char in message]
    return c1, c2

def decrypt_message_elgamal(p, a, c1, c2):
    """Decrypts the ElGamal ciphertext using the private key."""
    s = pow(c1, a, p)             # Reconstruct the shared secret
    s_inv = mod_inverse(s, p)     # Calculate modular inverse of the secret
    decrypted_message = ''.join([chr((char * s_inv) % p) for char in c2])
    return decrypted_message

# ==============================================================================
# PHASE 3: RSA ALGORITHM & DIGITAL SIGNATURES
# ==============================================================================

def generate_rsa_keys(bits=256):
    """
    Generates RSA key pairs.
    Returns: n (modulus), e (public exponent), d (private exponent)
    """
    p = generate_large_prime(bits)
    q = generate_large_prime(bits)
    n = p * q
    phi = (p - 1) * (q - 1)
    e = 65537  # Standard optimized prime for public exponent (Fermat prime)
    d = mod_inverse(e, phi)
    return n, e, d

def hash_message(message):
    """Generates a SHA-256 cryptographic hash of the message payload."""
    return int(sha256(message.encode('utf-8')).hexdigest(), 16)

def sign_message_rsa(message, d, n):
    """Creates a digital signature by encrypting the message hash with the RSA private key."""
    hashed_message = hash_message(message)
    signature = pow(hashed_message, d, n)
    return signature

def verify_signature_rsa(message, signature, e, n):
    """Verifies authenticity by decrypting the signature with the RSA public key."""
    hashed_message = hash_message(message)
    decrypted_hash = pow(signature, e, n)
    return hashed_message == decrypted_hash

# ==============================================================================
# PHASE 4: EXECUTION PIPELINE & FILE I/O
# ==============================================================================

def ensure_test_file():
    """Utility to create a dummy message file if it doesn't exist."""
    if not os.path.exists('message.txt'):
        with open('message.txt', 'w') as f:
            f.write("CONFIDENTIAL: The eagle flies at midnight.")

def main():
    print("=" * 70)
    print(" SECURE PKI PIPELINE: ELGAMAL ENCRYPTION + RSA SIGNATURES ")
    print("=" * 70)

    # 0. Setup test environment
    ensure_test_file()

    # --- SENDER SIDE (ENCRYPTION & SIGNING) ---
    print("\n[+] SENDER PROTOCOL INITIALIZED")
    
    # Generate ElGamal Keys
    p, g, a, h = generate_elgamal_keys()
    print("  --> Generating ElGamal Key Pair...")
    print(f"      [Public Key] p: {p}\n      [Public Key] g: {g}\n      [Public Key] h: {h}")

    # Read plaintext payload
    with open('message.txt', 'r') as file:
        message = file.read()
    print(f"  --> Original Payload Loaded: '{message}'")

    # Encrypt Payload
    c1, c2 = encrypt_message_elgamal(p, g, h, message)
    with open('encrypted_message.txt', 'w') as file:
        file.write(f"{c1}\n")
        file.write(' '.join(map(str, c2)))
    print("  --> Payload Encrypted via ElGamal and saved to 'encrypted_message.txt'.")

    # Generate RSA Keys for Digital Signature
    n, e, d = generate_rsa_keys()
    print("\n  --> Generating RSA Key Pair for Digital Signature...")
    print(f"      [RSA Modulus] n: {n}\n      [RSA Public]  e: {e}")

    # Sign the encrypted payload
    c2_str = ''.join(map(str, c2))
    signature = sign_message_rsa(c2_str, d, n)
    with open('signature.txt', 'w') as file:
        file.write(str(signature))
    print("  --> SHA-256 Hash Generated and Signed via RSA. Saved to 'signature.txt'.")

    print("-" * 70)

    # --- RECEIVER SIDE (DECRYPTION & VERIFICATION) ---
    print("\n[+] RECEIVER PROTOCOL INITIALIZED")

    # Read transmitted files
    with open('encrypted_message.txt', 'r') as file:
        c1_received = int(file.readline().strip())
        c2_received = list(map(int, file.readline().strip().split()))

    with open('signature.txt', 'r') as file:
        signature_received = int(file.read().strip())

    # Verify Signature First (Non-Repudiation Check)
    c2_str_received = ''.join(map(str, c2_received))
    is_valid = verify_signature_rsa(c2_str_received, signature_received, e, n)
    
    print(f"  --> Cryptographic Signature Verification: {'VALID' if is_valid else 'INVALID'}")

    if is_valid:
        print("      [Security Check Passed]: Sender identity confirmed. Message integrity verified.")
        # Proceed to decrypt
        decrypted_message = decrypt_message_elgamal(p, a, c1_received, c2_received)
        print(f"\n  --> Decrypted Message: '{decrypted_message}'")
    else:
        print("      [SECURITY ALERT]: Signature validation failed. Payload may be tampered with!")

    print("\n" + "=" * 70)


if __name__ == "__main__":
    main()