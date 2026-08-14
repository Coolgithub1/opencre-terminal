export const formatScore = (value: number) => value.toFixed(1)
export const formatSignedScore = (value: number) => `${value >= 0 ? '+' : ''}${value.toFixed(1)}`
export const formatDate = (value: string) => new Intl.DateTimeFormat('en-US', { month: 'short', year: 'numeric' }).format(new Date(`${value}T00:00:00`))
export const titleCase = (value: string) => value.replaceAll('_', ' ').replace(/\b\w/g, (letter) => letter.toUpperCase())
