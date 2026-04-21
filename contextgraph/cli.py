#!/usr/bin/env python3
"""
ContextGraph CLI - Command Line Interface

Usage:
    cg init                  Initialize a new knowledge graph session
    cg add <text>            Add context or concept
    cg link <from> <to> [rel]  Link two concepts
    cg export                Export portable context block
    cg import <file>         Import context from file
    cg status                Show graph summary
    cg serve                 Start API server
"""

import click
import json
import sys
from pathlib import Path

from .core import (
    KnowledgeGraph,
    export_context as export_graph_context,
    import_context as import_graph_context,
    get_graph_summary,
)


@click.group()
@click.version_option(version='1.0.0')
def main():
    """ContextGraph - Portable AI Context Management"""
    pass


@main.command()
@click.option('--name', default='default', help='Session name')
def init(name):
    """Initialize a new knowledge graph session."""
    kg = KnowledgeGraph(session_name=name)
    data_file = Path(f'kg_session_{name}.json')
    
    if data_file.exists():
        click.echo(f"Session '{name}' already exists.")
    else:
        save_session(kg, data_file)
        click.echo(f"Initialized new session '{name}'")
        click.echo(f"Data file: {data_file}")


@main.command()
@click.argument('text')
@click.option('--label', default='context', help='Node label/type')
@click.option('--category', default=None, help='Category for concepts')
def add(text, label, category):
    """Add context or concept to the graph."""
    kg = load_or_create_session()
    
    if category:
        kg.add_concept(text, text, category=category)
        click.echo(f"Added concept: {text} ({category})")
    else:
        kg.add_context(text)
        click.echo(f"Added context: {text[:50]}...")
    
    save_session(kg)


@main.command()
@click.argument('from_node')
@click.argument('to_node')
@click.argument('relation', default='related_to')
def link(from_node, to_node, relation):
    """Link two concepts in the graph."""
    kg = load_or_create_session()
    kg.add_relationship(from_node, to_node, relation)
    save_session(kg)
    click.echo(f"Linked: {from_node} --[{relation}]--> {to_node}")


@main.command()
@click.option('--output', '-o', default=None, help='Output file path')
def export(output):
    """Export portable context block."""
    kg = load_or_create_session()
    portable = export_graph_context(kg)
    
    if output:
        with open(output, 'w') as f:
            f.write(portable)
        click.echo(f"Exported to {output}")
    else:
        click.echo(portable)


@main.command()
@click.argument('input_file')
def import_ctx(input_file):
    """Import context from file or stdin."""
    if input_file == '-':
        content = sys.stdin.read()
    else:
        with open(input_file, 'r') as f:
            content = f.read()
    
    kg = import_graph_context(content)
    save_session(kg)
    click.echo("Context imported successfully!")
    click.echo(get_graph_summary(kg))


@main.command()
def status():
    """Show current graph summary."""
    kg = load_or_create_session()
    click.echo(get_graph_summary(kg))


@main.command()
@click.option('--host', default='0.0.0.0')
@click.option('--port', default=8000)
def serve(host, port):
    """Start the API server."""
    try:
        import uvicorn
        from .api import app
        click.echo(f"Starting server at http://{host}:{port}")
        uvicorn.run(app, host=host, port=port)
    except ImportError:
        click.echo("Error: uvicorn not installed. Run: pip install uvicorn fastapi")
        sys.exit(1)


def get_session_file(name='default'):
    """Get the session file path."""
    return Path(f'kg_session_{name}.json')


def load_or_create_session(name='default'):
    """Load existing session or create new one."""
    data_file = get_session_file(name)
    
    if data_file.exists():
        with open(data_file, 'r') as f:
            data = json.load(f)
        kg = KnowledgeGraph(session_name=name)
        kg.nodes = {k: Node(**v) for k, v in data.get('nodes', {}).items()}
        kg.edges = [Edge(**e) for e in data.get('edges', [])]
        kg.context_stack = data.get('context_stack', [])
        return kg
    else:
        return KnowledgeGraph(session_name=name)


def save_session(kg, data_file=None):
    """Save session to file."""
    if data_file is None:
        data_file = get_session_file(kg.session_name)
    
    data = {
        'session_name': kg.session_name,
        'session_id': kg.session_id,
        'created_at': kg.created_at,
        'nodes': {k: asdict(v) for k, v in kg.nodes.items()},
        'edges': [asdict(e) for e in kg.edges],
        'context_stack': kg.context_stack,
    }
    
    with open(data_file, 'w') as f:
        json.dump(data, f, indent=2)


# Need to import these after definition
from .core import Node, Edge, asdict


if __name__ == '__main__':
    main()
