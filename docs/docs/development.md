---
icon: lucide/code
---

# Development & Contributing

Guidelines for setting up a local development environment, running tests, database migrations, and contributing to Ponup.

---

## Local Development Workflow

Ponup uses a `Makefile` to simplify common development tasks.

### Quick Commands

```bash
make dev       # Start the entire Docker Compose development stack
make down      # Stop running containers
make migrate   # Run Alembic database migrations
make seed      # Seed a demo Space with sample content
make test      # Run backend (pytest) and frontend (vitest) tests
make lint      # Run ruff check on backend and ESLint on frontend
```

---

## Codebase Architecture

```
ponup/app/
├── backend/            # Python 3.12+ FastAPI backend
│   ├── app/
│   │   ├── api/        # REST API route handlers
│   │   ├── core/       # Database & Pydantic config
│   │   ├── graphql/    # Strawberry GraphQL schema
│   │   ├── mcp/        # FastMCP Streamable HTTP server
│   │   ├── services/   # Extraction, generation, embeddings, vision
│   │   ├── models.py   # SQLAlchemy ORM models & pgvector definitions
│   │   ├── schemas.py  # Pydantic input/output schemas
│   │   └── worker.py   # Celery worker application
│   └── alembic/        # Database migrations
├── frontend/           # React 19 + TypeScript + Vite frontend
│   └── src/
│       ├── components/ # UI components & modals
│       └── lib/        # API client and utility helpers
├── docs/               # Zensical documentation site
├── compose.yaml        # Docker Compose configuration
└── Makefile            # Development task automation
```

---

## Documentation Site

The documentation in `docs/` is built using [Zensical](https://zensical.org) and Python 3.13+.

### Running Docs Locally

```bash
cd docs
uv sync
uv run zensical serve
```

### Building Docs

```bash
cd docs
uv run zensical build --clean
```

---

## Contribution Guidelines

### Pull Requests & Branching
1. Fork the repository and create a feature branch (`feature/my-feature` or `fix/my-bug`).
2. Ensure tests pass by running `make test`.
3. Ensure linters pass by running `make lint`.
4. Submit a Pull Request targeting the `main` branch.

### Changelog Maintenance
Always update `CHANGELOG.md` for user-visible changes. Add entries under the `[Unreleased]` heading following [Keep a Changelog](https://keepachangelog.com) conventions:
- `Added` for new features.
- `Changed` for changes in existing functionality.
- `Deprecated` for soon-to-be removed features.
- `Removed` for now removed features.
- `Fixed` for any bug fixes.
- `Security` in case of vulnerabilities.
