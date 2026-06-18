# ==============================================================================
# PLAYFAIR CIPHER IMPLEMENTATION
# A cryptographic system that encrypts and decrypts text using a 5x5 matrix
# generated from a custom keyword. Implements Row, Column, and Rectangle rules.
# ==============================================================================

import sys

# ==============================================================================
# PHASE 1: TEXT PREPROCESSING & MATRIX GENERATION
# ==============================================================================

def toLowerCase(text):
    return text.lower()

def removeSpaces(text):
    return text.replace(" ", "")

def Diagraph(text):
    """Splits text into pairs of characters (diagraphs)."""
    Diagraph = []
    group = 0
    for i in range(2, len(text), 2):
        Diagraph.append(text[group:i])
        group = i
    Diagraph.append(text[group:])
    return Diagraph

def FillerLetter(text):
    """Inserts filler letters ('x') between identical consecutive characters."""
    k = len(text)
    if k % 2 == 0:
        for i in range(0, k, 2):
            if text[i] == text[i + 1]:
                new_word = text[0:i + 1] + str('x') + text[i + 1:]
                new_word = FillerLetter(new_word)
                break
            else:
                new_word = text
    else:
        for i in range(0, k - 1, 2):
            if text[i] == text[i + 1]:
                new_word = text[0:i + 1] + str('x') + text[i + 1:]
                new_word = FillerLetter(new_word)
                break
            else:
                new_word = text
    return new_word

list1 = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'k', 'l', 'm',
         'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z']

def generateKeyTable(word, list1):
    """Generates a 5x5 key matrix based on the provided keyword."""
    key_letters = []
    for i in word:
        if i not in key_letters:
            key_letters.append(i)

    compElements = []
    for i in key_letters:
        if i not in compElements:
            compElements.append(i)
    for i in list1:
        if i not in compElements:
            compElements.append(i)

    matrix = []
    while compElements != []:
        matrix.append(compElements[:5])
        compElements = compElements[5:]

    return matrix

def search(mat, element):
    """Locates the coordinates of a character within the 5x5 matrix."""
    for i in range(5):
        for j in range(5):
            if (mat[i][j] == element):
                return i, j

# ==============================================================================
# PHASE 2: ENCRYPTION LOGIC
# ==============================================================================

def encrypt_RowRule(matr, e1r, e1c, e2r, e2c):
    char1 = matr[e1r][0] if e1c == 4 else matr[e1r][e1c + 1]
    char2 = matr[e2r][0] if e2c == 4 else matr[e2r][e2c + 1]
    return char1, char2

def encrypt_ColumnRule(matr, e1r, e1c, e2r, e2c):
    char1 = matr[0][e1c] if e1r == 4 else matr[e1r + 1][e1c]
    char2 = matr[0][e2c] if e2r == 4 else matr[e2r + 1][e2c]
    return char1, char2

def encrypt_RectangleRule(matr, e1r, e1c, e2r, e2c):
    char1 = matr[e1r][e2c]
    char2 = matr[e2r][e1c]
    return char1, char2

def encryptByPlayfairCipher(Matrix, plainList):
    """Processes diagraphs and applies the appropriate Playfair transformation."""
    CipherText = []
    for i in range(0, len(plainList)):
        ele1_x, ele1_y = search(Matrix, plainList[i][0])
        ele2_x, ele2_y = search(Matrix, plainList[i][1])

        if ele1_x == ele2_x:
            c1, c2 = encrypt_RowRule(Matrix, ele1_x, ele1_y, ele2_x, ele2_y)
        elif ele1_y == ele2_y:
            c1, c2 = encrypt_ColumnRule(Matrix, ele1_x, ele1_y, ele2_x, ele2_y)
        else:
            c1, c2 = encrypt_RectangleRule(Matrix, ele1_x, ele1_y, ele2_x, ele2_y)

        cipher = c1 + c2
        CipherText.append(cipher)
    return CipherText

def encrypt_file(input_file, output_file, key):
    with open(input_file, 'r') as f:
        text_Plain = f.read().strip()

    text_Plain = removeSpaces(toLowerCase(text_Plain))
    PlainTextList = Diagraph(FillerLetter(text_Plain))
    
    # Pad last element if it's a single character
    if len(PlainTextList[-1]) != 2:
        PlainTextList[-1] = PlainTextList[-1] + 'z'

    key = toLowerCase(key)
    Matrix = generateKeyTable(key, list1)
    CipherList = encryptByPlayfairCipher(Matrix, PlainTextList)

    CipherText = "".join(CipherList)

    with open(output_file, 'w') as f:
        f.write(CipherText)

    print(f"Encryption successful. Cipher text written to {output_file}")

# ==============================================================================
# PHASE 3: DECRYPTION LOGIC
# ==============================================================================

def decrypt_RowRule(matr, e1r, e1c, e2r, e2c):
    char1 = matr[e1r][4] if e1c == 0 else matr[e1r][e1c - 1]
    char2 = matr[e2r][4] if e2c == 0 else matr[e2r][e2c - 1]
    return char1, char2

def decrypt_ColumnRule(matr, e1r, e1c, e2r, e2c):
    char1 = matr[4][e1c] if e1r == 0 else matr[e1r - 1][e1c]
    char2 = matr[4][e2c] if e2r == 0 else matr[e2r - 1][e2c]
    return char1, char2

def decrypt_RectangleRule(matr, e1r, e1c, e2r, e2c):
    char1 = matr[e1r][e2c]
    char2 = matr[e2r][e1c]
    return char1, char2

def decryptByPlayfairCipher(Matrix, cipherList):
    PlainText = []
    for i in range(0, len(cipherList)):
        ele1_x, ele1_y = search(Matrix, cipherList[i][0])
        ele2_x, ele2_y = search(Matrix, cipherList[i][1])

        if ele1_x == ele2_x:
            c1, c2 = decrypt_RowRule(Matrix, ele1_x, ele1_y, ele2_x, ele2_y)
        elif ele1_y == ele2_y:
            c1, c2 = decrypt_ColumnRule(Matrix, ele1_x, ele1_y, ele2_x, ele2_y)
        else:
            c1, c2 = decrypt_RectangleRule(Matrix, ele1_x, ele1_y, ele2_x, ele2_y)

        plain = c1 + c2
        PlainText.append(plain)
    return PlainText

def decrypt_file(input_file, key):
    with open(input_file, 'r') as f:
        cipher_Text = f.read().strip()

    CipherTextList = Diagraph(cipher_Text)
    key = toLowerCase(key)
    Matrix = generateKeyTable(key, list1)

    PlainTextList = decryptByPlayfairCipher(Matrix, CipherTextList)
    PlainText = "".join(PlainTextList)

    print("Decryption successful. Plain text is:\n", PlainText)

# ==============================================================================
# PHASE 4: CLI ENTRY POINT
# ==============================================================================

if __name__ == "__main__":
    if len(sys.argv) < 5:
        print("Insufficient arguments provided. Initiating interactive mode.")
        mode = input("Select mode (encrypt/decrypt): ").strip().lower()
        input_file = input("Enter path to input file: ").strip()
        
        if mode == "encrypt":
            output_file = input("Enter path to output file: ").strip()
        else:
            output_file = None
            
        key = input("Enter keyword: ").strip()
    else:
        mode = sys.argv[1].lower()
        input_file = sys.argv[2]
        output_file = sys.argv[3]
        key = sys.argv[4]

    if mode == 'encrypt':
        encrypt_file(input_file, output_file, key)
    elif mode == 'decrypt':
        decrypt_file(input_file, key)
    else:
        print("Invalid mode. Please use 'encrypt' or 'decrypt'.")
        sys.exit(1)