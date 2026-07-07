from __future__ import annotations
import argparse, json, sys
from typing import Optional, List
from .ontology import ONTOLOGY
from .parser import parse_script
from .ast_nodes import ast_to_dict
from .runtime import RuntimeConfig, ExecutionReport, SpiraRuntime
from .validation import validate_script, print_command_help

DEMO_SCRIPT = """
import std.repair
import std.agent

backend llm mock
backend quantum mock

func build_policy source:str:
    chokhmah source
    binah
    daat
    remember seed
    superpose policy chesed tiferet gevurah
    entangle policy seed
    measure policy
    return last_result

world create atzilut_plus flow=1.1
world use atzilut_plus

partzuf create abba_plus mode=analytic
partzuf use abba_plus

vessel create core capacity=1.2 screen=1.0
vessel use core

let base_or: float = 0.55
let extra_steps: list = [0.15, 0.10, 0.08]

or base_or
noise 0.1

call build_policy "sefer yetzirah"
db remember seed

if or_level > kli_capacity:
    tikkun
else:
    manifest "no overload at first pass"

for step:float in extra_steps:
    or step

call stabilize

db save_state checkpoint_alpha
recall seed
status
manifest
"""


LONG_TEST_SCRIPT = """
import std.repair
import std.agent

backend llm mock
backend quantum mock
trace on

func build_seed source:str:
    chokhmah source
    binah
    daat
    remember raw_seed
    return last_result

func choose_path source:str budget:float:
    call build_seed source
    superpose path chesed tiferet gevurah netzach hod
    entangle path raw_seed
    if budget > 1.2:
        masach strict
    else:
        masach soft
    measure path
    remember chosen_path
    return last_result

world create atzilut flow=1.05
world use atzilut

partzuf create abba mode=analytic
partzuf use abba

vessel create core capacity=1.4 screen=1.0
vessel use core

let title:str = "quantum-kabbalah synthesis"
let phases:list = [0.25, 0.19, 0.21, 0.08, 0.11, 0.14]
let budget:float = 1.35

call choose_path title budget
agent triad "stabilize the synthesis"

for step:float in phases:
    or step
    if or_level > kli_capacity:
        tikkun
    else:
        manifest "stable increment"

checkpoint long_checkpoint
inspect state
status
manifest "LONG_TEST_DONE"
"""


RECOVERY_TEST_SCRIPT = """
backend llm mock
backend quantum mock

vessel create core capacity=1.0 screen=1.0
vessel use core
or 1.5
checkpoint before_break
undefined_command boom
recover before_break
status
manifest "RECOVERY_DONE"
"""


LOOP_GUARD_TEST_SCRIPT = """
let i:int = 0
while true:
    let i:int = i + 1
"""


EXPRESSION_EVAL_TEST_SCRIPT = """
let nums:list = [1, 2, 3, 4]
let nested:dict = {"a": [10, 20, 30]}
let ok1:bool = len(nums) == 4
let ok2:bool = nums[1:3] == [2, 3]
let ok3:bool = 3 in nums
let ok4:bool = nested["a"][0] == 10
let ok5:bool = ({"x": 2}).x == 2
if ok1 and ok2 and ok3 and ok4 and ok5:
    manifest "EXPR_OK"
else:
    manifest "EXPR_BAD"
"""


STRICT_CONTROL_FLOW_TEST_SCRIPT = """
let i:int = 0
while i < 3:
    let i:int = i + 1
if i == 3:
    manifest "STRICT_OK"
else:
    manifest "STRICT_BAD"
"""


INVALID_EXPRESSION_VALIDATE_SCRIPT = """
let x:int = 1 +
"""

INTERPRETER_UNSUPPORTED_VALIDATE_SCRIPT = """
let x:any = sorted([3, 1, 2])
"""

FALLBACK_BUDGET_TEST_SCRIPT = """
let x:any = sorted([3,1,2])
manifest "BUDGET_BAD"
"""

INTERPRETER_FIRST_DEFAULT_TEST_SCRIPT = """
let i:int = 0
let total:int = 0
while i < 3:
    let i:int = i + 1
    let total:int = total + i
if total == 6:
    manifest "INTERPRETER_FIRST_OK"
else:
    manifest "INTERPRETER_FIRST_BAD"
"""


def run_script(
    script: str,
    *,
    db_path: str = "spira_memory.db",
    quiet: bool = False,
    trace: bool = False,
    continue_on_error: bool = False,
    auto_checkpoint_label: Optional[str] = None,
    profile: bool = False,
    export_ir: Optional[str] = None,
    max_loop_iters: Optional[int] = None,
    max_logs: Optional[int] = None,
) -> ExecutionReport:
    nodes = parse_script(script)
    ir = ast_to_dict(nodes)
    if export_ir:
        with open(export_ir, "w", encoding="utf-8") as f:
            json.dump(ir, f, ensure_ascii=False, indent=2)
    rt = SpiraRuntime(
        program_ir=ir,
        db_path=db_path,
        echo_logs=not quiet,
        trace=trace,
        continue_on_error=continue_on_error,
        auto_checkpoint_label=auto_checkpoint_label,
        profile=profile,
        max_loop_iters=max_loop_iters,
        max_logs=max_logs,
    )
    try:
        report = rt.execute(nodes)
        rt.flush()
        return report
    finally:
        rt.close()


def run_internal_tests() -> int:
    cases = [
        ("demo", DEMO_SCRIPT, False, None),
        ("long", LONG_TEST_SCRIPT, False, None),
        ("recovery", RECOVERY_TEST_SCRIPT, True, None),
        ("loop_guard", LOOP_GUARD_TEST_SCRIPT, True, 10),
        ("expression_eval", EXPRESSION_EVAL_TEST_SCRIPT, False, None),
        ("strict_control", STRICT_CONTROL_FLOW_TEST_SCRIPT, False, None),
        ("interpreter_first_default", INTERPRETER_FIRST_DEFAULT_TEST_SCRIPT, False, None),
    ]
    failures: List[str] = []
    for name, script, continue_on_error, max_loop_iters in cases:
        db_path = f"test_{name}.db"
        try:
            report = run_script(
                script,
                db_path=db_path,
                quiet=True,
                trace=False,
                continue_on_error=continue_on_error,
                auto_checkpoint_label=f"auto_{name}",
                max_loop_iters=max_loop_iters,
                max_logs=200,
            )
            if name in {"demo", "long", "expression_eval"} and not report.ok:
                failures.append(f"{name}: unexpected errors {report.errors}")
            if name == "strict_control":
                rt_strict = SpiraRuntime(
                    db_path=f"strict_{name}.db",
                    echo_logs=False,
                    config=RuntimeConfig(control_flow_eval_strict=True),
                )
                try:
                    strict_nodes = parse_script(STRICT_CONTROL_FLOW_TEST_SCRIPT)
                    strict_report = rt_strict.execute(strict_nodes)
                    if rt_strict.s.last_result != "STRICT_OK" or not strict_report.ok:
                        failures.append(f"strict_control: expected STRICT_OK, got {rt_strict.s.last_result}, errors={strict_report.errors}")
                finally:
                    rt_strict.close()
            if name == "expression_eval":
                rt_check = SpiraRuntime(db_path=f"check_{name}.db", echo_logs=False)
                try:
                    expr_nodes = parse_script(EXPRESSION_EVAL_TEST_SCRIPT)
                    expr_report = rt_check.execute(expr_nodes)
                    if rt_check.s.last_result != "EXPR_OK" or not expr_report.ok:
                        failures.append(f"expression_eval: expected EXPR_OK, got {rt_check.s.last_result}, errors={expr_report.errors}")
                finally:
                    rt_check.close()
            if name == "recovery" and len(report.errors) == 0:
                failures.append("recovery: expected at least one handled error")
            if name == "loop_guard" and not any("while loop guard exceeded" in err for err in report.errors):
                failures.append(f"loop_guard: expected guard error, got {report.errors}")
            if name == "strict_control" and report.ok is False:
                failures.append(f"strict_control: unexpected errors {report.errors}")
            if name == "interpreter_first_default":
                rt_default = SpiraRuntime(db_path=f"default_{name}.db", echo_logs=False)
                try:
                    nodes_default = parse_script(INTERPRETER_FIRST_DEFAULT_TEST_SCRIPT)
                    rep_default = rt_default.execute(nodes_default)
                    if rt_default.s.last_result != "INTERPRETER_FIRST_OK" or not rep_default.ok:
                        failures.append(f"interpreter_first_default: expected INTERPRETER_FIRST_OK, got {rt_default.s.last_result}, errors={rep_default.errors}")
                    stats = rt_default.expression_stats()
                    if stats["fallbacks_by_purpose"]:
                        failures.append(f"interpreter_first_default: unexpected fallbacks {stats['fallbacks_by_purpose']}")
                finally:
                    rt_default.close()
        except Exception as e:
            failures.append(f"{name}: {e}")

    validate_ok, validate_errors = validate_script(INVALID_EXPRESSION_VALIDATE_SCRIPT, quiet=True)
    if validate_ok or not any("Invalid let expression" in err for err in validate_errors):
        failures.append(f"validator: expected invalid expression error, got {validate_errors}")

    interp_ok, interp_errors = validate_script(INTERPRETER_UNSUPPORTED_VALIDATE_SCRIPT, quiet=True)
    if interp_ok or not any("Interpreter-unsupported let expression" in err for err in interp_errors):
        failures.append(f"validator: expected interpreter unsupported error, got {interp_errors}")

    try:
        rt_budget = SpiraRuntime(db_path="test_fallback_budget.db", echo_logs=False, config=RuntimeConfig(expression_fallback_budget=0, control_flow_eval_strict=False))
        try:
            rt_budget._eval_interpreted_expression = lambda expr: (_ for _ in ()).throw(ExpressionEvaluationError("forced fallback"))
            rt_budget.eval_runtime_expression("1 + 1", purpose="generic", allow_fallback=True)
            failures.append("fallback_budget: expected budget failure, got success")
        except Exception as exc:
            if "fallback budget exceeded" not in str(exc):
                failures.append(f"fallback_budget: unexpected error {exc}")
        finally:
            rt_budget.close()
    except Exception as exc:
        failures.append(f"fallback_budget: setup error {exc}")

    # bridge smoke tests
    try:
        bridge = SpiraBridge(SpiraBridgeConfig(enable_trace=False, auto_checkpoint=False))
        decision = bridge.decide({"query": "expand?"}, ["expand", "wait", "contract"])
        if decision not in {"expand", "wait", "contract"}:
            failures.append(f"bridge: unexpected decision {decision}")
        anomaly = bridge.detect_anomaly({"cpu": 0.1, "mem": 0.2})
        if "is_anomaly" not in anomaly:
            failures.append("bridge: anomaly result malformed")
        session = bridge.create_session("t1")
        if bridge.get_session(session.session_id) is None:
            failures.append("bridge: session isolation failed")
        bridge.close_session("t1")
        bridge.close()
    except Exception as e:
        failures.append(f"bridge: {e}")

    # validator smoke test
    ok, validation_errors = validate_script("world create a\n")
    if not ok or validation_errors:
        failures.append(f"validator: expected simple script to validate, got {validation_errors}")
    ok2, validation_errors2 = validate_script("return 1\n", quiet=True)
    if ok2 or not any("Top-level return" in err for err in validation_errors2):
        failures.append(f"validator: expected top-level return failure, got {validation_errors2}")
    ok3, validation_errors3 = validate_script("call missing_fn\n", quiet=True)
    if ok3 or not any("Unknown function call" in err for err in validation_errors3):
        failures.append(f"validator: expected missing call failure, got {validation_errors3}")
    ok4, validation_errors4 = validate_script("func x a:int a:int:\n    manifest\n", quiet=True)
    if ok4 or not any("Duplicate parameter" in err for err in validation_errors4):
        failures.append(f"validator: expected duplicate parameter failure, got {validation_errors4}")
    ok5, validation_errors5 = validate_script("world create\n", quiet=True)
    if ok5 or not any("requires a target name" in err or "expects at least" in err for err in validation_errors5):
        failures.append(f"validator: expected command arity failure, got {validation_errors5}")

    if failures:
        print("SELF-TEST FAILED")
        for item in failures:
            print(" -", item)
        return 1
    print("SELF-TEST OK")
    return 0


def repl(args: argparse.Namespace) -> int:
    rt = SpiraRuntime(
        db_path=args.db,
        echo_logs=not args.quiet,
        trace=args.trace,
        continue_on_error=args.continue_on_error,
        max_errors=args.max_errors,
        auto_checkpoint_label=args.auto_checkpoint,
        profile=args.profile,
        max_loop_iters=args.max_loop_iters,
        max_logs=args.max_logs,
    )
    print("SPIRA Production Final REPL | type :help for help | Ctrl-D to exit")
    buffer: List[str] = []
    try:
        while True:
            prompt = "... " if buffer else "spira> "
            try:
                line = input(prompt)
            except EOFError:
                print()
                break
            if not buffer and not line.strip():
                continue
            stripped = line.strip()
            if not buffer and stripped.startswith(":"):
                if stripped == ":help":
                    print(":run | :clear | :state | :vars | :trace on|off | :help-commands | :quit")
                    continue
                if stripped == ":quit":
                    break
                if stripped == ":clear":
                    buffer.clear()
                    print("buffer cleared")
                    continue
                if stripped == ":state":
                    rt.inspect_view("state")
                    continue
                if stripped == ":vars":
                    rt.inspect_view("vars")
                    continue
                if stripped == ":help-commands":
                    print_command_help()
                    continue
                if stripped.startswith(":trace"):
                    _, *rest = stripped.split()
                    mode = rest[0] if rest else "status"
                    if mode in {"on", "off"}:
                        rt.set_trace(mode == "on")
                    else:
                        print(f"trace={rt.config.trace}")
                    continue
                if stripped == ":run":
                    pass
                else:
                    print("unknown repl command")
                    continue
            buffer.append(line)
            if stripped == ":run":
                script = "\n".join(buffer[:-1]).strip()
                buffer.clear()
            else:
                has_block = any(x.rstrip().endswith(":") for x in buffer)
                if has_block and stripped:
                    continue
                if has_block and not stripped:
                    script = "\n".join(buffer[:-1]).strip()
                    buffer.clear()
                elif not has_block:
                    script = "\n".join(buffer).strip()
                    buffer.clear()
                else:
                    continue
            if not script:
                continue
            try:
                nodes = parse_script(script)
                rt.program_ir = ast_to_dict(nodes)
                rt.execute(nodes)
                rt.flush()
            except Exception as e:
                print(f"REPL_ERROR: {e}")
    finally:
        rt.close()
    return 0


# -----------------------------------------------------------------------------
# 11. CLI
# -----------------------------------------------------------------------------


