import { describe, expect, it } from 'vitest'
import extractedEvents from '../../public/data/v1/events/extracted.json'
import economicIndicators from '../../public/data/v1/economic/latest.json'
import backtestResults from '../../public/data/v1/backtesting/results.json'
import signals from '../../public/data/v1/signals/latest.json'

describe('published frontend data contract', () => {
  it('contains current synthetic signals with auditable components', () => {
    expect(signals).toHaveLength(20)
    expect(signals.every((signal) => signal.data_label.includes('DEMO DATA'))).toBe(true)
    expect(signals.every((signal) => signal.score >= 0 && signal.score <= 100)).toBe(true)
    expect(signals.every((signal) => signal.components.length === 6)).toBe(true)
  })

  it('contains a clearly labeled, reproducible economic baseline', () => {
    expect(economicIndicators).toHaveLength(5)
    expect(economicIndicators.every((indicator) => indicator.data_label.includes('DEMO DATA'))).toBe(true)
    expect(economicIndicators.every((indicator) => typeof indicator.value === 'number')).toBe(true)
    expect(economicIndicators.every((indicator) => typeof indicator.change === 'number')).toBe(true)
  })

  it('contains static non-causal historical-association configurations', () => {
    expect(backtestResults).toHaveLength(234)
    expect(backtestResults.every((result) => result.data_label.includes('DEMO DATA'))).toBe(true)
    expect(backtestResults.every((result) => result.hit_rate >= 0 && result.hit_rate <= 100)).toBe(true)
  })

  it('contains traceable, deterministic RSS event records', () => {
    expect(extractedEvents).toHaveLength(20)
    expect(extractedEvents.every((event) => event.data_label.includes('DEMO DATA'))).toBe(true)
    expect(extractedEvents.every((event) => event.confidence >= 0 && event.confidence <= 1)).toBe(true)
    expect(extractedEvents.every((event) => event.article_id && event.market_id && event.company)).toBe(true)
  })
})
