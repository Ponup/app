[![YouTube](https://img.shields.io/badge/YouTube-FF0000?style=for-the-badge&logo=youtube&logoColor=white)](https://youtube.com/@ponup)
[![X](https://img.shields.io/badge/X-000000?style=for-the-badge&logo=x&logoColor=white)](https://x.com/ponup)
[![LinkedIn](https://img.shields.io/badge/LinkedIn-0A66C2?style=for-the-badge&logo=linkedin&logoColor=white)](https://linkedin.com/company/ponup)
[![Facebook](https://img.shields.io/badge/Facebook-1877F2?style=for-the-badge&logo=facebook&logoColor=white)](https://facebook.com/ponup)

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

### Generate content automatically

The New Content modal can draft Markdown or JSON from its title, description,
and tags. Configure any OpenAI-compatible chat-completions provider on the
server; credentials never reach the browser. For example, use Ollama with
`LLM_BASE_URL=http://host.docker.internal:11434/v1` and
`LLM_MODEL=llama3.2`, or set `LLM_BASE_URL`, `LLM_API_KEY`, and `LLM_MODEL`
for OpenAI, OpenRouter, or another compatible provider. When running the API
outside Docker, an Ollama URL is usually `http://localhost:11434/v1`.
On Linux Docker hosts, Ponup's Compose configuration maps
`host.docker.internal` to the host gateway automatically.

## Connect an MCP client

After starting Ponup, add its Streamable HTTP endpoint to your agent's MCP
configuration. Most agents that use a JSON configuration accept the following
shape:

```json
{
  "mcpServers": {
    "ponup": {
      "url": "http://localhost:8000/mcp"
    }
  }
}
```

Save the entry in the agent's MCP configuration file, then restart or reload
the agent. Configuration filenames and the optional transport field vary by
client; if a transport is required, select `streamable-http` (sometimes named
`http`).

When the agent itself runs in a container, `localhost` refers to that container.
Use `http://host.docker.internal:8000/mcp` when the agent needs to reach Ponup
through the host, or use Ponup's Compose service name when both applications
share a Docker network.

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
