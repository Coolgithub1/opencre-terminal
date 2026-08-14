import { useEffect, useMemo, useState } from 'react'
import { LoadState } from '../components/LoadState'
import { getMarketAnalytics, getMarketGeography, getSignals, type MarketAnalytics, type MarketGeoFeature, type SignalRecord } from '../data/client'
import { MarketMap } from '../maps/MarketMap'
import { formatScore, formatSignedScore } from '../utils/format'

type MapMarket = { feature: MarketGeoFeature; signal: SignalRecord; analytics: MarketAnalytics }
type MapPageProps = { onInspectSignal: (marketId: string) => void }

export function MapPage({ onInspectSignal }: MapPageProps) {
  const [markets, setMarkets] = useState<MapMarket[]>()
  const [selectedMarketId, setSelectedMarketId] = useState<string>()
  const [assetClass, setAssetClass] = useState('All')
  const [error, setError] = useState<string>()

  useEffect(() => {
    Promise.all([getMarketGeography(), getSignals(), getMarketAnalytics()])
      .then(([geography, signals, analytics]) => {
        const signalByMarket = new Map(signals.map((signal) => [signal.market_id, signal]))
        const analyticsByMarket = new Map(analytics.map((market) => [market.market_id, market]))
        const nextMarkets = geography.features.flatMap((feature) => {
          const signal = signalByMarket.get(feature.properties.market_id)
          const marketAnalytics = analyticsByMarket.get(feature.properties.market_id)
          return signal && marketAnalytics ? [{ feature, signal, analytics: marketAnalytics }] : []
        })
        setMarkets(nextMarkets)
        setSelectedMarketId([...nextMarkets].sort((left, right) => right.signal.score - left.signal.score)[0]?.signal.market_id)
      })
      .catch((reason: unknown) => setError(reason instanceof Error ? reason.message : 'Could not load market map datasets'))
  }, [])

  const assetClasses = useMemo(() => ['All', ...new Set(markets?.map((market) => market.signal.asset_class) ?? [])], [markets])
  const visibleMarkets = useMemo(() => (markets ?? []).filter((market) => assetClass === 'All' || market.signal.asset_class === assetClass), [assetClass, markets])
  const selected = markets?.find((market) => market.signal.market_id === selectedMarketId) ?? visibleMarkets[0]
  const mapFeatures = useMemo(() => visibleMarkets.map((market) => ({ type: 'Feature' as const, id: market.feature.id, geometry: market.feature.geometry, properties: { market_id: market.signal.market_id, market_name: market.signal.market_name, score: market.signal.score, asset_class: market.signal.asset_class, classification: market.signal.classification } })), [visibleMarkets])

  if (error || !markets || !selected) return <LoadState error={error} label="Loading static market geography…" />
  return <>
    <div className="page-intro"><div><p className="eyebrow">STATIC GEOGRAPHY</p><h1>Market Map</h1><p>Map points are representative city centroids for synthetic demo markets, joined to current deterministic scores in the browser.</p></div></div>
    <div className="demo-banner">{selected.feature.properties.data_label} Market points are not legal market boundaries.</div>
    <div className="filter-row"><label>Asset class <select value={assetClass} onChange={(event) => setAssetClass(event.target.value)}>{assetClasses.map((option) => <option key={option}>{option}</option>)}</select></label><span>{visibleMarkets.length} market points</span></div>
    <section className="map-workspace"><article className="panel map-panel"><div className="section-heading"><div><p className="eyebrow">SIGNAL LAYER</p><h2>US market points</h2></div><span>Click a point</span></div><MarketMap features={mapFeatures} onSelect={setSelectedMarketId} /><div className="map-legend"><span><i className="weak" />Weak / Neutral</span><span><i className="emerging" />Emerging</span><span><i className="strong" />Strong / Exceptional</span></div></article><aside className="panel map-detail"><p className="eyebrow">SELECTED MARKET</p><h2>{selected.signal.market_name} <span>{selected.signal.asset_class}</span></h2><p className="map-location">{selected.feature.properties.msa}</p><div className="map-score"><strong>{formatScore(selected.signal.score)}</strong><span>{selected.signal.classification}</span></div><dl><dt>Demand</dt><dd>{formatScore(selected.analytics.demand_score)}</dd><dt>Supply balance</dt><dd>{formatScore(selected.analytics.supply_balance_score)}</dd><dt>Performance</dt><dd>{formatScore(selected.analytics.performance_score)}</dd><dt>Capital activity</dt><dd>{formatScore(selected.analytics.capital_activity_score)}</dd><dt>6M change</dt><dd className={selected.analytics.six_month_change >= 0 ? 'up' : 'down'}>{formatSignedScore(selected.analytics.six_month_change)}</dd></dl><button className="primary-button" type="button" onClick={() => onInspectSignal(selected.signal.market_id)}>Inspect signal decomposition</button><div className="map-market-list">{visibleMarkets.sort((left, right) => right.signal.score - left.signal.score).map((market) => <button className={market.signal.market_id === selected.signal.market_id ? 'selected' : ''} key={market.signal.market_id} type="button" onClick={() => setSelectedMarketId(market.signal.market_id)}><span>{market.signal.market_name}<small>{market.signal.asset_class}</small></span><strong>{formatScore(market.signal.score)}</strong></button>)}</div></aside></section>
  </>
}
