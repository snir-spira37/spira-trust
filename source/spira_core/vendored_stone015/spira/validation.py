from __future__ import annotations
import ast
import os
from typing import Dict, List, Optional, Tuple
from .ast_nodes import Node, Import, FuncDef, Command, If, While, For, Return, Let
from .modules import BUILTIN_MODULES
from .parser import parse_script
from .safe_eval import validate_interpreter_expression

COMMAND_HELP: Dict[str, str] = {
    "world": "create/use/set worlds for flow routing",
    "partzuf": "create/use/set partzufim (modes)",
    "vessel": "create/use/set vessels (capacity/screen)",
    "or": "add light/energy to active vessel",
    "noise": "add noise to the active runtime",
    "screen": "set active vessel screen strength",
    "tzimtzum": "contract or/noise",
    "masach": "strengthen active screen",
    "shevira": "manually mark shattering",
    "tikkun": "repair runtime state",
    "superpose": "create a named superposition",
    "entangle": "entangle two names",
    "measure": "collapse a superposition",
    "remember": "store last result or provided value",
    "recall": "load a memory value into last_result",
    "checkpoint": "save current state",
    "recover": "restore a saved state",
    "inspect": "print state/vars/memory/errors",
    "trace": "toggle tracing",
    "status": "show current runtime metrics",
}


def print_command_help() -> None:
    print("\nSPIRA COMMAND REFERENCE (production-final)\n")
    print(f"{'Command':<18} Description")
    print("-" * 54)
    for cmd, desc in sorted(COMMAND_HELP.items()):
        print(f"{cmd:<18} {desc}")


COMMAND_ARITY_RULES: Dict[str, Tuple[int, Optional[int]]] = {
    "backend": (2, 2),
    "set": (2, 2),
    "db": (2, None),
    "agent": (1, None),
    "call": (1, None),
    "export_ir": (1, 1),
    "flush": (0, 0),
    "manifest": (0, None),
    "emit": (0, None),
    "remember": (1, None),
    "recall": (1, 1),
    "superpose": (2, None),
    "entangle": (2, 2),
    "measure": (0, None),
    "pipeline": (1, None),
    "checkpoint": (1, 1),
    "recover": (1, 1),
    "inspect": (0, 1),
    "trace": (0, 1),
    "status": (0, 0),
    "kli": (1, 1),
    "or": (1, 1),
    "or_set": (1, 1),
    "noise": (1, 1),
    "noise_set": (1, 1),
    "screen": (1, 1),
    "tzimtzum": (0, 1),
    "masach": (0, 1),
    "shevira": (0, 0),
    "tikkun": (0, 0),
    "chokhmah": (0, None),
    "binah": (0, None),
    "daat": (0, None),
}


def _validate_command_arity(node: Command) -> List[str]:
    errors: List[str] = []
    pos = [a for a in node.args if "=" not in a]
    if node.name in {"world", "partzuf", "vessel"}:
        if not pos:
            return [f"{node.name} requires action (line {node.line})"]
        action = pos[0]
        if action not in {"create", "use", "set"}:
            return [f"unknown {node.name} action: {action} (line {node.line})"]
        if action in {"create", "use", "set"} and len(pos) < 2:
            return [f"{node.name} {action} requires a target name (line {node.line})"]
        return errors
    rule = COMMAND_ARITY_RULES.get(node.name)
    if rule is None:
        return errors
    min_args, max_args = rule
    if len(pos) < min_args:
        errors.append(f"{node.name} expects at least {min_args} positional arg(s) (line {node.line})")
    if max_args is not None and len(pos) > max_args:
        errors.append(f"{node.name} expects at most {max_args} positional arg(s) (line {node.line})")
    return errors


def validate_script(script: str, quiet: bool = False) -> Tuple[bool, List[str]]:
    errors: List[str] = []
    try:
        nodes = parse_script(script)
    except SyntaxError as e:
        return False, [f"Syntax error: {e}"]

    known_commands = set(COMMAND_HELP) | {
        "backend", "set", "db", "agent", "call", "pipeline", "export_ir", "flush", "manifest", "emit"
    }
    defined_funcs: set[str] = set()
    for node in nodes:
        if isinstance(node, FuncDef):
            if node.name in defined_funcs:
                errors.append(f"Duplicate function: {node.name} (line {node.line})")
            defined_funcs.add(node.name)
            param_names: set[str] = set()
            for param in node.params:
                if param.name in param_names:
                    errors.append(f"Duplicate parameter: {param.name} in function {node.name} (line {node.line})")
                param_names.add(param.name)
        elif isinstance(node, Import):
            if node.module_name not in BUILTIN_MODULES and not os.path.exists(node.module_name):
                errors.append(f"Unknown import: {node.module_name} (line {node.line})")

    def walk(items: List[Node], inside_func: bool = False) -> None:
        for node in items:
            if isinstance(node, FuncDef):
                walk(node.body, inside_func=True)
            elif isinstance(node, Let):
                try:
                    ast.parse(node.expr, mode="eval")
                except Exception as exc:
                    errors.append(f"Invalid let expression at line {node.line}: {exc}")
                else:
                    interp_err = validate_interpreter_expression(node.expr)
                    if interp_err is not None:
                        errors.append(f"Interpreter-unsupported let expression at line {node.line}: {interp_err}")
            elif isinstance(node, Return):
                if not inside_func:
                    errors.append(f"Top-level return is not allowed (line {node.line})")
                elif node.expr:
                    try:
                        ast.parse(node.expr, mode="eval")
                    except Exception as exc:
                        errors.append(f"Invalid return expression at line {node.line}: {exc}")
                    else:
                        interp_err = validate_interpreter_expression(node.expr)
                        if interp_err is not None:
                            errors.append(f"Interpreter-unsupported return expression at line {node.line}: {interp_err}")
            elif isinstance(node, Command):
                errors.extend(_validate_command_arity(node))
                if node.name == "call":
                    pos = [a for a in node.args if "=" not in a]
                    if pos and pos[0] not in defined_funcs:
                        errors.append(f"Unknown function call: {pos[0]} (line {node.line})")
                elif node.name not in known_commands and node.name not in defined_funcs:
                    errors.append(f"Unknown command: {node.name} (line {node.line})")
            elif isinstance(node, If):
                try:
                    ast.parse(node.condition, mode="eval")
                except Exception as exc:
                    errors.append(f"Invalid if condition at line {node.line}: {exc}")
                else:
                    interp_err = validate_interpreter_expression(node.condition)
                    if interp_err is not None:
                        errors.append(f"Interpreter-unsupported if condition at line {node.line}: {interp_err}")
                walk(node.body, inside_func=inside_func)
                walk(node.else_body, inside_func=inside_func)
            elif isinstance(node, While):
                try:
                    ast.parse(node.condition, mode="eval")
                except Exception as exc:
                    errors.append(f"Invalid while condition at line {node.line}: {exc}")
                else:
                    interp_err = validate_interpreter_expression(node.condition)
                    if interp_err is not None:
                        errors.append(f"Interpreter-unsupported while condition at line {node.line}: {interp_err}")
                walk(node.body, inside_func=inside_func)
            elif isinstance(node, For):
                try:
                    ast.parse(node.iterable_expr, mode="eval")
                except Exception as exc:
                    errors.append(f"Invalid for iterable expression at line {node.line}: {exc}")
                else:
                    interp_err = validate_interpreter_expression(node.iterable_expr)
                    if interp_err is not None:
                        errors.append(f"Interpreter-unsupported for iterable expression at line {node.line}: {interp_err}")
                walk(node.body, inside_func=inside_func)

    walk(nodes, inside_func=False)
    if not quiet:
        if errors:
            print(f"Validation failed: {len(errors)} error(s)")
            for err in errors:
                print(f" - {err}")
        else:
            print(f"Validation passed: {len(nodes)} top-level nodes")
    return len(errors) == 0, errors


