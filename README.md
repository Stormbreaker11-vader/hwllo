# ContextGraph

**Portable Knowledge Graph for AI Context Management**

Never lose your AI conversation context again. ContextGraph automatically stores your work as a knowledge graph and generates portable blocks you can paste into ANY AI model (ChatGPT, Claude, local LLMs, etc.) to restore full context across any machine, browser, or app.

## 🚀 Features

- **Automatic Context Storage**: Store concepts, relationships, and conversation history
- **Platform Independent**: Works everywhere - any AI model, any machine, any browser
- **Portable Export**: Generate compact, encoded blocks that preserve your entire knowledge graph
- **Multiple Interfaces**: Python library, CLI tool, and REST API
- **No Vendor Lock-in**: Your data is yours - export anytime, use anywhere

## 💰 Business Model

This is a **startup-ready product** with multiple revenue streams:

1. **SaaS Platform**: Hosted service with web UI ($10-50/month)
2. **Enterprise API**: Custom integrations for teams ($500+/month)
3. **Self-hosted License**: One-time fee for on-prem deployment ($2000+)
4. **White-label**: Resell to AI platforms and tool builders

## Installation

### From Source
```bash
git clone https://github.com/yourusername/contextgraph
cd contextgraph
pip install -e .
```

### From PyPI (coming soon)
```bash
pip install contextgraph
```

## Quick Start

### Python Library

```python
from contextgraph import (
    store_context, 
    store_concept, 
    link_concepts, 
    export_context,
    import_context
)

# Store your work
store_context("Building a customer churn prediction model")
store_concept("Random Forest", "Ensemble ML algorithm", category="ML")
store_concept("Feature Engineering", "Creating predictive features", category="Data Science")
link_concepts("Random Forest", "customer churn", "applied_to")
link_concepts("Feature Engineering", "Random Forest", "improves")

# Hit token limit? Export everything!
portable_block = export_context()
print(portable_block)

# Copy that block and paste it into ANY AI model
# In the new AI session:
# kg = import_context(pasted_block)
```

### Command Line

```bash
# Initialize a session
cg init --name my-project

# Add concepts
cg add "Customer churn prediction" --category "project"
cg add "Random Forest" --category "ML"

# Link concepts
cg link "Random Forest" "customer churn" applied_to

# Export when needed
cg export > context_block.txt

# Check status
cg status
```

### REST API

```bash
# Start server
cg serve

# Create session
curl -X POST http://localhost:8000/session/create

# Add concept
curl -X POST http://localhost:8000/session/{id}/concept \
  -H "Content-Type: application/json" \
  -d '{"label": "Random Forest", "content": "ML algorithm", "category": "ML"}'

# Export
curl http://localhost:8000/session/{id}/export
```

## How It Works

1. **Build Your Graph**: As you work with AI, store key concepts and relationships
2. **Auto-Organize**: ContextGraph structures information as nodes and edges
3. **Export Anytime**: When approaching token limits, generate a portable block
4. **Paste Anywhere**: The block contains base64-encoded JSON with your entire graph
5. **Restore Instantly**: Any AI model can decode and restore your full context

## Use Cases

### For Developers
- Maintain context across coding sessions
- Document architecture decisions
- Track bug fixes and feature development

### For Researchers
- Organize research findings
- Connect related papers and concepts
- Preserve literature review context

### For Content Creators
- Track story arcs and character development
- Maintain brand voice across projects
- Organize research for articles

### For Teams
- Share project context between team members
- Onboard new members quickly
- Preserve institutional knowledge

## API Reference

### Core Functions

- `store_context(text, metadata)` - Store conversation context
- `store_concept(label, content, category, metadata)` - Add a concept node
- `link_concepts(from_node, to_node, relation)` - Create relationship
- `export_context(kg)` - Generate portable block
- `import_context(block_string)` - Restore from portable block
- `get_graph_summary(kg)` - Get human-readable summary

### CLI Commands

- `cg init` - Initialize session
- `cg add` - Add context/concept
- `cg link` - Link concepts
- `cg export` - Export portable block
- `cg import` - Import from file
- `cg status` - Show summary
- `cg serve` - Start API server

## Roadmap

- [ ] Web UI dashboard
- [ ] Browser extension for ChatGPT/Claude
- [ ] VS Code extension
- [ ] Auto-sync with popular AI platforms
- [ ] Collaborative graphs (multi-user)
- [ ] Graph visualization
- [ ] Advanced search and filtering
- [ ] Plugin ecosystem

## Contributing

We welcome contributions! See our contributing guidelines for details.

## License

MIT License - See LICENSE file for details

## Contact

- Website: [your-website.com]
- Email: your@email.com
- Twitter: @yourhandle

---

**Ready to scale?** Contact us for enterprise licensing and custom integrations.
