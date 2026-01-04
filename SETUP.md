# Prophecy Vision - Setup Guide

## Prerequisites

1. **Python 3.10+**
2. **Stellarium** (with RemoteControl plugin enabled)
3. **Ollama** (for local LLM inference - optional)

## Quick Start

### 1. Install Dependencies

```bash
cd /home/darthvader/AI_Projects/astronomy_bible_prophecy
pip install -e .
```

Or install manually:
```bash
pip install httpx mcp chromadb sentence-transformers langchain langchain-ollama langgraph
```

### 2. Enable Stellarium RemoteControl

1. Open Stellarium
2. Press F2 → Plugins → Remote Control
3. Check "Load at startup"
4. Restart Stellarium
5. Go back to Remote Control settings → Configure
6. Click "Start Server" (default port 8090)

### 3. Set Up Database

```bash
python src/database/setup.py
```

This creates:
- Local SQLite database with cosmic prophecy verses
- ChromaDB vector index for semantic search

### 4. Run the Application

**Interactive mode:**
```bash
python src/main.py --interactive
```

**Demo mode:**
```bash
python src/main.py --demo
```

**Search specific themes:**
```bash
python src/main.py --search "blood moon"
python src/main.py --analyze "Revelation 12:1"
```

## MCP Server Integration

### For Claude Desktop

Add to your Claude Desktop MCP configuration:

```json
{
  "mcpServers": {
    "stellarium": {
      "command": "python",
      "args": ["/home/darthvader/AI_Projects/astronomy_bible_prophecy/src/mcp_servers/stellarium_server.py"],
      "transport": "stdio"
    },
    "scripture": {
      "command": "python",
      "args": ["/home/darthvader/AI_Projects/astronomy_bible_prophecy/src/mcp_servers/scripture_server.py"],
      "transport": "stdio"
    }
  }
}
```

### Available MCP Tools

**Stellarium Server:**
- `get_stellarium_status` - Check Stellarium connection
- `set_biblical_location` - Set observer to Jerusalem, Babylon, etc.
- `set_time_julian` - Set simulation time by Julian date
- `set_time_gregorian` - Set simulation time by Gregorian date
- `focus_on_object` - Point at Sun, Moon, Virgo, etc.
- `show_prophetic_event` - Display known prophetic events
- `list_prophetic_events` - List available events
- `list_biblical_locations` - List available locations

**Scripture Server:**
- `search_cosmic_prophecies` - Semantic search for celestial themes
- `get_verse` - Get specific verse by reference
- `analyze_prophetic_passage` - Analyze passage for astronomical imagery
- `find_cross_references` - Find related passages
- `get_all_cosmic_verses` - List all pre-loaded cosmic verses

## Agent Orchestration (Optional)

For multi-agent workflows with Ollama:

### 1. Install Ollama
```bash
curl -fsSL https://ollama.com/install.sh | sh
```

### 2. Pull Required Models
```bash
ollama pull llama3.1:8b-instruct-q4_K_M
ollama pull qwen2.5:7b-instruct-q4_K_M
```

### 3. Run Agent System
```bash
python src/agents/orchestrator.py
```

## Testing

```bash
pip install pytest pytest-asyncio
pytest tests/ -v
```

## Troubleshooting

### Stellarium not connecting

1. Ensure Stellarium is running
2. Check RemoteControl is enabled (F2 → Plugins)
3. Verify server is running on port 8090
4. Test: `curl http://localhost:8090/api/main/status`

### ChromaDB import errors

```bash
pip install chromadb sentence-transformers torch
```

### Ollama not responding

```bash
systemctl status ollama  # Check service
ollama list              # List installed models
curl http://localhost:11434/api/tags  # Test API
```

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    User Interface                           │
│  (CLI / Tauri Desktop App)                                  │
└─────────────────────────────────────────────────────────────┘
                              │
              ┌───────────────┼───────────────┐
              ▼               ▼               ▼
┌──────────────────┐ ┌──────────────────┐ ┌──────────────────┐
│ MCP Server:      │ │ MCP Server:      │ │  Agent System    │
│ Stellarium       │ │ Scripture        │ │  (LangGraph)     │
└──────────────────┘ └──────────────────┘ └──────────────────┘
         │                    │                    │
         ▼                    ▼                    ▼
┌──────────────────┐ ┌──────────────────┐ ┌──────────────────┐
│   Stellarium     │ │  SQLite + Chroma │ │  Ollama Local    │
│   Desktop App    │ │  Databases       │ │  LLM Inference   │
└──────────────────┘ └──────────────────┘ └──────────────────┘
```

## License

MIT
