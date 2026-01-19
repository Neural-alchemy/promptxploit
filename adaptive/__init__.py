# rapture/adaptive/__init__.py
"""
Adaptive attack engine for Rapture
Uses mini SLM (local or API) to evolve attacks based on target responses
"""

from .mutation_engine import MutationEngine, AdaptiveAttacker
from .api_mutation_engine import APIMutationEngine
from .strategies import (
    ParaphraseMutation,
    EncodingMutation,
    CombinationMutation,
    ContextMutation
)

__all__ = [
    "MutationEngine",          # Local LLM
    "APIMutationEngine",        # API-based
    "AdaptiveAttacker",
    "ParaphraseMutation",
    "EncodingMutation",
    "CombinationMutation",
    "ContextMutation",
]
