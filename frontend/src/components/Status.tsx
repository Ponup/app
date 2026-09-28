import type { Content } from '../lib/api'

export function Status({ value }: { value: Content['processing_status'] }) {
  return <span className={`status status-${value}`}><i />{value}</span>
}

export function Tags({ values }: { values: string[] }) {
  return <span className="tags">{values.map((tag) => <span key={tag}>#{tag}</span>)}</span>
}
