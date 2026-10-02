---
icon: lucide/rocket
---

# Quickstart

Get a complete Ponup instance running on your machine with Docker Compose in minutes.

---

## Prerequisites

- [Docker](https://docs.docker.com/get-docker/) (v24.0+ recommended)
- [Docker Compose](https://docs.docker.com/compose/install/) (v2.20+ recommended)

---

## Launch with Docker Compose

1. Clone the repository:

   ```bash
   git clone https://github.com/Ponup/app.git
   cd app
   ```

2. Start all services:

   ```bash
   docker compose up --build
   ```

   !!! tip "First-time Startup & Embeddings"
       On the first startup, the local embedding model (`sentence-transformers/all-MiniLM-L6-v2`) will be downloaded to the cached Docker volume automatically. Subsequent startups will use the cached weights instantly.

3. (Optional) In another terminal, seed demo data:

   ```bash
   make seed
   ```

   This creates a demonstration Space populated with sample Markdown, JSON, and file items.

---

## Exposed Services & Endpoints

Once the containers are healthy, the following endpoints are available:

| Service / Interface | Local URL | Description |
| :--- | :--- | :--- |
| **Web UI** | <http://localhost:3000> | Interactive dashboard for spaces, content editing, and search |
| **REST API Documentation** | <http://localhost:8000/docs> | Interactive OpenAPI (Swagger) documentation |
| **GraphQL Playground** | <http://localhost:8000/graphql> | GraphiQL explorer for queries and schemas |
| **MCP Streamable HTTP** | <http://localhost:8000/mcp> | Model Context Protocol endpoint for AI agents |
| **Public Content Links** | `http://localhost:3000/p/{space_slug}/{content_slug}` | Shareable public content viewer |

---

## First Steps in Ponup

### 1. Create a Space
Open <http://localhost:3000> and click **New Space**. Provide a name (e.g., `Engineering Context`) and an optional description. Ponup automatically generates a unique slug (e.g., `engineering-context`).

### 2. Add Content
Navigate into your space and click **New Content**:
- **Authored Markdown**: Write documentation with live Markdown preview.
- **Structured JSON**: Store structured schemas, configurations, or entity data with built-in JSON validation.
- **File Uploads**: Drag and drop PDF documents, plain text files, or images.

### 3. Generate Content with AI
Inside the **New Content** modal, fill in a Title, optional Description, and Tags, then click **Generate with AI**. If an LLM endpoint is configured (e.g., local Ollama with `llama3.2`), Ponup will automatically draft structured Markdown or JSON.

### 4. Search Semantically
Click the **Search** button (or press `Cmd+K` / `Ctrl+K`) in the top navigation bar. Enter natural language queries (such as *"how do migrations work"* or *"architecture overview"*) to retrieve contextually ranked chunks from your space.

### 5. Publish Content
Toggle content visibility from **Private** to **Public** to make it accessible via public URLs without authentication:
```
http://localhost:3000/p/{space-slug}/{content-slug}
```

---

## Stopping the Services

To stop running containers:

```bash
docker compose down
```

To stop containers and remove persistent database and file volumes:

```bash
docker compose down -v
```
