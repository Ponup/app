import { FormEvent, useRef, useState } from 'react'
import { useMutation, useQueryClient } from '@tanstack/react-query'
import { api } from '../lib/api'

export function NewContent({ spaceId, close }: { spaceId: string; close: () => void }) {
  const queryClient = useQueryClient()
  const [mode, setMode] = useState<'markdown' | 'json' | 'upload'>('markdown')
  const formRef = useRef<HTMLFormElement>(null)
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
  const generate = useMutation({
    mutationFn: async () => {
      const form = formRef.current
      if (!form) throw new Error('The form is not ready')
      const data = new FormData(form)
      const title = String(data.get('title') || '').trim()
      if (!title) throw new Error('Add a title before generating content')
      return api.generateContent(spaceId, {
        title,
        description: String(data.get('description') || '').trim(),
        tags: String(data.get('tags') || '').split(',').map((tag) => tag.trim()).filter(Boolean),
        kind: mode as 'markdown' | 'json',
      })
    },
    onSuccess: ({ body }) => {
      const field = formRef.current?.elements.namedItem('body') as HTMLTextAreaElement | null
      if (field) field.value = typeof body === 'string' ? body : JSON.stringify(body, null, 2)
    },
  })
  const submit = (event: FormEvent<HTMLFormElement>) => { event.preventDefault(); mutation.mutate(event.currentTarget) }

  return <div className="modal-backdrop" onMouseDown={(event) => event.target === event.currentTarget && close()}>
    <section className="modal">
      <div className="modal-head"><div><p className="eyebrow">Add context</p><h2>New Content</h2></div><button className="icon-button" onClick={close}>×</button></div>
      <div className="tabs">
        {(['markdown', 'json', 'upload'] as const).map((value) => <button key={value} className={mode === value ? 'active' : ''} onClick={() => setMode(value)}>{value}</button>)}
      </div>
      <form ref={formRef} onSubmit={submit}>
        <label>Title<input name="title" required placeholder="A useful, specific title" /></label>
        <label>Description<input name="description" placeholder="What does this context cover?" /></label>
        <label>Tags<input name="tags" placeholder="product, research, reference" /></label>
        {mode === 'upload'
          ? <label className="dropzone">Choose a file<input name="file" type="file" required /></label>
          : <div className="content-field"><div className="content-label"><span>Content</span><button type="button" className="generate-button" onClick={() => generate.mutate()} disabled={generate.isPending}>✦ {generate.isPending ? 'Generating…' : 'Generate automatically'}</button></div><textarea name="body" required rows={12} placeholder={mode === 'json' ? '{\n  "key": "value"\n}' : '# Start writing…'} /></div>}
        {(mutation.error || generate.error) && <p className="error">{mutation.error?.message || generate.error?.message}</p>}
        <div className="actions"><button type="button" className="button secondary" onClick={close}>Cancel</button><button className="button" disabled={mutation.isPending}>{mutation.isPending ? 'Saving…' : 'Create Content'}</button></div>
      </form>
    </section>
  </div>
}
