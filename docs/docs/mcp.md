---
icon: lucide/cpu
---

# Model Context Protocol (MCP)

Ponup features a first-class, built-in **Model Context Protocol (MCP)** server over **Streamable HTTP**. This enables AI agents, assistants, and IDE extensions to manage knowledge bases and retrieve relevant context dynamically.

---

## Endpoint & Transport

- **Endpoint URL**: `http://localhost:8000/mcp`
- **Transport Type**: `streamable-http` (or `http`)
- **Protocol**: [Model Context Protocol](https://modelcontextprotocol.io) (FastMCP)

---

## Connecting MCP Clients

### Claude Desktop

To add Ponup to Claude Desktop, edit `claude_desktop_config.json`:

=== "macOS"
    ```json title="~/Library/Application Support/Claude/claude_desktop_config.json"
    {
      "mcpServers": {
        "ponup": {
          "url": "http://localhost:8000/mcp"
        }
      }
    }
    ```

=== "Windows"
    ```json title="%APPDATA%\\Claude\\claude_desktop_config.json"
    {
      "mcpServers": {
        "ponup": {
          "url": "http://localhost:8000/mcp"
        }
      }
    }
    ```

=== "Linux"
    ```json title="~/.config/Claude/claude_desktop_config.json"
    {
      "mcpServers": {
        "ponup": {
          "url": "http://localhost:8000/mcp"
        }
      }
    }
    ```

---

### Cursor / Windsurf / Cline / Open Interpreter

In client configuration settings that accept JSON-based MCP servers:

```json
{
  "mcpServers": {
    "ponup": {
      "url": "http://localhost:8000/mcp"
    }
  }
}
```

!!! note "Container Networking"
    When your agent or IDE runs inside a separate Docker container, `localhost` will point to that agent's container.
    - If connecting across the host gateway, use `http://host.docker.internal:8000/mcp`.
    - If your agent joins Ponup's Docker Compose network (`ponup-local_default`), use `http://api:8000/mcp`.

---

## MCP Tools Reference

Ponup provides 13 built-in tools covering Space management, Content operations, and Vector Search:

### 1. `list_spaces`
List all Spaces in the system.

- **Parameters**: None
- **Returns**: `list[SpaceOut]`

---

### 2. `get_space`
Get a single Space by UUID or slug.

- **Parameters**:
  - `space` (*string*, required): UUID or slug of the space.
- **Returns**: `SpaceOut`

---

### 3. `create_space`
Create a new Space.

- **Parameters**:
  - `name` (*string*, required): Space name.
  - `description` (*string*, optional): Context description.
  - `slug` (*string*, optional): Desired custom slug.
- **Returns**: `SpaceOut`

---

### 4. `update_space`
Update an existing Space's name or description.

- **Parameters**:
  - `space` (*string*, required): UUID or slug of the space.
  - `name` (*string*, optional): Updated name.
  - `description` (*string*, optional): Updated description.
- **Returns**: `SpaceOut`

---

### 5. `delete_space`
Permanently delete a Space and all of its associated Content, chunks, and storage objects.

- **Parameters**:
  - `space` (*string*, required): UUID or slug of the space.
- **Returns**: `"deleted"`

---

### 6. `list_contents`
List Content items in a space, optionally filtering by tags.

- **Parameters**:
  - `space` (*string*, required): UUID or slug of the space.
  - `tags` (*list[string]*, optional): Filter items containing all specified tags.
- **Returns**: `list[ContentOut]`

---

### 7. `get_content`
Get Content metadata, and for authored items (Markdown/JSON), include its full body.

- **Parameters**:
  - `content_id` (*string*, required): UUID or slug of the content item.
  - `include_body` (*boolean*, optional, default `true`): Whether to include the source text/JSON body.
- **Returns**: `ContentDetail`

---

### 8. `download_content`
Download the raw file data or body of Content as base64-encoded bytes alongside metadata and decoded text (when applicable).

- **Parameters**:
  - `content_id` (*string*, required): UUID or slug of the content item.
- **Returns**: Object with `id`, `slug`, `title`, `filename`, `mime_type`, `size`, `encoding` (`"base64"`), `data` (base64-encoded string), and `text` (UTF-8 decoded string if applicable).

---

### 9. `create_content`
Create authored Markdown or JSON content and queue it for vector indexing.

- **Parameters**:
  - `space` (*string*, required): UUID or slug of the destination space.
  - `title` (*string*, required): Content title.
  - `body` (*string*, required): Raw Markdown text or JSON string.
  - `kind` (*string*, optional, default `"markdown"`): `"markdown"` or `"json"`.
  - `description` (*string*, optional): Content summary.
  - `tags` (*list[string]*, optional): Array of lowercase tags.
  - `metadata` (*object*, optional): Arbitrary custom JSON metadata.
- **Returns**: `ContentOut`

---

### 10. `update_content`
Update existing Content metadata or body. Supplying a new body queues re-indexing.

- **Parameters**:
  - `content_id` (*string*, required): UUID of the content item.
  - `title` (*string*, optional): Updated title.
  - `body` (*string*, optional): Updated body (triggers reindexing).
  - `description` (*string*, optional): Updated description.
  - `tags` (*list[string]*, optional): Updated tags list.
  - `metadata` (*object*, optional): Updated custom metadata.
- **Returns**: `ContentOut`

---

### 11. `publish_content`
Publish or unpublish a Content item.

- **Parameters**:
  - `content_id` (*string*, required): UUID of the content item.
  - `published` (*boolean*, optional, default `true`): `true` to make public, `false` to make private.
- **Returns**: `ContentOut`

---

### 12. `delete_content`
Permanently delete a Content item and its embeddings.

- **Parameters**:
  - `content_id` (*string*, required): UUID of the content item.
- **Returns**: `"deleted"`

---

### 13. `search_content`
Perform semantic vector search to retrieve ranked relevant passages from a space.

- **Parameters**:
  - `space` (*string*, required): UUID or slug of the space.
  - `query` (*string*, required): Natural language search query.
  - `top_k` (*integer*, optional, default `10`, range `1-50`): Maximum number of ranked chunks to return.
  - `tags` (*list[string]*, optional): Filter results to content items matching specific tags.
- **Returns**: `list[SearchResult]` containing `content_id`, `content_slug`, `title`, `description`, `tags`, `chunk_position`, `text`, and `score`.

---

## MCP Resources

Ponup exposes stable URI resources for agents to inspect authored content directly:

### URI Scheme
```
ponup://spaces/{space_slug}/contents/{content_slug}
```

- Returns the decoded source Markdown or formatted JSON body.
- If the content is an uploaded binary file, returns JSON metadata about the file.
