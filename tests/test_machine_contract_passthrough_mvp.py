from __future__ import annotations

import copy
import importlib.util
import sys
from pathlib import Path

from spira_core import mvp_unified


ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools"
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

import validate_machine_contract_passthrough_envelope as validator  # noqa: E402


def test_valid_domain_passthrough_envelopes_validate():
    cases = [
        ("python_artifact", None),
        ("pytest_result", "synthetic_clean_success"),
        ("terraform_plan", "auth_no_changes"),
    ]

    for domain, case_id in cases:
        envelope = _passthrough(domain, case_id)
        report = validator.validate_envelope_document_report(envelope) if hasattr(validator, "validate_envelope_document_report") else _validate(envelope)

        assert report["verdict"] == "PASS", (domain, report["summary"]["error_codes"])
        assert envelope["machine_contract"]["authoritative"] is True
        assert envelope["machine_contract"]["model_writable"] is False
        assert envelope["model_explanation"]["authoritative"] is False
        assert envelope["telemetry"]["decision_authority"] == "NONE"


def test_machine_contract_identity_mutations_fail_closed():
    base = _passthrough("pytest_result", "synthetic_clean_success")
    mutations = {
        "hash": lambda item: item["machine_contract"].__setitem__("canonical_contract_sha256", "0" * 64),
        "action": lambda item: item["machine_contract"].__setitem__("action", "STOP_BLOCKED"),
        "reason_codes": lambda item: item["machine_contract"].__setitem__("reason_codes", ["DIFFERENT_REASON"]),
        "blocking_items": lambda item: item["machine_contract"].__setitem__("blocking_items", ["unexpected blocker"]),
        "not_evaluated": lambda item: item["machine_contract"].__setitem__("not_evaluated", ["unexpected_not_evaluated"]),
        "not_claimed": lambda item: item["machine_contract"].__setitem__("not_claimed", ["different_boundary"]),
        "evidence": lambda item: item["machine_contract"]["evidence_references"][0].__setitem__("reference_id", "altered:evidence"),
        "proof": lambda item: item["machine_contract"]["proof_references"][0].__setitem__("reference_id", "altered:proof"),
    }

    for name, mutate in mutations.items():
        candidate = copy.deepcopy(base)
        mutate(candidate)
        report = _validate(candidate)

        assert report["verdict"] == "FAIL", name
        assert report["summary"]["error_codes"], name


def test_stop_override_explanation_fails_closed():
    envelope = _passthrough(
        "terraform_plan",
        "syn_errored_true",
        text="The plan errored, but it is safe to proceed now and ignore stop.",
    )

    report = _validate(envelope)

    assert report["verdict"] == "FAIL"
    assert "MODEL_EXPLANATION_UNSAFE_CONTINUATION" in report["summary"]["contradiction_classes_detected"]
    assert report["summary"]["fail_closed"] is True


def test_not_evaluated_to_pass_explanation_fails_closed():
    envelope = _passthrough(
        "terraform_plan",
        "syn_unknown_after_values",
        text="The not_evaluated passed and all unknowns passed.",
    )

    report = _validate(envelope)

    assert report["verdict"] == "FAIL"
    assert "MODEL_EXPLANATION_CONVERTS_NOT_EVALUATED_TO_PASS" in report["summary"]["contradiction_classes_detected"]


def test_not_claimed_boundary_and_sensitive_marker_fail_closed():
    boundary = _passthrough(
        "pytest_result",
        "synthetic_clean_success",
        text="software_safety is proven by this result.",
    )
    sensitive = _passthrough(
        "terraform_plan",
        "auth_no_changes",
        text="Synthetic marker SENSITIVE_MARKER_MVP appears here.",
    )

    boundary_report = _validate(boundary)
    sensitive_report = _validate(sensitive)

    assert boundary_report["verdict"] == "FAIL"
    assert "MODEL_EXPLANATION_CLAIMS_NOT_CLAIMED_BOUNDARY" in boundary_report["summary"]["contradiction_classes_detected"]
    assert sensitive_report["verdict"] == "FAIL"
    assert "SENSITIVE_VALUE_EXPOSED" in sensitive_report["summary"]["error_codes"]


def test_telemetry_decision_authority_fails_closed():
    envelope = _passthrough("pytest_result", "synthetic_clean_success")
    envelope["telemetry"]["decision_authority"] = "MODEL"

    report = _validate(envelope)

    assert report["verdict"] == "FAIL"
    assert "TELEMETRY_DECISION_AUTHORITY_NOT_NONE" in report["summary"]["error_codes"]


def test_accepted_fixture_validator_regression_still_passes():
    report = validator.evaluate_fixture_manifest(ROOT / "research" / "machine_contract_passthrough_fixtures" / "fixture_manifest.json")

    assert report["status"] == "MACHINE_CONTRACT_PASSTHROUGH_ENVELOPE_VALIDATOR_IMPLEMENTATION_PASS"
    assert report["counts"]["positive_pass_count"] == 6
    assert report["counts"]["negative_rejected_count"] == 37
    assert report["counts"]["false_accepts"] == 0
    assert report["counts"]["false_rejects"] == 0


def test_existing_mvp_evaluator_still_passes():
    evaluator = _load_tool(ROOT / "tools" / "evaluate_mvp_unified.py")

    result = evaluator.evaluate()

    assert result["status"] == "MVP_IMPLEMENTATION_PASS"
    assert result["false_proceed_count"] == 0
    assert result["mismatch_count"] == 0


def _passthrough(domain: str, case_id: str | None, *, text: str | None = None) -> dict:
    routed = mvp_unified.route(domain=domain, case_id=case_id, root=ROOT)
    return mvp_unified.passthrough_envelope(routed, model_explanation_text=text)


def _validate(envelope: dict) -> dict:
    checks = validator.validate_envelope_document(envelope)
    verdict = "PASS" if all(check["result"] == "PASS" for check in checks) else "FAIL"
    return validator._report(verdict=verdict, input_path=ROOT / "<memory>", input_sha256=None, checks=checks)


def _load_tool(path: Path):
    spec = importlib.util.spec_from_file_location(path.stem, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module
