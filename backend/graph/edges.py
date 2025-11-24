# ============================================================================
# FILE: backend/graph/edges.py
# ============================================================================

from backend.core.state import ContentState
from typing import Literal


def should_continue(state: ContentState) -> Literal["writer", "end"]:
    """Conditional edge: Continue loop or end"""
    
    if state['loop_continue']:
        return "writer"
    else:
        return "end"
