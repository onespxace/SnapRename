import { useState } from 'react'
import { DndContext, closestCenter, PointerSensor, useSensor, useSensors, type DragEndEvent } from '@dnd-kit/core'
import { SortableContext, horizontalListSortingStrategy } from '@dnd-kit/sortable'
import { useAppStore } from '@/store/useAppStore'
import { SegmentCard } from './SegmentCard'
import { AddSegmentMenu } from './AddSegmentMenu'

const pointerSensorOptions = {
  activationConstraint: {
    distance: 3,
  },
}

export function SegmentBar() {
  const segments = useAppStore((s) => s.segments)
  const selectedIndex = useAppStore((s) => s.selectedSegmentIndex)
  const moveSegment = useAppStore((s) => s.moveSegment)
  const [sortKey, setSortKey] = useState(0)

  const sensors = useSensors(useSensor(PointerSensor, pointerSensorOptions))
  const items = segments.map((_, i) => `${i}`)

  return (
    <div className="min-h-[104px] rounded-2xl border border-border bg-surface p-3 flex items-center gap-2">
      <DndContext key={sortKey} sensors={sensors} collisionDetection={closestCenter}
        onDragEnd={(e: DragEndEvent) => {
          if (e.over && e.active.id !== e.over.id) {
            moveSegment(Number(e.active.id), Number(e.over.id))
            setSortKey(k => k + 1)
          }
        }}>
        <SortableContext items={items} strategy={horizontalListSortingStrategy}>
          <div className="flex gap-2 overflow-x-auto flex-1 items-center px-1">
            {segments.map((seg, i) => (<SegmentCard key={`${i}`} segment={seg} index={i} isSelected={i === selectedIndex} />))}
            {segments.length === 0 && <span className="text-[13px] text-text-dim px-2 select-none">点击 + 添加规则片段</span>}
          </div>
        </SortableContext>
      </DndContext>
      <div className="shrink-0"><AddSegmentMenu /></div>
    </div>
  )
}
