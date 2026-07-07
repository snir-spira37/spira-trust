from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable, Literal


SUPPORTED_OPERATORS = {"==", "!=", "<", "<=", ">", ">="}
UNSUPPORTED_RESULT = "UNVERIFIED"

ParseStatus = Literal["SUPPORTED", "UNVERIFIED"]
EvaluationResult = Literal["SATISFIED", "CONFLICT", "UNVERIFIED"]


@dataclass(frozen=True)
class VersionConstraint:
    operator: str
    version: tuple[int, ...]
    raw_version: str


@dataclass(frozen=True)
class ParsedSpecifierSet:
    raw: str
    status: ParseStatus
    constraints: tuple[VersionConstraint, ...] = ()
    note: str | None = None


def parse_numeric_version(value: str) -> tuple[int, ...] | None:
    """Parse the V2 numeric-tuple version subset.

    This deliberately rejects PEP 440 features such as rc/dev/post/local
    segments, epochs, wildcards, and non-numeric tokens. V2 reports those as
    UNVERIFIED instead of pretending to understand them.
    """

    text = value.strip()
    if not text:
        return None
    parts = text.split(".")
    parsed: list[int] = []
    for part in parts:
        if not part or not part.isdigit():
            return None
        parsed.append(int(part))
    return tuple(parsed)


def compare_numeric_versions(left: tuple[int, ...], right: tuple[int, ...]) -> int:
    width = max(len(left), len(right))
    padded_left = left + (0,) * (width - len(left))
    padded_right = right + (0,) * (width - len(right))
    if padded_left < padded_right:
        return -1
    if padded_left > padded_right:
        return 1
    return 0


def parse_specifier_set(raw_specifier: str) -> ParsedSpecifierSet:
    raw = str(raw_specifier)
    text = raw.strip()
    if not text:
        return ParsedSpecifierSet(raw=raw, status="SUPPORTED", constraints=())
    if "~=" in text:
        return ParsedSpecifierSet(
            raw=raw,
            status=UNSUPPORTED_RESULT,
            note="unsupported compatible-release operator ~= in V2",
        )

    constraints: list[VersionConstraint] = []
    for part in text.split(","):
        item = part.strip()
        if not item:
            return ParsedSpecifierSet(raw=raw, status=UNSUPPORTED_RESULT, note="empty specifier segment")
        match = re.fullmatch(r"(==|!=|<=|>=|<|>)\s*([A-Za-z0-9_.!+*:-]+)", item)
        if not match:
            return ParsedSpecifierSet(raw=raw, status=UNSUPPORTED_RESULT, note=f"unsupported specifier syntax: {item}")
        operator, version_text = match.groups()
        version = parse_numeric_version(version_text)
        if version is None:
            return ParsedSpecifierSet(
                raw=raw,
                status=UNSUPPORTED_RESULT,
                note=f"unsupported non-numeric version in specifier: {version_text}",
            )
        constraints.append(VersionConstraint(operator=operator, version=version, raw_version=version_text))

    return ParsedSpecifierSet(raw=raw, status="SUPPORTED", constraints=tuple(constraints))


def evaluate_provided_versions(raw_specifier: str, provided_versions: Iterable[str]) -> dict[str, Any]:
    parsed = parse_specifier_set(raw_specifier)
    provided = [str(version) for version in provided_versions]
    if parsed.status != "SUPPORTED":
        return {
            "raw": raw_specifier,
            "result": "UNVERIFIED",
            "evaluated": False,
            "satisfied_by_provided": None,
            "satisfying_versions": [],
            "unsupported_provided_versions": [],
            "note": parsed.note,
        }

    unsatisfiable_reason = _unsatisfiable_by_construction(parsed.constraints)
    if unsatisfiable_reason:
        return {
            "raw": raw_specifier,
            "result": "CONFLICT",
            "evaluated": True,
            "satisfied_by_provided": False,
            "satisfying_versions": [],
            "unsupported_provided_versions": [],
            "note": unsatisfiable_reason,
        }

    satisfying_versions: list[str] = []
    unsupported_provided_versions: list[str] = []
    for version_text in provided:
        version = parse_numeric_version(version_text)
        if version is None:
            unsupported_provided_versions.append(version_text)
            continue
        if _version_satisfies_all(version, parsed.constraints):
            satisfying_versions.append(version_text)

    if satisfying_versions:
        return {
            "raw": raw_specifier,
            "result": "SATISFIED",
            "evaluated": True,
            "satisfied_by_provided": True,
            "satisfying_versions": satisfying_versions,
            "unsupported_provided_versions": unsupported_provided_versions,
            "note": None,
        }
    if unsupported_provided_versions:
        return {
            "raw": raw_specifier,
            "result": "UNVERIFIED",
            "evaluated": False,
            "satisfied_by_provided": None,
            "satisfying_versions": [],
            "unsupported_provided_versions": unsupported_provided_versions,
            "note": "one or more provided versions are outside the V2 numeric-tuple model",
        }
    return {
        "raw": raw_specifier,
        "result": "CONFLICT",
        "evaluated": True,
        "satisfied_by_provided": False,
        "satisfying_versions": [],
        "unsupported_provided_versions": [],
        "note": "no provided numeric version satisfies the supported constraints",
    }


def parser_source_uses_external_packaging() -> bool:
    source = Path(__file__).read_text(encoding="utf-8")
    return bool(re.search(r"^\s*(import|from)\s+packaging\b", source, flags=re.MULTILINE))


def _version_satisfies_all(version: tuple[int, ...], constraints: Iterable[VersionConstraint]) -> bool:
    return all(_version_satisfies(version, constraint) for constraint in constraints)


def _version_satisfies(version: tuple[int, ...], constraint: VersionConstraint) -> bool:
    comparison = compare_numeric_versions(version, constraint.version)
    if constraint.operator == "==":
        return comparison == 0
    if constraint.operator == "!=":
        return comparison != 0
    if constraint.operator == "<":
        return comparison < 0
    if constraint.operator == "<=":
        return comparison <= 0
    if constraint.operator == ">":
        return comparison > 0
    if constraint.operator == ">=":
        return comparison >= 0
    return False


def _unsatisfiable_by_construction(constraints: Iterable[VersionConstraint]) -> str | None:
    equals: list[VersionConstraint] = []
    not_equals: list[VersionConstraint] = []
    lower: tuple[tuple[int, ...], bool] | None = None
    upper: tuple[tuple[int, ...], bool] | None = None

    for constraint in constraints:
        if constraint.operator == "==":
            equals.append(constraint)
        elif constraint.operator == "!=":
            not_equals.append(constraint)
        elif constraint.operator in {">", ">="}:
            inclusive = constraint.operator == ">="
            if _is_stronger_lower_bound(constraint.version, inclusive, lower):
                lower = (constraint.version, inclusive)
        elif constraint.operator in {"<", "<="}:
            inclusive = constraint.operator == "<="
            if _is_stronger_upper_bound(constraint.version, inclusive, upper):
                upper = (constraint.version, inclusive)

    unique_equals = {_canonical_version_text(item.version) for item in equals}
    if len(unique_equals) > 1:
        return "constraint set has multiple incompatible exact versions"
    if equals:
        exact = equals[0].version
        if any(compare_numeric_versions(exact, item.version) == 0 for item in not_equals):
            return "constraint set excludes its exact required version"
        if lower and not _satisfies_lower(exact, lower):
            return "exact required version violates lower bound"
        if upper and not _satisfies_upper(exact, upper):
            return "exact required version violates upper bound"
        return None

    if lower and upper:
        comparison = compare_numeric_versions(lower[0], upper[0])
        if comparison > 0:
            return "lower bound is greater than upper bound"
        if comparison == 0 and (not lower[1] or not upper[1]):
            return "lower and upper bounds meet only at an excluded version"
    return None


def _is_stronger_lower_bound(
    version: tuple[int, ...],
    inclusive: bool,
    current: tuple[tuple[int, ...], bool] | None,
) -> bool:
    if current is None:
        return True
    comparison = compare_numeric_versions(version, current[0])
    return comparison > 0 or (comparison == 0 and not inclusive and current[1])


def _is_stronger_upper_bound(
    version: tuple[int, ...],
    inclusive: bool,
    current: tuple[tuple[int, ...], bool] | None,
) -> bool:
    if current is None:
        return True
    comparison = compare_numeric_versions(version, current[0])
    return comparison < 0 or (comparison == 0 and not inclusive and current[1])


def _satisfies_lower(version: tuple[int, ...], lower: tuple[tuple[int, ...], bool]) -> bool:
    comparison = compare_numeric_versions(version, lower[0])
    return comparison > 0 or (comparison == 0 and lower[1])


def _satisfies_upper(version: tuple[int, ...], upper: tuple[tuple[int, ...], bool]) -> bool:
    comparison = compare_numeric_versions(version, upper[0])
    return comparison < 0 or (comparison == 0 and upper[1])


def _canonical_version_text(version: tuple[int, ...]) -> str:
    return ".".join(str(part) for part in version)
