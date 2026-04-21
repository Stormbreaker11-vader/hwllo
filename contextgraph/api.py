"""
ContextGraph API - FastAPI Server

Provides REST API endpoints for knowledge graph operations.
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import json

from .core import (
    KnowledgeGraph,
    export_context,
    import_context,
    get_graph_summary,
)

app = FastAPI(
    title="ContextGraph API",
    description="Portable Knowledge Graph for AI Context Management",
    version="1.0.0",
)

# In-memory session storage (for production, use a database)
sessions: Dict[str, KnowledgeGraph] = {}


class ConceptRequest(BaseModel):
    label: str
    content: str
    category: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class LinkRequest(BaseModel):
    from_node: str
    to_node: str
    relation: str = "related_to"


class ContextRequest(BaseModel):
    text: str
    metadata: Optional[Dict[str, Any]] = None


class ImportRequest(BaseModel):
    context_block: str


@app.get("/")
async def root():
    return {
        "message": "ContextGraph API",
        "version": "1.0.0",
        "endpoints": [
            "POST /session/create",
            "GET /session/{session_id}",
            "POST /session/{session_id}/concept",
            "POST /session/{session_id}/context",
            "POST /session/{session_id}/link",
            "GET /session/{session_id}/export",
            "POST /import",
            "GET /session/{session_id}/summary",
        ],
    }


@app.post("/session/create")
async def create_session(session_name: Optional[str] = None):
    """Create a new knowledge graph session."""
    kg = KnowledgeGraph(session_name=session_name or "default")
    sessions[kg.session_id] = kg
    return {
        "session_id": kg.session_id,
        "session_name": kg.session_name,
        "created_at": kg.created_at,
    }


@app.get("/session/{session_id}")
async def get_session(session_id: str):
    """Get session information."""
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    kg = sessions[session_id]
    return {
        "session_id": kg.session_id,
        "session_name": kg.session_name,
        "created_at": kg.created_at,
        "node_count": len(kg.nodes),
        "edge_count": len(kg.edges),
    }


@app.post("/session/{session_id}/concept")
async def add_concept(session_id: str, request: ConceptRequest):
    """Add a concept to the knowledge graph."""
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    kg = sessions[session_id]
    node_id = kg.store_concept(
        label=request.label,
        content=request.content,
        category=request.category,
        metadata=request.metadata,
    )
    
    return {"node_id": node_id, "label": request.label}


@app.post("/session/{session_id}/context")
async def add_context(session_id: str, request: ContextRequest):
    """Add context to the knowledge graph."""
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    kg = sessions[session_id]
    kg.store_context(request.text, request.metadata)
    
    return {"message": "Context added", "total_context": len(kg.context_history)}


@app.post("/session/{session_id}/link")
async def add_link(session_id: str, request: LinkRequest):
    """Link two concepts in the knowledge graph."""
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    kg = sessions[session_id]
    success = kg.link_concepts(
        request.from_node,
        request.to_node,
        request.relation,
    )
    
    if not success:
        raise HTTPException(status_code=400, detail="Failed to create link")
    
    return {"message": "Link created"}


@app.get("/session/{session_id}/export")
async def export_session(session_id: str):
    """Export portable context block."""
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    kg = sessions[session_id]
    portable = export_context(kg)
    
    return {"portable_context": portable}


@app.post("/import")
async def import_session(request: ImportRequest):
    """Import context from a portable block."""
    try:
        kg = import_context(request.context_block)
        sessions[kg.session_id] = kg
        return {
            "session_id": kg.session_id,
            "message": "Context imported successfully",
            "node_count": len(kg.nodes),
            "edge_count": len(kg.edges),
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Import failed: {str(e)}")


@app.get("/session/{session_id}/summary")
async def get_summary(session_id: str):
    """Get knowledge graph summary."""
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    kg = sessions[session_id]
    summary = get_graph_summary(kg)
    
    # Parse the summary text into structured data
    lines = summary.split('\n')
    nodes = []
    relationships = []
    
    in_nodes = False
    in_relationships = False
    
    for line in lines:
        if line.strip() == 'Nodes:':
            in_nodes = True
            in_relationships = False
            continue
        elif line.strip() == 'Relationships:':
            in_nodes = False
            in_relationships = True
            continue
        elif line.startswith('='):
            in_nodes = False
            in_relationships = False
            continue
        
        if in_nodes and line.strip().startswith('- '):
            nodes.append(line.strip()[2:])
        elif in_relationships and line.strip().startswith('- '):
            relationships.append(line.strip()[2:])
    
    return {
        "session_id": kg.session_id,
        "total_nodes": len(kg.nodes),
        "total_relationships": len(kg.edges),
        "nodes": nodes,
        "relationships": relationships,
    }


@app.delete("/session/{session_id}")
async def delete_session(session_id: str):
    """Delete a session."""
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    del sessions[session_id]
    return {"message": "Session deleted"}
