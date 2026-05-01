import { useState, useEffect } from 'react'
import { Button } from '@/components/ui/button'
import { useAppStore } from '@/store/useAppStore'
import { bridge } from '@/bridge'
import { FolderOpen, FilePlus, Table, Undo2, Trash2, SunMoon, List, Play, FolderOutput } from 'lucide-react'
import { Popover, PopoverContent, PopoverTrigger } from '@/components/ui/popover'
import { ChevronDown } from 'lucide-react'

interface Props { onExecute: () => void; onSavePreset: () => void; onClassifyExport: () => void }

export function Toolbar({ onExecute, onSavePreset, onClassifyExport }: Props) {
  const [presets, setPresets] = useState<string[]>([])
  const [presetOpen, setPresetOpen] = useState(false)
  const addFiles = useAppStore((s) => s.addFiles)
  const addFolder = useAppStore((s) => s.addFolder)
  const clearFiles = useAppStore((s) => s.clearFiles)
  const importTable = useAppStore((s) => s.importTable)
  const undoRename = useAppStore((s) => s.undoRename)
  const cycleTheme = useAppStore((s) => s.cycleTheme)
  const loadPreset = useAppStore((s) => s.loadPreset)
  const toggleFileDrawer = useAppStore((s) => s.toggleFileDrawer)

  useEffect(() => { bridge.listPresets().then(setPresets) }, [])

  return (
    <div className="flex items-center gap-1 flex-wrap">
      <Button variant="ghost" size="default" onClick={async () => { const p = await bridge.pickFolder(); if (p) addFolder(p) }}>
        <FolderOpen className="size-3.5" />文件夹
      </Button>
      <Button variant="ghost" size="default" onClick={async () => { const p = await bridge.pickFiles(); if (p.length) addFiles(p) }}>
        <FilePlus className="size-3.5" />文件
      </Button>
      <Button variant="ghost" size="default" onClick={async () => { const p = await bridge.pickTable(); if (p) importTable(p) }}>
        <Table className="size-3.5" />表格
      </Button>
      <div className="w-px h-5 bg-border mx-1" />
      <Popover open={presetOpen} onOpenChange={setPresetOpen}>
        <PopoverTrigger asChild>
          <Button variant="ghost" size="default">预设 <ChevronDown className="size-3 opacity-50" /></Button>
        </PopoverTrigger>
        <PopoverContent className="w-44" align="start">
          {presets.map((name) => (
            <button key={name} className="w-full text-left px-3 py-2 rounded-lg text-[13px] text-text-primary hover:bg-primary/10 hover:text-primary transition-colors"
              onClick={() => { loadPreset(name); setPresetOpen(false) }}>{name}</button>
          ))}
          <div className="h-px bg-border my-1" />
          <button className="w-full text-left px-3 py-2 rounded-lg text-[13px] text-text-dim hover:bg-primary/10 hover:text-primary transition-colors"
            onClick={() => { onSavePreset(); setPresetOpen(false) }}>保存当前为预设...</button>
        </PopoverContent>
      </Popover>
      <div className="w-px h-5 bg-border mx-1" />
      <Button variant="ghost" size="default" onClick={undoRename}><Undo2 className="size-3.5" />撤销</Button>
      <Button variant="ghost" size="default" onClick={clearFiles}><Trash2 className="size-3.5" />清空</Button>
      <Button variant="ghost" size="default" onClick={cycleTheme}><SunMoon className="size-3.5" />主题</Button>
      <Button variant="ghost" size="default" onClick={toggleFileDrawer}><List className="size-3.5" />列表</Button>
      <div className="flex-1" />
      <Button variant="default" size="default" onClick={onClassifyExport}><FolderOutput className="size-3.5" />分组导出</Button>
      <Button variant="default" size="default" onClick={onExecute}><Play className="size-3.5" />执行重命名</Button>
    </div>
  )
}
