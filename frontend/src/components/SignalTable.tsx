import type { SignalRecord } from '../data/client'
import { formatScore } from '../utils/format'

type SignalTableProps = {
  signals: SignalRecord[]
  selectedId?: string
  onSelect: (signal: SignalRecord) => void
}

export function SignalTable({ signals, selectedId, onSelect }: SignalTableProps) {
  return <div className="terminal-table" role="table" aria-label="Market signal leaderboard">
    <div className="table-header" role="row"><span>Market</span><span>Asset</span><span>Signal</span><span>Score</span></div>
    {signals.map((signal) => <button className={`table-row ${selectedId === signal.signal_id ? 'selected' : ''}`} key={signal.signal_id} onClick={() => onSelect(signal)} type="button">
      <span><strong>{signal.market_name}</strong><small>{signal.classification}</small></span>
      <span>{signal.asset_class}</span>
      <span>{signal.signal_name}</span>
      <em>{formatScore(signal.score)}</em>
    </button>)}
  </div>
}
