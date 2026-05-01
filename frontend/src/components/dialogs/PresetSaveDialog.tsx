import * as Dialog from '@radix-ui/react-dialog'
import { Button } from '@/components/ui/button'
import { useAppStore } from '@/store/useAppStore'
import { X } from 'lucide-react'
import { useState } from 'react'

interface Props { open: boolean; onOpenChange: (v: boolean) => void }

export function PresetSaveDialog({ open, onOpenChange }: Props) {
  const [name, setName] = useState('')
  const savePreset = useAppStore((s) => s.savePreset)

  return (
    <Dialog.Root open={open} onOpenChange={onOpenChange}>
      <Dialog.Portal>
        <Dialog.Overlay className="fixed inset-0 bg-black/50 backdrop-blur-sm data-[state=open]:animate-in data-[state=closed]:animate-out data-[state=closed]:fade-out-0 data-[state=open]:fade-in-0" />
        <Dialog.Content className="fixed left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2 w-[380px] bg-surface-overlay backdrop-blur-2xl border border-border rounded-3xl p-6 shadow-2xl shadow-black/20 data-[state=open]:animate-in data-[state=closed]:animate-out data-[state=closed]:fade-out-0 data-[state=open]:fade-in-0 data-[state=closed]:zoom-out-95 data-[state=open]:zoom-in-95">
          <div className="flex items-center justify-between mb-4">
            <Dialog.Title className="text-[15px] font-bold text-text-primary">保存为预设</Dialog.Title>
            <Dialog.Close className="text-text-dim hover:text-text-primary transition-colors"><X className="size-4" /></Dialog.Close>
          </div>
          <label className="text-[12px] font-medium text-text-dim">预设名称</label>
          <input className="w-full h-10 rounded-2xl bg-surface-raised border border-border px-4 text-[13px] text-text-primary placeholder:text-text-dim focus:outline-none focus:border-primary mt-2"
            placeholder="输入预设名称..." value={name} onChange={(e) => setName(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && name.trim() && (savePreset(name.trim()), setName(''), onOpenChange(false))} />
          <div className="flex justify-end gap-2 mt-5">
            <Dialog.Close asChild><Button variant="ghost">取消</Button></Dialog.Close>
            <Button variant="default" onClick={() => { if (name.trim()) { savePreset(name.trim()); setName(''); onOpenChange(false) }}}>保存</Button>
          </div>
        </Dialog.Content>
      </Dialog.Portal>
    </Dialog.Root>
  )
}
