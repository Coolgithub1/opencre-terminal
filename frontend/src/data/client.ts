export type SignalComponent = {
  key: string
  label: string
  source_field: string
  score: number
  weight: number
  contribution: number
}

export type SignalRecord = {
  signal_id: string
  signal_key: string
  signal_name: string
  signal_version: string
  market_id: string
  market_name: string
  asset_class: string
  score: number
  classification: string
  components: SignalComponent[]
  observation_date: string
  data_label: string
}

export type SignalHistoryPoint = Omit<SignalRecord, 'components'> & {
  employment_contribution: number
  rent_growth_contribution: number
  absorption_contribution: number
  vacancy_contribution: number
  investment_contribution: number
  construction_contribution: number
}

export type MarketAnalytics = {
  market_id: string
  market_name: string
  asset_class: string
  market_activity_score: number
  demand_score: number
  supply_balance_score: number
  performance_score: number
  capital_activity_score: number
  event_activity_score: number
  rent_growth: number
  six_month_change: number
  observation_date: string
  data_label: string
}

export type EventRecord = {
  event_id: string
  event_type: string
  location: string
  event_date: string
  company: string
  employment: number
}

export type PipelineStatus = {
  pipeline: string
  status: string
  last_updated: string
  data_label: string
  datasets: { name: string; records: number; status: string }[]
}

export type SignalRankings = {
  as_of_date: string
  data_label: string
  rankings: {
    top_signals: Array<Pick<SignalRecord, 'market_id' | 'market_name' | 'asset_class' | 'signal_name' | 'score' | 'classification'>>
    bottom_signals: Array<Pick<SignalRecord, 'market_id' | 'market_name' | 'asset_class' | 'signal_name' | 'score' | 'classification'>>
  }
}

export type SourceRegistry = {
  data_label: string
  sources: { source: string; source_url: string; license: string; update_frequency: string; methodology: string }[]
}

export type DatasetIndex = {
  schema_version: string
  last_updated: string
  data_label: string
  datasets: { name: string; path: string; format: string; record_count: number; schema_version: string }[]
}

const dataUrl = (path: string) => `${import.meta.env.BASE_URL}data/v1/${path}`

async function getJson<T>(path: string): Promise<T> {
  const response = await fetch(dataUrl(path), { cache: 'no-cache' })
  if (!response.ok) throw new Error(`Could not load ${path} (${response.status})`)
  return response.json() as Promise<T>
}

export const getSignals = () => getJson<SignalRecord[]>('signals/latest.json')
export const getSignalHistory = (marketId: string) => getJson<SignalHistoryPoint[]>(`signals/history/${marketId}.json`)
export const getSignalRankings = () => getJson<SignalRankings>('signals/rankings.json')
export const getMarketAnalytics = () => getJson<MarketAnalytics[]>('markets/latest_analytics.json')
export const getEvents = () => getJson<EventRecord[]>('events/latest.json')
export const getPipelineStatus = () => getJson<PipelineStatus>('metadata/pipeline_status.json')
export const getSources = () => getJson<SourceRegistry>('metadata/sources.json')
export const getDatasetIndex = () => getJson<DatasetIndex>('index.json')
