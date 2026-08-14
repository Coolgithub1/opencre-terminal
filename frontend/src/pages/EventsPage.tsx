import { useEffect, useMemo, useState } from 'react'
import { LoadState } from '../components/LoadState'
import {
  getExtractedEvents,
  getRssArticles,
  type ExtractedEvent,
  type RssArticle,
} from '../data/client'
import { titleCase } from '../utils/format'

const currency = (value: number) => (value ? `$${(value / 1_000_000).toFixed(0)}M` : 'Not stated')

export function EventsPage() {
  const [events, setEvents] = useState<ExtractedEvent[]>()
  const [articles, setArticles] = useState<RssArticle[]>()
  const [eventType, setEventType] = useState('All')
  const [selectedEventId, setSelectedEventId] = useState<string>()
  const [error, setError] = useState<string>()

  useEffect(() => {
    Promise.all([getExtractedEvents(), getRssArticles()])
      .then(([nextEvents, nextArticles]) => {
        setEvents(nextEvents)
        setArticles(nextArticles)
        setSelectedEventId(nextEvents[0]?.event_id)
      })
      .catch((reason: unknown) => {
        setError(reason instanceof Error ? reason.message : 'Could not load RSS events')
      })
  }, [])

  const eventTypes = useMemo(
    () => ['All', ...new Set(events?.map((event) => event.event_type) ?? [])],
    [events],
  )
  const visibleEvents = useMemo(
    () => (events ?? []).filter((event) => eventType === 'All' || event.event_type === eventType),
    [eventType, events],
  )
  const selected = events?.find((event) => event.event_id === selectedEventId) ?? visibleEvents[0]
  const categories = new Set(articles?.map((article) => article.category) ?? [])

  if (error || !events || !articles || !selected) {
    return <LoadState error={error} label="Loading static RSS event data..." />
  }

  return <>
    <div className="page-intro"><div><p className="eyebrow">RULE-BASED RSS</p><h1>Corporate Events</h1><p>Publisher feed metadata is normalized, deduplicated, and matched to transparent event, entity, and market rules.</p></div></div>
    <div className="demo-banner">{selected.data_label} Event classifications are deterministic rules, not editorial reporting or predictions.</div>
    <div className="filter-row"><label>Event type <select aria-label="Event type" value={eventType} onChange={(event) => setEventType(event.target.value)}>{eventTypes.map((option) => <option key={option} value={option}>{titleCase(option)}</option>)}</select></label><span>{visibleEvents.length} extracted events · {articles.length} RSS records · {categories.size} categories</span></div>
    <section className="event-workspace"><article className="panel"><div className="section-heading"><div><p className="eyebrow">STATIC EVENT FEED</p><h2>Recent structured events</h2></div><span>Metadata only</span></div><div className="rss-event-list">{visibleEvents.map((event) => <button className={event.event_id === selected.event_id ? 'selected' : ''} key={event.event_id} type="button" onClick={() => setSelectedEventId(event.event_id)}><span className="event-type">{titleCase(event.event_type)}</span><strong>{event.article_title}</strong><small>{event.location} · {event.company} · {event.event_date}</small><em>{Math.round(event.confidence * 100)}% rule confidence</em></button>)}</div></article><aside className="panel event-detail"><p className="eyebrow">EVENT DETAIL</p><h2>{selected.company}</h2><p className="event-detail-type">{titleCase(selected.event_type)} · {selected.location}</p><p>{selected.article_title}</p><dl><dt>Rule confidence</dt><dd>{Math.round(selected.confidence * 100)}%</dd><dt>Investment</dt><dd>{currency(selected.amount_usd)}</dd><dt>Employment</dt><dd>{selected.employment ? `${selected.employment.toLocaleString()} jobs` : 'Not stated'}</dd><dt>Entity match</dt><dd>{titleCase(selected.entity_resolution)}</dd><dt>Published</dt><dd>{selected.published_at}</dd></dl><div className="rule-tags">{selected.extraction_rules.map((rule) => <span key={rule}>{rule}</span>)}</div><a className="event-source-link" href={selected.url} target="_blank" rel="noreferrer">Open publisher link ↗</a><p className="event-provenance">Source: {selected.publisher}. The RSS process does not fetch the article page or retain its full text.</p></aside></section>
  </>
}
