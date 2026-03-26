"""
code_parser.py
Parses Python source using ast. Returns parse tree, errors, and metrics.
"""

import ast
from ai_code_reviewer.code_visitor import CodeVisitor


def parse_code(code: str) -> dict:
    result = {
        "success": False,
        "tree": None,
        "syntax_errors": [],
        "context": {"variables": [], "functions": [], "imports": []},
    }

    if not code or not code.strip():
        result["syntax_errors"].append("No code provided.")
        return result

    try:
        tree = ast.parse(code)
        result["success"] = True
        result["tree"] = tree
        visitor = CodeVisitor()
        visitor.visit(tree)
        result["context"] = visitor.get_context()
    except SyntaxError as e:
        result["syntax_errors"].append(f"SyntaxError at line {e.lineno}: {e.msg}")
    except Exception as e:
        result["syntax_errors"].append(f"Parse error: {str(e)}")

    return result


def get_code_metrics(code: str) -> dict:
    lines = code.splitlines()
    total = len(lines)
    blank = sum(1 for l in lines if not l.strip())
    comments = sum(1 for l in lines if l.strip().startswith("#"))
    code_lines = total - blank - comments

    parse_result = parse_code(code)
    func_count = 0
    class_count = 0

    if parse_result["success"] and parse_result["tree"]:
        for node in ast.walk(parse_result["tree"]):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                func_count += 1
            elif isinstance(node, ast.ClassDef):
                class_count += 1

    return {
        "total_lines": total,
        "code_lines": code_lines,
        "blank_lines": blank,
        "comment_lines": comments,
        "function_count": func_count,
        "class_count": class_count,
    }
