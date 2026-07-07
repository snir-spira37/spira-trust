from __future__ import annotations

import hashlib
import importlib.util
import sys
import types
from pathlib import Path
from typing import Any


VENDORED_SPIRA_DIR = Path(__file__).resolve().parent / "spira"
PRIVATE_PACKAGE_NAME = "spira_core._vendored_stone015_runtime"

EXPECTED_SHA256 = {
    "spira/__init__.py": "7b48dc743d74d2ade215de4f799e1001e7c5b7a35d4d4251c8158a293ec3b013",
    "spira/api.py": "da9daa05605f5e26a9d881ef1163b0d476cbaece2f66f68d1a0486b97396b0f0",
    "spira/ast_nodes.py": "68ecce736b7aa58dc2c9a3cd18066055d1bf8c2802db3c7c06bff0a595104322",
    "spira/backends.py": "efc93b245b86d3ebef199173a1470834dfbd9ec3970461738a604203501995f6",
    "spira/bridge.py": "c0648870a481f9d24f3ea70faa6a9a2b82a73224690ca432f69752751a4265d6",
    "spira/cli.py": "1fd7c7d3d14e0afb610ee3268e0518fc0255e1ef1e06688e2df846ef956699e2",
    "spira/demo.py": "9eedd68e880e3aeeec303a02a0465bb2eba0f47a00e07af7437b5ed70ef1cb27",
    "spira/modules.py": "e05798d54935401156e52e9ce524fbc3994845d3e7bee9e0209e23b46fdc1ce9",
    "spira/ontology.py": "3f723e9a2eec427a53ff60b7c0920a609a1dbc7b37aa5f146229d79d2cd01f00",
    "spira/orchestrator.py": "fdc2e21a68a53cf0365ddf7509024b927978676e7ff7cf82b9451c85d674d19c",
    "spira/parser.py": "537d1192d589b295a90ad177c1d61ce52220bf5067136f81c387b6b81444e1af",
    "spira/runtime.py": "952aa8b76fad8ee85329093f271558b04bd3afc78878ec2e96d3beae1aad717d",
    "spira/safe_eval.py": "6d938d93069172cefccf6ba3dd8101d0170a1ec127ef4cf7a0cbb3e2e1e21bab",
    "spira/schemas.py": "b35164bab599de308e5f93b3e50f85e88be641068e5e5c4c9cebf9469b53d4d3",
    "spira/storage.py": "6eeb8e943102de3db40ccd675838932b946b6feb950df7f62f3abfe893994170",
    "spira/typesystem.py": "846b974cf602cfcb8c59bd4cf55a50b3d0407b5e27398d7a641b300d416ec9cc",
    "spira/validation.py": "7527dc502e3c94e5de43fb62a9b14236b349c004a337e54af06cf4962a607936",
}


class VendoredStone015Error(RuntimeError):
    pass


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def verify_vendored_stone015(reference_root: str | Path | None = None) -> dict[str, Any]:
    root = Path(reference_root).resolve() if reference_root else Path(__file__).resolve().parent
    missing: list[str] = []
    mismatched: list[dict[str, str]] = []
    for rel_path, expected in EXPECTED_SHA256.items():
        file_path = root / rel_path
        if not file_path.is_file():
            missing.append(rel_path)
            continue
        actual = _sha256_file(file_path)
        if actual != expected:
            mismatched.append({"path": rel_path, "expected": expected, "actual": actual})
    return {
        "verdict": "VENDORED_STONE015_SHA_VERIFIED" if not missing and not mismatched else "VENDORED_STONE015_SHA_MISMATCH",
        "source": "byte-identical vendored Stone 015 Python source files",
        "file_count": len(EXPECTED_SHA256),
        "missing": missing,
        "mismatched": mismatched,
        "pass": not missing and not mismatched,
        "not_claimed": [
            "does not modify Stone 015 source files",
            "does not verify Stone 015 tests/docs/db files",
            "does not claim live production runtime",
        ],
    }


def _ensure_private_package() -> None:
    if PRIVATE_PACKAGE_NAME in sys.modules:
        return
    package = types.ModuleType(PRIVATE_PACKAGE_NAME)
    package.__path__ = [str(VENDORED_SPIRA_DIR)]  # type: ignore[attr-defined]
    package.__package__ = PRIVATE_PACKAGE_NAME
    sys.modules[PRIVATE_PACKAGE_NAME] = package


def load_bridge_classes() -> tuple[Any, Any]:
    verification = verify_vendored_stone015()
    if not verification["pass"]:
        raise VendoredStone015Error(f"vendored Stone 015 SHA verification failed: {verification}")
    _ensure_private_package()
    module_name = f"{PRIVATE_PACKAGE_NAME}.bridge"
    module = sys.modules.get(module_name)
    if module is None:
        bridge_path = VENDORED_SPIRA_DIR / "bridge.py"
        spec = importlib.util.spec_from_file_location(module_name, bridge_path)
        if spec is None or spec.loader is None:
            raise VendoredStone015Error(f"could not load vendored Stone 015 bridge: {bridge_path}")
        module = importlib.util.module_from_spec(spec)
        sys.modules[module_name] = module
        spec.loader.exec_module(module)
    return module.SpiraBridge, module.SpiraBridgeConfig
