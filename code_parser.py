# Import required libraries
import ast
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Access the GROQ API key
api_key = os.getenv("GROQ_API_KEY")

print("Environment Loaded Successfully!")
print("API Key Found:", bool(api_key))

print("Paste your Python code below (Press ENTER twice to finish):")

lines = []
while True:
    line = input()
    if line == "":
        break
    lines.append(line)

user_code = "\n".join(lines)


print("\nOriginal Code:\n")
print(user_code)

# -----------------------------
# Analyze code using AST NodeVisitor
# -----------------------------
class CodeAnalyzer(ast.NodeVisitor):
    def __init__(self):
        self.functions = 0
        self.loops = 0
        self.conditions = 0

    def visit_FunctionDef(self, node):
        self.functions += 1
        self.generic_visit(node)

    def visit_For(self, node):
        self.loops += 1
        self.generic_visit(node)

    def visit_While(self, node):
        self.loops += 1
        self.generic_visit(node)

    def visit_If(self, node):
        self.conditions += 1
        self.generic_visit(node)

# Parse code using AST
tree = ast.parse(user_code)

# Run analysis on the parsed tree
analyzer = CodeAnalyzer()
analyzer.visit(tree)

print("\nCode Analysis:")
print("Functions:", analyzer.functions)
print("Loops:", analyzer.loops)
print("Conditions:", analyzer.conditions)

print("\nAST Representation:\n")
print(ast.dump(tree, indent=4))

# Convert AST back to formatted code
formatted_code = ast.unparse(tree)

print("\nFormatted Code:\n")
print(formatted_code)
