import { useEffect, useMemo, useState } from 'react'
import { SignalHistoryChart } from '../charts/SignalHistoryChart'
import { LoadState } from '../components/LoadState'
import { ScoreDecomposition } from '../components/ScoreDecomposition'
import { SignalTable } from '../components/SignalTable'
import { getSignalHistory, getSignals, type SignalHistoryPoint, type SignalRecord } from '../data/client'
import { formatScore } from '../utils/format'

type SignalsPageProps = { initialMarketId?: string }

export function SignalsPage({ initialMarketId }: SignalsPageProps) {
  const [signals, setSignals] = useState<SignalRecord[]>()
  const [selected, setSelected] = useState<SignalRecord>()
  const [history, setHistory] = useState<SignalHistoryPoint[]>()
  const [assetClass, setAssetClass] = useState('All')
  const [error, setError] = useState<string>()

  useEffect(() => { getSignals().then((nextSignals) => { setSignals(nextSignals); setSelected(nextSignals.find((signal) => signal.market_id === initialMarketId) ?? [...nextSignals].sort((left, right) => right.score - left.score)[0]) }).catch((reason: unknown) => setError(reason instanceof Error ? reason.message : 'Could not load current signals')) }, [initialMarketId])
  useEffect(() => { if (!selected) return; setHistory(undefined); getSignalHistory(selected.market_id).then(setHistory).catch((reason: unknown) => setError(reason instanceof Error ? reason.message : 'Could not load signal history')) }, [selected])

  const assetClasses = useMemo(() => ['All', ...new Set(signals?.map((signal) => signal.asset_class) ?? [])], [signals])
  const filteredSignals = useMemo(() => (signals ?? []).filter((signal) => assetClass === 'All' || signal.asset_class === assetClass).sort((left, right) => right.score - left.score), [assetClass, signals])
  if (error || !signals || !selected) return <LoadState error={error} label="Loading current signal scores…" />

  return <>
    <div className="page-intro"><div><p className="eyebrow">CONFIGURABLE SIGNALS</p><h1>Signals</h1><p>Scores are deterministic, documented, and decomposed into their exact weighted components.</p></div></div>
    <div className="filter-row"><label>Asset class <select value={assetClass} onChange={(event) => setAssetClass(event.target.value)}>{assetClasses.map((option) => <option key={option}>{option}</option>)}</select></label><span>{filteredSignals.length} current signals</span></div>
    <section className="signal-workspace"><article className="panel signal-table-panel"><div className="section-heading"><div><p className="eyebrow">LEADERBOARD</p><h2>Current signals</h2></div><span>0–100</span></div><SignalTable signals={filteredSignals} selectedId={selected.signal_id} onSelect={setSelected} /></article><div className="signal-detail"><section className="panel selected-signal"><div><p className="eyebrow">SELECTED MARKET</p><h2>{selected.market_name} <span>{selected.asset_class}</span></h2><p>{selected.signal_name} · {selected.observation_date}</p></div><strong>{formatScore(selected.score)}<small>{selected.classification}</small></strong></section><ScoreDecomposition signal={selected} /></div></section>
    <section className="panel chart-panel"><div className="section-heading"><div><p className="eyebrow">HISTORY</p><h2>{selected.market_name} signal trend</h2></div><span>Lazy-loaded</span></div>{history ? <SignalHistoryChart history={history} marketName={selected.market_name} /> : <LoadState label="Loading selected market history…" />}</section>
  </>
}
