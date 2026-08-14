import { useEffect, useRef } from 'react'
import type { GeoJSONSource, Map as MapLibreMap } from 'maplibre-gl'
import 'maplibre-gl/dist/maplibre-gl.css'

type MapFeature = {
  type: 'Feature'
  id: string
  geometry: { type: 'Point'; coordinates: [number, number] }
  properties: { market_id: string; market_name: string; score: number; asset_class: string; classification: string }
}

type MarketMapProps = { features: MapFeature[]; onSelect: (marketId: string) => void }

const terminalStyle = {
  version: 8 as const,
  sources: {},
  layers: [{ id: 'terminal-background', type: 'background' as const, paint: { 'background-color': '#0b1723' } }],
}

export function MarketMap({ features, onSelect }: MarketMapProps) {
  const container = useRef<HTMLDivElement>(null)
  const map = useRef<MapLibreMap | null>(null)
  const mapLibrary = useRef<typeof import('maplibre-gl') | null>(null)
  const markers = useRef<Array<{ remove: () => void }>>([])
  const select = useRef(onSelect)
  select.current = onSelect

  const renderMarkers = (
    maplibregl: typeof import('maplibre-gl'),
    nextMap: MapLibreMap,
    nextFeatures: MapFeature[],
  ) => {
    markers.current.forEach((marker) => marker.remove())
    markers.current = nextFeatures.map((feature) => {
      const marker = document.createElement('button')
      marker.type = 'button'
      marker.className = `market-map-marker ${feature.properties.classification.toLowerCase()}`
      marker.style.width = `${Math.round(10 + feature.properties.score / 7)}px`
      marker.style.height = marker.style.width
      marker.setAttribute('aria-label', `Select ${feature.properties.market_name} ${feature.properties.asset_class} ${feature.properties.score.toFixed(1)}`)
      marker.addEventListener('click', () => select.current(feature.properties.market_id))
      return new maplibregl.Marker({ element: marker, anchor: 'center' })
        .setLngLat(feature.geometry.coordinates)
        .addTo(nextMap)
    })
  }

  useEffect(() => {
    let disposed = false
    void import('maplibre-gl').then((maplibregl) => {
      if (!container.current || disposed) return
      const nextMap = new maplibregl.Map({ container: container.current, style: terminalStyle, center: [-96, 38], zoom: 3.15, minZoom: 2.5, maxZoom: 9, attributionControl: false })
      map.current = nextMap
      mapLibrary.current = maplibregl
      nextMap.addControl(new maplibregl.NavigationControl({ showCompass: false }), 'top-right')
      const addMarketLayers = () => {
        nextMap.addSource('markets', { type: 'geojson', data: { type: 'FeatureCollection', features } })
        nextMap.addLayer({ id: 'market-halos', type: 'circle', source: 'markets', paint: { 'circle-radius': ['interpolate', ['linear'], ['get', 'score'], 0, 7, 100, 19], 'circle-color': '#2de3b8', 'circle-opacity': 0.13 } })
        nextMap.addLayer({ id: 'market-points', type: 'circle', source: 'markets', paint: { 'circle-radius': ['interpolate', ['linear'], ['get', 'score'], 0, 4, 100, 11], 'circle-color': ['interpolate', ['linear'], ['get', 'score'], 0, '#ff7480', 50, '#f0cf65', 70, '#2de3b8'], 'circle-stroke-width': 1, 'circle-stroke-color': '#dffdf5', 'circle-opacity': 0.95 } })
        nextMap.on('mouseenter', 'market-points', () => { nextMap.getCanvas().style.cursor = 'pointer' })
        nextMap.on('mouseleave', 'market-points', () => { nextMap.getCanvas().style.cursor = '' })
        nextMap.on('click', 'market-points', (event) => {
          const marketId = event.features?.[0]?.properties?.market_id
          if (marketId) select.current(marketId)
        })
        renderMarkers(maplibregl, nextMap, features)
      }
      if (nextMap.isStyleLoaded()) addMarketLayers()
      else nextMap.once('load', addMarketLayers)
    })
    return () => {
      disposed = true
      markers.current.forEach((marker) => marker.remove())
      markers.current = []
      map.current?.remove()
      map.current = null
      mapLibrary.current = null
    }
  }, [])

  useEffect(() => {
    const source = map.current?.getSource('markets') as GeoJSONSource | undefined
    source?.setData({ type: 'FeatureCollection', features })
    if (map.current && mapLibrary.current) renderMarkers(mapLibrary.current, map.current, features)
  }, [features])

  return <div className="market-map" ref={container} role="application" aria-label="Interactive market signal map" />
}
