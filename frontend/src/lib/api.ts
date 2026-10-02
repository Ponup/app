export const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

export interface Space {
  id: string
  slug: string
  name: string
  description: string
  created_at: string
  updated_at: string
}

export interface Content {
  id: string
  space_id: string
  slug: string
  title: string
  description: string
  kind: 'markdown' | 'json' | 'file'
  mime_type: string
  tags: string[]
  metadata: Record<string, unknown>
  visibility: 'private' | 'public'
  processing_status: 'queued' | 'processing' | 'ready' | 'failed'
  processing_error: string | null
  image_analysis: { description: string; objects: string[]; text: string } | null
  extracted_text: string | null
  checksum: string
  size: number
  body?: string | Record<string, unknown> | unknown[] | null
  created_at: string
  updated_at: string
}

export interface SearchResult {
  content_id: string
  content_slug: string
  title: string
  description: string
  tags: string[]
  chunk_position: number
  text: string
  score: number
}

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const response = await fetch(`${API_URL}${path}`, {
    ...options,
    headers: options?.body instanceof FormData ? options.headers : { 'Content-Type': 'application/json', ...options?.headers },
  })
  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: response.statusText }))
    throw new Error(error.detail || 'Request failed')
  }
  return response.status === 204 ? (undefined as T) : response.json()
}

export const api = {
  spaces: () => request<Space[]>('/api/v1/spaces'),
  space: (id: string) => request<Space>(`/api/v1/spaces/${id}`),
  createSpace: (data: { name: string; description: string }) => request<Space>('/api/v1/spaces', { method: 'POST', body: JSON.stringify(data) }),
  deleteSpace: (id: string) => request<void>(`/api/v1/spaces/${id}`, { method: 'DELETE' }),
  contents: (spaceId: string) => request<Content[]>(`/api/v1/spaces/${spaceId}/contents`),
  content: (id: string) => request<Content>(`/api/v1/contents/${id}`),
  createContent: (spaceId: string, data: object) => request<Content>(`/api/v1/spaces/${spaceId}/contents`, { method: 'POST', body: JSON.stringify(data) }),
  generateContent: (spaceId: string, data: { title: string; description: string; tags: string[]; kind: 'markdown' | 'json' }) => request<{ body: string | Record<string, unknown> | unknown[] }>(`/api/v1/spaces/${spaceId}/contents/generate`, { method: 'POST', body: JSON.stringify(data) }),
  updateContent: (id: string, data: object) => request<Content>(`/api/v1/contents/${id}`, { method: 'PATCH', body: JSON.stringify(data) }),
  deleteContent: (id: string) => request<void>(`/api/v1/contents/${id}`, { method: 'DELETE' }),
  publish: (id: string, publish: boolean) => request<Content>(`/api/v1/contents/${id}/${publish ? 'publish' : 'unpublish'}`, { method: 'POST' }),
  retry: (id: string) => request<Content>(`/api/v1/contents/${id}/retry`, { method: 'POST' }),
  upload: (spaceId: string, data: FormData) => request<Content>(`/api/v1/spaces/${spaceId}/uploads`, { method: 'POST', body: data }),
  search: (spaceId: string, query: string) => request<{ query: string; results: SearchResult[] }>(`/api/v1/spaces/${spaceId}/search?q=${encodeURIComponent(query)}`),
}
