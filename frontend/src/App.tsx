import { FormEvent, useState } from 'react'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { Link, NavLink, Route, Routes, useNavigate, useParams } from 'react-router-dom'
import { api, API_URL, type Content } from './lib/api'
import { NewContent } from './components/NewContent'
import { SearchPanel } from './components/SearchPanel'
import { Status, Tags } from './components/Status'

function Shell() {
  const spaces = useQuery({ queryKey: ['spaces'], queryFn: api.spaces })
  const [creating, setCreating] = useState(false)
  const queryClient = useQueryClient()
  const navigate = useNavigate()
  const create = useMutation({
    mutationFn: (form: HTMLFormElement) => { const data = new FormData(form); return api.createSpace({ name: String(data.get('name')), description: String(data.get('description') || '') }) },
    onSuccess: async (space) => { await queryClient.invalidateQueries({ queryKey: ['spaces'] }); setCreating(false); navigate(`/spaces/${space.id}`) },
  })
  return <div className="shell">
    <aside>
      <Link className="brand" to="/"><span className="mark">P</span><strong>Ponup</strong></Link>
      <div className="aside-heading"><span>Spaces</span><button aria-label="Create Space" onClick={() => setCreating(true)}>+</button></div>
      <nav>{spaces.data?.map((space) => <NavLink key={space.id} to={`/spaces/${space.id}`}><span>{space.name.slice(0, 1).toUpperCase()}</span><div><strong>{space.name}</strong><small>{space.description || 'No description'}</small></div></NavLink>)}</nav>
      <footer><a href={`${API_URL}/docs`} target="_blank">API docs ↗</a><a href={`${API_URL}/graphql`} target="_blank">GraphQL ↗</a></footer>
    </aside>
    <main><Routes><Route path="/" element={<Welcome hasSpaces={Boolean(spaces.data?.length)} />} /><Route path="/spaces/:spaceId" element={<SpaceView />} /><Route path="/spaces/:spaceId/content/:contentId" element={<ContentView />} /></Routes></main>
    {creating && <div className="modal-backdrop"><section className="modal compact"><div className="modal-head"><div><p className="eyebrow">A home for context</p><h2>Create a Space</h2></div><button className="icon-button" onClick={() => setCreating(false)}>×</button></div><form onSubmit={(event: FormEvent<HTMLFormElement>) => { event.preventDefault(); create.mutate(event.currentTarget) }}><label>Name<input name="name" required autoFocus placeholder="Product knowledge" /></label><label>Description<textarea name="description" rows={3} placeholder="What belongs here?" /></label>{create.error && <p className="error">{create.error.message}</p>}<div className="actions"><button className="button" disabled={create.isPending}>Create Space</button></div></form></section></div>}
  </div>
}

function Welcome({ hasSpaces }: { hasSpaces: boolean }) {
  return <div className="welcome"><div className="orb">P</div><p className="eyebrow">Context, made useful</p><h1>Your knowledge.<br /><em>Ready when needed.</em></h1><p>Ponup keeps human-readable content and agent-ready context in the same calm, searchable place.</p><p className="hint">{hasSpaces ? 'Choose a Space to continue.' : 'Create your first Space with the + button.'}</p></div>
}

function SpaceView() {
  const { spaceId = '' } = useParams()
  const [adding, setAdding] = useState(false)
  const [mode, setMode] = useState<'library' | 'search'>('library')
  const space = useQuery({ queryKey: ['space', spaceId], queryFn: () => api.space(spaceId) })
  const contents = useQuery({ queryKey: ['contents', spaceId], queryFn: () => api.contents(spaceId), refetchInterval: (q) => q.state.data?.some((item) => ['queued', 'processing'].includes(item.processing_status)) ? 2000 : false })
  return <div className="page">
    <header className="page-header"><div><p className="eyebrow">Space</p><h1>{space.data?.name || 'Loading…'}</h1><p>{space.data?.description}</p></div><button className="button" onClick={() => setAdding(true)}>+ Add Content</button></header>
    <div className="view-tabs"><button className={mode === 'library' ? 'active' : ''} onClick={() => setMode('library')}>Library <b>{contents.data?.length || 0}</b></button><button className={mode === 'search' ? 'active' : ''} onClick={() => setMode('search')}>Semantic search</button></div>
    {mode === 'search' ? <SearchPanel spaceId={spaceId} /> : <ContentGrid values={contents.data || []} />}
    {adding && <NewContent spaceId={spaceId} close={() => setAdding(false)} />}
  </div>
}

function ContentGrid({ values }: { values: Content[] }) {
  if (!values.length) return <div className="empty"><div>◇</div><h2>This Space is ready</h2><p>Add Markdown, JSON, PDFs, images, or plain text to begin building context.</p></div>
  return <div className="content-grid">{values.map((item) => <Link to={`content/${item.id}`} className="content-card" key={item.id}><div className="card-top"><span className="kind">{item.kind === 'file' ? item.mime_type.split('/').pop() : item.kind}</span><Status value={item.processing_status} /></div><h2>{item.title}</h2><p>{item.description || 'No description'}</p><Tags values={item.tags} /><small>Updated {new Date(item.updated_at).toLocaleDateString()}</small></Link>)}</div>
}

function ContentView() {
  const { spaceId = '', contentId = '' } = useParams()
  const navigate = useNavigate()
  const queryClient = useQueryClient()
  const content = useQuery({ queryKey: ['content', contentId], queryFn: () => api.content(contentId), refetchInterval: (q) => ['queued', 'processing'].includes(q.state.data?.processing_status || '') ? 2000 : false })
  const space = useQuery({ queryKey: ['space', spaceId], queryFn: () => api.space(spaceId) })
  const [editing, setEditing] = useState(false)
  const invalidate = async () => { await queryClient.invalidateQueries({ queryKey: ['content', contentId] }); await queryClient.invalidateQueries({ queryKey: ['contents', spaceId] }) }
  const publish = useMutation({ mutationFn: (value: boolean) => api.publish(contentId, value), onSuccess: invalidate })
  const remove = useMutation({ mutationFn: () => api.deleteContent(contentId), onSuccess: async () => { await queryClient.invalidateQueries({ queryKey: ['contents', spaceId] }); navigate(`/spaces/${spaceId}`) } })
  const save = useMutation({ mutationFn: (form: HTMLFormElement) => { const data = new FormData(form); const item = content.data!; const raw = String(data.get('body')); return api.updateContent(contentId, { title: data.get('title'), description: data.get('description'), tags: String(data.get('tags')).split(',').map((v) => v.trim()).filter(Boolean), ...(item.kind === 'file' ? {} : { body: item.kind === 'json' ? JSON.parse(raw) : raw }) }) }, onSuccess: async () => { await invalidate(); setEditing(false) } })
  const item = content.data
  if (!item) return <div className="page">Loading…</div>
  const body = typeof item.body === 'string' ? item.body : item.body ? JSON.stringify(item.body, null, 2) : ''
  return <div className="page detail-page">
    <Link className="back" to={`/spaces/${spaceId}`}>← Back to Space</Link>
    <header className="detail-head"><div><div className="card-top"><span className="kind">{item.kind}</span><Status value={item.processing_status} /></div><h1>{item.title}</h1><p>{item.description}</p><Tags values={item.tags} /></div><div className="header-actions"><button className="button secondary" onClick={() => setEditing(!editing)}>{editing ? 'Cancel' : 'Edit'}</button><button className="button" onClick={() => publish.mutate(item.visibility !== 'public')}>{item.visibility === 'public' ? 'Unpublish' : 'Publish'}</button></div></header>
    {item.processing_error && <div className="notice error"><strong>Processing failed</strong><p>{item.processing_error}</p><button onClick={() => api.retry(item.id).then(invalidate)}>Retry</button></div>}
    {item.visibility === 'public' && <div className="notice"><strong>Public link</strong><a href={`${API_URL}/p/${space.data?.slug}/${item.slug}`} target="_blank">Open published Content ↗</a><small>Anyone with this link can read the source.</small></div>}
    {editing ? <form className="editor" onSubmit={(event) => { event.preventDefault(); save.mutate(event.currentTarget) }}><label>Title<input name="title" defaultValue={item.title} required /></label><label>Description<input name="description" defaultValue={item.description} /></label><label>Tags<input name="tags" defaultValue={item.tags.join(', ')} /></label>{item.kind !== 'file' && <label>Content<textarea name="body" defaultValue={body} rows={20} /></label>}{save.error && <p className="error">{save.error.message}</p>}<div className="actions"><button className="button">Save changes</button></div></form> : <section className="preview"><div className="preview-bar"><span>Source</span><a href={`${API_URL}/api/v1/contents/${item.id}/raw`} target="_blank">Raw ↗</a></div>{item.mime_type.startsWith('image/') ? <img src={`${API_URL}/api/v1/contents/${item.id}/raw`} alt={item.title} /> : item.kind === 'file' ? <a className="download" href={`${API_URL}/api/v1/contents/${item.id}/raw`}>Download file</a> : <pre>{body}</pre>}</section>}
    <section className="danger"><div><strong>Delete Content</strong><p>Permanently remove its source and search index.</p></div><button onClick={() => confirm('Delete this Content permanently?') && remove.mutate()}>Delete</button></section>
  </div>
}

export default Shell
