---
icon: simple/graphql
---

# GraphQL API Reference

Ponup provides a [Strawberry GraphQL](https://strawberry.rocks)-powered API at `/graphql`.

---

## Endpoint & Explorer

- **URL**: `http://localhost:8000/graphql`
- **Interactive GraphiQL Explorer**: Open <http://localhost:8000/graphql> in any web browser to explore types, fields, and test live queries.

---

## Schema Types

```graphql
type SpaceType {
  id: UUID!
  slug: String!
  name: String!
  description: String!
  createdAt: DateTime!
  updatedAt: DateTime!
}

type ContentType {
  id: UUID!
  spaceId: UUID!
  slug: String!
  title: String!
  description: String!
  kind: String!
  mimeType: String!
  tags: [String!]!
  metadata: JSON!
  visibility: String!
  processingStatus: String!
  processingError: String
  size: Int!
  createdAt: DateTime!
  updatedAt: DateTime!
}

type SearchResultType {
  contentId: UUID!
  contentSlug: String!
  title: String!
  description: String!
  tags: [String!]!
  chunkPosition: Int!
  text: String!
  score: Float!
}

type Query {
  spaces: [SpaceType!]!
  space(id: UUID!): SpaceType
  contents(spaceId: UUID!, tags: [String!]): [ContentType!]!
  content(id: UUID!): ContentType
  semanticSearch(spaceId: UUID!, query: String!, topK: Int = 10, tags: [String!]): [SearchResultType!]!
}
```

---

## Sample Queries

### 1. List All Spaces

```graphql
query ListSpaces {
  spaces {
    id
    slug
    name
    description
  }
}
```

---

### 2. Fetch Space by ID with its Contents

```graphql
query GetSpaceAndContents($spaceId: UUID!) {
  space(id: $spaceId) {
    id
    name
    slug
    description
  }
  contents(spaceId: $spaceId) {
    id
    title
    kind
    tags
    processingStatus
    size
  }
}
```

#### Variables
```json
{
  "spaceId": "3fa85f64-5717-4562-b3fc-2c963f66afa6"
}
```

---

### 3. Semantic Vector Search

```graphql
query SearchSpace($spaceId: UUID!, $query: String!, $topK: Int) {
  semanticSearch(spaceId: $spaceId, query: $query, topK: $topK) {
    contentId
    contentSlug
    title
    chunkPosition
    text
    score
  }
}
```

#### Variables
```json
{
  "spaceId": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
  "query": "authentication and security guidelines",
  "topK": 5
}
```
