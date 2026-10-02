---
icon: lucide/book-open
---

# Ponup

**Context engineering and content management for humans and AI.**

Ponup stores authored and uploaded content in **Spaces**, makes it instantly searchable via semantic embeddings, and serves it seamlessly to people and AI agents through a modern Web App, REST API, GraphQL, Model Context Protocol (MCP), and public links.

```mermaid
flowchart TD
    subgraph Clients["Clients & Interfaces"]
        WebUI["Web App (React/Vite) :3000"]
        Agent["AI Agents / MCP Clients (Claude, Cursor, etc.)"]
        APIClient["REST / GraphQL Clients"]
        PublicUser["Public Web Users (/p/...)"]
    end

    subgraph PonupBackend["Ponup API & Services (:8000)"]
        FastAPI["FastAPI App"]
        MCP["Streamable HTTP MCP (/mcp)"]
        GQL["GraphQL (/graphql)"]
        REST["REST API (/api/v1, /public/v1)"]
        Celery["Celery Worker (Asynchronous Processing)"]
    end

    subgraph StoragePipeline["Storage & Vector Search"]
        Postgres[("PostgreSQL + pgvector (HNSW)")]
        Redis[("Redis (Queue / Broker)")]
        S3[("Object Storage (S3 / RustFS)")]
    end

    subgraph AIServices["AI & Model Integrations"]
        Embeddings["Embedding Provider (Local / OpenAI-compatible)"]
        Vision["Vision Analysis (Ollama / OpenAI-compatible)"]
        LLMDraft["Content Drafting LLM (Ollama / OpenAI-compatible)"]
    end

    WebUI --> REST
    Agent --> MCP
    APIClient --> REST & GQL
    PublicUser --> REST

    FastAPI --> Postgres & Redis & S3
    Celery --> Redis & Postgres & S3
    Celery --> Embeddings & Vision
    FastAPI --> LLMDraft & Embeddings
```

---

## Why Ponup?

AI agents require accurate, structured, and fast contextual grounding. Human teams require intuitive knowledge organization, rich previews, and easy collaboration. Ponup bridges this gap:

- **Unified Knowledge Store**: Manage Markdown documents, structured JSON records, PDFs, plain text, and images within isolated **Spaces**.
- **Agent-Ready with MCP**: Built-in [Model Context Protocol (MCP)](mcp.md) endpoint over Streamable HTTP (`/mcp`), enabling agents like Claude Desktop, Cursor, and custom tools to discover, read, update, and semantically search content.
- **Multimodal Ingestion**: Preserves original image and document uploads while automatically extracting structured descriptions, detected objects, and legible text via vision models.
- **Semantic Vector Search**: High-performance semantic retrieval powered by PostgreSQL and `pgvector` with HNSW cosine indexes.
- **AI-Assisted Content Drafting**: Generate rich Markdown or JSON templates directly from titles and tags using local (Ollama) or hosted LLMs.
- **Multiple Integration Surfaces**: Access your data over a modern web UI, REST API, GraphQL, MCP, and slug-based public web URLs.

---

## Documentation Roadmap

- [**Quickstart Guide**](getting-started.md): Get Ponup up and running with Docker Compose in under two minutes.
- [**Core Concepts**](core-concepts.md): Deep dive into Spaces, Content kinds, the ingestion pipeline, and vector search.
- [**Model Context Protocol (MCP)**](mcp.md): Connect AI agents, configure MCP clients, and explore available tools and resources.
- [**AI & Multimodal Capabilities**](ai-multimodal.md): Configure vision models, LLM drafting, and embedding providers.
- [**REST API Reference**](api/rest.md): Comprehensive documentation for administrative and public REST endpoints.
- [**GraphQL API Reference**](api/graphql.md): Schema definitions, query types, and GraphiQL usage.
- [**Configuration & Hosting**](configuration.md): Environment variables, Docker Compose architecture, and production deployment tips.
- [**Development & Contributing**](development.md): Local development workflows, testing, migrations, and contributor guidelines.
