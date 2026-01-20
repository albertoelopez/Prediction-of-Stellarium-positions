# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Prophecy Vision connects Biblical prophecy with astronomical visualization using Stellarium. It provides semantic search for celestial themes in scripture and real-time planetarium control via MCP (Model Context Protocol) servers.

## Common Commands

```bash
# Install
pip install -e .                    # Standard install
pip install -e ".[dev]"             # With dev dependencies (pytest, ruff, mypy)

# Database setup (required before first run)
python src/database/setup.py        # Creates SQLite + ChromaDB

# Run application
prophecy-vision --interactive       # CLI REPL mode
prophecy-vision --demo              # Automated demo
prophecy-vision --search "blood moon"
prophecy-vision --analyze "Revelation 12:1"

# MCP servers (for Claude Desktop integration)
stellarium-mcp                      # Stellarium control server
scripture-mcp                       # Scripture search server

# Testing
pytest tests/ -v                    # Run all tests
pytest tests/test_scripture_server.py -v   # Single test file
pytest tests/ --cov                 # With coverage

# Linting
ruff check src/                     # Check code
ruff format src/                    # Format code
mypy src/                           # Type checking
```

## Architecture

```
src/
├── main.py                  # CLI entry point (ProphecyVisionApp class)
├── mcp_servers/
│   ├── stellarium_server.py # MCP server: Stellarium RemoteControl API (port 8090)
│   └── scripture_server.py  # MCP server: semantic search via ChromaDB
├── agents/
│   └── orchestrator.py      # LangGraph multi-agent system (requires Ollama)
└── database/
    ├── setup.py             # SQLite + ChromaDB initialization
    └── categories.py        # Verse categorization with scholarly sources
```

### Key Components

**Stellarium Server** (`stellarium_server.py`): Controls Stellarium via HTTP. Key tools: `set_biblical_location`, `set_time_julian`, `set_time_gregorian`, `focus_on_object`, `show_prophetic_event`. Requires Stellarium running with RemoteControl plugin on localhost:8090.

**Scripture Server** (`scripture_server.py`): Semantic search using ChromaDB with `all-mpnet-base-v2` embeddings. Falls back to keyword search if ChromaDB unavailable.

**Categorization System** (`categories.py`): Classifies verses into categories (PROPHETIC_SIGN, HISTORICAL_EVENT, METAPHORICAL, etc.) with confidence scores and scholarly sources.

### Data Flow

1. User queries cosmic themes via CLI or MCP
2. Scripture server performs semantic search in ChromaDB
3. Stellarium server configures planetarium to visualize relevant events
4. Agent orchestrator (optional) coordinates multi-step workflows via Ollama

## Pre-configured Events

The Stellarium server includes pre-configured prophetic events:
- `revelation_12_sign` - Sept 23, 2017
- `star_of_bethlehem_jupiter_venus` - June 17, 2 BC (Jupiter-Venus super-conjunction)
- `star_of_bethlehem_jupiter_regulus_1/2/3` - Sept 3 BC to May 2 BC (triple conjunction)
- `star_of_bethlehem_magi_arrive` - Dec 25, 2 BC (Jupiter stationary)
- `crucifixion_eclipse` - April 3, 33 AD
- `joshua_long_day` - Oct 30, 1207 BC
- `blood_moon_prophecy` - April 15, 2014
- See `PROPHETIC_EVENTS` dict in `stellarium_server.py` for full list
- See `PROPHETIC_EVENTS.md` for detailed documentation and verification results

## External Dependencies

- **Stellarium**: Must run with RemoteControl plugin (F2 > Plugins > Remote Control)
- **Ollama** (optional): For agent orchestration, requires `llama3.1:8b-instruct-q4_K_M` and `qwen2.5:7b-instruct-q4_K_M`

## Code Patterns

- All network operations use `asyncio` + `httpx.AsyncClient`
- MCP tools defined via FastMCP decorators (`@mcp.tool()`)
- ChromaDB persists in `data/chroma_db/`, SQLite in `data/bible.db`
- Biblical dates use Julian Date format for astronomical precision
- BC dates use astronomical year numbering (0 = 1 BC, -1 = 2 BC, etc.)

## Astronomical Verification

When verifying celestial configurations:
1. Use `set_biblical_location()` to set observer location
2. Use `set_time_gregorian()` to set the date
3. Use `get_object_info()` to query object positions
4. Check the `iauConstellation` field for IAU boundary-accurate constellation

**Important:** Skyfield's constellation boundaries differ from Stellarium's IAU boundaries. Always verify with Stellarium for final confirmation.
