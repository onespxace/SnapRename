import { useState } from 'react'
import { DndContext, closestCenter, PointerSensor, useSensor, useSensors, type DragEndEvent } from '@dnd-kit/core'
import { SortableContext, horizontalListSortingStrategy, useSortable } from '@dnd-kit/sortable'
import { CSS } from '@dnd-kit/utilities'
import { useAppStore } from '@/store/useAppStore'
import { GripVertical, Trash2, Plus, Tags } from 'lucide-react'
import { Popover, PopoverContent, PopoverTrigger } from '@/components/ui/popover'
import { Button } from '@/components/ui/button'
import { cn } from '@/lib/utils'
import { AnimatePresence, motion } from 'framer-motion'

const pointerSensorOptions = {
  activationConstraint: { distance: 3 },
}

function ClassifyCard({ field, index, onRemove }: { field: string; index: number; onRemove: (i: number) => void }) {
  const { attributes, listeners, setNodeRef, transform, transition, isDragging } = useSortable({ id: `${index}` })
  const style = { transform: CSS.Transform.toString(transform), transition, opacity: isDragging ? 0.4 : 1, zIndex: isDragging ? 50 : 0 }
  const labelMap: Record<string, string> = {
    '年级': '年级(自动)', '大学号前2位': '年份2位', '大学号前4位': '年份4位', '大学号前6位': '院系6位',
  }

  return (
    <div ref={setNodeRef} style={style}
      className={cn(
        'flex-shrink-0 flex items-center gap-1.5 h-9 rounded-xl border border-border bg-surface px-3 cursor-pointer transition-all',
        isDragging && 'shadow-xl shadow-black/20 scale-105 border-primary/40',
      )}>
      <button {...attributes} {...listeners} className="text-text-dim hover:text-text-secondary cursor-grab active:cursor-grabbing touch-none">
        <GripVertical className="size-3" /></button>
      <Tags className="size-3 text-text-dim" />
      <span className="text-[12px] font-medium text-text-primary whitespace-nowrap">{labelMap[field] || field}</span>
      <button className="text-text-dim hover:text-error shrink-0" onClick={(e) => { e.stopPropagation(); onRemove(index) }}>
        <Trash2 className="size-2.5" /></button>
    </div>
  )
}

export function ClassifyBar() {
  const classifyRules = useAppStore((s) => s.classifyRules)
  const classifyFields = useAppStore((s) => s.classifyFields)
  const setClassifyRules = useAppStore((s) => s.setClassifyRules)
  const [open, setOpen] = useState(false)
  const [sortKey, setSortKey] = useState(0)

  const sensors = useSensors(useSensor(PointerSensor, pointerSensorOptions))
  const items = classifyRules.map((_, i) => `${i}`)

  const addRule = (field: string) => {
    if (!classifyRules.includes(field)) {
      setClassifyRules([...classifyRules, field])
    }
    setOpen(false)
  }
  const removeRule = (index: number) => {
    setClassifyRules(classifyRules.filter((_, i) => i !== index))
  }
  const reorder = (from: number, to: number) => {
    if (from === to) return
    const arr = [...classifyRules]
    const [m] = arr.splice(from, 1)
    arr.splice(to, 0, m)
    setClassifyRules(arr)
    setSortKey(k => k + 1)
  }

  return (
    <div className="rounded-2xl border border-border/50 bg-surface/50 p-3 flex items-center gap-2">
      <span className="text-[11px] font-semibold text-text-dim uppercase tracking-wider shrink-0 mr-1">分组</span>
      <DndContext key={sortKey} sensors={sensors} collisionDetection={closestCenter}
        onDragEnd={(e: DragEndEvent) => {
          if (e.over && e.active.id !== e.over.id) reorder(Number(e.active.id), Number(e.over.id))
        }}>
        <SortableContext items={items} strategy={horizontalListSortingStrategy}>
          <div className="flex gap-1.5 overflow-x-auto flex-1 items-center">
            {classifyRules.map((field, i) => (
              <ClassifyCard key={`${i}`} field={field} index={i} onRemove={removeRule} />
            ))}
            {classifyRules.length === 0 && <span className="text-[11px] text-text-dim">选择分组字段...</span>}
          </div>
        </SortableContext>
      </DndContext>
      <Popover open={open} onOpenChange={setOpen}>
        <PopoverTrigger asChild>
          <Button size="icon" className="rounded-xl size-7 shrink-0" variant="ghost">
            <Plus className="size-3.5" /></Button>
        </PopoverTrigger>
        <PopoverContent className="w-44" align="end">
          <div className="px-3 py-1.5 text-[11px] text-text-dim font-semibold uppercase tracking-wider">自动分组</div>
          <button className="w-full text-left px-3 py-2 rounded-xl text-[13px] text-text-primary hover:bg-primary/10 hover:text-primary transition-colors"
            onClick={() => addRule('年级')}>年级 (自动)</button>
          <button className="w-full text-left px-3 py-2 rounded-xl text-[13px] text-text-primary hover:bg-primary/10 hover:text-primary transition-colors"
            onClick={() => addRule('大学号前2位')}>按年份2位</button>
          <button className="w-full text-left px-3 py-2 rounded-xl text-[13px] text-text-primary hover:bg-primary/10 hover:text-primary transition-colors"
            onClick={() => addRule('大学号前4位')}>按年份4位</button>
          <button className="w-full text-left px-3 py-2 rounded-xl text-[13px] text-text-primary hover:bg-primary/10 hover:text-primary transition-colors"
            onClick={() => addRule('大学号前6位')}>按院系6位</button>
          <div className="h-px bg-border my-1.5" />
          <div className="px-3 py-1.5 text-[11px] text-text-dim font-semibold uppercase tracking-wider">字段分组</div>
          {classifyFields.filter(f => !['年级', '大学号前2位', '大学号前4位', '大学号前6位'].includes(f)).length > 0
            ? classifyFields.filter(f => !['年级', '大学号前2位', '大学号前4位', '大学号前6位'].includes(f)).map((f) => (
                <button key={f} className="w-full text-left px-3 py-2 rounded-xl text-[13px] text-text-primary hover:bg-primary/10 hover:text-primary transition-colors"
                  onClick={() => addRule(f)}>{f}</button>
              ))
            : <div className="px-3 py-1.5 text-[12px] text-text-dim">(添加文件后自动检测)</div>}
          <div className="h-px bg-border my-1.5" />
          <button className="w-full text-left px-3 py-2 rounded-xl text-[13px] text-text-dim hover:bg-primary/10 hover:text-primary transition-colors"
            onClick={() => setClassifyRules([])}>清除分组</button>
        </PopoverContent>
      </Popover>
    </div>
  )
}

export function ClassifyResult() {
  const classifyGroups = useAppStore((s) => s.classifyGroups)
  const groups = Object.entries(classifyGroups)
  if (groups.length === 0) return null

  return (
    <AnimatePresence>
      <motion.div initial={{ height: 0, opacity: 0 }} animate={{ height: 'auto', opacity: 1 }} exit={{ height: 0, opacity: 0 }}
        transition={{ duration: 0.25 }} className="overflow-hidden mx-4 mb-2">
        <div className="rounded-2xl border border-border/50 bg-surface/50 p-3 mt-2">
          <div className="text-[11px] font-semibold text-text-dim uppercase tracking-wider mb-2">分组结果 ({groups.length} 组)</div>
          <div className="flex flex-wrap gap-2">
            {groups.map(([label, files]) => (
              <div key={label} className="rounded-xl border border-border bg-surface-raised px-3 py-1.5 text-[12px] text-text-primary">
                <span className="font-semibold text-primary">{label}</span>
                <span className="text-text-dim ml-1">({files.length})</span>
              </div>
            ))}
          </div>
        </div>
      </motion.div>
    </AnimatePresence>
  )
}
