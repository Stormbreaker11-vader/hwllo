#!/usr/bin/env python3
"""
ContextGraph - Core Knowledge Graph Implementation

A portable knowledge graph system for AI context management.
Stores concepts, relationships, and conversation history in a graph structure
that can be exported and restored across any AI model, machine, or platform.
"""

import json
import hashlib
from datetime import datetime
from typing import Any, Dict, List, Optional, Set, Tuple
from dataclasses import dataclass, field, asdict
import base64


# Global default instance for module-level functions
_default_graph: Optional['KnowledgeGraph'] = None


@dataclass
class Node:
    """Represents a node in the knowledge graph."""
    id: str
    label: str
    content: Any
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    
    def to_dict(self) -> Dict:
        return {
            'id': self.id,
            'label': self.label,
            'content': self.content,
            'metadata': self.metadata,
            'created_at': self.created_at
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Node':
        return cls(**data)


@dataclass
class Edge:
    """Represents a relationship between two nodes."""
    source: str
    target: str
    relation: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict:
        return {
            'source': self.source,
            'target': self.target,
            'relation': self.relation,
            'metadata': self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Edge':
        return cls(**data)


class KnowledgeGraph:
    """
    A knowledge graph that stores context and generates portable representations.
    
    Features:
    - Automatic context storage
    - Portable serialization (JSON-based)
    - Compact encoding for easy copy-paste
    - Platform-independent restoration
    """
    
    def __init__(self, session_name: str = "default"):
        self.nodes: Dict[str, Node] = {}
        self.edges: List[Edge] = []
        self.context_stack: List[Dict] = []
        self.session_name = session_name
        self.session_id: str = self._generate_session_id()
        self.created_at = datetime.now().isoformat()
        
    def _generate_session_id(self) -> str:
        """Generate a unique session identifier."""
        timestamp = datetime.now().isoformat()
        return hashlib.md5(timestamp.encode()).hexdigest()[:12]
    
    def _generate_node_id(self, content: str) -> str:
        """Generate a unique ID for a node based on its content."""
        return hashlib.sha256(content.encode()).hexdigest()[:16]
    
    def add_concept(self, concept: str, content: Any, 
                   category: str = "general", **metadata) -> str:
        """
        Add a concept to the knowledge graph.
        
        Args:
            concept: The name/label of the concept
            content: The actual content/data
            category: Category of the concept
            **metadata: Additional metadata
            
        Returns:
            The node ID
        """
        node_id = self._generate_node_id(f"{concept}:{str(content)}")
        
        if node_id not in self.nodes:
            node = Node(
                id=node_id,
                label=concept,
                content=content,
                metadata={
                    'category': category,
                    **metadata
                }
            )
            self.nodes[node_id] = node
        
        # Track in context stack
        self.context_stack.append({
            'type': 'concept',
            'node_id': node_id,
            'timestamp': datetime.now().isoformat()
        })
        
        return node_id
    
    def add_relationship(self, concept1: str, concept2: str, 
                        relation: str, **metadata) -> None:
        """
        Add a relationship between two concepts.
        
        Args:
            concept1: First concept (label or ID)
            concept2: Second concept (label or ID)
            relation: The relationship type
            **metadata: Additional metadata
        """
        # Find node IDs
        source_id = self._find_node_id(concept1)
        target_id = self._find_node_id(concept2)
        
        if source_id and target_id:
            edge = Edge(
                source=source_id,
                target=target_id,
                relation=relation,
                metadata=metadata
            )
            self.edges.append(edge)
            
            self.context_stack.append({
                'type': 'relationship',
                'edge': edge.to_dict(),
                'timestamp': datetime.now().isoformat()
            })
    
    def _find_node_id(self, identifier: str) -> Optional[str]:
        """Find a node ID by label or return the ID if already provided."""
        if identifier in self.nodes:
            return identifier
        
        for node_id, node in self.nodes.items():
            if node.label == identifier:
                return node_id
        
        return None
    
    def add_context(self, context_text: str, source: str = "user", 
                   **metadata) -> str:
        """
        Add arbitrary context (e.g., conversation turns, notes).
        
        Args:
            context_text: The context content
            source: Source of the context (user, assistant, system)
            **metadata: Additional metadata
            
        Returns:
            The node ID
        """
        return self.add_concept(
            concept=f"context_{len(self.context_stack)}",
            content=context_text,
            category="context",
            source=source,
            **metadata
        )
    
    def get_portable_context(self, compact: bool = True) -> str:
        """
        Generate a portable representation of the entire knowledge graph.
        
        Args:
            compact: If True, returns a compact base64-encoded string
                    If False, returns formatted JSON
                    
        Returns:
            A string that can be pasted into any AI model
        """
        # Build the complete state
        state = {
            'knowledge_graph_version': '1.0',
            'session_id': self.session_id,
            'exported_at': datetime.now().isoformat(),
            'nodes': [node.to_dict() for node in self.nodes.values()],
            'edges': [edge.to_dict() for edge in self.edges],
            'context_stack': self.context_stack,
            'statistics': {
                'total_nodes': len(self.nodes),
                'total_edges': len(self.edges),
                'context_entries': len(self.context_stack)
            }
        }
        
        if compact:
            # Convert to JSON string, then base64 encode for compactness
            json_str = json.dumps(state, separators=(',', ':'))
            encoded = base64.b64encode(json_str.encode()).decode()
            
            # Create a formatted block with instructions
            output = f"""# KNOWLEDGE GRAPH CONTEXT BLOCK
# Copy this entire block and paste it into any AI model to restore context

## SESSION INFO
Session ID: {self.session_id}
Exported: {state['exported_at']}
Nodes: {state['statistics']['total_nodes']} | Edges: {state['statistics']['total_edges']}

## PORTABLE CONTEXT DATA
```kg_context
{encoded}
```

## INSTRUCTIONS FOR AI MODELS
To restore this context, parse the base64-encoded data in the kg_context block above.
Decode it as JSON to reconstruct the knowledge graph state.
Use this context to continue the conversation with full awareness of previous interactions.
"""
            return output
        else:
            # Return pretty-printed JSON
            return json.dumps(state, indent=2)
    
    @classmethod
    def from_portable_context(cls, context_block: str) -> 'KnowledgeGraph':
        """
        Restore a knowledge graph from a portable context block.
        
        Args:
            context_block: The previously generated context block
            
        Returns:
            A restored KnowledgeGraph instance
        """
        import re
        
        # Extract the base64-encoded data
        match = re.search(r'```kg_context\n([A-Za-z0-9+/=]+)\n```', context_block)
        if not match:
            # Try to decode the entire block if no markers found
            encoded_data = context_block.strip()
        else:
            encoded_data = match.group(1)
        
        # Decode and parse
        try:
            json_str = base64.b64decode(encoded_data).decode()
            state = json.loads(json_str)
        except Exception as e:
            raise ValueError(f"Failed to decode context: {e}")
        
        # Reconstruct the graph
        kg = cls()
        kg.session_id = state.get('session_id', kg.session_id)
        
        # Restore nodes
        for node_data in state.get('nodes', []):
            node = Node.from_dict(node_data)
            kg.nodes[node.id] = node
        
        # Restore edges
        for edge_data in state.get('edges', []):
            edge = Edge.from_dict(edge_data)
            kg.edges.append(edge)
        
        # Restore context stack
        kg.context_stack = state.get('context_stack', [])
        
        return kg
    
    def query(self, concept: str) -> Optional[Any]:
        """Query the knowledge graph for a concept."""
        node_id = self._find_node_id(concept)
        if node_id:
            return self.nodes[node_id].content
        return None
    
    def get_related(self, concept: str, relation_type: Optional[str] = None) -> List[Tuple[str, str, Any]]:
        """
        Get all concepts related to a given concept.
        
        Returns:
            List of tuples: (relation, target_label, target_content)
        """
        results = []
        node_id = self._find_node_id(concept)
        
        if not node_id:
            return results
        
        for edge in self.edges:
            if relation_type and edge.relation != relation_type:
                continue
                
            if edge.source == node_id:
                target_node = self.nodes.get(edge.target)
                if target_node:
                    results.append((edge.relation, target_node.label, target_node.content))
            elif edge.target == node_id:
                source_node = self.nodes.get(edge.source)
                if source_node:
                    results.append((f"inverse:{edge.relation}", source_node.label, source_node.content))
        
        return results
    
    def clear(self):
        """Clear the knowledge graph."""
        self.nodes.clear()
        self.edges.clear()
        self.context_stack.clear()
        self.session_id = self._generate_session_id()
    
    def summary(self) -> str:
        """Generate a human-readable summary of the knowledge graph."""
        lines = [
            f"Knowledge Graph Summary",
            f"======================",
            f"Session ID: {self.session_id}",
            f"Total Nodes: {len(self.nodes)}",
            f"Total Relationships: {len(self.edges)}",
            f"Context Entries: {len(self.context_stack)}",
            "",
            "Nodes:",
        ]
        
        for node in self.nodes.values():
            lines.append(f"  - {node.label} ({node.metadata.get('category', 'general')})")
        
        if self.edges:
            lines.append("\nRelationships:")
            for edge in self.edges:
                source = self.nodes.get(edge.source, Node(id='', label='?', content=''))
                target = self.nodes.get(edge.target, Node(id='', label='?', content=''))
                lines.append(f"  - {source.label} --[{edge.relation}]--> {target.label}")
        
        return "\n".join(lines)


# Convenience functions for quick usage
_default_kg: Optional[KnowledgeGraph] = None

def get_knowledge_graph() -> KnowledgeGraph:
    """Get or create the default knowledge graph instance."""
    global _default_kg
    if _default_kg is None:
        _default_kg = KnowledgeGraph()
    return _default_kg

def store_context(text: str, **kwargs) -> str:
    """Store a piece of context in the default knowledge graph."""
    kg = get_knowledge_graph()
    return kg.add_context(text, **kwargs)

def store_concept(label: str, content: Any, **kwargs) -> str:
    """Store a concept in the default knowledge graph."""
    kg = get_knowledge_graph()
    return kg.add_concept(label, content, **kwargs)

def link_concepts(concept1: str, concept2: str, relation: str, **kwargs) -> None:
    """Link two concepts in the default knowledge graph."""
    kg = get_knowledge_graph()
    kg.add_relationship(concept1, concept2, relation, **kwargs)

def export_context(compact: bool = True) -> str:
    """Export the current context as a portable string."""
    kg = get_knowledge_graph()
    return kg.get_portable_context(compact=compact)

def import_context(context_block: str) -> KnowledgeGraph:
    """Import context from a portable string."""
    global _default_kg
    _default_kg = KnowledgeGraph.from_portable_context(context_block)
    return _default_kg

def get_graph_summary(kg: Optional[KnowledgeGraph] = None) -> str:
    """Get a human-readable summary of the knowledge graph."""
    if kg is None:
        kg = get_knowledge_graph()
    return kg.summary()


if __name__ == "__main__":
    # Demo usage
    print("Knowledge Graph Base - Demo")
    print("=" * 50)
    
    # Create a new knowledge graph
    kg = KnowledgeGraph()
    
    # Add some concepts
    kg.add_concept("Python", "Programming language", category="technology", level="beginner")
    kg.add_concept("Machine Learning", "AI technique", category="technology", level="advanced")
    kg.add_concept("Data Science", "Interdisciplinary field", category="technology")
    
    # Add relationships
    kg.add_relationship("Python", "Machine Learning", "used_for")
    kg.add_relationship("Python", "Data Science", "used_for")
    kg.add_relationship("Machine Learning", "Data Science", "subset_of")
    
    # Add conversation context
    kg.add_context("User asked about creating a knowledge graph system", source="user")
    kg.add_context("System explained the architecture and features", source="assistant")
    
    # Display summary
    print(kg.summary())
    print("\n" + "=" * 50)
    
    # Export portable context
    print("\nExporting portable context...")
    portable = kg.get_portable_context(compact=True)
    print(portable[:500] + "..." if len(portable) > 500 else portable)
    
    print("\n" + "=" * 50)
    print("Demo complete! You can copy the exported context and paste it")
    print("into any AI model to restore this knowledge graph.")
