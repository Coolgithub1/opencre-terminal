import { useEffect, useState } from 'react'
import { LoadState } from '../components/LoadState'
import { getDatasetIndex, getSources, type DatasetIndex, type SourceRegistry } from '../data/client'

export function DataSourcesPage() {
  const [sources, setSources] = useState<SourceRegistry>()
  const [index, setIndex] = useState<DatasetIndex>()
  const [error, setError] = useState<string>()

  useEffect(() => { Promise.all([getSources(), getDatasetIndex()]).then(([nextSources, nextIndex]) => { setSources(nextSources); setIndex(nextIndex) }).catch((reason: unknown) => setError(reason instanceof Error ? reason.message : 'Could not load data provenance')) }, [])
  if (error || !sources || !index) return <LoadState error={error} label="Loading data provenance…" />
  return <><div className="page-intro"><div><p className="eyebrow">AUDIT TRAIL</p><h1>Data Sources</h1><p>Every displayed dataset is static, versioned, and labeled with its source and methodology.</p></div></div><div className="demo-banner">{sources.data_label}</div><section className="source-grid">{sources.sources.map((source) => <article className="panel" key={source.source}><h2>{source.source}</h2><p>{source.methodology}</p><dl><dt>License</dt><dd>{source.license}</dd><dt>Update cadence</dt><dd>{source.update_frequency}</dd></dl><a href={source.source_url} target="_blank" rel="noreferrer">Methodology source ↗</a></article>)}</section><section className="panel dataset-index"><div className="section-heading"><div><p className="eyebrow">CATALOGUE</p><h2>Published datasets</h2></div><span>v{index.schema_version}</span></div>{index.datasets.map((dataset) => <div key={dataset.path}><span>{dataset.name}</span><code>{dataset.path}</code><strong>{dataset.record_count.toLocaleString()}</strong></div>)}</section></>
}
