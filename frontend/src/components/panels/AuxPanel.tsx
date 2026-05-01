import { useAppStore } from '@/store/useAppStore'
import type { RuleSegment } from '@/store/types'
import { AnimatePresence, motion } from 'framer-motion'

export function AuxPanel() {
  const segments = useAppStore((s) => s.segments)
  const selectedIndex = useAppStore((s) => s.selectedSegmentIndex)
  const updateSegment = useAppStore((s) => s.updateSegment)
  const seg: RuleSegment | undefined = selectedIndex >= 0 ? segments[selectedIndex] : undefined

  return (
    <AnimatePresence>
      {seg && (
        <motion.div initial={{ height: 0, opacity: 0 }} animate={{ height: 152, opacity: 1 }} exit={{ height: 0, opacity: 0 }}
          transition={{ duration: 0.25, ease: [0.25, 0.1, 0.25, 1] }} className="overflow-hidden mx-4">
          <div className="rounded-2xl border border-border bg-surface p-4 mt-2">
            <div className="flex items-center gap-4 flex-wrap">
              <span className="text-[13px] font-bold text-primary">【{seg.label}】</span>
              {seg.type === 'KEYWORD' && (<>
                <label className="text-[11px] font-medium text-text-dim">关键词</label>
                <input className="w-60 h-7 rounded-xl bg-surface-raised border border-border px-2.5 text-[12px] text-text-primary placeholder:text-text-dim focus:outline-none focus:border-primary"
                  value={seg.keyword_list} placeholder="逗号分隔多个关键词..." onChange={(e) => updateSegment(selectedIndex, { keyword_list: e.target.value })} />
                <label className="text-[11px] font-medium text-text-dim">范围</label>
                <input type="number" min={0} max={20} className="w-12 h-7 rounded-xl bg-surface-raised border border-border px-1 text-[12px] text-text-primary text-center focus:outline-none focus:border-primary"
                  value={seg.keyword_range} onChange={(e) => updateSegment(selectedIndex, { keyword_range: Number(e.target.value) })} />
              </>)}
              {seg.type === 'EXTRACT' && (<>
                <label className="text-[11px] font-medium text-text-dim">正则</label>
                <input className="w-44 h-7 rounded-xl bg-surface-raised border border-border px-2.5 text-[12px] text-text-primary placeholder:text-text-dim focus:outline-none focus:border-primary"
                  value={seg.extract_regex} placeholder="自定义正则..." onChange={(e) => updateSegment(selectedIndex, { extract_regex: e.target.value })} />
                <label className="text-[11px] font-medium text-text-dim">字数</label>
                <input type="number" min={1} max={64} className="w-10 h-7 rounded-xl bg-surface-raised border border-border px-1 text-[12px] text-text-primary text-center focus:outline-none focus:border-primary"
                  value={seg.extract_min_len} onChange={(e) => updateSegment(selectedIndex, { extract_min_len: Number(e.target.value) })} />
                <span className="text-[12px] text-text-dim">—</span>
                <input type="number" min={1} max={64} className="w-10 h-7 rounded-xl bg-surface-raised border border-border px-1 text-[12px] text-text-primary text-center focus:outline-none focus:border-primary"
                  value={seg.extract_max_len} onChange={(e) => updateSegment(selectedIndex, { extract_max_len: Number(e.target.value) })} />
                <label className="text-[11px] font-medium text-text-dim">前置词</label>
                <input className="w-24 h-7 rounded-xl bg-surface-raised border border-border px-2.5 text-[12px] text-text-primary focus:outline-none focus:border-primary"
                  value={seg.extract_keywords_before} onChange={(e) => updateSegment(selectedIndex, { extract_keywords_before: e.target.value })} />
                <label className="text-[11px] font-medium text-text-dim">后置词</label>
                <input className="w-24 h-7 rounded-xl bg-surface-raised border border-border px-2.5 text-[12px] text-text-primary focus:outline-none focus:border-primary"
                  value={seg.extract_keywords_after} onChange={(e) => updateSegment(selectedIndex, { extract_keywords_after: e.target.value })} />
              </>)}
              {seg.type === 'COUNTER' && (<>
                <label className="text-[11px] font-medium text-text-dim">起始</label>
                <input type="number" min={0} max={9999} className="w-16 h-7 rounded-xl bg-surface-raised border border-border px-1 text-[12px] text-text-primary text-center focus:outline-none focus:border-primary"
                  value={seg.counter_start} onChange={(e) => updateSegment(selectedIndex, { counter_start: Number(e.target.value) })} />
                <label className="text-[11px] font-medium text-text-dim">步长</label>
                <input type="number" min={1} max={100} className="w-12 h-7 rounded-xl bg-surface-raised border border-border px-1 text-[12px] text-text-primary text-center focus:outline-none focus:border-primary"
                  value={seg.counter_step} onChange={(e) => updateSegment(selectedIndex, { counter_step: Number(e.target.value) })} />
                <label className="text-[11px] font-medium text-text-dim">补零</label>
                <input type="number" min={0} max={10} className="w-12 h-7 rounded-xl bg-surface-raised border border-border px-1 text-[12px] text-text-primary text-center focus:outline-none focus:border-primary"
                  value={seg.counter_padding} onChange={(e) => updateSegment(selectedIndex, { counter_padding: Number(e.target.value) })} />
              </>)}
              {seg.type === 'DATE' && (<>
                <label className="text-[11px] font-medium text-text-dim">格式</label>
                <select className="w-36 h-7 rounded-xl bg-surface-raised border border-border px-2 text-[12px] text-text-primary focus:outline-none focus:border-primary"
                  value={seg.date_format} onChange={(e) => updateSegment(selectedIndex, { date_format: e.target.value })}>
                  <option value="%Y%m%d">%Y%m%d</option><option value="%Y-%m-%d">%Y-%m-%d</option>
                  <option value="%Y_%m_%d">%Y_%m_%d</option><option value="%m%d">%m%d</option>
                  <option value="%Y%m">%Y%m</option><option value="%Y">%Y</option>
                  <option value="%Y%m%d_%H%M">%Y%m%d_%H%M</option><option value="%d%m%Y">%d%m%Y</option>
                </select>
              </>)}
              {seg.type === 'TABLE_FIELD' && (<>
                <label className="text-[11px] font-medium text-text-dim">匹配列</label>
                <select className="w-36 h-7 rounded-xl bg-surface-raised border border-border px-2 text-[12px] text-text-primary focus:outline-none focus:border-primary"
                  value={seg.table_column || ''} onChange={(e) => updateSegment(selectedIndex, { table_column: e.target.value })}>
                  <option value="">（请先导入表格）</option>
                </select>
              </>)}
            </div>
          </div>
        </motion.div>
      )}
    </AnimatePresence>
  )
}
