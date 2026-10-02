# Ponup Documentation

This directory contains the source files and configuration for the official Ponup documentation site, powered by [Zensical](https://zensical.org).

## Getting Started

### Prerequisites

- Python >= 3.13
- [`uv`](https://github.com/astral-sh/uv) (recommended) or `pip`

### Install Dependencies

Install the project dependencies into a virtual environment:

```bash
uv sync
```

### Local Live Preview

Start the local live-reloading preview server:

```bash
uv run zensical serve
```

By default, the documentation preview will be available at <http://localhost:8000> (or the port indicated in your terminal).

### Build Static Site

To build the static HTML site (output to `site/`):

```bash
uv run zensical build --clean
```

## Directory Layout

- `zensical.toml` - Main documentation site configuration, theme options, extensions, and navigation tree.
- `docs/` - Markdown documentation source files:
  - `index.md` - Overview and architecture
  - `getting-started.md` - Quickstart guide
  - `core-concepts.md` - Spaces, Content, Pipeline, and Vector Search
  - `mcp.md` - Model Context Protocol (MCP) server guide and tool reference
  - `ai-multimodal.md` - LLM drafting, vision analysis, and embedding configurations
  - `api/rest.md` - Complete REST API reference
  - `api/graphql.md` - GraphQL schema and query examples
  - `configuration.md` - Environment variables and self-hosting guide
  - `development.md` - Local development, testing, and contribution instructions
- `pyproject.toml` - Python project definition and dependency declarations.
