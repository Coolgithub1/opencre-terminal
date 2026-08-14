import type { SignalRecord } from '../data/client'
import { formatScore } from '../utils/format'

export function ScoreDecomposition({ signal }: { signal: SignalRecord }) {
  return <section className="panel decomposition">
    <div className="section-heading"><div><p className="eyebrow">WHY THIS SCORE</p><h2>Mathematical decomposition</h2></div><strong>{formatScore(signal.score)}</strong></div>
    <div className="decomposition-table">
      {signal.components.map((component) => <div className="decomposition-row" key={component.key}>
        <span>{component.label}</span>
        <span>{formatScore(component.score)} × {component.weight}%</span>
        <strong>{formatScore(component.contribution)}</strong>
      </div>)}
    </div>
    <p className="decomposition-total">Total <strong>{formatScore(signal.score)}</strong> · {signal.classification}</p>
  </section>
}
