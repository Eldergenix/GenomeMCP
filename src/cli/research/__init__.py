"""
Research module for GenomeMCP.

Integrates Denario multi-agent system for end-to-end scientific research.
"""

from .pipeline import GenomicsResearchPipeline
from .commands import research_app

__all__ = [
    "GenomicsResearchPipeline",
    "research_app",
]
