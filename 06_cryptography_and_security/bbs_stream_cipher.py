# ==============================================================================
# BLUM BLUM SHUB (BBS) STREAM CIPHER
# A cryptographically secure pseudorandom number generator (CSPRNG) used 
# to generate a key stream for XOR-based text encryption.
# ==============================================================================

import random
from sympy import isprime, gcd

# ==============================================================================
# PHASE 1: MATHEMATICAL UTILITIES & PRNG
# ==============================================================================

def generate_large_prime(bits):
    """Generates a large prime number congruent to 3 modulo 4."""
    while True:
        prime_candidate = random.getrandbits(bits)
        if isprime(prime_candidate) and prime_candidate % 4 == 3:
            return prime_candidate

def bbs_generator(n, seed, length):
    """
    Executes the Blum Blum Shub algorithm to generate a pseudorandom bit sequence.
    Formula: X_{n+1} = X_n^2 mod M
    """
    x = seed
    result = []
    for _ in range(length):
        x = (x * x) % n
        result.append(x % 2)  # Extract the least significant bit (LSB)
    return result

# ==============================================================================
# PHASE 2: DATA TRANSFORMATION (TEXT TO BINARY)
# ==============================================================================

def text_to_bits(text):
    """Converts a standard ASCII string into a continuous binary string."""
    bits = ""
    for char in text:
        char_bits = bin(ord(char))[2:]  # Convert character to binary
        char_bits = char_bits.zfill(8)  # Pad to ensure 8-bit length
        bits += char_bits
    return bits

def bits_to_text(bits):
    """Converts a continuous binary string back into an ASCII string."""
    text = ""
    for i in range(0, len(bits), 8):
        byte = bits[i:i+8]
        text += chr(int(byte, 2))
    return text

# ==============================================================================
# PHASE 3: ENCRYPTION / DECRYPTION LOGIC
# ==============================================================================

def encrypt_decrypt(bits, key_stream):
    """
    Performs a symmetric XOR operation between the payload bits and the PRNG key stream.
    Since (A XOR B) XOR B = A, this function handles both encryption and decryption.
    """
    encrypted_bits = ""
    for i in range(len(bits)):
        encrypted_bits += str(int(bits[i]) ^ key_stream[i])
    return encrypted_bits

# ==============================================================================
# PHASE 4: EXECUTION PIPELINE
# ==============================================================================

if __name__ == "__main__":
    print("=" * 60)
    print(" BLUM BLUM SHUB (BBS) ENCRYPTION INITIALIZATION ")
    print("=" * 60)

    # 1. Generate Large Primes (p, q) and compute modulus (n)
    bits = 20
    p = generate_large_prime(bits)
    q = generate_large_prime(bits)
    n = p * q
    print(f"[+] Primes generated: p = {p}, q = {q}")
    print(f"[+] Modulus (n = p * q): {n}")

    # 2. Select a random seed (r) that is coprime to n
    while True:
        r = random.randint(2, n-1)
        if gcd(r, n) == 1:
            break
    print(f"[+] Coprime Seed (r): {r}")

    # 3. Calculate initial state (x0)
    x0 = (r * r) % n
    print(f"[+] Initial State (x0 = r^2 mod n): {x0}\n")

    # 4. Define Payload
    message = "Sunny weather"
    print(f"[*] Original Payload:      '{message}'")

    # 5. Generate Key Stream
    message_bits = text_to_bits(message)
    key_stream = bbs_generator(n, x0, len(message_bits))

    # 6. Encrypt
    encrypted_bits = encrypt_decrypt(message_bits, key_stream)
    print(f"[*] Encrypted Bitstream:   {encrypted_bits}")

    # 7. Decrypt
    decrypted_bits = encrypt_decrypt(encrypted_bits, key_stream)
    decrypted_message = bits_to_text(decrypted_bits)
    print(f"[*] Decrypted Payload:     '{decrypted_message}'\n")