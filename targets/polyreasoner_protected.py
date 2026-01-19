"""
Rapture Target: PolyReasoner v3 (Protected with PromptShield)
Tests the protected PolyReasoner with PromptShield L5
"""

import sys
from pathlib import Path

# Add poly-reasoner-v3 to path
poly_path = str(Path(__file__).parent.parent.parent / 'poly-reasoner-v3')
if poly_path not in sys.path:
    sys.path.insert(0, poly_path)

# Import from poly-reasoner-v3 main_protected module
import importlib.util
spec = importlib.util.spec_from_file_location(
    "polyreasoner_protected",
    Path(poly_path) / "main_protected.py"
)
protected_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(protected_module)

# Initialize protected reasoner once
reasoner = protected_module.SecurePolyreasoner(shield_level=5)

def run(prompt: str) -> str:
    """
    Target function for Rapture.
    Takes attack payload, returns protected PolyReasoner response.
    """
    try:
        response = reasoner.process(prompt)
        return response
    except Exception as e:
        return f"Error: {str(e)}"
