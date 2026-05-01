import { useAppStore } from '@/store/useAppStore'

export function StatusBar() {
  const text = useAppStore((s) => s.statusText)
  const level = useAppStore((s) => s.statusLevel)
  const colors = { info: 'text-text-dim', warning: 'text-warning', error: 'text-error' }
  return (
    <div className="h-8 border-t border-border bg-surface/50 backdrop-blur-xl flex items-center px-4 shrink-0">
      <span className={`text-[11px] font-medium ${colors[level]}`}>{text}</span>
    </div>
  )
}
