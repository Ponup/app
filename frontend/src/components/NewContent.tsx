import { FormEvent, useState } from 'react'
import { useMutation, useQueryClient } from '@tanstack/react-query'
import { api } from '../lib/api'

export function NewContent({ spaceId, close }: { spaceId: string; close: () => void }) {
  const queryClient = useQueryClient()
  const [mode, setMode] = useState<'markdown' | 'json' | 'upload'>('markdown')
  const mutation = useMutation({
    mutationFn: async (form: HTMLFormElement) => {
      const data = new FormData(form)
      if (mode === 'upload') return api.upload(spaceId, data)
      const raw = String(data.get('body'))
      const body = mode === 'json' ? JSON.parse(raw) : raw
      return api.createContent(spaceId, {
        title: data.get('title'), description: data.get('description'), kind: mode, body,
        tags: String(data.get('tags') || '').split(',').map((tag) => tag.trim()).filter(Boolean), metadata: {},
      })
    },
    onSuccess: async () => { await queryClient.invalidateQueries({ queryKey: ['contents', spaceId] }); close() },
  })
  const submit = (event: FormEvent<HTMLFormElement>) => { event.preventDefault(); mutation.mutate(event.currentTarget) }

  return <div className="modal-backdrop" onMouseDown={(event) => event.target === event.currentTarget && close()}>
    <section className="modal">
      <div className="modal-head"><div><p className="eyebrow">Add context</p><h2>New Content</h2></div><button className="icon-button" onClick={close}>×</button></div>
      <div className="tabs">
        {(['markdown', 'json', 'upload'] as const).map((value) => <button key={value} className={mode === value ? 'active' : ''} onClick={() => setMode(value)}>{value}</button>)}
      </div>
      <form onSubmit={submit}>
        <label>Title<input name="title" required placeholder="A useful, specific title" /></label>
        <label>Description<input name="description" placeholder="What does this context cover?" /></label>
        <label>Tags<input name="tags" placeholder="product, research, reference" /></label>
        {mode === 'upload'
          ? <label className="dropzone">Choose a file<input name="file" type="file" required /></label>
          : <label>Content<textarea name="body" required rows={12} placeholder={mode === 'json' ? '{\n  "key": "value"\n}' : '# Start writing…'} /></label>}
        {mutation.error && <p className="error">{mutation.error.message}</p>}
        <div className="actions"><button type="button" className="button secondary" onClick={close}>Cancel</button><button className="button" disabled={mutation.isPending}>{mutation.isPending ? 'Saving…' : 'Create Content'}</button></div>
      </form>
    </section>
  </div>
}
