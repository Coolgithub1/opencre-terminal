import { useEffect, useRef } from 'react'
import type { ECharts } from 'echarts/core'
import type { SignalHistoryPoint } from '../data/client'
import { formatDate } from '../utils/format'

export function SignalHistoryChart({ history, marketName }: { history: SignalHistoryPoint[]; marketName: string }) {
  const container = useRef<HTMLDivElement>(null)

  useEffect(() => {
    let chart: ECharts | undefined
    let observer: ResizeObserver | undefined
    let cancelled = false
    void import('./echarts').then(({ init }) => {
      if (!container.current || cancelled) return
      chart = init(container.current)
      chart.setOption({
        animationDuration: 250,
        backgroundColor: 'transparent',
        tooltip: { trigger: 'axis', valueFormatter: (value: number | string) => `${Number(value).toFixed(1)} / 100` },
        grid: { left: 42, right: 20, top: 36, bottom: 36 },
        xAxis: { type: 'category', data: history.map((point) => formatDate(point.observation_date)), axisLabel: { color: '#7f95a8', fontSize: 10 }, axisLine: { lineStyle: { color: '#294054' } } },
        yAxis: { type: 'value', min: 0, max: 100, splitLine: { lineStyle: { color: '#1c3142' } }, axisLabel: { color: '#7f95a8', fontSize: 10 } },
        series: [{ name: `${marketName} signal`, type: 'line', smooth: true, showSymbol: false, data: history.map((point) => point.score), lineStyle: { color: '#2de3b8', width: 2 }, areaStyle: { color: 'rgba(45, 227, 184, 0.12)' } }],
      })
      observer = new ResizeObserver(() => chart?.resize())
      observer.observe(container.current)
    })
    return () => { cancelled = true; observer?.disconnect(); chart?.dispose() }
  }, [history, marketName])

  return <div className="signal-chart" ref={container} aria-label={`${marketName} signal history chart`} />
}
