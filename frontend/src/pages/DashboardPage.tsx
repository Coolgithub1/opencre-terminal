import { useEffect, useState } from 'react'
import { LoadState } from '../components/LoadState'
import { type EventRecord, getEvents, getPipelineStatus, getSignalRankings, getSignals, type PipelineStatus, type SignalRankings, type SignalRecord } from '../data/client'
import { formatScore, titleCase } from '../utils/format'

type DashboardPageProps = { onInspectSignal: (marketId: string) => void }

export function DashboardPage({ onInspectSignal }: DashboardPageProps) {
  const [rankings, setRankings] = useState<SignalRankings>()
  const [signals, setSignals] = useState<SignalRecord[]>()
  const [events, setEvents] = useState<EventRecord[]>()
  const [pipeline, setPipeline] = useState<PipelineStatus>()
  const [error, setError] = useState<string>()

  useEffect(() => {
    Promise.all([getSignalRankings(), getSignals(), getEvents(), getPipelineStatus()])
      .then(([nextRankings, nextSignals, nextEvents, nextPipeline]) => {
        setRankings(nextRankings)
        setSignals(nextSignals)
        setEvents(nextEvents)
        setPipeline(nextPipeline)
      })
      .catch((reason: unknown) => setError(reason instanceof Error ? reason.message : 'Could not load dashboard datasets'))
  }, [])

  if (error || !rankings || !signals || !events || !pipeline) return <LoadState error={error} />
  const strongSignals = signals.filter((signal) => signal.classification === 'Strong' || signal.classification === 'Exceptional')

  return <>
    <div className="page-intro"><div><p className="eyebrow">US COMMERCIAL REAL ESTATE</p><h1>Market Intelligence</h1><p>Current market state, deterministic signals, and traceable source data.</p></div><div className="pipeline-badge"><strong>● {pipeline.status.toUpperCase()}</strong><span>{pipeline.last_updated}</span></div></div>
    <div className="demo-banner">{pipeline.data_label}</div>
    <section className="metric-grid">
      <article className="metric-card"><span>Current Signals</span><strong>{signals.length}</strong><small>Across five asset classes</small></article>
      <article className="metric-card"><span>Strong or Exceptional</span><strong>{strongSignals.length}</strong><small>Deterministic classifications</small></article>
      <article className="metric-card"><span>Tracked Markets</span><strong>{pipeline.datasets.find((dataset) => dataset.name === 'markets')?.records ?? '—'}</strong><small>Synthetic demo markets</small></article>
      <article className="metric-card"><span>Signal Observations</span><strong>{pipeline.datasets.find((dataset) => dataset.name === 'signal_history')?.records ?? '—'}</strong><small>Historical monthly records</small></article>
    </section>
    <section className="dashboard-grid">
      <article className="panel leaderboard-panel"><div className="section-heading"><div><p className="eyebrow">CURRENT</p><h2>Top Market Signals</h2></div><span>0–100</span></div>
        <div className="signal-list">{rankings.rankings.top_signals.slice(0, 5).map((signal, index) => <button key={signal.market_id} onClick={() => onInspectSignal(signal.market_id)} type="button"><b>{String(index + 1).padStart(2, '0')}</b><span><strong>{signal.market_name}</strong><small>{signal.asset_class} · {signal.classification}</small></span><em>{formatScore(signal.score)}</em></button>)}</div>
      </article>
      <article className="panel events-panel"><div className="section-heading"><div><p className="eyebrow">LATEST</p><h2>Corporate Events</h2></div><span>DEMO</span></div>
        <div className="event-list">{events.slice(0, 5).map((event) => <div key={event.event_id}><span className="event-type">{titleCase(event.event_type)}</span><span><strong>{event.location}</strong><small>{event.company} · {event.employment.toLocaleString()} jobs</small></span><time>{event.event_date}</time></div>)}</div>
      </article>
    </section>
    <section className="panel data-health"><div className="section-heading"><div><p className="eyebrow">STATIC DATA</p><h2>Pipeline Health</h2></div><span>{pipeline.datasets.length} datasets</span></div><div className="health-grid">{pipeline.datasets.map((dataset) => <div key={dataset.name}><strong>{dataset.records.toLocaleString()}</strong><span>{titleCase(dataset.name)}</span><small>{dataset.status}</small></div>)}</div></section>
  </>
}
