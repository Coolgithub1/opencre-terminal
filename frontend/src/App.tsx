import { useState } from 'react'
import { DashboardPage } from './pages/DashboardPage'
import { DataSourcesPage } from './pages/DataSourcesPage'
import { MarketsPage } from './pages/MarketsPage'
import { SignalsPage } from './pages/SignalsPage'
import './styles.css'

type Page = 'dashboard' | 'markets' | 'signals' | 'data-sources'

const navigation: Array<{ label: string; page?: Page; phase?: string }> = [
  { label: 'Dashboard', page: 'dashboard' },
  { label: 'Markets', page: 'markets' },
  { label: 'Signals', page: 'signals' },
  { label: 'Map', phase: 'Phase 6' },
  { label: 'Events', phase: 'Phase 7' },
  { label: 'Hotels', phase: 'Phase 10' },
  { label: 'Valuation', phase: 'Phase 11' },
  { label: 'Backtesting', phase: 'Phase 9' },
  { label: 'Research', phase: 'Phase 13' },
  { label: 'Data Sources', page: 'data-sources' },
  { label: 'Methodology', phase: 'Docs' },
]

function App() {
  const [page, setPage] = useState<Page>('dashboard')
  const [selectedMarketId, setSelectedMarketId] = useState<string>()

  const inspectSignal = (marketId: string) => {
    setSelectedMarketId(marketId)
    setPage('signals')
  }

  return <main className="terminal">
    <aside className="sidebar">
      <div className="brand"><span>OPEN</span>CRE <small>TERMINAL</small></div>
      <nav aria-label="Terminal navigation">{navigation.map((item) => item.page ? <button className={page === item.page ? 'active' : ''} key={item.label} onClick={() => setPage(item.page!)} type="button">{item.label}</button> : <span className="nav-disabled" key={item.label} title={`${item.label} arrives in ${item.phase}`}>{item.label}<small>{item.phase}</small></span>)}</nav>
      <p className="sidebar-note">STATIC-FIRST<br />GITHUB PAGES READY</p>
    </aside>
    <section className="content">
      {page === 'dashboard' && <DashboardPage onInspectSignal={inspectSignal} />}
      {page === 'markets' && <MarketsPage onInspectSignal={inspectSignal} />}
      {page === 'signals' && <SignalsPage initialMarketId={selectedMarketId} />}
      {page === 'data-sources' && <DataSourcesPage />}
    </section>
  </main>
}

export default App
