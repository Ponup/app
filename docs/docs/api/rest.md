---
icon: lucide/terminal
---

# REST API Reference

The Ponup REST API is divided into administrative endpoints (`/api/v1`) and public anonymous endpoints (`/public/v1`).

---

## Interactive Documentation

When running locally, interactive documentation is available at:
- **Swagger UI**: <http://localhost:8000/docs>
- **ReDoc**: <http://localhost:8000/redoc>

---

## Base URLs

- Admin API: `/api/v1`
- Public API: `/public/v1`

---

## Spaces Endpoints

### List Spaces
```http
GET /api/v1/spaces
```
Returns a list of all Spaces ordered by name.

#### Response `200 OK`
```json
[
  {
    "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
    "slug": "engineering-docs",
    "name": "Engineering Docs",
    "description": "Technical documentation and architecture",
    "created_at": "2026-10-02T12:00:00Z",
    "updated_at": "2026-10-02T12:00:00Z"
  }
]
```

---

### Create Space
```http
POST /api/v1/spaces
```

#### Request Body
```json
{
  "name": "Product Specs",
  "slug": "product-specs",
  "description": "Feature requirements and specifications"
}
```

#### Response `201 Created`
Returns the created `SpaceOut` object.

---

### Get Space
```http
GET /api/v1/spaces/{space_id}
```

#### Response `200 OK`
Returns the `SpaceOut` object.

---

### Update Space
```http
PATCH /api/v1/spaces/{space_id}
```

#### Request Body
```json
{
  "name": "Updated Name",
  "description": "Updated Description"
}
```

#### Response `200 OK`
Returns the updated `SpaceOut` object.

---

### Delete Space
```http
DELETE /api/v1/spaces/{space_id}
```
Permanently deletes the space, its contents, object storage files, and chunks.

#### Response `204 No Content`

---

## Content Endpoints

### List Content in Space
```http
GET /api/v1/spaces/{space_id}/contents?tag=backend&tag=guide
```

#### Query Parameters
- `tag` (*list[string]*, optional): Filter items containing specified tags.

#### Response `200 OK`
```json
[
  {
    "id": "8fa85f64-5717-4562-b3fc-2c963f66afa6",
    "space_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
    "slug": "getting-started",
    "title": "Getting Started Guide",
    "description": "Introduction to our backend architecture",
    "kind": "markdown",
    "mime_type": "text/markdown",
    "tags": ["backend", "guide"],
    "metadata": {},
    "visibility": "private",
    "processing_status": "ready",
    "processing_error": null,
    "image_analysis": null,
    "size": 1420,
    "created_at": "2026-10-02T12:00:00Z",
    "updated_at": "2026-10-02T12:00:00Z"
  }
]
```

---

### Create Content
```http
POST /api/v1/spaces/{space_id}/contents
```

#### Request Body
```json
{
  "title": "System Architecture",
  "slug": "system-architecture",
  "kind": "markdown",
  "body": "# Architecture Overview\n\nThis document describes...",
  "description": "High level system diagram",
  "tags": ["architecture", "backend"],
  "metadata": {"author": "Jane Doe"}
}
```

#### Response `201 Created`
Returns the created `ContentOut` object and queues background vector indexing.

---

### Generate Content Body with AI
```http
POST /api/v1/spaces/{space_id}/contents/generate
```

#### Request Body
```json
{
  "title": "Database Optimization Strategies",
  "description": "Best practices for PostgreSQL indexes and vacuuming",
  "tags": ["postgres", "database", "performance"],
  "kind": "markdown"
}
```

#### Response `200 OK`
```json
{
  "body": "# Database Optimization Strategies\n\n..."
}
```

---

### Upload File
```http
POST /api/v1/spaces/{space_id}/uploads
```
Content-Type: `multipart/form-data`

#### Form Fields:
- `file` (*binary*, required): Uploaded document or image.
- `title` (*string*, optional): Display title.
- `description` (*string*, optional): Summary.
- `tags` (*string*, optional): Comma-separated tags (e.g. `diagram, architecture`).

#### Response `201 Created`
Returns `ContentOut`.

---

### Get Content Detail (with Body)
```http
GET /api/v1/contents/{content_id}
```

#### Response `200 OK`
Returns `ContentDetail` including `body` string/JSON for authored content.

---

### Get Raw Content Object
```http
GET /api/v1/contents/{content_id}/raw
```
Returns raw binary bytes directly from object storage with the item's `mime_type`.

---

### Update Content
```http
PATCH /api/v1/contents/{content_id}
```

#### Request Body
```json
{
  "title": "New Title",
  "body": "Updated content body...",
  "description": "Updated description",
  "tags": ["tag1", "tag2"],
  "metadata": {"key": "value"}
}
```

---

### Delete Content
```http
DELETE /api/v1/contents/{content_id}
```

#### Response `204 No Content`

---

### Publish / Unpublish
```http
POST /api/v1/contents/{content_id}/publish
POST /api/v1/contents/{content_id}/unpublish
```

---

### Retry Failed Processing
```http
POST /api/v1/contents/{content_id}/retry
```
Resets `processing_status` to `queued` and enqueues re-indexing.

---

## Semantic Search Endpoint

```http
GET /api/v1/spaces/{space_id}/search?q=query+string&top_k=10&tag=backend
```

#### Query Parameters:
- `q` (*string*, required): Natural language search prompt.
- `top_k` (*integer*, optional, default `10`): Number of passages to return (1-50).
- `tag` (*list[string]*, optional): Tag filters.

#### Response `200 OK`
```json
{
  "query": "how do embeddings work",
  "results": [
    {
      "content_id": "8fa85f64-5717-4562-b3fc-2c963f66afa6",
      "content_slug": "getting-started",
      "title": "Getting Started Guide",
      "description": "Introduction to our backend architecture",
      "tags": ["backend", "guide"],
      "chunk_position": 0,
      "text": "Embeddings convert textual passages into 384-dimensional dense vectors...",
      "score": 0.8924
    }
  ]
}
```

---

## Public Sharing Endpoints

Public endpoints require no authentication and operate on slugs for published items:

- `GET /public/v1/spaces/{space_slug}/contents/{content_slug}` - Metadata
- `GET /public/v1/spaces/{space_slug}/contents/{content_slug}/raw` - Raw file / image stream
- `GET /public/v1/spaces/{space_slug}/contents/{content_slug}/body` - Markdown or JSON payload
