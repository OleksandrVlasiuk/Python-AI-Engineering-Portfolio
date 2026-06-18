# ==============================================================================
# RECURSIVE DESCENT INTERPRETER & MINI-LANGUAGE EVALUATOR
# An advanced abstract syntax tree (AST) evaluator using a recursive descent 
# parsing algorithm. Supports operator precedence (PEMDAS), variable assignment, 
# trigonometric functions, exponential scientific notation, and a print statement.
# ==============================================================================

import math
import re

class ParserException(Exception):
    """Custom exception for lexical and syntactic parsing errors."""
    pass

class RecursiveDescentInterpreter:
    # --- Token Definitions ---
    TOKEN_EMPTY = 0
    TOKEN_NUMBER = 1
    TOKEN_OPEN_BRACKET = 2
    TOKEN_CLOSE_BRACKET = 3
    TOKEN_ADD = 4
    TOKEN_SUBTRACT = 5
    TOKEN_MULTIPLY = 6
    TOKEN_DIVIDE = 7
    TOKEN_DIVIDE_WHOLE = 8      
    TOKEN_REMAINDER = 9        
    TOKEN_POW = 10             
    TOKEN_SIN = 11             
    TOKEN_COS = 12             
    TOKEN_IDENTIFIER = 13      # Variables

    def __init__(self):
        # Execution environment state (stores variable assignments)
        self.variables = {}

    def remove_whitespace(self, text):
        return text.replace(' ', '')

    def tokenize(self, text):
        """Lexical analysis: Converts raw text into a sequence of recognizable tokens."""
        self.text = self.remove_whitespace(text)
        self.tokens = []
        self.i = 0
        
        while self.i < len(self.text):
            ch = self.text[self.i]
            
            # Parentheses
            if ch == '(':
                self.tokens.append((self.TOKEN_OPEN_BRACKET, '('))
                self.i += 1
            elif ch == ')':
                self.tokens.append((self.TOKEN_CLOSE_BRACKET, ')'))
                self.i += 1
                
            # Operators
            elif ch == '+':
                self.tokens.append((self.TOKEN_ADD, '+'))
                self.i += 1
            elif ch == '-':
                self.tokens.append((self.TOKEN_SUBTRACT, '-'))
                self.i += 1
            elif ch == '*':
                if self.i + 1 < len(self.text) and self.text[self.i + 1] == '*':
                    self.tokens.append((self.TOKEN_POW, '**'))
                    self.i += 2
                else:
                    self.tokens.append((self.TOKEN_MULTIPLY, '*'))
                    self.i += 1
            elif ch == '/':
                if self.i + 1 < len(self.text) and self.text[self.i + 1] == '/':
                    self.tokens.append((self.TOKEN_DIVIDE_WHOLE, '//'))
                    self.i += 2
                else:
                    self.tokens.append((self.TOKEN_DIVIDE, '/'))
                    self.i += 1
            elif ch == '%':
                self.tokens.append((self.TOKEN_REMAINDER, '%'))
                self.i += 1
                
            # Numbers (including floating point and scientific notation like 1e-3)
            elif ch.isdigit() or ch == '.' or ch in '+-':
                self.parse_number()
                
            # Identifiers (Variables and Math Functions)
            elif ch.isalpha() or ch == '_':
                start = self.i
                while self.i < len(self.text) and (self.text[self.i].isalnum() or self.text[self.i] == '_'):
                    self.i += 1
                name = self.text[start:self.i]
                
                if name == 'sin':
                    self.tokens.append((self.TOKEN_SIN, 'sin'))
                elif name == 'cos':
                    self.tokens.append((self.TOKEN_COS, 'cos'))
                else:
                    self.tokens.append((self.TOKEN_IDENTIFIER, name))
            else:
                return False
                
        self.tokens.append((self.TOKEN_EMPTY, '#'))
        return True

    def parse_number(self):
        """Uses Regex to extract complex floating point and scientific notation numbers."""
        match = re.match(r'[+-]?(\d+(\.\d*)?|\.\d+)([eE][+-]?\d+)?', self.text[self.i:])
        if match:
            num_str = match.group(0)
            self.tokens.append((self.TOKEN_NUMBER, float(num_str)))
            self.i += len(num_str)
        else:
            raise ParserException(f"Lexical error in number formulation near: '{self.text[self.i:]}'")

    def advance(self):
        """Moves the parser to the next token."""
        if self.k < len(self.tokens) - 1:
            self.k += 1
        else:
            raise ParserException("Unexpected end of expression.")

    # ==========================================================================
    # RECURSIVE DESCENT PARSER (Enforces Operator Precedence)
    # ==========================================================================

    def parse_expression(self):
        """Handles lowest precedence operations (Addition and Subtraction)."""
        y = self.parse_term()
        while self.tokens[self.k][0] in (self.TOKEN_ADD, self.TOKEN_SUBTRACT):
            op = self.tokens[self.k][0]
            self.advance()
            y = y + self.parse_term() if op == self.TOKEN_ADD else y - self.parse_term()
        return y

    def parse_term(self):
        """Handles medium precedence operations (Multiplication, Division, Modulo)."""
        z = self.parse_factor()
        while self.tokens[self.k][0] in (self.TOKEN_MULTIPLY, self.TOKEN_DIVIDE, self.TOKEN_DIVIDE_WHOLE, self.TOKEN_REMAINDER):
            op = self.tokens[self.k][0]
            self.advance()
            if op == self.TOKEN_MULTIPLY:
                z *= self.parse_factor()
            elif op == self.TOKEN_DIVIDE:
                z /= self.parse_factor()
            elif op == self.TOKEN_DIVIDE_WHOLE:
                z //= self.parse_factor()
            elif op == self.TOKEN_REMAINDER:
                z %= self.parse_factor()
        return z

    def parse_factor(self):
        """Handles highest precedence operations (Brackets, Powers, Functions, Unary signs)."""
        negative = False
        
        # Unary operations
        if self.tokens[self.k][0] == self.TOKEN_SUBTRACT:
            negative = True
            self.advance()
        elif self.tokens[self.k][0] == self.TOKEN_ADD:
            self.advance()

        tok = self.tokens[self.k]
        
        # Resolving primitives
        if tok[0] == self.TOKEN_NUMBER:
            self.advance()
            val = tok[1]
            
        elif tok[0] == self.TOKEN_IDENTIFIER:
            varname = tok[1]
            if varname not in self.variables:
                raise ParserException(f"Reference Error: Variable '{varname}' is undefined.")
            val = self.variables[varname]
            self.advance()
            
        elif tok[0] in (self.TOKEN_SIN, self.TOKEN_COS):
            func = tok[0]
            self.advance()
            if self.tokens[self.k][0] != self.TOKEN_OPEN_BRACKET:
                raise ParserException("Syntax Error: Expected '(' after function declaration.")
            self.advance()
            
            arg = self.parse_expression()
            
            if self.tokens[self.k][0] != self.TOKEN_CLOSE_BRACKET:
                raise ParserException("Syntax Error: Expected ')' after function arguments.")
            self.advance()
            val = math.sin(arg) if func == self.TOKEN_SIN else math.cos(arg)
            
        elif tok[0] == self.TOKEN_OPEN_BRACKET:
            self.advance()
            val = self.parse_expression()
            if self.tokens[self.k][0] != self.TOKEN_CLOSE_BRACKET:
                raise ParserException("Syntax Error: Missing closing parenthesis.")
            self.advance()
            
        else:
            raise ParserException(f"Syntax Error: Unrecognized token '{tok[1]}'.")

        if negative:
            val = -val

        # Powers (evaluated right-to-left conventionally, implemented iteratively here)
        while self.tokens[self.k][0] == self.TOKEN_POW:
            self.advance()
            val = val ** self.parse_factor()

        return val

    # ==========================================================================
    # EXECUTION PIPELINE
    # ==========================================================================

    def evaluate_expression(self, expr):
        """Main entry point to tokenize and parse a single mathematical string."""
        if not self.tokenize(expr):
            return False, f"Lexical scanner failed to recognize sequence: {expr}"
        self.k = 0
        try:
            val = self.parse_expression()
            if self.tokens[self.k][0] != self.TOKEN_EMPTY:
                return False, f"Syntax Error: Unprocessed trailing tokens: {self.tokens[self.k][1]}"
            return True, val
        except Exception as e:
            return False, str(e)

    def execute(self, line):
        """Processes a line of code: handles prints, assignments, or evaluations."""
        line = line.strip()
        if not line:
            return True, None 

        # Handle Print Statement
        if line.startswith("print(") and line.endswith(")"):
            content = line[6:-1]
            parts = [part.strip() for part in content.split(',')]
            result = []

            for part in parts:
                if part.startswith('"') and part.endswith('"'):
                    result.append(part.strip('"')) # String literal
                elif part in self.variables:
                    result.append(str(self.variables[part])) # Variable lookup
                else:
                    ok, val = self.evaluate_expression(part) # Inline evaluation
                    if ok:
                        result.append(str(val))
                    else:
                        return False, f"Reference Error: Variable or string '{part}' not found."

            return True, " ".join(result)

        # Handle Variable Assignment
        elif '=' in line:
            var, expr = line.split('=', 1)
            var = var.strip()
            if not var.isidentifier():
                return False, f"Syntax Error: Invalid variable identifier '{var}'."
            ok, val = self.evaluate_expression(expr)
            if ok:
                self.variables[var] = val
                return True, None 
            return False, val

        # Handle Raw Evaluation
        else:
            return self.evaluate_expression(line)

    def interpret_program(self, lines):
        """Executes a full script line by line maintaining the environment state."""
        results = []
        for line in lines:
            if not line.strip():
                continue 
            ok, out = self.execute(line)
            results.append((ok, out))
        return results

# ==============================================================================
# SCRIPT ENTRY POINT
# ==============================================================================
if __name__ == "__main__":
    
    # Mocking a script file for the custom language
    test_script = [
        'radius = 5',
        'pi = 3.14159',
        'area = pi * (radius ** 2)',
        'print("The area of the circle is:", area)',
        'x = 45',
        'y = 2 * sin(x) + 1.5e2',
        'print("Trig and Scientific Notation Test:", y)'
    ]

    print("=" * 60)
    print(" CUSTOM MINI-LANGUAGE INTERPRETER ")
    print("=" * 60)
    
    interp = RecursiveDescentInterpreter()
    results = interp.interpret_program(test_script)

    print("\n[Execution Output]")
    for ok, out in results:
        if ok and out is not None:
            print(f"> {out}")
        elif not ok:
            print(f"[!] Compilation Error: {out}")