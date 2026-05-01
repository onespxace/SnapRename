import * as Dialog from '@radix-ui/react-dialog'
import { Button } from '@/components/ui/button'
import { useAppStore } from '@/store/useAppStore'
import { X, ArrowRight } from 'lucide-react'

interface Props { open: boolean; onOpenChange: (v: boolean) => void }

export function ConfirmDialog({ open, onOpenChange }: Props) {
  const files = useAppStore((s) => s.files)
  const executeRename = useAppStore((s) => s.executeRename)

  return (
    <Dialog.Root open={open} onOpenChange={onOpenChange}>
      <Dialog.Portal>
        <Dialog.Overlay className="fixed inset-0 bg-black/50 backdrop-blur-sm data-[state=open]:animate-in data-[state=closed]:animate-out data-[state=closed]:fade-out-0 data-[state=open]:fade-in-0" />
        <Dialog.Content className="fixed left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2 w-[720px] max-h-[560px] bg-surface-overlay backdrop-blur-2xl border border-border rounded-3xl p-6 shadow-2xl shadow-black/20 data-[state=open]:animate-in data-[state=closed]:animate-out data-[state=closed]:fade-out-0 data-[state=open]:fade-in-0 data-[state=closed]:zoom-out-95 data-[state=open]:zoom-in-95">
          <div className="flex items-center justify-between mb-3">
            <Dialog.Title className="text-[15px] font-bold text-text-primary">确认批量重命名</Dialog.Title>
            <Dialog.Close className="text-text-dim hover:text-text-primary transition-colors"><X className="size-4" /></Dialog.Close>
          </div>
          <p className="text-[12px] text-text-dim mb-3">即将重命名 {files.length} 个文件</p>
          <div className="grid grid-cols-2 gap-px bg-border rounded-2xl overflow-hidden mb-1">
            <div className="bg-surface-raised px-4 py-2 text-[11px] font-semibold text-text-dim uppercase tracking-wider">原文件名</div>
            <div className="bg-surface-raised px-4 py-2 text-[11px] font-semibold text-text-dim uppercase tracking-wider">新文件名</div>
          </div>
          <div className="h-[320px] overflow-auto rounded-b-2xl">
            {files.map((f, i) => {
              const changed = f.new_name !== f.original_name
              return (
                <div key={i} className="grid grid-cols-2 items-center py-1.5">
                  <div className="px-4 truncate">
                    <span className={`text-[12px] ${changed ? 'text-text-dim line-through' : 'text-text-primary'}`}>{f.original_name}</span>
                  </div>
                  <div className="px-4 truncate flex items-center gap-2">
                    {changed && <ArrowRight className="size-3 shrink-0 text-primary" />}
                    <span className={`text-[12px] ${changed ? 'text-primary font-semibold' : 'text-text-dim'}`}>{f.new_name}</span>
                  </div>
                </div>
              )
            })}
          </div>
          <div className="flex justify-end gap-2 mt-4">
            <Dialog.Close asChild><Button variant="ghost">取消</Button></Dialog.Close>
            <Button variant="success" onClick={async () => { await executeRename(); onOpenChange(false) }}>确认执行</Button>
          </div>
        </Dialog.Content>
      </Dialog.Portal>
    </Dialog.Root>
  )
}
