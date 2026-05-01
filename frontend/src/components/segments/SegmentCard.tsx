import { useSortable } from '@dnd-kit/sortable'
import { CSS } from '@dnd-kit/utilities'
import { GripVertical, Trash2 } from 'lucide-react'
import type { RuleSegment } from '@/store/types'
import { useAppStore } from '@/store/useAppStore'
import { cn } from '@/lib/utils'

const TYPE_ICONS: Record<string, string> = { TEXT: 'Aa', COUNTER: '#', DATE: '日', EXTRACT: '识', TABLE_FIELD: '表', KEYWORD: 'K' }

interface Props { segment: RuleSegment; index: number; isSelected: boolean }

export function SegmentCard({ segment, index, isSelected }: Props) {
  const { attributes, listeners, setNodeRef, transform, transition, isDragging } = useSortable({ id: `${index}` })
  const selectSegment = useAppStore((s) => s.selectSegment)
  const removeSegment = useAppStore((s) => s.removeSegment)
  const updateSegment = useAppStore((s) => s.updateSegment)
  const availableFields = useAppStore((s) => s.availableFields)
  const tableColumns = useAppStore((s) => s.tableInfo?.columns) ?? []
  const style = { transform: CSS.Transform.toString(transform), transition, opacity: isDragging ? 0.4 : 1, zIndex: isDragging ? 50 : 0 }

  return (
    <div ref={setNodeRef} style={style}
      {...attributes}
      {...listeners}
      className={cn(
        'flex-shrink-0 w-[180px] rounded-2xl border p-3 cursor-grab active:cursor-grabbing transition-all duration-200 touch-none',
        isDragging && 'shadow-2xl shadow-black/20 scale-105 z-50',
        isSelected
          ? 'border-primary/40 bg-primary/5 shadow-sm shadow-primary/10'
          : 'border-border bg-surface hover:border-border-hover hover:bg-surface-raised',
      )}
      onClick={(e) => { e.stopPropagation(); selectSegment(index) }}>
      <div className="flex items-center gap-1.5 mb-2">
        <GripVertical className="size-3.5 text-text-dim shrink-0" />
        <span className={cn(
          'inline-flex items-center justify-center size-6 rounded-lg text-white text-[10px] font-bold shrink-0',
          isSelected ? 'bg-primary' : 'bg-text-dim',
        )}>
          {TYPE_ICONS[segment.type] || '?'}</span>
        <span className="text-[12px] font-semibold text-text-primary truncate flex-1">{segment.label}</span>
        <button className="text-text-dim hover:text-error shrink-0 transition-colors cursor-pointer"
          onPointerDown={(e) => e.stopPropagation()}
          onClick={(e) => { e.stopPropagation(); removeSegment(index) }}>
          <Trash2 className="size-3" /></button>
      </div>
      <div className="flex items-center gap-1" onPointerDown={(e) => e.stopPropagation()}>
        {segment.type === 'TEXT' && (
          <input className="w-full h-8 rounded-xl bg-surface-raised border border-border px-2.5 text-[12px] text-text-primary placeholder:text-text-dim focus:outline-none focus:border-primary"
            value={segment.text} placeholder="输入文本..." onChange={(e) => updateSegment(index, { text: e.target.value })} />
        )}
        {segment.type === 'COUNTER' && (
          <div className="flex items-center gap-1 text-[12px] text-text-dim">
            <span>起</span>
            <input type="number" min={0} max={9999} className="w-10 h-8 rounded-xl bg-surface-raised border border-border px-1 text-[12px] text-text-primary text-center focus:outline-none focus:border-primary"
              value={segment.counter_start} onChange={(e) => updateSegment(index, { counter_start: Number(e.target.value) })} />
            <span>位</span>
            <input type="number" min={0} max={10} className="w-8 h-8 rounded-xl bg-surface-raised border border-border px-1 text-[12px] text-text-primary text-center focus:outline-none focus:border-primary"
              value={segment.counter_padding} onChange={(e) => updateSegment(index, { counter_padding: Number(e.target.value) })} />
          </div>
        )}
        {segment.type === 'KEYWORD' && (
          <input className="w-full h-8 rounded-xl bg-surface-raised border border-border px-2.5 text-[12px] text-text-primary placeholder:text-text-dim focus:outline-none focus:border-primary"
            value={segment.keyword_list} placeholder="关键词,逗号分隔..." onChange={(e) => updateSegment(index, { keyword_list: e.target.value })} />
        )}
        {segment.type === 'DATE' && (
          <select className="w-full h-8 rounded-xl bg-surface-raised border border-border px-1.5 text-[12px] text-text-primary focus:outline-none focus:border-primary"
            value={segment.date_format} onChange={(e) => updateSegment(index, { date_format: e.target.value })}>
            <option value="%Y%m%d">%Y%m%d</option>
            <option value="%Y-%m-%d">%Y-%m-%d</option>
            <option value="%Y_%m_%d">%Y_%m_%d</option>
            <option value="%m%d">%m%d</option>
            <option value="%Y%m">%Y%m</option>
          </select>
        )}
        {segment.type === 'EXTRACT' && (
          <select className="w-full h-8 rounded-xl bg-surface-raised border border-border px-1.5 text-[12px] text-text-primary focus:outline-none focus:border-primary"
            value={segment.extract_field || ''} onChange={(e) => updateSegment(index, { extract_field: e.target.value })}>
            <option value="">选择字段</option>
            {availableFields.map((f) => <option key={f} value={f}>{f}</option>)}
          </select>
        )}
        {segment.type === 'TABLE_FIELD' && (
          <select className="w-full h-8 rounded-xl bg-surface-raised border border-border px-1.5 text-[12px] text-text-primary focus:outline-none focus:border-primary"
            value={segment.table_column || ''} onChange={(e) => updateSegment(index, { table_column: e.target.value })}>
            <option value="">选择列</option>
            {tableColumns.map((c) => <option key={c} value={c}>{c}</option>)}
          </select>
        )}
      </div>
    </div>
  )
}
