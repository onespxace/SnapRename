import { useState } from 'react'
import { Popover, PopoverContent, PopoverTrigger } from '@/components/ui/popover'
import { Button } from '@/components/ui/button'
import { Plus } from 'lucide-react'
import { useAppStore } from '@/store/useAppStore'

export function AddSegmentMenu() {
  const [open, setOpen] = useState(false)
  const addSegment = useAppStore((s) => s.addSegment)
  const availableFields = useAppStore((s) => s.availableFields)
  const tableInfo = useAppStore((s) => s.tableInfo)

  const doAdd = (type: string, kwargs?: Record<string, any>) => { addSegment(type, kwargs); setOpen(false) }

  return (
    <Popover open={open} onOpenChange={setOpen}>
      <PopoverTrigger asChild>
        <Button size="icon" className="rounded-2xl size-9"><Plus className="size-[18px]" /></Button>
      </PopoverTrigger>
      <PopoverContent className="w-48" align="end">
        <button className="w-full text-left px-3 py-2.5 rounded-xl text-[13px] text-text-primary hover:bg-primary/10 hover:text-primary transition-colors"
          onClick={() => doAdd('TEXT', { text: '输入文本' })}>固定文本</button>
        <button className="w-full text-left px-3 py-2.5 rounded-xl text-[13px] text-text-primary hover:bg-primary/10 hover:text-primary transition-colors"
          onClick={() => doAdd('COUNTER', { counter_start: 1, counter_padding: 2 })}>序号</button>
        <button className="w-full text-left px-3 py-2.5 rounded-xl text-[13px] text-text-primary hover:bg-primary/10 hover:text-primary transition-colors"
          onClick={() => doAdd('DATE')}>日期</button>
        <button className="w-full text-left px-3 py-2.5 rounded-xl text-[13px] text-text-primary hover:bg-primary/10 hover:text-primary transition-colors"
          onClick={() => doAdd('KEYWORD', { keyword_list: '', keyword_range: 3 })}>关键词</button>
        <div className="h-px bg-border my-1.5" />
        <div className="px-3 py-1.5 text-[11px] text-text-dim font-semibold uppercase tracking-wider">自动识别</div>
        {availableFields.length > 0
          ? availableFields.map((f) => (
              <button key={f} className="w-full text-left px-3 py-2.5 rounded-xl text-[13px] text-text-primary hover:bg-primary/10 hover:text-primary transition-colors"
                onClick={() => doAdd('EXTRACT', { extract_field: f })}>{f}</button>
            ))
          : <div className="px-3 py-1.5 text-[12px] text-text-dim">(添加文件后自动检测)</div>}
        <div className="h-px bg-border my-1.5" />
        <div className="px-3 py-1.5 text-[11px] text-text-dim font-semibold uppercase tracking-wider">表格字段</div>
        {tableInfo
          ? tableInfo.columns.map((c) => (
              <button key={c} className="w-full text-left px-3 py-2.5 rounded-xl text-[13px] text-text-primary hover:bg-primary/10 hover:text-primary transition-colors"
                onClick={() => doAdd('TABLE_FIELD', { table_column: c })}>{c}</button>
            ))
          : <div className="px-3 py-1.5 text-[12px] text-text-dim">(需先导入表格)</div>}
      </PopoverContent>
    </Popover>
  )
}
