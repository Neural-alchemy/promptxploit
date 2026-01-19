"""
Rapture Target: PolyReasoner v3 (Unprotected)
Tests the original PolyReasoner without PromptShield
"""

import sys
from pathlib import Path

# Add poly-reasoner-v3 to path
poly_path = str(Path(__file__).parent.parent.parent / 'poly-reasoner-v3')
if poly_path not in sys.path:
    sys.path.insert(0, poly_path)

# Import from poly-reasoner-v3 main module
import importlib.util
spec = importlib.util.spec_from_file_location(
    "polyreasoner_main",
    Path(poly_path) / "main.py"
)
polyreasoner_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(polyreasoner_module)

# Initialize reasoner once
reasoner = polyreasoner_module.Polyreasoner()

def run(prompt: str) -> str:
    """
    Target function for Rapture.
    Takes attack payload, returns PolyReasoner response.
    """
    try:
        response = reasoner.process(prompt)
        return response
    except Exception as e:
        return f"Error: {str(e)}"
