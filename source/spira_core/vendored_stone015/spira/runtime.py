from __future__ import annotations
import json, os, time, traceback
from dataclasses import dataclass, field, asdict
from typing import Any, Dict, Iterable, List, Optional, Tuple
from .ast_nodes import Node, Import, Command, Let, If, While, For, FuncDef, Return
from .ontology import ONTOLOGY, canonical_name
from .typesystem import assert_type, normalize_type_name, finite_number
from .safe_eval import safe_eval, ExpressionEvaluator
from .modules import BUILTIN_MODULES
from .parser import parse_script
from .backends import LLMBackend, MockLLMBackend, OpenAICompatibleLLMBackend, QuantumBackend, MockQuantumBackend, QiskitQuantumBackend
from .storage import SpiraMemoryDB

@dataclass
class World:
    name: str
    flow: float = 1.0
    note: str = ""


@dataclass
class Partzuf:
    name: str
    mode: str = "balanced"
    note: str = ""


@dataclass
class Vessel:
    name: str
    capacity: float = 1.0
    or_level: float = 0.0
    screen_strength: float = 1.0


@dataclass
class Frame:
    variables: Dict[str, Any] = field(default_factory=dict)
    types: Dict[str, str] = field(default_factory=dict)


@dataclass
class SpiraState:
    """Represents the mutable state of a Spira runtime.

    A schema_version field is included to support future migrations. When
    serializing, this value is persisted so that older snapshots can be
    migrated forward. New fields should provide sensible defaults when
    restoring from snapshots that predate their introduction.
    """
    # Version identifier for the serialized state format. Increment when adding
    # new fields that require migration. Version 1 corresponds to the initial
    # production RC schema.
    schema_version: int = 1

    active_world: str = "assiah"
    active_partzuf: str = "za"
    active_vessel: str = "default"
    worlds: Dict[str, World] = field(default_factory=lambda: {"assiah": World(name="assiah")})
    partzufim: Dict[str, Partzuf] = field(default_factory=lambda: {"za": Partzuf(name="za")})
    vessels: Dict[str, Vessel] = field(default_factory=lambda: {"default": Vessel(name="default")})
    noise: float = 0.0
    coherence: float = 1.0
    derived_coherence: float = 1.0
    shevira_flag: bool = False
    manual_coherence_bonus: float = 0.0
    manual_coherence_penalty: float = 0.0
    manual_shevira_flag: bool = False
    memory: Dict[str, Any] = field(default_factory=dict)
    last_result: Any = None
    superpositions: Dict[str, List[Any]] = field(default_factory=dict)
    entanglements: List[Tuple[str, str]] = field(default_factory=list)
    log: List[str] = field(default_factory=list)



@dataclass
class RuntimeConfig:
    echo_logs: bool = True
    trace: bool = False
    continue_on_error: bool = False
    max_errors: int = 25
    auto_checkpoint_label: Optional[str] = None
    profile: bool = False
    log_batch_size: int = 50
    max_loop_iters: int = 1000
    max_logs: Optional[int] = None
    # In 1.9.4 control-flow paths are interpreter-first by default.
    control_flow_eval_strict: bool = True
    trace_expression_fallbacks: bool = False
    expression_fallback_budget: Optional[int] = None
    interpreter_only_purposes: Tuple[str, ...] = ("let", "if", "while", "for", "return")


@dataclass
class ExecutionReport:
    ok: bool = True
    nodes_executed: int = 0
    errors: List[str] = field(default_factory=list)
    elapsed_ms: float = 0.0


class ReturnSignal(Exception):
    def __init__(self, value: Any):
        super().__init__()
        self.value = value


class SpiraRuntime:
    def __init__(
        self,
        program_ir: Optional[List[Dict[str, Any]]] = None,
        db_path: str = "spira_memory.db",
        echo_logs: bool = True,
        log_batch_size: int = 50,
        *,
        trace: bool = False,
        continue_on_error: bool = False,
        max_errors: int = 25,
        auto_checkpoint_label: Optional[str] = None,
        profile: bool = False,
        max_loop_iters: Optional[int] = None,
        max_logs: Optional[int] = None,
        config: Optional[RuntimeConfig] = None,
    ) -> None:
        self.s = SpiraState()
        self.frames: List[Frame] = [Frame()]
        self.functions: Dict[str, FuncDef] = {}
        self.imported_modules: set[str] = set()
        self.program_ir = program_ir or []
        self.llm: LLMBackend = MockLLMBackend()
        self.quantum: QuantumBackend = MockQuantumBackend()

        base_config = RuntimeConfig(
            echo_logs=echo_logs,
            trace=trace,
            continue_on_error=continue_on_error,
            max_errors=max_errors,
            auto_checkpoint_label=auto_checkpoint_label,
            profile=profile,
            log_batch_size=log_batch_size,
        )
        if config:
            for field_name in base_config.__dataclass_fields__:
                if hasattr(config, field_name):
                    setattr(base_config, field_name, getattr(config, field_name))
        if max_loop_iters is not None:
            base_config.max_loop_iters = int(max_loop_iters)
        if max_logs is not None:
            base_config.max_logs = max_logs
        base_config.log_batch_size = max(1, int(base_config.log_batch_size))
        base_config.max_loop_iters = max(1, int(base_config.max_loop_iters))
        if base_config.max_logs is not None:
            base_config.max_logs = max(1, int(base_config.max_logs))
        self.config = base_config

        self.db = SpiraMemoryDB(db_path, log_batch_size=self.config.log_batch_size, max_logs=self.config.max_logs)
        self.echo_logs = self.config.echo_logs
        self._last_auto_shevira_state: Optional[bool] = None
        self.errors: List[str] = []
        self.nodes_executed: int = 0
        self.expression_interpreted_count: int = 0
        self.expression_fallback_count: int = 0
        self.expression_fallbacks_by_purpose: Dict[str, int] = {}

    @property
    def frame(self) -> Frame:
        return self.frames[-1]

    @property
    def vars(self) -> Dict[str, Any]:
        return self.frame.variables

    @property
    def types(self) -> Dict[str, str]:
        return self.frame.types

    def push_frame(self, variables: Optional[Dict[str, Any]] = None, types: Optional[Dict[str, str]] = None) -> None:
        self.frames.append(Frame(variables=variables or {}, types=types or {}))

    def pop_frame(self) -> None:
        if len(self.frames) <= 1:
            raise RuntimeError("cannot pop global frame")
        self.frames.pop()

    def world_obj(self) -> World:
        if self.s.active_world not in self.s.worlds:
            self.s.worlds[self.s.active_world] = World(name=self.s.active_world)
        return self.s.worlds[self.s.active_world]

    def partzuf_obj(self) -> Partzuf:
        if self.s.active_partzuf not in self.s.partzufim:
            self.s.partzufim[self.s.active_partzuf] = Partzuf(name=self.s.active_partzuf)
        return self.s.partzufim[self.s.active_partzuf]

    def vessel(self) -> Vessel:
        if self.s.active_vessel not in self.s.vessels:
            self.s.vessels[self.s.active_vessel] = Vessel(name=self.s.active_vessel)
        return self.s.vessels[self.s.active_vessel]

    def flush(self) -> None:
        self.db.flush()

    def close(self) -> None:
        self.db.close()

    def log(self, msg: str) -> None:
        self.s.log.append(msg)
        self.db.log(msg)
        if self.echo_logs:
            print(msg)

    def trace_log(self, msg: str) -> None:
        if self.config.trace:
            self.log(f"[trace] {msg}")

    def set_trace(self, enabled: bool) -> None:
        self.config.trace = bool(enabled)
        self.log(f"[trace:set] enabled={self.config.trace}")

    def inspect_view(self, target: str = "state") -> Any:
        target = target.lower()
        if target == "state":
            data = self.serialize_state()
        elif target == "vars":
            data = self.env()
        elif target == "memory":
            data = dict(self.s.memory)
        elif target == "functions":
            data = sorted(self.functions.keys())
        elif target == "superpositions":
            data = dict(self.s.superpositions)
        elif target == "entanglements":
            data = list(self.s.entanglements)
        elif target == "errors":
            data = list(self.errors)
        elif target == "expression_stats":
            data = self.expression_stats()
        else:
            raise ValueError(f"unknown inspect target: {target}")
        text = json.dumps(data, ensure_ascii=False, indent=2, default=str)
        self.s.last_result = data
        self.log(f"[inspect:{target}]\n{text}")
        return data

    def expression_stats(self) -> Dict[str, Any]:
        return {
            "interpreted_count": self.expression_interpreted_count,
            "fallback_count": self.expression_fallback_count,
            "fallbacks_by_purpose": dict(self.expression_fallbacks_by_purpose),
            "fallback_budget": self.config.expression_fallback_budget,
        }

    def checkpoint(self, label: str) -> None:
        self.db_save_state(label)

    def recover(self, label: str) -> None:
        self.db_load_state(label)

    def record_error(self, line: int, exc: Exception) -> str:
        message = f"Line {line}: {exc}"
        self.errors.append(message)
        self.log(f"[error] {message}")
        if self.config.trace:
            tb = traceback.format_exc(limit=3).strip()
            if tb:
                self.log(f"[traceback] {tb}")
        if self.config.auto_checkpoint_label:
            try:
                self.db_save_state(self.config.auto_checkpoint_label)
            except Exception as save_exc:
                self.log(f"[checkpoint:error] {save_exc}")
        return message

    def node_label(self, node: Node) -> str:
        if isinstance(node, Command):
            return f"Command({node.name})"
        if isinstance(node, Let):
            return f"Let({node.var})"
        if isinstance(node, FuncDef):
            return f"FuncDef({node.name})"
        if isinstance(node, Return):
            return "Return"
        if isinstance(node, Import):
            return f"Import({node.module_name})"
        if isinstance(node, If):
            return "If"
        if isinstance(node, While):
            return "While"
        if isinstance(node, For):
            return f"For({node.var})"
        return type(node).__name__

    def env(self) -> Dict[str, Any]:
        """Return the execution environment for expression evaluation.

        Order of precedence:
          1. Reserved runtime values (world, partzuf, vessel, metrics)
          2. Local frame variables
          3. Memory exposed under the 'mem' key
        """
        env: Dict[str, Any] = {}
        # reserved runtime names
        w, p, v = self.world_obj(), self.partzuf_obj(), self.vessel()
        env.update({
            "world": self.s.active_world,
            "partzuf": self.s.active_partzuf,
            "vessel": self.s.active_vessel,
            "world_flow": w.flow,
            "partzuf_mode": p.mode,
            "or_level": v.or_level,
            "kli_capacity": v.capacity,
            "screen_strength": v.screen_strength,
            "noise": self.s.noise,
            "coherence": self.s.coherence,
            "derived_coherence": self.s.derived_coherence,
            "shevira": self.s.shevira_flag,
            "last_result": self.s.last_result,
        })
        # local variables (outer frames first, inner frames override reserved names where appropriate)
        for fr in self.frames:
            for key, value in fr.variables.items():
                if key not in env:
                    env[key] = value
        # expose memory via 'mem' to avoid shadowing
        env["mem"] = dict(self.s.memory)
        return env

    def eval_expression(self, expr: str, *, strict: bool = True) -> Any:
        text = expr.strip()
        env = self.env()

        if not text:
            return None
        if text in env:
            return env[text]
        if text in ONTOLOGY:
            return text

        low = text.lower()
        if low == "true":
            return True
        if low == "false":
            return False
        if low == "none":
            return None

        try:
            return ast.literal_eval(text)
        except Exception:
            pass

        try:
            return ExpressionEvaluator(env).evaluate(text)
        except Exception:
            pass

        try:
            return safe_eval(text, env)
        except Exception:
            if strict:
                raise
            return text

    def _eval_interpreted_expression(self, expr: str) -> Any:
        """Evaluate an expression using only literal parsing and ExpressionEvaluator."""
        text = expr.strip()
        env = self.env()
        if not text:
            return None
        if text in env:
            return env[text]
        if text in ONTOLOGY:
            return text
        low = text.lower()
        if low == "true":
            return True
        if low == "false":
            return False
        if low == "none":
            return None
        try:
            return ast.literal_eval(text)
        except Exception:
            pass
        return ExpressionEvaluator(env).evaluate(text)

    def eval_runtime_expression(
        self,
        expr: str,
        *,
        strict: bool = True,
        allow_fallback: bool = True,
        purpose: str = "generic",
    ) -> Any:
        """Evaluate an expression with optional fallback to safe_eval for compatibility.

        When allow_fallback=False, only the interpreter path is allowed.
        Tracks how often fallback still occurs so the fallback path can be reduced safely over time.
        """
        # Some purposes are interpreter-only by policy in 1.9.4.
        if purpose in getattr(self.config, "interpreter_only_purposes", ()):  # pragma: no cover - tiny guard
            allow_fallback = False
        try:
            value = self._eval_interpreted_expression(expr)
            self.expression_interpreted_count += 1
            return value
        except Exception as interp_exc:
            if self.config.trace_expression_fallbacks:
                self.trace_log(f"[expr:fallback-check] purpose={purpose} expr={expr!r} reason={interp_exc}")
            if not allow_fallback:
                if strict:
                    raise
                return expr
        if allow_fallback:
            try:
                if self.config.trace_expression_fallbacks:
                    self.trace_log(f"[expr:fallback] purpose={purpose} expr={expr!r}")
                self.expression_fallback_count += 1
                self.expression_fallbacks_by_purpose[purpose] = self.expression_fallbacks_by_purpose.get(purpose, 0) + 1
                budget = self.config.expression_fallback_budget
                if budget is not None and self.expression_fallback_count > budget:
                    raise RuntimeError(f"expression fallback budget exceeded ({budget})")
                return safe_eval(expr, self.env())
            except Exception:
                if strict:
                    raise
        return expr

    def resolve(self, raw: str) -> Any:
        return self.eval_expression(raw, strict=False)

    def parse_kv(self, args: List[str]) -> Tuple[List[str], Dict[str, str]]:
        pos, kv = [], {}
        for a in args:
            if "=" in a:
                k, v = a.split("=", 1)
                kv[k] = v
            else:
                pos.append(a)
        return pos, kv

    def require_pos(self, pos: List[str], min_count: int, message: str) -> None:
        if len(pos) < min_count:
            raise ValueError(message)

    def set_typed_var(self, name: str, value: Any, type_name: str) -> None:
        coerced = assert_type(value, type_name, name)
        self.vars[name] = coerced
        self.types[name] = normalize_type_name(type_name)

    def serialize_state(self) -> Dict[str, Any]:
        """Serialize the runtime state into a JSON-serializable dictionary.

        The resulting dict always includes a schema_version key so that
        future versions can migrate older snapshots. New fields must be
        included here and handled in restore_state().
        """
        return {
            "schema_version": self.s.schema_version,
            "active_world": self.s.active_world,
            "active_partzuf": self.s.active_partzuf,
            "active_vessel": self.s.active_vessel,
            "worlds": {k: asdict(v) for k, v in self.s.worlds.items()},
            "partzufim": {k: asdict(v) for k, v in self.s.partzufim.items()},
            "vessels": {k: asdict(v) for k, v in self.s.vessels.items()},
            "noise": self.s.noise,
            "coherence": self.s.coherence,
            "derived_coherence": self.s.derived_coherence,
            "shevira_flag": self.s.shevira_flag,
            "manual_coherence_bonus": self.s.manual_coherence_bonus,
            "manual_coherence_penalty": self.s.manual_coherence_penalty,
            "manual_shevira_flag": self.s.manual_shevira_flag,
            "memory": self.s.memory,
            "last_result": self.s.last_result,
            "superpositions": self.s.superpositions,
            "entanglements": self.s.entanglements,
        }

    def restore_state(self, data: Dict[str, Any]) -> None:
        """Restore the runtime state from a serialized snapshot.

        Unknown keys are ignored. Missing keys fall back to defaults on
        the SpiraState dataclass. The schema_version field is used to
        handle backward compatibility.
        """
        # Schema version (defaults to 1 if missing)
        self.s.schema_version = int(data.get("schema_version", 1))
        self.s.active_world = data.get("active_world", self.s.active_world)
        self.s.active_partzuf = data.get("active_partzuf", self.s.active_partzuf)
        self.s.active_vessel = data.get("active_vessel", self.s.active_vessel)
        worlds = data.get("worlds")
        if worlds:
            self.s.worlds = {k: World(**v) for k, v in worlds.items()}
        partzufim = data.get("partzufim")
        if partzufim:
            self.s.partzufim = {k: Partzuf(**v) for k, v in partzufim.items()}
        vessels = data.get("vessels")
        if vessels:
            self.s.vessels = {k: Vessel(**v) for k, v in vessels.items()}
        if "noise" in data:
            self.s.noise = float(data["noise"])
        if "coherence" in data:
            self.s.coherence = float(data["coherence"])
        # derived coherence falls back to coherence if not present
        derived = data.get("derived_coherence", data.get("coherence", self.s.coherence))
        self.s.derived_coherence = float(derived)
        if "shevira_flag" in data:
            self.s.shevira_flag = bool(data["shevira_flag"])
        self.s.manual_coherence_bonus = float(data.get("manual_coherence_bonus", self.s.manual_coherence_bonus))
        self.s.manual_coherence_penalty = float(data.get("manual_coherence_penalty", self.s.manual_coherence_penalty))
        self.s.manual_shevira_flag = bool(data.get("manual_shevira_flag", self.s.manual_shevira_flag))
        self.s.memory = dict(data.get("memory", self.s.memory))
        self.s.last_result = data.get("last_result", self.s.last_result)
        superpositions = data.get("superpositions")
        if superpositions:
            self.s.superpositions = {k: list(v) for k, v in superpositions.items()}
        entanglements = data.get("entanglements")
        if entanglements:
            self.s.entanglements = [tuple(x) for x in entanglements]
        # Reset last auto shevira state so recompute_state can detect transitions
        self._last_auto_shevira_state = self.s.shevira_flag

    def recompute_state(self) -> None:
        v, w = self.vessel(), self.world_obj()
        effective_capacity = max(0.001, v.capacity * max(0.1, v.screen_strength))
        overload = max(0.0, v.or_level - effective_capacity)
        disorder = self.s.noise + overload / max(v.capacity, 1.0) + max(0.0, w.flow - 1.0) * 0.05
        derived_coherence = max(0.0, min(1.0, 1.0 - disorder))
        self.s.derived_coherence = derived_coherence
        adjusted = derived_coherence + self.s.manual_coherence_bonus - self.s.manual_coherence_penalty
        self.s.coherence = max(0.0, min(1.0, adjusted))
        current_shevira = self.s.manual_shevira_flag or overload > 0.0 or self.s.coherence < 0.35
        transitioned = (self._last_auto_shevira_state is None) or (current_shevira != self._last_auto_shevira_state)
        self.s.shevira_flag = current_shevira
        if current_shevira and transitioned:
            self.log(
                f"[shevira:auto] world={self.s.active_world} | vessel={v.name} | overload={overload:.3f} | derived={self.s.derived_coherence:.3f} | coherence={self.s.coherence:.3f}"
            )
        elif (not current_shevira) and transitioned and self._last_auto_shevira_state:
            self.log(
                f"[shevira:resolved] world={self.s.active_world} | vessel={v.name} | derived={self.s.derived_coherence:.3f} | coherence={self.s.coherence:.3f}"
            )
        self._last_auto_shevira_state = current_shevira


    def set_backend(self, kind: str, name: str) -> None:
        kind, name = kind.lower(), name.lower()
        if kind == "llm":
            if name == "mock":
                self.llm = MockLLMBackend()
            elif name == "openai":
                self.llm = OpenAICompatibleLLMBackend()
            else:
                raise ValueError(f"unknown llm backend: {name}")
            self.log(f"[backend] llm={name}")
            return
        if kind == "quantum":
            if name == "mock":
                self.quantum = MockQuantumBackend()
            elif name == "qiskit":
                self.quantum = QiskitQuantumBackend()
            else:
                raise ValueError(f"unknown quantum backend: {name}")
            self.log(f"[backend] quantum={name}")
            return
        raise ValueError(f"unknown backend kind: {kind}")

    def import_module(self, module_name: str) -> None:
        if module_name in self.imported_modules:
            self.log(f"[import] already loaded: {module_name}")
            return
        if module_name in BUILTIN_MODULES:
            script = BUILTIN_MODULES[module_name]
        elif os.path.exists(module_name):
            with open(module_name, "r", encoding="utf-8") as f:
                script = f.read()
        else:
            raise ValueError(f"Unknown module: {module_name}")
        nodes = parse_script(script)
        self.log(f"[import] loading {module_name}")
        self.execute(nodes)
        self.imported_modules.add(module_name)

    def world_create(self, name: str, flow: float = 1.0, note: str = "") -> None:
        self.s.worlds[name] = World(name=name, flow=finite_number(flow, "world.flow", minimum=0.0), note=note)
        self.log(f"[world:create] {name} | flow={flow}")

    def world_use(self, name: str) -> None:
        if name not in self.s.worlds:
            self.s.worlds[name] = World(name=name)
        self.s.active_world = name
        self.recompute_state()
        self.log(f"[world:use] {name}")

    def world_set(self, name: str, **updates: Any) -> None:
        if name not in self.s.worlds:
            self.s.worlds[name] = World(name=name)
        w = self.s.worlds[name]
        if "flow" in updates:
            w.flow = finite_number(self.resolve(str(updates["flow"])), "world.flow", minimum=0.0)
        if "note" in updates:
            w.note = str(updates["note"])
        self.recompute_state()
        self.log(f"[world:set] {name} | flow={w.flow}")

    def partzuf_create(self, name: str, mode: str = "balanced", note: str = "") -> None:
        self.s.partzufim[name] = Partzuf(name=name, mode=mode, note=note)
        self.log(f"[partzuf:create] {name} | mode={mode}")

    def partzuf_use(self, name: str) -> None:
        if name not in self.s.partzufim:
            self.s.partzufim[name] = Partzuf(name=name)
        self.s.active_partzuf = name
        self.recompute_state()
        self.log(f"[partzuf:use] {name}")

    def partzuf_set(self, name: str, **updates: Any) -> None:
        if name not in self.s.partzufim:
            self.s.partzufim[name] = Partzuf(name=name)
        p = self.s.partzufim[name]
        if "mode" in updates:
            p.mode = str(updates["mode"])
        if "note" in updates:
            p.note = str(updates["note"])
        self.log(f"[partzuf:set] {name} | mode={p.mode}")

    def vessel_create(self, name: str, capacity: float = 1.0, screen: float = 1.0) -> None:
        self.s.vessels[name] = Vessel(
            name=name,
            capacity=finite_number(capacity, "vessel.capacity", minimum=0.001),
            screen_strength=finite_number(screen, "vessel.screen", minimum=0.1),
        )
        self.log(f"[vessel:create] {name} | capacity={capacity:.3f} | screen={screen:.3f}")

    def vessel_use(self, name: str) -> None:
        if name not in self.s.vessels:
            self.s.vessels[name] = Vessel(name=name)
        self.s.active_vessel = name
        self.recompute_state()
        self.log(f"[vessel:use] {name}")

    def vessel_set(self, name: str, **updates: Any) -> None:
        if name not in self.s.vessels:
            self.s.vessels[name] = Vessel(name=name)
        v = self.s.vessels[name]
        if "capacity" in updates:
            v.capacity = finite_number(self.resolve(str(updates["capacity"])), "vessel.capacity", minimum=0.001)
        if "or_level" in updates:
            v.or_level = finite_number(self.resolve(str(updates["or_level"])), "vessel.or_level", minimum=0.0)
        if "screen" in updates:
            v.screen_strength = finite_number(self.resolve(str(updates["screen"])), "vessel.screen", minimum=0.1)
        if "screen_strength" in updates:
            v.screen_strength = finite_number(self.resolve(str(updates["screen_strength"])), "vessel.screen_strength", minimum=0.1)
        self.recompute_state()
        self.log(f"[vessel:set] {name} | capacity={v.capacity:.3f} | or={v.or_level:.3f} | screen={v.screen_strength:.3f}")

    def set_kli(self, value: Any) -> None:
        v = self.vessel()
        v.capacity = finite_number(value, "kli", minimum=0.001)
        self.recompute_state()
        self.log(f"[kli] vessel={v.name} | capacity={v.capacity:.3f}")

    def draw_or(self, value: Any) -> None:
        v = self.vessel()
        v.or_level += finite_number(value, "or", minimum=0.0)
        self.recompute_state()
        self.log(f"[or] vessel={v.name} | level={v.or_level:.3f}")

    def set_or(self, value: Any) -> None:
        v = self.vessel()
        v.or_level = finite_number(value, "or_set", minimum=0.0)
        self.recompute_state()
        self.log(f"[or:set] vessel={v.name} | level={v.or_level:.3f}")

    def add_noise(self, value: Any) -> None:
        self.s.noise += finite_number(value, "noise", minimum=0.0)
        self.recompute_state()
        self.log(f"[noise] {self.s.noise:.3f}")

    def set_noise(self, value: Any) -> None:
        self.s.noise = finite_number(value, "noise_set", minimum=0.0)
        self.recompute_state()
        self.log(f"[noise:set] {self.s.noise:.3f}")

    def set_screen(self, value: Any) -> None:
        v = self.vessel()
        v.screen_strength = finite_number(value, "screen", minimum=0.1)
        self.recompute_state()
        self.log(f"[screen] vessel={v.name} | strength={v.screen_strength:.3f}")

    def tzimtzum(self, level: str = "medium") -> None:
        presets = {"soft": 0.90, "medium": 0.75, "strong": 0.55}
        factor = presets.get(level)
        if factor is None:
            factor = finite_number(self.resolve(level), "tzimtzum.factor", minimum=0.0)
        v = self.vessel()
        v.or_level *= factor
        self.s.noise *= factor
        self.recompute_state()
        self.log(f"[tzimtzum] factor={factor:.3f} | or={v.or_level:.3f} | noise={self.s.noise:.3f}")

    def masach(self, mode: str = "truth") -> None:
        v = self.vessel()
        if mode == "strict":
            v.screen_strength *= 1.25
        elif mode == "soft":
            v.screen_strength *= 1.05
        else:
            v.screen_strength *= 1.15
        self.recompute_state()
        self.log(f"[masach] mode={mode} | screen={v.screen_strength:.3f}")

    def shevira(self) -> None:
        self.s.manual_shevira_flag = True
        self.s.manual_coherence_penalty = min(1.0, self.s.manual_coherence_penalty + 0.5)
        self.recompute_state()
        self.log(f"[shevira:manual] coherence={self.s.coherence:.3f}")

    def tikkun(self) -> None:
        v = self.vessel()
        v.or_level *= 0.7
        self.s.noise *= 0.6
        v.screen_strength *= 1.2
        self.s.manual_coherence_penalty = max(0.0, self.s.manual_coherence_penalty - 0.25)
        self.s.manual_coherence_bonus = max(0.0, self.s.manual_coherence_bonus - 0.02)
        self.recompute_state()
        if self.s.shevira_flag:
            v.or_level *= 0.8
            self.s.noise *= 0.8
            self.recompute_state()
        if self.s.coherence >= 0.35 and v.or_level <= max(0.001, v.capacity * max(0.1, v.screen_strength)):
            self.s.manual_shevira_flag = False
            self.recompute_state()
        self.log(
            f"[tikkun] vessel={v.name} | or={v.or_level:.3f} | noise={self.s.noise:.3f} | screen={v.screen_strength:.3f} | coherence={self.s.coherence:.3f} | shevira={self.s.shevira_flag}"
        )

    def chokhmah(self, *source: str) -> Any:
        src = " ".join(source) if source else str(self.s.last_result)
        out = self.llm.generate(src, mode="creative")
        self.s.last_result = f"insight({out})"
        self.log(f"[chokhmah] {self.s.last_result}")
        return self.s.last_result

    def binah(self, *data: str) -> Any:
        item = " ".join(data) if data else self.s.last_result
        if item is None:
            raise ValueError("binah requires input or last_result")
        out = self.llm.generate(str(item), mode="analysis")
        self.s.last_result = f"analysis({out})"
        self.log(f"[binah] {self.s.last_result}")
        return self.s.last_result

    def daat(self, *info: str) -> Any:
        item = " ".join(info) if info else self.s.last_result
        if item is None:
            raise ValueError("daat requires input or last_result")
        out = self.llm.generate(str(item), mode="judge")
        self.s.last_result = f"knowledge({out})"
        self.log(f"[daat] {self.s.last_result}")
        return self.s.last_result

    def remember(self, key: str, *value: str) -> None:
        if value:
            raw = " ".join(value)
            v = self.resolve(raw)
        else:
            v = self.s.last_result
        if v is None:
            raise ValueError("remember requires value or last_result")
        self.s.memory[key] = v
        self.log(f"[remember] {key}={v}")

    def recall(self, key: str) -> Any:
        v = self.s.memory.get(key)
        self.s.last_result = v
        self.log(f"[recall] {key}={v}")
        return v

    def db_remember(self, key: str) -> None:
        self.db.put(key, self.s.memory.get(key, self.s.last_result))
        self.log(f"[db:remember] {key}")

    def db_recall(self, key: str) -> None:
        value = self.db.get(key)
        self.s.memory[key] = value
        self.s.last_result = value
        self.log(f"[db:recall] {key}={value}")

    def db_save_state(self, label: str) -> None:
        self.db.save_state(label, self.serialize_state())
        self.log(f"[db:save_state] {label}")

    def db_load_state(self, label: str) -> None:
        data = self.db.load_state(label)
        if data is None:
            raise ValueError(f"state not found: {label}")
        self.restore_state(data)
        self.log(f"[db:load_state] {label}")

    def agent(self, mode: str, *prompt: str) -> Any:
        text = " ".join(prompt) if prompt else str(self.s.last_result)
        if mode == "triad":
            self.chokhmah(text)
            self.binah()
            self.daat()
            self.log(f"[agent:triad] {self.s.last_result}")
            return self.s.last_result
        if mode == "verify":
            out = self.llm.generate(text, mode="judge")
            self.s.last_result = f"verify({out})"
            self.log(f"[agent:verify] {self.s.last_result}")
            return self.s.last_result
        if mode == "plan":
            out = self.llm.generate(text, mode="plan")
            self.s.last_result = f"plan({out})"
            self.log(f"[agent:plan] {self.s.last_result}")
            return self.s.last_result
        raise ValueError(f"unknown agent mode: {mode}")

    def superpose(self, name: str, *options: str) -> None:
        values = [self.resolve(x) for x in options]
        if not values:
            raise ValueError("superpose requires at least one option")
        backend_result = self.quantum.superpose(values)
        self.s.superpositions[name] = values
        self.s.last_result = backend_result
        self.draw_or(max(0.1, 0.15 * len(values)))
        self.add_noise(max(0.0, 0.04 * max(len(values) - 1, 0)))
        self.log(f"[superpose] {name}={values}")

    def entangle(self, left: str, right: str) -> None:
        result = self.quantum.entangle(left, right)
        self.s.entanglements.append((left, right))
        self.s.last_result = result
        self.s.manual_coherence_bonus = min(0.25, self.s.manual_coherence_bonus + 0.05)
        self.recompute_state()
        self.log(f"[entangle] {left}<->{right}")

    def measure(self, name: Optional[str] = None) -> Any:
        target = name or next(iter(self.s.superpositions), None)
        if target is None or target not in self.s.superpositions:
            self.log("[measure] nothing to collapse")
            self.s.last_result = None
            return None
        options = self.s.superpositions[target]
        choice = self.quantum.measure(options, prefer_balance=True)
        self.s.superpositions[target] = [choice]
        self.s.last_result = choice
        self.log(f"[measure] {target} -> {choice}")
        return choice

    def pipeline(self, *steps: str) -> Any:
        for step in steps:
            s = canonical_name(step)
            if s == "chokhmah":
                self.chokhmah()
            elif s == "binah":
                self.binah()
            elif s == "daat":
                self.daat()
            elif s == "tikkun":
                self.tikkun()
            elif s == "measure":
                self.measure()
            else:
                raise ValueError(f"unknown pipeline step: {step}")
        self.log(f"[pipeline] result={self.s.last_result}")
        return self.s.last_result

    def call_function(self, name: str, args: List[Any]) -> Any:
        if name not in self.functions:
            raise ValueError(f"Unknown function: {name}")
        fn = self.functions[name]
        if len(args) != len(fn.params):
            raise ValueError(f"Function {name} expects {len(fn.params)} args, got {len(args)}")
        values: Dict[str, Any] = {}
        types: Dict[str, str] = {}
        for param, arg in zip(fn.params, args):
            coerced = assert_type(arg, param.type_name, f"param {param.name}")
            values[param.name] = coerced
            types[param.name] = normalize_type_name(param.type_name)
        self.push_frame(values, types)
        try:
            try:
                self.execute(fn.body)
            except ReturnSignal as rs:
                self.s.last_result = rs.value
                self.log(f"[call:{name}] -> {rs.value}")
                return rs.value
            self.s.last_result = None
            self.log(f"[call:{name}] -> None")
            return None
        finally:
            self.pop_frame()

    def export_ir(self, path: str) -> None:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(self.program_ir, f, ensure_ascii=False, indent=2)
        self.log(f"[export_ir] {path}")

    def status(self) -> None:
        w, p, v = self.world_obj(), self.partzuf_obj(), self.vessel()
        self.log(
            f"[status] world={w.name} flow={w.flow:.3f} | partzuf={p.name} mode={p.mode} | vessel={v.name} | or={v.or_level:.3f} | kli={v.capacity:.3f} | screen={v.screen_strength:.3f} | noise={self.s.noise:.3f} | derived={self.s.derived_coherence:.3f} | coherence={self.s.coherence:.3f} | shevira={self.s.shevira_flag}"
        )

    def manifest(self, *value: str) -> Any:
        result = " ".join(value) if value else self.s.last_result
        self.s.last_result = result
        self.log(f"[manifest] {result}")
        return result

    def execute_command(self, cmd: Command) -> None:
        name = cmd.name
        pos, kv = self.parse_kv(cmd.args)

        if name == "backend":
            self.require_pos(pos, 2, "backend requires: backend <llm|quantum> <name>")
            return self.set_backend(pos[0], pos[1])

        if name == "set":
            self.require_pos(pos, 2, "set requires field and value")
            field, value = pos[0], pos[1]
            if field == "world":
                return self.world_use(value)
            if field == "partzuf":
                return self.partzuf_use(value)
            raise ValueError(f"unknown set field: {field}")

        if name == "world":
            self.require_pos(pos, 1, "world requires action")
            action = pos[0]
            if action == "create":
                self.require_pos(pos, 2, "world create <name> [flow=...] [note=...]")
                return self.world_create(pos[1], float(self.resolve(kv.get("flow", "1.0"))), kv.get("note", ""))
            if action == "use":
                if len(pos) != 2:
                    raise ValueError("world use <name>")
                return self.world_use(pos[1])
            if action == "set":
                self.require_pos(pos, 2, "world set <name> [flow=...] [note=...]")
                return self.world_set(pos[1], **kv)
            raise ValueError(f"unknown world action: {action}")

        if name == "partzuf":
            self.require_pos(pos, 1, "partzuf requires action")
            action = pos[0]
            if action == "create":
                self.require_pos(pos, 2, "partzuf create <name> [mode=...] [note=...]")
                return self.partzuf_create(pos[1], kv.get("mode", "balanced"), kv.get("note", ""))
            if action == "use":
                if len(pos) != 2:
                    raise ValueError("partzuf use <name>")
                return self.partzuf_use(pos[1])
            if action == "set":
                self.require_pos(pos, 2, "partzuf set <name> [mode=...] [note=...]")
                return self.partzuf_set(pos[1], **kv)
            raise ValueError(f"unknown partzuf action: {action}")

        if name == "vessel":
            self.require_pos(pos, 1, "vessel requires action")
            action = pos[0]
            if action == "create":
                self.require_pos(pos, 2, "vessel create <name> [capacity=...] [screen=...]")
                return self.vessel_create(
                    pos[1],
                    float(self.resolve(kv.get("capacity", "1.0"))),
                    float(self.resolve(kv.get("screen", "1.0"))),
                )
            if action == "use":
                if len(pos) != 2:
                    raise ValueError("vessel use <name>")
                return self.vessel_use(pos[1])
            if action == "set":
                self.require_pos(pos, 2, "vessel set <name> [capacity=...] [or_level=...] [screen=...]")
                return self.vessel_set(pos[1], **kv)
            raise ValueError(f"unknown vessel action: {action}")

        if name == "kli":
            self.require_pos(pos, 1, "kli requires a value")
            return self.set_kli(self.resolve(pos[0]))
        if name == "or":
            self.require_pos(pos, 1, "or requires a value")
            return self.draw_or(self.resolve(pos[0]))
        if name == "or_set":
            self.require_pos(pos, 1, "or_set requires a value")
            return self.set_or(self.resolve(pos[0]))
        if name == "noise":
            self.require_pos(pos, 1, "noise requires a value")
            return self.add_noise(self.resolve(pos[0]))
        if name == "noise_set":
            self.require_pos(pos, 1, "noise_set requires a value")
            return self.set_noise(self.resolve(pos[0]))
        if name == "screen":
            self.require_pos(pos, 1, "screen requires a value")
            return self.set_screen(self.resolve(pos[0]))
        if name == "tzimtzum":
            return self.tzimtzum(pos[0] if pos else "medium")
        if name == "masach":
            return self.masach(pos[0] if pos else "truth")
        if name == "shevira":
            return self.shevira()
        if name == "tikkun":
            return self.tikkun()
        if name == "chokhmah":
            return self.chokhmah(*[str(self.resolve(x)) for x in pos])
        if name == "binah":
            return self.binah(*[str(self.resolve(x)) for x in pos])
        if name == "daat":
            return self.daat(*[str(self.resolve(x)) for x in pos])
        if name == "remember":
            self.require_pos(pos, 1, "remember requires a key")
            return self.remember(pos[0], *pos[1:])
        if name == "recall":
            self.require_pos(pos, 1, "recall requires a key")
            return self.recall(pos[0])

        if name == "db":
            self.require_pos(pos, 1, "db requires action")
            action = pos[0]
            if action == "remember":
                self.require_pos(pos, 2, "db remember <key>")
                return self.db_remember(pos[1])
            if action == "recall":
                self.require_pos(pos, 2, "db recall <key>")
                return self.db_recall(pos[1])
            if action == "save_state":
                self.require_pos(pos, 2, "db save_state <label>")
                return self.db_save_state(pos[1])
            if action == "load_state":
                self.require_pos(pos, 2, "db load_state <label>")
                return self.db_load_state(pos[1])
            raise ValueError(f"unknown db action: {action}")

        if name == "agent":
            self.require_pos(pos, 1, "agent requires mode")
            return self.agent(pos[0], *pos[1:])

        if name == "superpose":
            self.require_pos(pos, 2, "superpose requires a name and options")
            return self.superpose(pos[0], *pos[1:])
        if name == "entangle":
            if len(pos) != 2:
                raise ValueError("entangle requires exactly two names")
            return self.entangle(pos[0], pos[1])
        if name == "measure":
            return self.measure(pos[0] if pos else None)
        if name == "pipeline":
            self.require_pos(pos, 1, "pipeline requires steps")
            return self.pipeline(*pos)
        if name == "call":
            self.require_pos(pos, 1, "call requires function name")
            return self.call_function(pos[0], [self.resolve(x) for x in pos[1:]])
        if name == "export_ir":
            self.require_pos(pos, 1, "export_ir requires path")
            return self.export_ir(pos[0])
        if name == "status":
            return self.status()
        if name == "expr_stats":
            stats = self.expression_stats()
            self.s.last_result = stats
            self.log(f"[expr_stats] {json.dumps(stats, ensure_ascii=False, sort_keys=True)}")
            return stats
        if name == "trace":
            mode = (pos[0].lower() if pos else "status")
            if mode in {"on", "true", "1"}:
                return self.set_trace(True)
            if mode in {"off", "false", "0"}:
                return self.set_trace(False)
            self.log(f"[trace:status] enabled={self.config.trace}")
            self.s.last_result = self.config.trace
            return self.config.trace
        if name == "inspect":
            return self.inspect_view(pos[0] if pos else "state")
        if name == "checkpoint":
            self.require_pos(pos, 1, "checkpoint requires label")
            return self.checkpoint(pos[0])
        if name == "recover":
            self.require_pos(pos, 1, "recover requires label")
            return self.recover(pos[0])
        if name == "flush":
            self.flush()
            self.log("[flush] ok")
            return None
        if name in {"manifest", "emit"}:
            return self.manifest(*pos)

        raise ValueError(f"Unknown command: {name}")

    def execute_one(self, node: Node) -> None:
        self.trace_log(f"line={node.line} node={self.node_label(node)}")
        started = time.perf_counter()
        control_allow_fallback = not self.config.control_flow_eval_strict
        if isinstance(node, Import):
            self.import_module(node.module_name)
        elif isinstance(node, Let):
            value = self.eval_runtime_expression(
                node.expr,
                strict=True,
                allow_fallback=control_allow_fallback,
                purpose="let",
            )
            self.set_typed_var(node.var, value, node.type_name)
            self.log(f"[let] {node.var}:{node.type_name}={self.vars[node.var]}")
        elif isinstance(node, If):
            cond = bool(
                self.eval_runtime_expression(
                    node.condition,
                    strict=True,
                    allow_fallback=control_allow_fallback,
                    purpose="if",
                )
            )
            self.log(f"[if] {node.condition} -> {cond}")
            self.execute(node.body if cond else node.else_body)
        elif isinstance(node, While):
            guard = 0
            while bool(
                self.eval_runtime_expression(
                    node.condition,
                    strict=True,
                    allow_fallback=control_allow_fallback,
                    purpose="while",
                )
            ):
                guard += 1
                if guard % 25 == 0:
                    self.log(f"[while:progress] iter={guard} cond={node.condition}")
                if guard > self.config.max_loop_iters:
                    raise RuntimeError(f"while loop guard exceeded ({self.config.max_loop_iters})")
                self.execute(node.body)
            self.log(f"[while] {node.condition} -> False")
        elif isinstance(node, For):
            iterable = self.eval_runtime_expression(
                node.iterable_expr,
                strict=True,
                allow_fallback=control_allow_fallback,
                purpose="for",
            )
            if not isinstance(iterable, Iterable) or isinstance(iterable, (str, bytes, dict)):
                raise TypeError("for iterable must be a non-string iterable")
            snapshot = list(iterable)
            self.log(f"[for] {node.var}:{node.type_name} in {snapshot}")
            for item in snapshot:
                coerced = assert_type(item, node.type_name, node.var)
                self.push_frame({node.var: coerced}, {node.var: normalize_type_name(node.type_name)})
                try:
                    self.execute(node.body)
                finally:
                    self.pop_frame()
        elif isinstance(node, FuncDef):
            self.functions[node.name] = node
            signature = ", ".join(f"{p.name}:{p.type_name}" for p in node.params)
            self.log(f"[func] registered {node.name}({signature})")
        elif isinstance(node, Return):
            value = (
                self.eval_runtime_expression(
                    node.expr,
                    strict=True,
                    allow_fallback=control_allow_fallback,
                    purpose="return",
                )
                if node.expr else self.s.last_result
            )
            raise ReturnSignal(value)
        elif isinstance(node, Command):
            self.execute_command(node)
        else:
            raise TypeError(f"Unknown node type: {type(node).__name__}")
        self.nodes_executed += 1
        if self.config.profile:
            elapsed_ms = (time.perf_counter() - started) * 1000.0
            self.log(f"[profile] line={node.line} node={self.node_label(node)} ms={elapsed_ms:.3f}")

    def execute(self, nodes: List[Node]) -> ExecutionReport:
        """Execute a list of AST nodes and return a run-specific report.

        This method computes per-run statistics by taking a snapshot of the current counters and errors.
        """
        started = time.perf_counter()
        old_errors_count = len(self.errors)
        old_nodes_count = self.nodes_executed
        for node in nodes:
            try:
                self.execute_one(node)
            except ReturnSignal:
                raise
            except Exception as e:
                self.record_error(node.line, e)
                if not self.config.continue_on_error:
                    raise RuntimeError(f"Line {node.line}: {e}") from e
                if len(self.errors) - old_errors_count >= self.config.max_errors:
                    raise RuntimeError(f"maximum error budget reached ({self.config.max_errors})") from e
        run_errors = self.errors[old_errors_count:]
        run_nodes = self.nodes_executed - old_nodes_count
        ok = len(run_errors) == 0
        report = ExecutionReport(
            ok=ok,
            nodes_executed=run_nodes,
            errors=list(run_errors),
            elapsed_ms=(time.perf_counter() - started) * 1000.0,
        )
        return report


# -----------------------------------------------------------------------------
# 10. DEMO / VALIDATION / SELF TESTS / REPL
# -----------------------------------------------------------------------------

