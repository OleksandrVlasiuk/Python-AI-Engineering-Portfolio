# ==============================================================================
# ALGORITHMIC TEST SUITE & QUALITY ASSURANCE RUNNER
# A comprehensive testing framework executing core algorithmic tasks, 
# handling graceful file I/O operations (with in-memory fallbacks), 
# and generating structured test execution reports.
# ==============================================================================

import os

# ==============================================================================
# PHASE 1: CORE ALGORITHMIC LOGIC
# ==============================================================================

def task1_sequence_analysis(data):
    """Counts positive/negative numbers and calculates the average of negatives."""
    positives = negatives = negative_sum = 0
    
    for num in data:
        if num == 0:
            break
        if num > 0:
            positives += 1
        elif num < 0:
            negatives += 1
            negative_sum += num
            
    negative_avg = negative_sum / negatives if negatives else 0
    
    return [
        f"Positive count: {positives}",
        f"Negative count: {negatives}",
        f"Average of negatives: {negative_avg:.2f}"
    ]

def task2_triangle_validation(data_lines):
    """Validates triangle inequality theorem and classifies triangle types."""
    results = []
    for line in data_lines:
        try:
            a, b, c = map(float, line.split())
            if a <= 0 or b <= 0 or c <= 0:
                result = f"[{a}, {b}, {c}] -> REJECTED: Invalid dimensions (must be > 0)"
            elif a >= b + c or b >= a + c or c >= a + b:
                result = f"[{a}, {b}, {c}] -> REJECTED: Violates triangle inequality"
            elif a == b == c:
                result = f"[{a}, {b}, {c}] -> ACCEPTED: Equilateral"
            elif a == b or b == c or a == c:
                result = f"[{a}, {b}, {c}] -> ACCEPTED: Isosceles"
            else:
                result = f"[{a}, {b}, {c}] -> ACCEPTED: Scalene"
        except ValueError:
            result = f"[{line.strip()}] -> ERROR: Invalid payload format"
        results.append(result)
    return results

def task3_sentence_tokenization(sentence):
    """Tokenizes a string payload into a list of constituent words."""
    words = sentence.strip().split()
    return words

def task4_max_subrectangle(matrix):
    """Finds the contiguous sub-rectangle with the maximum sum (2D Kadane's Algorithm)."""
    n = len(matrix)
    max_sum = float('-inf')
    best_bounds = (0, 0, 0, 0) # top, left, bottom, right

    for top in range(n):
        temp = [0] * n
        for bottom in range(top, n):
            for i in range(n):
                temp[i] += matrix[bottom][i]

            # 1D Kadane's Algorithm on the collapsed temporary array
            current_sum = float('-inf')
            current_left = current_right = 0
            sum_here = 0
            
            for i in range(n):
                sum_here += temp[i]
                if sum_here > current_sum:
                    current_sum = sum_here
                    current_left = current_right
                    current_right = i
                if sum_here < 0:
                    sum_here = 0
                    current_left = i + 1

            # Update global max bounds
            if current_sum > max_sum:
                max_sum = current_sum
                best_bounds = (top, current_left, bottom, current_right)

    return [
        f"Maximum Subrectangle Sum: {max_sum}",
        f"Matrix Coordinates (Top, Left) to (Bottom, Right): {best_bounds}"
    ]

# ==============================================================================
# PHASE 2: TEST RUNNER & MOCK DATA MANAGEMENT
# ==============================================================================

# In-memory fallbacks ensure the portfolio script runs even without external .txt files
MOCK_DATA = {
    1: ["3 8 -4 4 -2 9 3 -5 7 -2 4 7 1 2 8 0 9", "1 2 3 0", "-1 -2 -3 0"],
    2: ["3 4 5", "1 1 10", "5 5 5", "0 4 4"],
    3: ["The quick brown fox jumps over the lazy dog."],
    4: ["1 2 -1\n-4 -20 -10\n-8 9 3", "1 2\n3 4"]
}

def extract_payload(task_number, filename):
    """Attempts to read from a file; falls back to mock data if absent."""
    if os.path.exists(filename):
        with open(filename, 'r', encoding='utf-8') as f:
            return f.read().strip().split('\n')
    else:
        print(f"[WARN] {filename} not found. Utilizing internal mock payload.")
        return MOCK_DATA.get(task_number, [])

def execute_test_suite(task_number):
    """Routes execution to the correct algorithm and formats the output log."""
    result_log = []
    test_name = f"Test Suite {task_number}"
    test_type = "Functional & Destructive Integration"

    try:
        if task_number == 1:
            test_name += " - Sequence Analysis"
            lines = extract_payload(1, 'InData1_1.txt')
            for idx, line in enumerate(lines):
                data = list(map(int, line.strip().split()))
                result_log.extend([f"--- Case {idx + 1} ---", f"Input: {line}", "Output:"])
                result_log.extend(task1_sequence_analysis(data))
                
        elif task_number == 2:
            test_name += " - Triangle Validation"
            lines = extract_payload(2, 'InData2_1.txt')
            result_log.extend([f"--- All Cases ---", "Output:"])
            result_log.extend(task2_triangle_validation(lines))

        elif task_number == 3:
            test_name += " - Sentence Tokenization"
            lines = extract_payload(3, 'InData3_1.txt')
            for idx, line in enumerate(lines):
                result_log.extend([f"--- Case {idx + 1} ---", f"Input: {line}", f"Output: {task3_sentence_tokenization(line)}"])

        elif task_number == 4:
            test_name += " - 2D Kadane's Max Subrectangle"
            payloads = extract_payload(4, 'InData4_1.txt')
            # Normalize split payloads for mock vs file
            matrices = "\n".join(payloads).split('\n\n') if os.path.exists('InData4_1.txt') else payloads
            
            for idx, matrix_str in enumerate(matrices):
                matrix = [list(map(int, row.split())) for row in matrix_str.strip().split('\n')]
                result_log.extend([f"--- Case {idx + 1} ---", "Input Matrix:"])
                result_log.extend([str(row) for row in matrix])
                result_log.extend(["Output:"] + task4_max_subrectangle(matrix))

        else:
            return ["Error: Unmapped task identifier."]

    except Exception as e:
        return [f"Critical Suite Failure: {e}"]

    # Append Results to an execution log file
    log_filename = 'test_execution_report.log'
    with open(log_filename, 'a', encoding='utf-8') as f:
        f.write("=" * 60 + "\n")
        f.write(f"TEST SUITE: {test_name}\n")
        f.write(f"METHODOLOGY: {test_type}\n")
        f.write("-" * 60 + "\n")
        f.write("\n".join(result_log) + "\n\n")

    return result_log

# ==============================================================================
# CLI INTERFACE
# ==============================================================================
if __name__ == "__main__":
    print("=" * 50)
    print(" ALGORITHMIC TEST SUITE RUNNER")
    print("=" * 50)
    
    while True:
        user_input = input("\nEnter Target Task ID (1-4) or 'exit': ").strip().lower()
        if user_input == 'exit':
            print("Terminating Test Runner...")
            break
            
        if user_input.isdigit() and 1 <= int(user_input) <= 4:
            output = execute_test_suite(int(user_input))
            print("\n" + "\n".join(output))
            print("\n[+] Execution complete. Results appended to 'test_execution_report.log'")
        else:
            print("Invalid input. Please enter a numerical ID between 1 and 4.")