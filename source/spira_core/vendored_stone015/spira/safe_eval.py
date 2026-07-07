from __future__ import annotations
import ast
import math
from typing import Any, Dict, Optional

_ALLOWED_AST = (
    ast.Expression,
    ast.BinOp,
    ast.UnaryOp,
    ast.Constant,
    ast.Name,
    ast.Load,
    ast.Add,
    ast.Sub,
    ast.Mult,
    ast.Div,
    ast.Mod,
    ast.Pow,
    ast.USub,
    ast.UAdd,
    ast.Compare,
    ast.Eq,
    ast.NotEq,
    ast.Gt,
    ast.GtE,
    ast.Lt,
    ast.LtE,
    ast.In,
    ast.NotIn,
    ast.BoolOp,
    ast.And,
    ast.Or,
    ast.Not,
    ast.Call,
    ast.keyword,
    ast.List,
    ast.Tuple,
    ast.Dict,
    ast.Subscript,
    ast.Slice,
)

SAFE_FUNCS = {
    "min": min,
    "max": max,
    "abs": abs,
    "round": round,
    "int": int,
    "float": float,
    "str": str,
    "len": len,
    "sqrt": math.sqrt,
    "sum": sum,
}


class ExpressionEvaluationError(Exception):
    """Raised when the expression evaluator cannot safely handle an AST node."""


class ExpressionSyntaxValidator(ast.NodeVisitor):
    """Static validator for the subset of expressions supported by ExpressionEvaluator."""

    _ALLOWED_BINOPS = (ast.Add, ast.Sub, ast.Mult, ast.Div, ast.Mod, ast.Pow)
    _ALLOWED_UNARY = (ast.UAdd, ast.USub, ast.Not)
    _ALLOWED_BOOLOPS = (ast.And, ast.Or)
    _ALLOWED_CMPOPS = (ast.Eq, ast.NotEq, ast.Gt, ast.GtE, ast.Lt, ast.LtE, ast.In, ast.NotIn, ast.Is, ast.IsNot)

    def generic_visit(self, node: ast.AST) -> None:
        supported = (
            ast.Expression, ast.Constant, ast.Name, ast.List, ast.Tuple, ast.Dict, ast.Set,
            ast.UnaryOp, ast.BinOp, ast.BoolOp, ast.IfExp, ast.Compare, ast.Call,
            ast.Subscript, ast.Attribute, ast.Slice, ast.Load
        )
        if not isinstance(node, supported):
            raise ExpressionEvaluationError(f"Interpreter does not support node: {type(node).__name__}")
        super().generic_visit(node)

    def visit_Call(self, node: ast.Call) -> None:
        if not isinstance(node.func, ast.Name):
            raise ExpressionEvaluationError("Only direct safe function calls are allowed")
        if node.func.id not in SAFE_FUNCS:
            raise ExpressionEvaluationError(f"Unsafe function call: {node.func.id}")
        for arg in node.args:
            self.visit(arg)
        for kw in node.keywords:
            self.visit(kw.value)

    def visit_Attribute(self, node: ast.Attribute) -> None:
        if node.attr.startswith('__'):
            raise ExpressionEvaluationError("Dunder attribute access is not allowed")
        self.visit(node.value)

    def visit_BinOp(self, node: ast.BinOp) -> None:
        if not isinstance(node.op, self._ALLOWED_BINOPS):
            raise ExpressionEvaluationError(f"Unsupported binary operator: {type(node.op).__name__}")
        self.visit(node.left)
        self.visit(node.right)

    def visit_UnaryOp(self, node: ast.UnaryOp) -> None:
        if not isinstance(node.op, self._ALLOWED_UNARY):
            raise ExpressionEvaluationError(f"Unsupported unary operator: {type(node.op).__name__}")
        self.visit(node.operand)

    def visit_BoolOp(self, node: ast.BoolOp) -> None:
        if not isinstance(node.op, self._ALLOWED_BOOLOPS):
            raise ExpressionEvaluationError(f"Unsupported bool operator: {type(node.op).__name__}")
        for value in node.values:
            self.visit(value)

    def visit_Compare(self, node: ast.Compare) -> None:
        for op in node.ops:
            if not isinstance(op, self._ALLOWED_CMPOPS):
                raise ExpressionEvaluationError(f"Unsupported comparison operator: {type(op).__name__}")
        self.visit(node.left)
        for c in node.comparators:
            self.visit(c)


def validate_interpreter_expression(expr: str) -> Optional[str]:
    try:
        tree = ast.parse(expr, mode='eval')
    except Exception as exc:
        return f"invalid syntax: {exc}"
    try:
        ExpressionSyntaxValidator().visit(tree)
    except ExpressionEvaluationError as exc:
        return str(exc)
    return None


class ExpressionEvaluator:
    """A small safe interpreter for a subset of Python expressions used by Spira.

    This evaluator supports literals, names, arithmetic, comparisons, boolean ops,
    direct calls to approved safe functions, and indexing/slicing. It is intended
    to reduce reliance on eval while preserving backward compatibility.
    """

    def __init__(self, env: Dict[str, Any]):
        self.env = env

    def evaluate(self, expr: str) -> Any:
        tree = ast.parse(expr, mode="eval")
        return self.visit(tree.body)

    def visit(self, node: ast.AST) -> Any:
        method = getattr(self, f"visit_{type(node).__name__}", None)
        if method is None:
            raise ExpressionEvaluationError(f"Unsupported expression node: {type(node).__name__}")
        return method(node)

    def visit_Constant(self, node: ast.Constant) -> Any:
        return node.value

    def visit_Name(self, node: ast.Name) -> Any:
        if node.id in self.env:
            return self.env[node.id]
        raise ExpressionEvaluationError(f"Unknown name: {node.id}")

    def visit_List(self, node: ast.List) -> Any:
        return [self.visit(x) for x in node.elts]

    def visit_Tuple(self, node: ast.Tuple) -> Any:
        return tuple(self.visit(x) for x in node.elts)

    def visit_Dict(self, node: ast.Dict) -> Any:
        return {self.visit(k): self.visit(v) for k, v in zip(node.keys, node.values)}

    def visit_Set(self, node: ast.Set) -> Any:
        return {self.visit(x) for x in node.elts}

    def visit_UnaryOp(self, node: ast.UnaryOp) -> Any:
        operand = self.visit(node.operand)
        if isinstance(node.op, ast.UAdd):
            return +operand
        if isinstance(node.op, ast.USub):
            return -operand
        if isinstance(node.op, ast.Not):
            return not operand
        raise ExpressionEvaluationError(f"Unsupported unary operator: {type(node.op).__name__}")

    def visit_BinOp(self, node: ast.BinOp) -> Any:
        left = self.visit(node.left)
        right = self.visit(node.right)
        op = node.op
        if isinstance(op, ast.Add):
            return left + right
        if isinstance(op, ast.Sub):
            return left - right
        if isinstance(op, ast.Mult):
            return left * right
        if isinstance(op, ast.Div):
            return left / right
        if isinstance(op, ast.Mod):
            return left % right
        if isinstance(op, ast.Pow):
            return left ** right
        raise ExpressionEvaluationError(f"Unsupported binary operator: {type(op).__name__}")

    def visit_BoolOp(self, node: ast.BoolOp) -> Any:
        if isinstance(node.op, ast.And):
            result = True
            for v in node.values:
                result = self.visit(v)
                if not result:
                    return result
            return result
        if isinstance(node.op, ast.Or):
            last = False
            for v in node.values:
                last = self.visit(v)
                if last:
                    return last
            return last
        raise ExpressionEvaluationError(f"Unsupported bool operator: {type(node.op).__name__}")

    def visit_IfExp(self, node: ast.IfExp) -> Any:
        return self.visit(node.body) if bool(self.visit(node.test)) else self.visit(node.orelse)

    def visit_Compare(self, node: ast.Compare) -> Any:
        current = self.visit(node.left)
        for op, comparator in zip(node.ops, node.comparators):
            right = self.visit(comparator)
            if isinstance(op, ast.Eq):
                ok = current == right
            elif isinstance(op, ast.NotEq):
                ok = current != right
            elif isinstance(op, ast.Gt):
                ok = current > right
            elif isinstance(op, ast.GtE):
                ok = current >= right
            elif isinstance(op, ast.Lt):
                ok = current < right
            elif isinstance(op, ast.LtE):
                ok = current <= right
            elif isinstance(op, ast.In):
                ok = current in right
            elif isinstance(op, ast.NotIn):
                ok = current not in right
            elif isinstance(op, ast.Is):
                ok = current is right
            elif isinstance(op, ast.IsNot):
                ok = current is not right
            else:
                raise ExpressionEvaluationError(f"Unsupported comparison operator: {type(op).__name__}")
            if not ok:
                return False
            current = right
        return True

    def visit_Call(self, node: ast.Call) -> Any:
        if not isinstance(node.func, ast.Name):
            raise ExpressionEvaluationError("Only direct safe function calls are allowed")
        fn_name = node.func.id
        if fn_name not in SAFE_FUNCS:
            raise ExpressionEvaluationError(f"Unsafe function call: {fn_name}")
        fn = SAFE_FUNCS[fn_name]
        args = [self.visit(arg) for arg in node.args]
        kwargs = {kw.arg: self.visit(kw.value) for kw in node.keywords}
        return fn(*args, **kwargs)

    def visit_Subscript(self, node: ast.Subscript) -> Any:
        value = self.visit(node.value)
        index = self.visit(node.slice)
        return value[index]

    def visit_Attribute(self, node: ast.Attribute) -> Any:
        value = self.visit(node.value)
        if isinstance(value, dict):
            if node.attr in value:
                return value[node.attr]
            raise ExpressionEvaluationError(f"Unknown dict attribute: {node.attr}")
        if node.attr.startswith("__"):
            raise ExpressionEvaluationError("Dunder attribute access is not allowed")
        if hasattr(value, node.attr):
            return getattr(value, node.attr)
        raise ExpressionEvaluationError(f"Unknown attribute: {node.attr}")

    def visit_Slice(self, node: ast.Slice) -> slice:
        lower = self.visit(node.lower) if node.lower is not None else None
        upper = self.visit(node.upper) if node.upper is not None else None
        step = self.visit(node.step) if node.step is not None else None
        return slice(lower, upper, step)


def validate_safe_expr(tree: ast.AST) -> None:
    for node in ast.walk(tree):
        if not isinstance(node, _ALLOWED_AST):
            raise ValueError(f"Unsupported expression node: {type(node).__name__}")
        if isinstance(node, ast.Call):
            if not isinstance(node.func, ast.Name):
                raise ValueError("Only direct safe function calls are allowed")
            if node.func.id not in SAFE_FUNCS:
                raise ValueError(f"Unsafe function call: {node.func.id}")


def safe_eval(expr: str, env: Dict[str, Any]) -> Any:
    tree = ast.parse(expr, mode="eval")
    validate_safe_expr(tree)
    return eval(compile(tree, "<spira-expr>", "eval"), {"__builtins__": {}}, {**SAFE_FUNCS, **env})


