"""
error_detector.py
Static analysis: unused imports, missing docstrings, dangerous patterns, etc.
"""

import ast
from typing import List, Dict


def detect_errors(code: str, tree: ast.AST) -> List[Dict]:
    issues = []
    issues.extend(_check_unused_imports(tree))
    issues.extend(_check_missing_docstrings(tree))
    issues.extend(_check_long_functions(tree, code))
    issues.extend(_check_dangerous_patterns(tree))
    issues.extend(_check_bare_except(tree))
    issues.extend(_check_mutable_defaults(tree))
    return sorted(issues, key=lambda x: x["line"])


def _check_unused_imports(tree):
    issues = []
    imported_names = {}
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                name = alias.asname if alias.asname else alias.name.split(".")[0]
                imported_names[name] = node.lineno
        elif isinstance(node, ast.ImportFrom):
            for alias in node.names:
                if alias.name == "*":
                    continue
                name = alias.asname if alias.asname else alias.name
                imported_names[name] = node.lineno

    used_names = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Name) and not isinstance(node.ctx, ast.Store):
            used_names.add(node.id)
        elif isinstance(node, ast.Attribute):
            if isinstance(node.value, ast.Name):
                used_names.add(node.value.id)

    for name, lineno in imported_names.items():
        if name not in used_names:
            issues.append({"severity": "warning", "line": lineno, "message": f"Unused import: '{name}'"})
    return issues


def _check_missing_docstrings(tree):
    issues = []
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            if node.name.startswith("_"):
                continue
            has_doc = (
                node.body
                and isinstance(node.body[0], ast.Expr)
                and isinstance(node.body[0].value, ast.Constant)
                and isinstance(node.body[0].value.value, str)
            )
            kind = "Function" if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) else "Class"
            if not has_doc:
                issues.append({"severity": "info", "line": node.lineno, "message": f"{kind} '{node.name}' is missing a docstring."})
    return issues


def _check_long_functions(tree, code):
    issues = []
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            start = node.lineno
            end = getattr(node, "end_lineno", start)
            length = end - start + 1
            if length > 50:
                issues.append({"severity": "warning", "line": start, "message": f"Function '{node.name}' is {length} lines long (consider splitting)."})
    return issues


def _check_dangerous_patterns(tree):
    issues = []
    dangerous = {"eval", "exec", "__import__"}
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name) and node.func.id in dangerous:
                issues.append({"severity": "error", "line": node.lineno, "message": f"Dangerous call: '{node.func.id}()' — security risk."})
    return issues


def _check_bare_except(tree):
    issues = []
    for node in ast.walk(tree):
        if isinstance(node, ast.ExceptHandler) and node.type is None:
            issues.append({"severity": "warning", "line": node.lineno, "message": "Bare `except:` — catch specific exceptions instead."})
    return issues


def _check_mutable_defaults(tree):
    issues = []
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            for default in node.args.defaults:
                if isinstance(default, (ast.List, ast.Dict, ast.Set)):
                    issues.append({"severity": "warning", "line": node.lineno, "message": f"'{node.name}' uses a mutable default argument (use None)."})
    return issues


def summarize_issues(issues: List[Dict]) -> Dict:
    counts = {"error": 0, "warning": 0, "info": 0}
    for issue in issues:
        counts[issue["severity"]] += 1
    return counts
