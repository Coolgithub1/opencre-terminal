import { describe, expect, it } from 'vitest'
import dashboard from '../../public/data/v1/dashboard.json'

describe('dashboard dataset contract', () => {
  it('uses the required synthetic-data label', () => {
    expect(dashboard.data_label).toContain('DEMO DATA')
    expect(dashboard.data_label).toContain('synthetic')
    expect(dashboard.signals).toHaveLength(5)
    expect(dashboard.signals.every((signal) => signal.score >= 0 && signal.score <= 100)).toBe(true)
  })
})
