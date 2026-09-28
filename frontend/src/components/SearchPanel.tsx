import { FormEvent, useState } from 'react'
import { useMutation } from '@tanstack/react-query'
import { Link } from 'react-router-dom'
import { api } from '../lib/api'

export function SearchPanel({ spaceId }: { spaceId: string }) {
  const [query, setQuery] = useState('')
  const search = useMutation({ mutationFn: () => api.search(spaceId, query) })
  const submit = (event: FormEvent) => { event.preventDefault(); if (query.trim()) search.mutate() }
  return <section className="search-panel">
    <form className="search-box" onSubmit={submit}><span>⌕</span><input aria-label="Search context" value={query} onChange={(e) => setQuery(e.target.value)} placeholder="Search this Space by meaning…" /><button disabled={search.isPending}>Search</button></form>
    {search.error && <p className="error">{search.error.message}</p>}
    {search.data && <div className="results">
      <p className="eyebrow">{search.data.results.length} ranked passages</p>
      {search.data.results.map((result) => <Link to={`content/${result.content_id}`} className="result" key={`${result.content_id}-${result.chunk_position}`}>
        <div><strong>{result.title}</strong><span>{Math.round(result.score * 100)}% match</span></div><p>{result.text}</p>
      </Link>)}
      {!search.data.results.length && <div className="empty small"><p>No indexed passages matched.</p></div>}
    </div>}
  </section>
}
