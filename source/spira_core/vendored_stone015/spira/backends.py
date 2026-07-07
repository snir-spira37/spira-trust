from __future__ import annotations
import math, os
from typing import Any, Dict, List, Optional

class LLMBackend:
    def generate(self, prompt: str, mode: str = "default") -> str:
        raise NotImplementedError


class MockLLMBackend(LLMBackend):
    def generate(self, prompt: str, mode: str = "default") -> str:
        prompt = prompt.strip()
        modes = {
            "creative": "creative_response",
            "analysis": "analysis_response",
            "judge": "judged_response",
            "plan": "plan_response",
        }
        return f"{modes.get(mode, 'llm_response')}({prompt})"


class OpenAICompatibleLLMBackend(LLMBackend):
    def __init__(self, api_key: Optional[str] = None, base_url: Optional[str] = None, model: Optional[str] = None, timeout: float = 20.0):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.base_url = base_url or os.getenv("OPENAI_BASE_URL")
        self.model = model or os.getenv("OPENAI_MODEL", "gpt-4o-mini")
        self.timeout = timeout
        self._client = None
        try:
            from openai import OpenAI
            kwargs = {k: v for k, v in {"api_key": self.api_key, "base_url": self.base_url, "timeout": self.timeout}.items() if v is not None}
            self._client = OpenAI(**kwargs)
        except Exception:
            self._client = None

    def generate(self, prompt: str, mode: str = "default") -> str:
        if self._client is None:
            return f"fallback_openai_unavailable({prompt})"
        system_map = {
            "creative": "You are a creative reasoning engine.",
            "analysis": "You are an analytical reasoning engine.",
            "judge": "You are a careful judge focused on coherence and truthfulness.",
            "plan": "You are a compact planning engine.",
            "default": "You are a helpful reasoning engine.",
        }
        try:
            resp = self._client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_map.get(mode, system_map["default"])},
                    {"role": "user", "content": prompt},
                ],
                temperature=0.4 if mode == "judge" else 0.8 if mode == "creative" else 0.5,
            )
            return resp.choices[0].message.content or ""
        except Exception as e:
            return f"openai_error({e})"


class QuantumBackend:
    def superpose(self, options: List[Any]) -> Dict[str, Any]:
        raise NotImplementedError

    def entangle(self, left: str, right: str) -> Dict[str, Any]:
        raise NotImplementedError

    def measure(self, options: List[Any], prefer_balance: bool = True) -> Any:
        raise NotImplementedError


class MockQuantumBackend(QuantumBackend):
    def superpose(self, options: List[Any]) -> Dict[str, Any]:
        return {"state": "superposed", "options": options}

    def entangle(self, left: str, right: str) -> Dict[str, Any]:
        return {"state": "entangled", "pair": (left, right)}

    def measure(self, options: List[Any], prefer_balance: bool = True) -> Any:
        if not options:
            return None
        if prefer_balance:
            for item in options:
                if str(item) in {"tiferet", "תפארת", "balance", "balanced"}:
                    return item
        return options[min(len(options) - 1, len(options) // 2)]


class QiskitQuantumBackend(QuantumBackend):
    def __init__(self) -> None:
        self.available = False
        self.circuit_history: List[Any] = []
        try:
            from qiskit import QuantumCircuit
            from qiskit.quantum_info import Statevector
            self.QuantumCircuit = QuantumCircuit
            self.Statevector = Statevector
            self.available = True
        except Exception:
            self.available = False

    def superpose(self, options: List[Any]) -> Dict[str, Any]:
        if not self.available:
            return {"backend": "fallback", "state": "superposed", "options": options}
        n_qubits = max(1, math.ceil(math.log2(max(1, len(options)))))
        qc = self.QuantumCircuit(n_qubits)
        for i in range(n_qubits):
            qc.h(i)
        self.circuit_history.append(qc)
        try:
            sv = self.Statevector.from_instruction(qc)
            probs = sv.probabilities_dict()
        except Exception:
            probs = {}
        return {"backend": "qiskit", "state": "superposed", "qubits": n_qubits, "options": options, "probabilities": probs}

    def entangle(self, left: str, right: str) -> Dict[str, Any]:
        if not self.available:
            return {"backend": "fallback", "state": "entangled", "pair": (left, right)}
        qc = self.QuantumCircuit(2)
        qc.h(0)
        qc.cx(0, 1)
        self.circuit_history.append(qc)
        try:
            sv = self.Statevector.from_instruction(qc)
            probs = sv.probabilities_dict()
        except Exception:
            probs = {}
        return {"backend": "qiskit", "state": "entangled", "pair": (left, right), "probabilities": probs}

    def measure(self, options: List[Any], prefer_balance: bool = True) -> Any:
        if not options:
            return None
        if prefer_balance:
            for item in options:
                if str(item) in {"tiferet", "תפארת", "balance", "balanced"}:
                    return item
        return options[0]


