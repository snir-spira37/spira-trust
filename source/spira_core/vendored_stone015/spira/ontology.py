from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, List, Tuple

@dataclass(frozen=True)
class Concept:
    name: str
    hebrew: str
    domain: str
    description: str
    compute: str
    ai_role: str
    quantum_role: str = "none"
    aliases: Tuple[str, ...] = ()


KABBALAH_CONCEPTS: List[Concept] = [
    Concept("or", "אור", "kabbalah", "light / signal", "signal_energy", "activation", "amplitude", aliases=("light",)),
    Concept("kli", "כלי", "kabbalah", "vessel / capacity", "bounded_capacity", "context_container", "register"),
    Concept("tzimtzum", "צמצום", "kabbalah", "contraction / reduction", "constraint", "context_compression", "state_space_restriction"),
    Concept("masach", "מסך", "kabbalah", "screen / truth filter", "gate_filter", "truth_gate", "measurement_filter"),
    Concept("shevira", "שבירה", "kabbalah", "shattering under overload", "overflow_failure", "instability", "decoherence"),
    Concept("tikkun", "תיקון", "kabbalah", "repair / rectification", "recalibration", "stabilization", "error_correction"),
    Concept("chokhmah", "חכמה", "kabbalah", "wisdom spark", "initial_generation", "generator", "proposal", aliases=("chochma", "wisdom")),
    Concept("binah", "בינה", "kabbalah", "structural understanding", "structural_analysis", "analyzer", "inspection", aliases=("bina",)),
    Concept("daat", "דעת", "kabbalah", "integrated knowledge", "integration", "judge", "collapse_selection", aliases=("daas", "knowledge")),
    Concept("chesed", "חסד", "kabbalah", "expansion / kindness", "expansion_bias", "creative_expansion", "superposition_growth", aliases=("chessed",)),
    Concept("gevurah", "גבורה", "kabbalah", "restraint / discipline", "pruning", "regularization", "projection"),
    Concept("tiferet", "תפארת", "kabbalah", "balance / beauty", "balanced_policy", "harmonic_choice", "balanced_state", aliases=("tiferes", "beauty")),
    Concept("netzach", "נצח", "kabbalah", "endurance", "persistence", "optimization_persistence", "coherence_persistence"),
    Concept("hod", "הוד", "kabbalah", "resonance / articulation", "resonance", "presentation", "phase_alignment"),
    Concept("yesod", "יסוד", "kabbalah", "foundation / conduit", "routing_layer", "memory_bridge", "channel"),
    Concept("malchut", "מלכות", "kabbalah", "manifestation / kingdom", "output_layer", "finalization", "measurement_result", aliases=("malchus",)),
    Concept("keter", "כתר", "kabbalah", "crown / ultimate will", "top_objective", "supervision", "global_phase", aliases=("keser",)),
    Concept("ein_sof", "אין סוף", "kabbalah", "the infinite", "unbounded_reference", "possibility_horizon", "continuous_spectrum"),
    Concept("ayin", "אין", "kabbalah", "nothingness", "null_origin", "latent_prior", "vacuum"),
    Concept("reshimo", "רשימו", "kabbalah", "trace / residue", "trace_memory", "memory_residual", "state_remnant"),
    Concept("kavanah", "כוונה", "kabbalah", "intention", "execution_intent", "prompt_intent", "control_parameter"),
    Concept("yichud", "ייחוד", "kabbalah", "union / merge", "merge", "alignment", "entangling_relation"),
]

QUANTUM_CONCEPTS: List[Concept] = [
    Concept("superposition", "סופרפוזיציה", "quantum", "multiple live possibilities", "superposed_candidates", "candidate_set", "superposition"),
    Concept("entanglement", "שזירה", "quantum", "linked dependency", "coupled_state", "cross_variable_dependency", "entanglement"),
    Concept("measurement", "מדידה", "quantum", "state collapse", "selection", "choice", "measurement"),
    Concept("decoherence", "דה-קוהרנטיות", "quantum", "loss of coherence", "stability_loss", "hallucination_analog", "decoherence"),
    Concept("qubit", "קיוביט", "quantum", "quantum bit", "uncertain_bit", "probabilistic_slot", "qubit"),
    Concept("wavefunction", "פונקציית גל", "quantum", "state distribution", "state_distribution", "candidate_landscape", "wavefunction"),
    Concept("amplitude", "משרעת", "quantum", "state weight", "confidence_weight", "logit_weight", "amplitude"),
    Concept("phase", "פאזה", "quantum", "relative phase", "alignment_signal", "reasoning_bias", "phase"),
]

AI_CONCEPTS: List[Concept] = [
    Concept("model", "מודל", "ai", "trained predictor", "predictor", "core_engine"),
    Concept("neural_network", "רשת עצבית", "ai", "layered function system", "deep_model", "core_representation"),
    Concept("transformer", "טרנספורמר", "ai", "attention-based model", "context_model", "llm_core"),
    Concept("attention", "קשב", "ai", "relevance weighting", "focus_mechanism", "focus_allocator"),
    Concept("embedding", "הטבעה", "ai", "vector representation", "representation", "semantic_geometry"),
    Concept("memory", "זיכרון", "ai", "retained information", "state_store", "memory_layer"),
    Concept("retrieval", "שליפה", "ai", "fetch stored knowledge", "lookup", "external_memory_query"),
    Concept("prompt", "פרומפט", "ai", "instructional context", "instruction_frame", "intent_carrier"),
    Concept("policy", "מדיניות", "ai", "action rule", "decision_rule", "behavior_profile"),
]

COMPUTING_CONCEPTS: List[Concept] = [
    Concept("algorithm", "אלגוריתם", "computing", "finite procedure", "procedure", "runnable_rule"),
    Concept("data_structure", "מבנה נתונים", "computing", "organized data form", "storage_shape", "state_storage"),
    Concept("database", "בסיס נתונים", "computing", "persistent storage", "persistent_memory", "knowledge_base"),
]

ALL_CONCEPTS = KABBALAH_CONCEPTS + QUANTUM_CONCEPTS + AI_CONCEPTS + COMPUTING_CONCEPTS


def build_ontology() -> Tuple[Dict[str, Concept], Dict[str, str]]:
    ontology: Dict[str, Concept] = {}
    aliases: Dict[str, str] = {}
    for c in ALL_CONCEPTS:
        ontology[c.name] = c
        aliases[c.name] = c.name
        aliases[c.hebrew] = c.name
        for alias in c.aliases:
            aliases[alias] = c.name
    return ontology, aliases


ONTOLOGY, ALIASES = build_ontology()


def canonical_name(name: str) -> str:
    return ALIASES.get(name, name)


