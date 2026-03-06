import ast

def detect_errors(code):
    """
    Detect syntax errors in the provided Python code.
    Returns error message if found, otherwise returns None.
    """
    try:
        ast.parse(code)
        return None
    except SyntaxError as e:
        return f"Syntax Error: {e}"

if __name__ == "__main__":
    
    print("Paste your Python code below (Press ENTER twice to finish):")

    lines = []
    while True:
        line = input()
        if line == "":
            break
        lines.append(line)

    user_code = "\n".join(lines)

    error = detect_errors(user_code)

    if error:
        print("\n❌ Error detected in code:")
        print(error)
    else:
        print("\n✅ No syntax errors found.")