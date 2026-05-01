import { useAppStore } from '@/store/useAppStore'
import { ArrowRight } from 'lucide-react'

export function PreviewCard() {
  const files = useAppStore((s) => s.files)
  const previewIndex = useAppStore((s) => s.previewIndex)
  if (files.length === 0) return null
  const file = files[previewIndex] ?? null
  const changed = file && file.original_name !== file.new_name

  return (
    <div className="shrink-0 w-[400px] rounded-2xl border border-border bg-surface p-4 flex flex-col gap-1.5">
      <div className="flex items-center gap-2 text-xs font-medium text-text-dim uppercase tracking-wider">文件预览 · 第 {previewIndex + 1} / {files.length} 个</div>
      <div className="flex items-center gap-3">
        <span className={`text-[13px] ${changed ? 'text-text-dim line-through' : 'text-text-primary font-medium'}`}>
          {file?.original_name ?? '—'}
        </span>
        {changed && (
          <>
            <ArrowRight className="size-3.5 text-primary" />
            <span className="text-[13px] font-semibold text-primary">{file?.new_name ?? '—'}</span>
          </>
        )}
      </div>
      {file?.status === 'conflict' && (
        <span className="text-[11px] text-error font-medium">⚠ 文件名冲突</span>
      )}
    </div>
  )
}
