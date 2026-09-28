# Ponup

Context engineering and content management for humans and AI.

Ponup is available under the [MIT License](LICENSE). Run the open-source edition
on your own infrastructure or use Ponup Cloud for a managed service.

Ponup stores authored and uploaded content in **Spaces**, makes it searchable, and
serves it to people and agents through a web app, REST, GraphQL, MCP, and public
links.

## Quick start

```bash
docker compose up --build
```

Open <http://localhost:3000>. API documentation is available at
<http://localhost:8000/docs>, GraphQL at <http://localhost:8000/graphql>, and
Streamable HTTP MCP at <http://localhost:8000/mcp>.

Copy `.env.example` to `.env` only when you want to override the Compose
defaults. The first startup downloads the local embedding model. Set
`EMBEDDING_PROVIDER=openai-compatible` and the corresponding variables in
`.env` to use a compatible hosted endpoint instead.

## Development

The backend uses Python 3.12, FastAPI, SQLAlchemy, PostgreSQL/pgvector, Celery,
and `uv`. The frontend uses React, TypeScript, Vite, and `pnpm`.

```bash
make dev           # start the Docker Compose stack
make test          # backend and frontend tests in containers
make migrate       # apply database migrations
make seed          # create a demo Space and Content
```

Administrative routes intentionally have no authentication in this first
self-hosted release. Do not expose `/api`, `/graphql`, or `/mcp` directly to an
untrusted network. Only `/p` and `/public` are designed as public surfaces.

Markdown, plain text, JSON, and PDF sources are extracted, chunked, embedded,
and stored in PostgreSQL. Images and other uploads remain downloadable but are
not indexed. Processing is asynchronous and reported as `queued`, `processing`,
`ready`, or `failed`.

The MCP server exposes Space and Content discovery, semantic search, and full
Content CRUD over Streamable HTTP.

## Marketing website

The static Next.js website lives in `website/`. Run it locally with
`cd website && npm install && npm run dev`, or generate deployable HTML with
`npm run build`.
