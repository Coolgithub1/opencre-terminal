export type Signal = { market: string; asset_class: string; score: number; change: number }
export type Event = { type: string; location: string; detail: string; time: string }
export type DashboardData = {
  data_label: string
  updated_at: string
  signals: Signal[]
  events: Event[]
  indicators: { label: string; value: string; change: string }[]
}

const datasetUrl = (path: string) => `${import.meta.env.BASE_URL}${path}`

export async function getDashboard(): Promise<DashboardData> {
  const response = await fetch(datasetUrl('data/v1/dashboard.json'))
  if (!response.ok) throw new Error(`Could not load dashboard dataset (${response.status})`)
  return response.json() as Promise<DashboardData>
}
