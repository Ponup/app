---
icon: lucide/settings
---

# Configuration & Self-Hosting

Ponup is designed for effortless self-hosting via Docker Compose or Kubernetes, with full control over database, object storage, embedding providers, and LLM backends.

---

## Environment Variables Reference

Create a `.env` file in the project root to override default settings:

| Variable | Default | Description |
| :--- | :--- | :--- |
| **Database & Cache** | | |
| `DATABASE_URL` | `postgresql+psycopg://ponup:ponup@postgres:5432/ponup` | SQLAlchemy connection string to PostgreSQL |
| `POSTGRES_DB` | `ponup` | Database name |
| `POSTGRES_USER` | `ponup` | Database username |
| `POSTGRES_PASSWORD` | `ponup` | Database password |
| `REDIS_URL` | `redis://redis:6379/0` | Redis connection URL for Celery task queue |
| **Object Storage (S3)** | | |
| `S3_ENDPOINT_URL` | `http://rustfs:9000` | S3-compatible API endpoint (e.g. MinIO, RustFS, AWS S3, Cloudflare R2) |
| `S3_ACCESS_KEY` | `ponup` | S3 access key |
| `S3_SECRET_KEY` | `ponup-development` | S3 secret key |
| `S3_BUCKET` | `ponup` | S3 bucket name |
| `S3_REGION` | `us-east-1` | S3 region identifier |
| **Vector Embeddings** | | |
| `EMBEDDING_PROVIDER` | `local` | `local` (SentenceTransformers) or `openai-compatible` |
| `EMBEDDING_MODEL` | `sentence-transformers/all-MiniLM-L6-v2` | Embedding model identifier |
| `EMBEDDING_DIMENSIONS` | `384` | Dimensionality of vectors stored in pgvector |
| `OPENAI_COMPATIBLE_BASE_URL` | `""` | Base URL for hosted embedding provider (e.g. `https://api.openai.com/v1`) |
| `OPENAI_COMPATIBLE_API_KEY` | `""` | API key for hosted embedding provider |
| `OPENAI_COMPATIBLE_MODEL` | `text-embedding-3-small` | Model name for hosted embedding provider |
| **AI Content Drafting (LLM)** | | |
| `LLM_BASE_URL` | `http://host.docker.internal:11434/v1` | Base URL for chat completions endpoint |
| `LLM_API_KEY` | `""` | API key for chat completions endpoint |
| `LLM_MODEL` | `llama3.2` | Model name for drafting content |
| `LLM_TIMEOUT_SECONDS` | `60` | Request timeout in seconds |
| **Multimodal Vision Analysis** | | |
| `IMAGE_ANALYSIS_PROVIDER` | `disabled` | `disabled`, `ollama`, or `openai-compatible` |
| `IMAGE_ANALYSIS_BASE_URL` | `""` | Vision endpoint base URL (e.g. `http://host.docker.internal:11434`) |
| `IMAGE_ANALYSIS_MODEL` | `""` | Vision model name (e.g. `llava`, `llama3.2-vision`, `gpt-4o-mini`) |
| `IMAGE_ANALYSIS_API_KEY` | `""` | API key for vision endpoint |
| `IMAGE_ANALYSIS_TIMEOUT_SECONDS` | `120` | Vision analysis timeout in seconds |
| **Frontend & General** | | |
| `PUBLIC_BASE_URL` | `http://localhost:8000` | Base URL used for public links |
| `VITE_API_URL` | `http://localhost:8000` | Backend API URL used during frontend build |

---

## Architecture & Compose Stack

The default `compose.yaml` defines 6 modular services:

```mermaid
graph TD
    subgraph StorageServices["Storage Layer"]
        PG["postgres (pgvector/pgvector:pg16)"]
        RD["redis (redis:7-alpine)"]
        S3["rustfs (rustfs/rustfs:latest)"]
    end

    subgraph ApplicationServices["Application Layer"]
        API["api (FastAPI + Alembic)"]
        WKR["worker (Celery worker)"]
        FE["frontend (Nginx + React App)"]
    end

    FE -->|HTTP :3000| API
    API -->|HTTP :8000| PG & RD & S3
    WKR --> RD & PG & S3
```

1. **`postgres`**: PostgreSQL 16 with the `pgvector` extension for relational storage and HNSW vector search.
2. **`redis`**: In-memory broker for Celery asynchronous background tasks.
3. **`rustfs`**: Lightweight, high-performance S3-compatible object storage container.
4. **`api`**: FastAPI application handling REST, GraphQL, and Streamable HTTP MCP. Automatically runs Alembic migrations on startup.
5. **`worker`**: Celery worker performing background file extraction, OCR/vision analysis, chunking, and embedding generation.
6. **`frontend`**: Production Vite React build served via Nginx on port `3000`.

---

## Security & Network Exposure

!!! important "Network Access in Self-Hosted Environments"
    In this self-hosted release, administrative routes (`/api`, `/graphql`, `/mcp`) are unauthenticated to allow flexible local integration with AI agents and developer workflows.
    - **Do NOT** expose ports `8000`, `5432`, `6379`, or `9000` directly to the open public internet.
    - If exposing Ponup publicly, configure a reverse proxy (such as Nginx or Caddy) to expose only the frontend (`:3000`) and the public routes (`/p` and `/public`).
