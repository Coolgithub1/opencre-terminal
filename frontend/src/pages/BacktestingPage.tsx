import { useEffect, useMemo, useState } from 'react'
import { LoadState } from '../components/LoadState'
import { getBacktestResults, type BacktestResult } from '../data/client'
import { formatDate } from '../utils/format'

const formatPercent = (value: number) => `${value.toFixed(2)}%`

export function BacktestingPage() {
  const [results, setResults] = useState<BacktestResult[]>()
  const [scopeId, setScopeId] = useState('all-markets')
  const [threshold, setThreshold] = useState(60)
  const [horizon, setHorizon] = useState(6)
  const [error, setError] = useState<string>()

  useEffect(() => { getBacktestResults().then(setResults).catch((reason: unknown) => setError(reason instanceof Error ? reason.message : 'Could not load backtest results')) }, [])
  const scopes = useMemo(() => [...new Map((results ?? []).map((result) => [result.scope_id, result])).values()].sort((left, right) => left.scope_name.localeCompare(right.scope_name)), [results])
  const selected = useMemo(() => results?.find((result) => result.scope_id === scopeId && result.threshold === threshold && result.forward_horizon_months === horizon), [horizon, results, scopeId, threshold])
  if (error || !results || !selected) return <LoadState error={error} label="Loading deterministic backtest results…" />

  return <>
    <div className="page-intro"><div><p className="eyebrow">HISTORICAL ASSOCIATION</p><h1>Backtesting</h1><p>Static, synthetic look-forward summaries. They describe associations in the demo history, not causation or investment performance.</p></div></div>
    <div className="demo-banner">{selected.data_label}</div>
    <section className="panel backtest-controls"><div className="filter-row"><label>Scope <select value={scopeId} onChange={(event) => setScopeId(event.target.value)}>{scopes.map((scope) => <option key={scope.scope_id} value={scope.scope_id}>{scope.scope_type === 'market' ? `${scope.scope_name} · ${scope.asset_class}` : scope.scope_name}</option>)}</select></label><label>Signal threshold <select value={threshold} onChange={(event) => setThreshold(Number(event.target.value))}>{[50, 60, 70].map((value) => <option key={value} value={value}>Signal ≥ {value}</option>)}</select></label><label>Forward horizon <select value={horizon} onChange={(event) => setHorizon(Number(event.target.value))}>{[3, 6, 12].map((value) => <option key={value} value={value}>{value} months</option>)}</select></label></div>
      <p className="backtest-period">Historical selection window: {formatDate(selected.historical_start)}–{formatDate(selected.historical_end)} · Outcome: forward rent growth</p>
    </section>
    <section className="backtest-metric-grid">
      <article><span>Sample Size</span><strong>{selected.sample_size.toLocaleString()}</strong><small>Selected observations</small></article>
      <article><span>Mean Outcome</span><strong>{formatPercent(selected.mean_outcome)}</strong><small>Forward rent growth</small></article>
      <article><span>Median Outcome</span><strong>{formatPercent(selected.median_outcome)}</strong><small>Forward rent growth</small></article>
      <article><span>Hit Rate</span><strong>{formatPercent(selected.hit_rate)}</strong><small>Above all-market median</small></article>
      <article><span>Outcome Percentile</span><strong>{formatPercent(selected.outcome_percentile)}</strong><small>Vs. all eligible observations</small></article>
    </section>
    <section className="dashboard-grid"><article className="panel"><div className="section-heading"><div><p className="eyebrow">SELECTED CONFIGURATION</p><h2>{selected.scope_name}</h2></div><span>SIGNAL ≥ {selected.threshold}</span></div><dl className="backtest-detail"><dt>Strategy</dt><dd>Signal threshold</dd><dt>Average selected signal</dt><dd>{selected.average_signal_score.toFixed(2)}</dd><dt>Forward horizon</dt><dd>{selected.forward_horizon_months} months</dd><dt>Standard deviation</dt><dd>{formatPercent(selected.standard_deviation)}</dd></dl></article><article className="panel"><div className="section-heading"><div><p className="eyebrow">INTERPRETATION</p><h2>Method boundary</h2></div><span>NON-CAUSAL</span></div><p className="backtest-explainer">A result groups dates where the selected synthetic market signal met the threshold, then observes that same market’s synthetic rent growth at the selected future horizon. The comparison is descriptive and cannot establish that a signal caused an outcome.</p></article></section>
  </>
}
