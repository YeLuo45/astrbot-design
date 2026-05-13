"""
Multi-Agent Teams - Built-in Agent Combinations

Provides pre-configured teams for common multi-agent scenarios:
- CodeReviewTeam: Code generation + review + critique
- ResearchTeam: Web search + document analysis + synthesis
- DebateTeam: Pro/con arguments + judgment
"""

from .code_review import CodeReviewTeam
from .debate import DebateTeam
from .research import ResearchTeam

__all__ = [
    "CodeReviewTeam",
    "ResearchTeam",
    "DebateTeam",
]
