"""
code_visitor.py
AST NodeVisitor that tracks variable assignments, function definitions,
and import statements.
"""

import ast


class CodeVisitor(ast.NodeVisitor):
    def __init__(self):
        self.variables = set()
        self.functions = set()
        self.imports = set()

    def visit_Assign(self, node):
        for target in node.targets:
            if isinstance(target, ast.Name):
                self.variables.add(target.id)
        self.generic_visit(node)

    def visit_AugAssign(self, node):
        if isinstance(node.target, ast.Name):
            self.variables.add(node.target.id)
        self.generic_visit(node)

    def visit_AnnAssign(self, node):
        if isinstance(node.target, ast.Name):
            self.variables.add(node.target.id)
        self.generic_visit(node)

    def visit_FunctionDef(self, node):
        self.functions.add(node.name)
        for arg in node.args.args:
            self.variables.add(arg.arg)
        self.generic_visit(node)

    def visit_AsyncFunctionDef(self, node):
        self.visit_FunctionDef(node)

    def visit_Import(self, node):
        for alias in node.names:
            name = alias.asname if alias.asname else alias.name
            self.imports.add(name.split(".")[0])
        self.generic_visit(node)

    def visit_ImportFrom(self, node):
        for alias in node.names:
            name = alias.asname if alias.asname else alias.name
            self.imports.add(name)
        self.generic_visit(node)

    def get_context(self) -> dict:
        return {
            "variables": sorted(self.variables),
            "functions": sorted(self.functions),
            "imports": sorted(self.imports),
        }
