# ==============================================================================
# LINEAR FEEDBACK SHIFT REGISTER (LFSR) CIPHER
# Hardware-oriented pseudorandom bit generator (PRBG) simulation used for 
# highly efficient stream cipher encryption.
# ==============================================================================

# ==============================================================================
# PHASE 1: LFSR CORE ALGORITHM
# ==============================================================================

def lfsr(seed, taps, n):
    """
    Simulates a Linear Feedback Shift Register.
    Calculates the feedback bit using XOR on designated tap positions.
    """
    state = seed.copy()  # Load initial register state
    results = []

    for i in range(n):
        # Calculate feedback using XOR (modulo 2 sum) on specific tap indexes
        feedback = sum(state[-tap] for tap in taps) % 2

        # Record current snapshot: (Step, Register State, Feedback Bit, Extracted Bit)
        results.append((i + 1, state.copy(), feedback, state[-1]))

        # Shift register right and insert the new feedback bit at the beginning
        state = [feedback] + state[:-1]

    return results

# ==============================================================================
# PHASE 2: ENCRYPTION / DECRYPTION LOGIC
# ==============================================================================

def encrypt_decrypt(text, key_stream):
    """
    Symmetric XOR cipher: Encrypts or decrypts a binary string 
    using the LFSR-generated key stream.
    """
    encrypted_bits = ""
    for i in range(len(text)):
        encrypted_bits += str(int(text[i]) ^ key_stream[i])
    return encrypted_bits

# ==============================================================================
# PHASE 3: EXECUTION PIPELINE
# ==============================================================================

if __name__ == "__main__":
    # 1. System Configuration
    initial_state = [1, 0, 0, 0, 0, 0, 0, 0, 0]
    
    # Polynomial taps: x^9 + x^3 + 1 (Using reverse 1-based indexing)
    taps = [9, 3, 1] 
    
    # Define generation length (should match payload length)
    open_text = "0001110110011"
    n = len(open_text)

    # 2. Execute LFSR Generation
    sequence = lfsr(initial_state, taps, n)

    # 3. Print Execution Matrix (State Table)
    print("\n" + "=" * 74)
    print(f"| {'Step':<6} | {'Internal Register State':<25} | {'Feedback':<8} | {'Output Bit':<12} |")
    print("=" * 74)
    for state_num, reg_state, feedback, output_bit in sequence:
        state_str = "".join(map(str, reg_state))
        print(f"| {state_num:<6} | {state_str:<25} | {feedback:<8} | {output_bit:<12} |")
    print("=" * 74 + "\n")

    # 4. Extract Key Stream
    key_stream = [output_bit for _, _, _, output_bit in sequence]
    
    print(f"[*] Input Bitstream:       {open_text}")
    print(f"[*] Generated Key Stream:  {''.join(map(str, key_stream))}")

    # 5. Encrypt Output
    encrypted_text = encrypt_decrypt(open_text, key_stream)
    print(f"[+] Encrypted Ciphertext:  {encrypted_text}")

    # 6. Decrypt Output (using the same key stream)
    decrypted_text = encrypt_decrypt(encrypted_text, key_stream)
    print(f"[+] Decrypted Plaintext:   {decrypted_text}\n")