from __future__ import annotations
import shlex
from typing import List, Tuple
from .ontology import canonical_name
from .ast_nodes import Node, Import, Command, Let, If, While, For, Param, FuncDef, Return
from .typesystem import normalize_type_name

def strip_inline_comment(raw: str) -> str:
    in_single = False
    in_double = False
    escaped = False
    out_chars: List[str] = []
    for ch in raw:
        if escaped:
            out_chars.append(ch)
            escaped = False
            continue
        if ch == "\\":
            out_chars.append(ch)
            escaped = True
            continue
        if ch == "'" and not in_double:
            in_single = not in_single
            out_chars.append(ch)
            continue
        if ch == '"' and not in_single:
            in_double = not in_double
            out_chars.append(ch)
            continue
        if ch == "#" and not in_single and not in_double:
            break
        out_chars.append(ch)
    return "".join(out_chars)


def parse_typed_name(text: str) -> Tuple[str, str]:
    text = text.strip()
    if ":" in text:
        left, right = text.split(":", 1)
        return left.strip(), normalize_type_name(right.strip())
    return text, "any"


def parse_script(script: str) -> List[Node]:
    lines = script.splitlines()
    nodes, _ = _parse_block(lines, 0, 0)
    return nodes


def _next_significant_index(lines: List[str], start: int) -> int:
    i = start
    while i < len(lines):
        raw = strip_inline_comment(lines[i])
        if raw.strip():
            return i
        i += 1
    return i


def _parse_block(lines: List[str], start: int, indent: int) -> Tuple[List[Node], int]:
    nodes: List[Node] = []
    i = start

    while i < len(lines):
        raw = strip_inline_comment(lines[i])
        if not raw.strip():
            i += 1
            continue

        current_indent = len(raw) - len(raw.lstrip(" "))
        if current_indent < indent:
            break
        if current_indent > indent:
            raise SyntaxError(f"Unexpected indentation at line {i + 1}: {lines[i]!r}")

        line = raw.strip()

        if line.startswith("import "):
            nodes.append(Import(line=i + 1, module_name=line[7:].strip()))
            i += 1
            continue

        if line.startswith("let ") and "=" in line:
            left, right = line[4:].split("=", 1)
            var_name, type_name = parse_typed_name(left.strip())
            nodes.append(Let(line=i + 1, var=var_name, type_name=type_name, expr=right.strip()))
            i += 1
            continue

        if line.startswith("if ") and line.endswith(":"):
            cond = line[3:-1].strip()
            body, next_i = _parse_block(lines, i + 1, indent + 4)
            else_body: List[Node] = []
            j = _next_significant_index(lines, next_i)
            if j < len(lines):
                nxt = strip_inline_comment(lines[j])
                next_indent = len(nxt) - len(nxt.lstrip(" "))
                if next_indent == indent and nxt.strip() == "else:":
                    else_body, next_i = _parse_block(lines, j + 1, indent + 4)
            nodes.append(If(line=i + 1, condition=cond, body=body, else_body=else_body))
            i = next_i
            continue

        if line.startswith("while ") and line.endswith(":"):
            cond = line[6:-1].strip()
            body, next_i = _parse_block(lines, i + 1, indent + 4)
            nodes.append(While(line=i + 1, condition=cond, body=body))
            i = next_i
            continue

        if line.startswith("for ") and " in " in line and line.endswith(":"):
            head = line[4:-1].strip()
            left, expr = head.split(" in ", 1)
            var_name, type_name = parse_typed_name(left.strip())
            body, next_i = _parse_block(lines, i + 1, indent + 4)
            nodes.append(For(line=i + 1, var=var_name, type_name=type_name, iterable_expr=expr.strip(), body=body))
            i = next_i
            continue

        if line.startswith("func ") and line.endswith(":"):
            head = line[5:-1].strip()
            parts = shlex.split(head)
            if not parts:
                raise SyntaxError(f"Invalid func definition at line {i + 1}")
            fname = canonical_name(parts[0])
            params = [Param(*parse_typed_name(p)) for p in parts[1:]]
            body, next_i = _parse_block(lines, i + 1, indent + 4)
            nodes.append(FuncDef(line=i + 1, name=fname, params=params, body=body))
            i = next_i
            continue

        if line.startswith("return"):
            expr = line[6:].strip()
            nodes.append(Return(line=i + 1, expr=expr or None))
            i += 1
            continue

        parts = shlex.split(line)
        if parts:
            nodes.append(Command(line=i + 1, name=canonical_name(parts[0]), args=parts[1:]))
        i += 1

    return nodes, i


