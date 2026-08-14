import { describe, expect, it } from 'vitest'
import signals from '../../public/data/v1/signals/latest.json'

describe('published frontend data contract', () => {
  it('contains current synthetic signals with auditable components', () => {
    expect(signals).toHaveLength(20)
    expect(signals.every((signal) => signal.data_label.includes('DEMO DATA'))).toBe(true)
    expect(signals.every((signal) => signal.score >= 0 && signal.score <= 100)).toBe(true)
    expect(signals.every((signal) => signal.components.length === 6)).toBe(true)
  })
})
