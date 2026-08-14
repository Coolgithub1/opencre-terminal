import { useEffect, useMemo, useState } from 'react'
import { LoadState } from '../components/LoadState'
import { getMarketAnalytics, type MarketAnalytics } from '../data/client'
import { formatScore, formatSignedScore } from '../utils/format'

type MarketsPageProps = { onInspectSignal: (marketId: string) => void }

export function MarketsPage({ onInspectSignal }: MarketsPageProps) {
  const [markets, setMarkets] = useState<MarketAnalytics[]>()
  const [assetClass, setAssetClass] = useState('All')
  const [error, setError] = useState<string>()

  useEffect(() => { getMarketAnalytics().then(setMarkets).catch((reason: unknown) => setError(reason instanceof Error ? reason.message : 'Could not load market analytics')) }, [])
  const assetClasses = useMemo(() => ['All', ...new Set(markets?.map((market) => market.asset_class) ?? [])], [markets])
  const filteredMarkets = useMemo(() => (markets ?? []).filter((market) => assetClass === 'All' || market.asset_class === assetClass).sort((left, right) => right.market_activity_score - left.market_activity_score), [assetClass, markets])

  if (error || !markets) return <LoadState error={error} label="Loading current market analytics…" />
  return <>
    <div className="page-intro"><div><p className="eyebrow">MARKET ANALYTICS</p><h1>Markets</h1><p>Historical-percentile market state across demand, supply, performance, capital, and event activity.</p></div></div>
    <div className="filter-row"><label>Asset class <select value={assetClass} onChange={(event) => setAssetClass(event.target.value)}>{assetClasses.map((option) => <option key={option}>{option}</option>)}</select></label><span>{filteredMarkets.length} markets</span></div>
    <section className="panel market-table-panel"><div className="terminal-table market-table" role="table" aria-label="Market analytics table"><div className="table-header" role="row"><span>Market</span><span>Demand</span><span>Supply</span><span>Performance</span><span>Activity</span><span>6M Δ</span></div>{filteredMarkets.map((market) => <button className="table-row" key={market.market_id} onClick={() => onInspectSignal(market.market_id)} type="button"><span><strong>{market.market_name}</strong><small>{market.asset_class}</small></span><span>{formatScore(market.demand_score)}</span><span>{formatScore(market.supply_balance_score)}</span><span>{formatScore(market.performance_score)}</span><em>{formatScore(market.market_activity_score)}</em><span className={market.six_month_change >= 0 ? 'up' : 'down'}>{formatSignedScore(market.six_month_change)}</span></button>)}</div></section>
  </>
}
