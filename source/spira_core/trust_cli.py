from __future__ import annotations

import argparse
import json
import sys
from importlib import metadata as importlib_metadata
from pathlib import Path
from typing import Any


PUBLIC_COMMANDS = {"trust", "graph", "status", "drift", "rebaseline", "version"}


def main(argv: list[str] | None = None) -> int:
    _configure_stdout()
    args = list(sys.argv[1:] if argv is None else argv)
    if not args or args[0] in {"-h", "--help", "help"}:
        _print_help()
        return 0
    if args[0] == "version":
        print(f"spira-trust {_version()}")
        return 0
    if args[0] not in PUBLIC_COMMANDS:
        print(f"spira-trust: unknown public command {args[0]!r}", file=sys.stderr)
        print("Run 'spira-trust --help' for public commands.", file=sys.stderr)
        return 2
    return _run_public(args)


def _run_public(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(prog="spira-trust")
    sub = parser.add_subparsers(dest="command", required=True)

    trust_cmd = sub.add_parser("trust")
    trust_cmd.add_argument("artifact_path")
    trust_cmd.add_argument("--output-dir", default="outputs/spira_trust_runs")
    trust_cmd.add_argument("--format", choices=("text", "json"), default="text")
    trust_cmd.add_argument("--no-color", action="store_true")
    trust_cmd.add_argument("--full-evidence", action="store_true")

    graph_cmd = sub.add_parser("graph")
    graph_cmd.add_argument("artifact_inputs", nargs="+")
    graph_cmd.add_argument("--output-dir", default="outputs/spira_graph_runs")
    graph_cmd.add_argument("--strict-closure", action="store_true")
    graph_cmd.add_argument("--bundle-sha256", default=None)
    graph_cmd.add_argument("--license-policy", default=None)
    graph_cmd.add_argument("--entry-point-policy", default=None)
    graph_cmd.add_argument("--target-environment", default=None)
    graph_cmd.add_argument("--lockfile", default=None)
    graph_cmd.add_argument("--policy-pack", default=None)
    graph_cmd.add_argument("--policy-sha256", default=None)
    graph_cmd.add_argument("--verify-embedded-sboms", action="store_true")
    graph_cmd.add_argument("--attestations", default=None)
    graph_cmd.add_argument("--attestation-trust-root", default=None)
    graph_cmd.add_argument("--attestation-trust-root-sha256", default=None)
    graph_cmd.add_argument("--sbom", choices=("cyclonedx-json",), default=None)
    graph_cmd.add_argument("--sbom-output", default=None)
    graph_cmd.add_argument("--evidence-pack", default=None)
    graph_cmd.add_argument("--include-local-paths", action="store_true")
    graph_cmd.add_argument("--agent-state-dir", default=None)
    graph_cmd.add_argument("--no-package-evidence", action="store_true")
    graph_cmd.add_argument("--format", choices=("text", "json"), default="text")

    status_cmd = sub.add_parser("status")
    status_cmd.add_argument("artifact_inputs", nargs="+")
    status_cmd.add_argument("--agent-state-dir", default=None)
    status_cmd.add_argument("--format", choices=("text", "json"), default="text")

    drift_cmd = sub.add_parser("drift")
    drift_cmd.add_argument("artifact_inputs", nargs="+")
    drift_cmd.add_argument("--baseline", required=True)
    drift_cmd.add_argument("--baseline-sha256", default=None)
    drift_cmd.add_argument("--output-dir", default="outputs/spira_drift_runs")
    drift_cmd.add_argument("--strict-closure", action="store_true")
    drift_cmd.add_argument("--bundle-sha256", default=None)
    drift_cmd.add_argument("--license-policy", default=None)
    drift_cmd.add_argument("--entry-point-policy", default=None)
    drift_cmd.add_argument("--target-environment", default=None)
    drift_cmd.add_argument("--lockfile", default=None)
    drift_cmd.add_argument("--policy-pack", default=None)
    drift_cmd.add_argument("--policy-sha256", default=None)
    drift_cmd.add_argument("--no-package-evidence", action="store_true")
    drift_cmd.add_argument("--format", choices=("text", "json"), default="text")

    rebaseline_cmd = sub.add_parser("rebaseline")
    rebaseline_cmd.add_argument("artifact_inputs", nargs="+")
    rebaseline_cmd.add_argument("--from-baseline", required=True)
    rebaseline_cmd.add_argument("--baseline-sha256", required=True)
    rebaseline_cmd.add_argument("--output-dir", default="outputs/spira_rebaseline_runs")
    rebaseline_cmd.add_argument("--yes", action="store_true")
    rebaseline_cmd.add_argument("--strict-closure", action="store_true")
    rebaseline_cmd.add_argument("--bundle-sha256", default=None)
    rebaseline_cmd.add_argument("--license-policy", default=None)
    rebaseline_cmd.add_argument("--entry-point-policy", default=None)
    rebaseline_cmd.add_argument("--target-environment", default=None)
    rebaseline_cmd.add_argument("--lockfile", default=None)
    rebaseline_cmd.add_argument("--policy-pack", default=None)
    rebaseline_cmd.add_argument("--policy-sha256", default=None)
    rebaseline_cmd.add_argument("--no-package-evidence", action="store_true")
    rebaseline_cmd.add_argument("--format", choices=("text", "json"), default="text")

    parsed = parser.parse_args(argv)
    if parsed.command == "trust":
        return _run_trust(parsed)
    if parsed.command == "graph":
        return _run_graph(parsed)
    if parsed.command == "status":
        return _run_status(parsed)
    if parsed.command == "drift":
        return _run_drift(parsed)
    if parsed.command == "rebaseline":
        return _run_rebaseline(parsed)
    return 2


def _run_trust(args: argparse.Namespace) -> int:
    from .trust import format_trust_summary, run_artifact_trust_cycle

    result = run_artifact_trust_cycle(args.artifact_path, args.output_dir)
    if args.format == "json":
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(
            format_trust_summary(
                result,
                color=(not args.no_color and sys.stdout.isatty()),
                full_evidence=args.full_evidence,
            )
        )
    return _trust_exit_code(result)


def _run_graph(args: argparse.Namespace) -> int:
    from .trust_graph import format_graph_summary, graph_exit_code, run_trust_graph

    try:
        result = run_trust_graph(
            args.artifact_inputs,
            args.output_dir,
            workspace_root=Path.cwd(),
            strict_closure=args.strict_closure,
            package_evidence=not args.no_package_evidence,
            bundle_sha256=args.bundle_sha256,
            license_policy_path=args.license_policy,
            entry_point_policy_path=args.entry_point_policy,
            target_environment_path=args.target_environment,
            lockfile_path=args.lockfile,
            policy_pack_path=args.policy_pack,
            policy_sha256=args.policy_sha256,
            verify_embedded_sboms=args.verify_embedded_sboms,
            attestation_path=args.attestations,
            attestation_trust_root_path=args.attestation_trust_root,
            attestation_trust_root_sha256=args.attestation_trust_root_sha256,
        )
        if args.sbom == "cyclonedx-json" and result.get("bill_of_materials_path"):
            try:
                from .cyclonedx_export import write_cyclonedx_bom

                bom = json.loads(Path(result["bill_of_materials_path"]).read_text(encoding="utf-8"))
                sbom_path = Path(args.sbom_output) if args.sbom_output else Path(args.output_dir) / "spira-trust.cdx.json"
                write_cyclonedx_bom(bom, sbom_path, include_local_paths=args.include_local_paths)
                result["cyclonedx_sbom_path"] = str(sbom_path.resolve())
                if result.get("report_path"):
                    Path(result["report_path"]).write_text(
                        json.dumps(result, ensure_ascii=False, indent=2) + "\n",
                        encoding="utf-8",
                        newline="\n",
                    )
            except OSError as error:
                result = _write_sbom_export_error(args.output_dir, str(error))
        if result.get("bill_of_materials_path") and result.get("verdict") != "SBOM_EXPORT_ERROR":
            from .decision_report import finalize_graph_outputs_for_decision, write_decision_report, write_evidence_pack

            current_exit = graph_exit_code(result)
            finalize_graph_outputs_for_decision(result, output_dir=args.output_dir)
            decision = write_decision_report(
                result,
                exit_code=current_exit,
                output_dir=args.output_dir,
                include_local_paths=args.include_local_paths,
            )
            from .agent_summary import write_agent_summary

            agent_summary = write_agent_summary(
                result,
                decision,
                output_dir=args.output_dir,
                evidence_pack_path=args.evidence_pack,
                include_local_paths=args.include_local_paths,
                state_dir=args.agent_state_dir,
            )
            result["agent_summary_path"] = agent_summary.get("agent_summary_path")
            if args.evidence_pack:
                pack = write_evidence_pack(result, decision, args.evidence_pack)
                result["decision_evidence_pack"] = pack
    except ValueError as error:
        result = _write_cli_input_error(args.output_dir, "graph", str(error))
    if args.format == "json":
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        if result.get("verdict") == "SBOM_EXPORT_ERROR":
            print(_format_sbom_export_error(result))
            return 6
        if result.get("verdict") == "GRAPH_INPUT_ERROR":
            print(_format_cli_input_error(result))
            return 1
        print(format_graph_summary(result))
    return graph_exit_code(result)


def _run_status(args: argparse.Namespace) -> int:
    from .agent_status import build_agent_status, format_agent_status

    result = build_agent_status(args.artifact_inputs, state_dir=args.agent_state_dir)
    if args.format == "json":
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(format_agent_status(result))
    counts = result.get("counts", {}) or {}
    if counts.get("changed_since_check", 0) or counts.get("unchecked", 0):
        return 2
    return 0


def _run_drift(args: argparse.Namespace) -> int:
    from .drift import drift_exit_code, format_drift_summary, run_baseline_drift

    try:
        result = run_baseline_drift(
            args.baseline,
            args.artifact_inputs,
            args.output_dir,
            workspace_root=Path.cwd(),
            baseline_sha256=args.baseline_sha256,
            strict_closure=args.strict_closure,
            package_evidence=not args.no_package_evidence,
            bundle_sha256=args.bundle_sha256,
            license_policy_path=args.license_policy,
            entry_point_policy_path=args.entry_point_policy,
            target_environment_path=args.target_environment,
            lockfile_path=args.lockfile,
            policy_pack_path=args.policy_pack,
            policy_sha256=args.policy_sha256,
        )
    except ValueError as error:
        result = _write_cli_input_error(args.output_dir, "drift", str(error))
    if args.format == "json":
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        if result.get("verdict") == "DRIFT_INPUT_ERROR":
            print(_format_cli_input_error(result))
            return 1
        print(format_drift_summary(result))
    return drift_exit_code(result)


def _run_rebaseline(args: argparse.Namespace) -> int:
    from .rebaseline import format_rebaseline_summary, rebaseline_exit_code, run_rebaseline

    try:
        result = run_rebaseline(
            args.artifact_inputs,
            args.output_dir,
            from_baseline=args.from_baseline,
            baseline_sha256=args.baseline_sha256,
            yes=args.yes,
            workspace_root=Path.cwd(),
            strict_closure=args.strict_closure,
            package_evidence=not args.no_package_evidence,
            bundle_sha256=args.bundle_sha256,
            license_policy_path=args.license_policy,
            entry_point_policy_path=args.entry_point_policy,
            target_environment_path=args.target_environment,
            lockfile_path=args.lockfile,
            policy_pack_path=args.policy_pack,
            policy_sha256=args.policy_sha256,
        )
    except ValueError as error:
        result = _write_cli_input_error(args.output_dir, "rebaseline", str(error))
    if args.format == "json":
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        if result.get("verdict") == "REBASELINE_INPUT_ERROR":
            print(_format_cli_input_error(result))
            return 1
        print(format_rebaseline_summary(result))
    return rebaseline_exit_code(result)


def _print_help() -> None:
    print(
        """SPIRA Trust CLI

Usage:
  spira-trust trust <package.whl> [--output-dir DIR]
  spira-trust graph <wheel-folder|wheel...> [--output-dir DIR] [policy options] [--sbom cyclonedx-json]
  spira-trust status <wheel-folder|wheel...> [--format json]
  spira-trust drift <wheel-folder|wheel...> --baseline BOM --baseline-sha256 SHA256
  spira-trust rebaseline <wheel-folder|wheel...> --from-baseline BOM --baseline-sha256 SHA256 --output-dir DIR [--yes]
  spira-trust version

Public commands:
  trust       Review one artifact and emit a trust verdict.
  graph       Build a local evidence graph over provided wheels only.
  status      Re-hash local wheels and index prior agent_summary.json outputs.
  drift       Compare current wheels against a pinned BOM baseline.
  rebaseline  Create a new baseline after explicit human confirmation.
  version     Print the installed SPIRA Trust version.
"""
    )


def _configure_stdout() -> None:
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError):
        pass


def _version() -> str:
    try:
        return importlib_metadata.version("spira-trust")
    except importlib_metadata.PackageNotFoundError:
        try:
            return importlib_metadata.version("spira-review")
        except importlib_metadata.PackageNotFoundError:
            return "0.5.2"


def _trust_exit_code(result: dict[str, Any]) -> int:
    trust_status = result.get("decision", {}).get("trust_status")
    if trust_status == "TRUST_BLOCK":
        return 1
    if trust_status == "TRUST_UNKNOWN":
        return 2
    return 0


def _write_cli_input_error(output_dir: str, command: str, reason: str) -> dict[str, Any]:
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)
    verdict = f"{command.upper()}_INPUT_ERROR"
    report = {
        "schema": "SPIRA_CLI_INPUT_ERROR_V1",
        "schema_version": "1.0",
        "command": command,
        "verdict": verdict,
        "exit_code": 1,
        "reason": reason,
        "not_claimed": [
            "no package trust verdict was computed",
            "input errors are reported as clean CLI failures, not Python tracebacks",
        ],
    }
    report_path = output / f"{command}_input_error_report.json"
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    report["report_path"] = str(report_path.resolve())
    return report


def _format_cli_input_error(report: dict[str, Any]) -> str:
    title = f"SPIRA {str(report.get('command', 'input')).title()} Input Error"
    return (
        f"{title}\n"
        f"{'=' * len(title)}\n"
        f"[{report.get('verdict')}] {report.get('reason')}\n\n"
        f"Report: {report.get('report_path')}\n"
    )


def _write_sbom_export_error(output_dir: str, reason: str) -> dict[str, Any]:
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)
    report = {
        "schema": "SPIRA_SBOM_EXPORT_ERROR_V1",
        "schema_version": "1.0",
        "verdict": "SBOM_EXPORT_ERROR",
        "exit_code": 6,
        "reason": reason,
        "not_claimed": [
            "SBOM export errors do not compute or alter package trust verdicts",
            "CycloneDX export is an evidence output, not a trust approval",
        ],
    }
    report_path = output / "sbom_export_error_report.json"
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    report["report_path"] = str(report_path.resolve())
    return report


def _format_sbom_export_error(report: dict[str, Any]) -> str:
    title = "SPIRA SBOM Export Error"
    return (
        f"{title}\n"
        f"{'=' * len(title)}\n"
        f"[SBOM_EXPORT_ERROR] {report.get('reason')}\n\n"
        f"Report: {report.get('report_path')}\n"
    )


if __name__ == "__main__":
    raise SystemExit(main())
