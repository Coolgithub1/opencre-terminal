type LoadStateProps = { error?: string; label?: string }

export function LoadState({ error, label = 'Loading static datasets…' }: LoadStateProps) {
  return <div className={error ? 'error' : 'loading'}>{error ?? label}</div>
}
