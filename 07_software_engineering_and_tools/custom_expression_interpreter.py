# ==============================================================================
# CUSTOM MATHEMATICAL EXPRESSION INTERPRETER
# A lexical scanner and evaluator that parses expressions from string input.
# Supports decimal, binary, and hexadecimal bases, binary/unary operators, 
# and comprehensive syntax error accumulation.
# ==============================================================================

import math

""" 
--- Syntactic Definition of the Formula (EBNF) ---
arith_expr ::= number ( operator number ( unary_op )* ) *
number     ::= ("0b" | "0x")? cipher cipher *
cipher     ::= "0"..."9" or "A"..."F" (for 0x)
operator   ::= "+" | "-" | "*" | "/" | "%" | "<" | ">" | "#"
unary_op   ::= "sqrt" | "exp" | "inv"
-------------------------------------------------- 
"""

class SimpleInterpret:
    def __init__(self, text):
        self.text = text      # Original formula text
        self.leks = []        # List of tokens (numbers, operators, unary operators)
        self.bases = []       # Tracks the numerical bases used (2, 10, 16)
        self.errors = []      # Accumulates all parsing and execution errors
        self.i = 0            # Scanning position index

    def calc(self):
        """Executes the scanning and evaluation pipeline."""
        print(f'[Input] Original string: "{self.text}"')
        self.delblank()
        print(f'[Pre-processing] After whitespace removal: "{self.text}"')

        # Pass 1: Scan the formula into tokens
        self.scanner()  

        if self.errors:
            return (False, self.errors)

        print(f'[Lexical Analysis] Tokenized sequence: {self.leks}')

        # Prepend a "+" to standardize the initial accumulation
        self.leks.insert(0, "+")  
        print(f'[Normalization] Prepend initial operator: {self.leks}')

        k = 0      # Token index
        res = 0    # Current result accumulator
        print(f'\n[Evaluation] Processing [Operator, Operand] pairs:')

        # Pass 2: Evaluate tokens
        while k < len(self.leks):
            oper = self.leks[k]
            k += 1

            if k >= len(self.leks):
                self.errors.append("Syntax Error: Expected a number after the operator.")
                break

            n = self.leks[k]
            k += 1

            print(f"  Evaluating: [ '{oper}', '{n}' ]")

            # Mathematical Error Handling
            if oper == '/' and n == 0:
                self.errors.append("Math Error: Division by zero.")
                return (False, self.errors)
            if oper == '%' and n == 0:
                self.errors.append("Math Error: Modulo division by zero.")
                return (False, self.errors)

            # Binary Operations
            res = res + n if oper == '+' else \
                  res - n if oper == '-' else \
                  res * n if oper == '*' else \
                  res / n if oper == '/' else \
                  res % n if oper == '%' else \
                  min(res, n) if oper == '<' else \
                  max(res, n) if oper == '>' else \
                  (res + n) / 2 if oper == '#' else res

            # Unary Operations (processed immediately after the number)
            while k < len(self.leks) and self.leks[k] in ["sqrt", "exp", "inv"]:
                uop = self.leks[k]
                k += 1
                res = self.apply_unary(res, uop)

        if self.errors:
            return (False, self.errors)

        # Output formatting based on detected numeral systems
        if all(base == 2 for base in self.bases):
            return (True, bin(int(res)))
        elif all(base == 16 for base in self.bases):
            return (True, hex(int(res)))
        else:
            return (True, res)

    def delblank(self):
        """Removes all whitespace characters from the input text."""
        self.text = self.text.replace(' ', '')

    def scanner(self):
        """Scans the sanitized text and populates the token array."""
        last_type = None  # Tracks if the last token was 'number' or 'operator'

        # Initial Number Extraction
        n = self.onenumber()
        if n is not None:
            self.leks.append(n)
            last_type = 'number'
        else:
            self.errors.append("Syntax Error: Expected a number at the beginning.")
            if self.i < len(self.text):
                self.i += 1

        # Continuous Scanning Loop
        while self.i < len(self.text):
            # Extract consecutive unary operators if present
            while True:
                uop = self.oneunary()
                if uop is not None:
                    self.leks.append(uop)
                else:
                    break

            # Validate current character against allowed syntax set
            if self.i < len(self.text) and not (
                self.text[self.i] in '+-*/%<>#' or
                self.text[self.i].isdigit() or
                self.text.startswith('sqrt', self.i) or
                self.text.startswith('exp', self.i) or
                self.text.startswith('inv', self.i)
            ):
                self.errors.append(f"Lexical Error: Invalid character '{self.text[self.i]}'.")
                self.i += 1
                continue

            # Extract Operator
            sign = self.onesign()
            if sign is not None:
                if last_type == 'operator':
                    self.errors.append(f"Syntax Error: Two consecutive operators '{self.leks[-1]}' and '{sign}'.")
                self.leks.append(sign)
                last_type = 'operator'
            else:
                if self.i < len(self.text) and not self.text[self.i].isdigit() and not self.text[self.i].isalpha():
                    self.errors.append(f"Lexical Error: Invalid character '{self.text[self.i]}'.")
                    self.i += 1
                    continue
                else:
                    self.errors.append("Syntax Error: Expected an operation sign.")
                    if self.i < len(self.text):
                        self.i += 1
                    continue

            # Extract Next Number
            n = self.onenumber()
            if n is not None:
                if last_type == 'number':
                    self.errors.append("Syntax Error: Two consecutive numbers without an operator.")
                self.leks.append(n)
                last_type = 'number'
            else:
                self.errors.append("Syntax Error: Expected a number after the operator.")
                if self.i < len(self.text):
                    self.i += 1
                continue

        return "OK"

    def onenumber(self):
        """Extracts a continuous numerical value (Decimal, Binary, or Hexadecimal)."""
        # Binary processing
        if self.text.startswith('0b', self.i):
            self.i += 2
            num = ""
            while self.i < len(self.text):
                if self.text[self.i] in '01':
                    num += self.text[self.i]
                    self.i += 1
                elif self.text[self.i].isdigit():
                    self.errors.append(f"Lexical Error: Invalid binary digit '{self.text[self.i]}'.")
                    return None
                else:
                    break
            if num:
                self.bases.append(2)
                return int(num, 2)
            else:
                self.errors.append("Lexical Error: Malformed binary sequence.")
                return None

        # Hexadecimal processing
        elif self.text.startswith('0x', self.i):
            self.i += 2
            num = ""
            while self.i < len(self.text):
                if self.text[self.i].isdigit() or self.text[self.i].lower() in 'abcdef':
                    num += self.text[self.i]
                    self.i += 1
                elif self.text[self.i].isalpha():
                    self.errors.append(f"Lexical Error: Invalid hexadecimal character '{self.text[self.i]}'.")
                    return None
                else:
                    break
            if num:
                self.bases.append(16)
                return int(num, 16)
            else:
                self.errors.append("Lexical Error: Malformed hexadecimal sequence.")
                return None

        # Standard Decimal processing
        else:
            num = ""
            while self.i < len(self.text) and self.text[self.i].isdigit():
                num += self.text[self.i]
                self.i += 1
            if num:
                self.bases.append(10)
                return int(num)
            else:
                return None

    def onesign(self):
        """Extracts a single mathematical operator."""
        if self.i < len(self.text) and self.text[self.i] in ['+', '-', '*', '/', '%', '<', '>', '#']:
            self.i += 1
            return self.text[self.i - 1]
        else:
            return None

    def oneunary(self):
        """Extracts supported unary functions."""
        for op in ["sqrt", "exp", "inv"]:
            if self.text.startswith(op, self.i):
                self.i += len(op)
                return op
        return None

    def apply_unary(self, res, uop):
        """Executes a unary mathematical operation on the current accumulator."""
        if uop == 'sqrt':
            if res < 0:
                self.errors.append("Math Error: Cannot compute square root of a negative number.")
                return res
            return math.sqrt(res)
        elif uop == 'exp':
            return math.exp(res)
        elif uop == 'inv':
            if res == 0:
                self.errors.append("Math Error: Cannot compute inverse of zero.")
                return res
            return 1 / res
        else:
            self.errors.append(f"Execution Error: Unknown unary operator '{uop}'.")
            return res

# ==============================================================================
# MAIN EXECUTION PIPELINE
# ==============================================================================
if __name__ == "__main__":
    print("=" * 60)
    print(" MATHEMATICAL EXPRESSION PARSER TEST ")
    print("=" * 60)
    
    # Intentionally malformed formula to demonstrate error handling
    formula = "5 + * 8 / 0"
    
    interpreter = SimpleInterpret(formula)
    res = interpreter.calc()
    
    print("\n" + "-" * 60)
    if res[0]:
        print(f"Final Result: {res[1]}")
    else:
        print("Execution Halted. Errors detected:")
        for error in res[1]:
            print(f"  [!] {error}")
    print("=" * 60)