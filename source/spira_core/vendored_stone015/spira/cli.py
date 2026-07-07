from __future__ import annotations

import argparse
import json
import sys

from .demo import DEMO_SCRIPT, LONG_TEST_SCRIPT, repl, run_internal_tests, run_script
from .ontology import ONTOLOGY
from .validation import print_command_help, validate_script
from .orchestrator import OrchestratorConfig, run_rollout_stress_test

CLI_DESCRIPTION = "Spira Production Final CLI"


def main() -> None:
    ap = argparse.ArgumentParser(description=CLI_DESCRIPTION)
    ap.add_argument("--demo", action="store_true")
    ap.add_argument("--long-demo", action="store_true")
    ap.add_argument("--orchestrator-demo", action="store_true", help="Run a short rollout orchestrator simulation")
    ap.add_argument("--orchestrator-100", action="store_true", help="Run a 100-step rollout orchestrator stress test")
    ap.add_argument("--count", action="store_true")
    ap.add_argument("--list", action="store_true")
    ap.add_argument("--file", type=str)
    ap.add_argument("--code", type=str, help="Execute Spira code passed directly on the command line")
    ap.add_argument("--stdin", action="store_true", help="Read Spira code from standard input")
    ap.add_argument("--repl", action="store_true", help="Start interactive REPL")
    ap.add_argument("--test", action="store_true", help="Run internal self-tests")
    ap.add_argument("--validate", action="store_true", help="Validate script syntax without executing")
    ap.add_argument("--help-commands", action="store_true", help="Show built-in command reference")
    ap.add_argument("--export-ir", type=str)
    ap.add_argument("--db", type=str, default="spira_memory.db")
    ap.add_argument("--quiet", action="store_true")
    ap.add_argument("--trace", action="store_true")
    ap.add_argument("--continue-on-error", action="store_true")
    ap.add_argument("--max-errors", type=int, default=25)
    ap.add_argument("--auto-checkpoint", type=str, default=None)
    ap.add_argument("--profile", action="store_true")
    ap.add_argument("--max-loop-iters", type=int, default=None, help="maximum iterations allowed in while loops before error")
    ap.add_argument("--max-logs", type=int, default=None, help="maximum number of log rows kept in the logs table")
    args = ap.parse_args()

    if args.help_commands:
        print_command_help()
        return

    if args.count:
        print(len(ONTOLOGY))
        return

    if args.list:
        for name in sorted(ONTOLOGY):
            c = ONTOLOGY[name]
            print(f"{c.name:18} | {c.hebrew:12} | {c.domain:10} | aliases={','.join(c.aliases)}")
        return

    if args.test:
        raise SystemExit(run_internal_tests())

    if args.validate:
        if args.file:
            with open(args.file, "r", encoding="utf-8") as f:
                script = f.read()
        elif args.code is not None:
            script = args.code
        elif args.stdin:
            script = sys.stdin.read()
        else:
            print("--validate requires --file, --code, or --stdin", file=sys.stderr)
            raise SystemExit(1)
        ok, _ = validate_script(script, quiet=args.quiet)
        raise SystemExit(0 if ok else 1)

    if args.repl:
        raise SystemExit(repl(args))

    if args.orchestrator_demo or args.orchestrator_100:
        steps = 25 if args.orchestrator_demo else 100
        orch_cfg = None if args.db == "spira_memory.db" else OrchestratorConfig(db_path=args.db)
        summary = run_rollout_stress_test(steps=steps, session_id=f"cli_orchestrator_{steps}", config=orch_cfg)
        print(json.dumps(summary["final_state"], ensure_ascii=False, indent=2))
        print(json.dumps(summary["decision_counts"], ensure_ascii=False, indent=2))
        return

    script_sources = sum(bool(x) for x in (args.demo, args.long_demo, args.file, args.code, args.stdin))
    if script_sources > 1:
        raise SystemExit("choose only one of: --demo, --long-demo, --file, --code, --stdin")

    script = None
    if args.demo:
        script = DEMO_SCRIPT
    elif args.long_demo:
        script = LONG_TEST_SCRIPT
    elif args.file:
        with open(args.file, "r", encoding="utf-8") as f:
            script = f.read()
    elif args.code is not None:
        script = args.code
    elif args.stdin:
        script = sys.stdin.read()

    if script is None:
        ap.print_help()
        return

    try:
        report = run_script(
            script,
            db_path=args.db,
            quiet=args.quiet,
            trace=args.trace,
            continue_on_error=args.continue_on_error,
            auto_checkpoint_label=args.auto_checkpoint,
            profile=args.profile,
            export_ir=args.export_ir,
            max_loop_iters=args.max_loop_iters,
            max_logs=args.max_logs,
        )
    except Exception as e:
        print(f"FATAL: {e}", file=sys.stderr)
        raise SystemExit(1)

    if not args.quiet:
        print(
            json.dumps(
                {
                    "ok": report.ok,
                    "nodes_executed": report.nodes_executed,
                    "errors": report.errors,
                    "elapsed_ms": round(report.elapsed_ms, 3),
                },
                ensure_ascii=False,
                indent=2,
            )
        )

    if report.errors and not args.continue_on_error:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
