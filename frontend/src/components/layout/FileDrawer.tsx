import { useRef, useCallback } from 'react'
import { useAppStore } from '@/store/useAppStore'
import { AnimatePresence, motion } from 'framer-motion'
import { X } from 'lucide-react'
import { useVirtualizer } from '@tanstack/react-virtual'

export function FileDrawer() {
  const show = useAppStore((s) => s.showFileDrawer)
  const files = useAppStore((s) => s.files)
  const previewIndex = useAppStore((s) => s.previewIndex)
  const setPreviewIndex = useAppStore((s) => s.setPreviewIndex)
  const toggleFileDrawer = useAppStore((s) => s.toggleFileDrawer)
  const parentRef = useRef<HTMLDivElement>(null!)
  const getScrollElement = useCallback(() => parentRef.current, [])
  const estimateSize = useCallback(() => 44, [])
  const rowVirtualizer = useVirtualizer({ count: files.length, getScrollElement, estimateSize, overscan: 5 })

  return (
    <AnimatePresence>
      {show && (
        <motion.aside initial={{ x: -420, opacity: 0 }} animate={{ x: 0, opacity: 1 }} exit={{ x: -420, opacity: 0 }}
          transition={{ type: 'spring', damping: 28, stiffness: 300 }}
          className="fixed left-0 top-0 bottom-0 w-[420px] bg-surface-overlay backdrop-blur-2xl border-r border-border z-50 flex flex-col shadow-2xl shadow-black/10">
          <div className="h-12 bg-transparent flex items-center px-5 shrink-0">
            <span className="text-[14px] font-bold text-text-primary">文件列表</span>
            <span className="ml-2 text-[12px] text-text-dim">({files.length})</span>
            <div className="flex-1" />
            <button className="size-7 flex items-center justify-center rounded-full text-text-dim hover:text-text-primary hover:bg-surface-raised transition-colors" onClick={toggleFileDrawer}>
              <X className="size-4" />
            </button>
          </div>
          <div ref={parentRef} className="flex-1 overflow-auto px-2">
            <div style={{ height: `${rowVirtualizer.getTotalSize()}px`, position: 'relative' }}>
              {rowVirtualizer.getVirtualItems().map((vRow) => {
                const f = files[vRow.index]
                if (!f) return null
                return (
                  <button key={vRow.index}
                    style={{ position: 'absolute', top: 0, left: 0, width: '100%', height: `${vRow.size}px`, transform: `translateY(${vRow.start}px)` }}
                    className={`flex items-center gap-3 px-3 rounded-xl text-left transition-colors ${
                      vRow.index === previewIndex
                        ? 'bg-primary text-white shadow-sm shadow-primary/20'
                        : 'text-text-primary hover:bg-surface-raised'
                    }`}
                    onClick={() => setPreviewIndex(vRow.index)}>
                    <span className="text-[11px] w-8 shrink-0 tabular-nums font-medium opacity-60">{vRow.index + 1}</span>
                    <span className="text-[12px] flex-1 truncate">{f.original_name}</span>
                  </button>
                )
              })}
            </div>
          </div>
        </motion.aside>
      )}
    </AnimatePresence>
  )
}
