"""
ContextGraph - Portable Knowledge Graph for AI Context Management
"""

from .core import (
    KnowledgeGraph,
    store_context,
    store_concept,
    link_concepts,
    export_context,
    import_context,
    get_graph_summary,
)

__version__ = "1.0.0"
__all__ = [
    "KnowledgeGraph",
    "store_context",
    "store_concept",
    "link_concepts",
    "export_context",
    "import_context",
    "get_graph_summary",
]
