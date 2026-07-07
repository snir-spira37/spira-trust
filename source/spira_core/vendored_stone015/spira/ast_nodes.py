from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

@dataclass
class Node:
    line: int


@dataclass
class Import(Node):
    module_name: str


@dataclass
class Command(Node):
    name: str
    args: List[str]


@dataclass
class Let(Node):
    var: str
    type_name: str
    expr: str


@dataclass
class If(Node):
    condition: str
    body: List["Node"] = field(default_factory=list)
    else_body: List["Node"] = field(default_factory=list)


@dataclass
class While(Node):
    condition: str
    body: List["Node"] = field(default_factory=list)


@dataclass
class For(Node):
    var: str
    type_name: str
    iterable_expr: str
    body: List["Node"] = field(default_factory=list)


@dataclass
class Param:
    name: str
    type_name: str = "any"


@dataclass
class FuncDef(Node):
    name: str
    params: List[Param]
    body: List["Node"] = field(default_factory=list)


@dataclass
class Return(Node):
    expr: Optional[str] = None


def ast_to_dict(nodes: List[Node]) -> List[Dict[str, Any]]:
    out: List[Dict[str, Any]] = []
    for n in nodes:
        if isinstance(n, Import):
            out.append({"type": "Import", "line": n.line, "module_name": n.module_name})
        elif isinstance(n, Command):
            out.append({"type": "Command", "line": n.line, "name": n.name, "args": n.args})
        elif isinstance(n, Let):
            out.append({"type": "Let", "line": n.line, "var": n.var, "type_name": n.type_name, "expr": n.expr})
        elif isinstance(n, If):
            out.append({"type": "If", "line": n.line, "condition": n.condition, "body": ast_to_dict(n.body), "else_body": ast_to_dict(n.else_body)})
        elif isinstance(n, While):
            out.append({"type": "While", "line": n.line, "condition": n.condition, "body": ast_to_dict(n.body)})
        elif isinstance(n, For):
            out.append({"type": "For", "line": n.line, "var": n.var, "type_name": n.type_name, "iterable_expr": n.iterable_expr, "body": ast_to_dict(n.body)})
        elif isinstance(n, FuncDef):
            out.append({
                "type": "FuncDef",
                "line": n.line,
                "name": n.name,
                "params": [{"name": p.name, "type_name": p.type_name} for p in n.params],
                "body": ast_to_dict(n.body),
            })
        elif isinstance(n, Return):
            out.append({"type": "Return", "line": n.line, "expr": n.expr})
        else:
            out.append({"type": type(n).__name__, "line": getattr(n, "line", -1)})
    return out


