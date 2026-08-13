import { useEffect, useState } from 'react'
import { getDashboard, type DashboardData } from './data/client'
import './styles.css'

const navItems = ['Dashboard', 'Markets', 'Signals', 'Map', 'Events', 'Hotels', 'Valuation', 'Backtesting', 'Research', 'Data Sources', 'Methodology']

function App() {
  const [data, setData] = useState<DashboardData>()
  const [error, setError] = useState<string>()

  useEffect(() => {
    getDashboard().then(setData).catch((reason: unknown) => setError(reason instanceof Error ? reason.message : 'Could not load dashboard'))
  }, [])

  return <main className="terminal">
    <aside className="sidebar">
      <div className="brand"><span>OPEN</span>CRE <small>TERMINAL</small></div>
      <nav>{navItems.map((item, index) => <button className={index === 0 ? 'active' : ''} key={item}>{item}</button>)}</nav>
      <p className="sidebar-note">STATIC-FIRST<br />GITHUB PAGES READY</p>
    </aside>
    <section className="content">
      <header>
        <div><p className="eyebrow">US COMMERCIAL REAL ESTATE</p><h1>Market Intelligence</h1></div>
        <div className="header-meta"><strong>● DATA PIPELINE HEALTHY</strong><span>{data?.updated_at ?? 'Loading dataset…'}</span></div>
      </header>
      <div className="demo-banner">{data?.data_label ?? 'Loading demo data…'}</div>
      {error ? <div className="error">{error}</div> : !data ? <div className="loading">Loading terminal datasets…</div> : <>
        <section className="summary-grid">
          <article className="map-card"><div className="section-heading"><h2>US Market Map</h2><span>PHASE 1 PREVIEW</span></div><div className="map"><div className="usa">US</div>{data.signals.map((signal, i) => <i key={signal.market} className={`dot dot-${i}`} title={signal.market} />)}<p>Static map layers arrive in Phase 6</p></div></article>
          <article className="leaderboard"><div className="section-heading"><h2>Top Market Signals</h2><span>0–100</span></div>{data.signals.map((signal, index) => <div className="signal" key={signal.market}><b>{String(index + 1).padStart(2, '0')}</b><div><strong>{signal.market}</strong><span>{signal.asset_class}</span></div><em>{signal.score}</em><small className={signal.change >= 0 ? 'up' : 'down'}>{signal.change >= 0 ? '+' : ''}{signal.change}</small></div>)}</article>
        </section>
        <section className="lower-grid">
          <article><div className="section-heading"><h2>Recent Corporate Events</h2><span>DEMO</span></div><div className="table">{data.events.map(event => <div className="row" key={`${event.type}-${event.location}`}><span className="event-type">{event.type}</span><span><strong>{event.location}</strong><small>{event.detail}</small></span><time>{event.time}</time></div>)}</div></article>
          <article><div className="section-heading"><h2>Economic Indicators</h2><span>DEMO</span></div><div className="indicators">{data.indicators.map(indicator => <div key={indicator.label}><span>{indicator.label}</span><strong>{indicator.value}</strong><small className="up">{indicator.change}</small></div>)}</div></article>
        </section>
      </>}
    </section>
  </main>
}

export default App
