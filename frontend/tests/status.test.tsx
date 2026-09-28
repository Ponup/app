import { render, screen } from '@testing-library/react'
import { describe, expect, it } from 'vitest'
import { Status, Tags } from '../src/components/Status'

describe('content indicators', () => {
  it('shows processing status', () => {
    render(<Status value="ready" />)
    expect(screen.getByText('ready')).toBeInTheDocument()
  })
  it('shows tags', () => {
    render(<Tags values={['product', 'guide']} />)
    expect(screen.getByText('#product')).toBeInTheDocument()
  })
})
