from __future__ import annotations
from typing import Dict

BUILTIN_MODULES: Dict[str, str] = {
    "std.balance": """
func choose_balance:
    superpose policy chesed tiferet gevurah
    measure policy
    return last_result
""",
    "std.repair": """
func stabilize:
    while shevira:
        tikkun
    return coherence
""",
    "std.agent": """
func triad source:str:
    chokhmah source
    binah
    daat
    return last_result
""",
}


