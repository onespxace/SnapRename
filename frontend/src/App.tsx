import { useEffect, useState, useRef, Component } from 'react'
import { Toolbar } from '@/components/layout/Toolbar'
import { StatusBar } from '@/components/layout/StatusBar'
import { SegmentBar } from '@/components/segments/SegmentBar'
import { PreviewCard } from '@/components/preview/PreviewCard'
import { AuxPanel } from '@/components/panels/AuxPanel'
import { FileDrawer } from '@/components/layout/FileDrawer'
import { ConfirmDialog } from '@/components/dialogs/ConfirmDialog'
import { PresetSaveDialog } from '@/components/dialogs/PresetSaveDialog'
import { ClassifyBar, ClassifyResult } from '@/components/segments/ClassifyBar'
import { useAppStore } from '@/store/useAppStore'
import { bridge } from '@/bridge'
import { AnimatePresence, motion } from 'framer-motion'
import { XCircle, CheckCircle, Info, Loader2 } from 'lucide-react'

class ErrorBoundary extends Component<{ children: React.ReactNode }, { error: Error | null }> {
  constructor(props: any) { super(props); this.state = { error: null } }
  static getDerivedStateFromError(error: Error) { return { error } }
  componentDidCatch(error: Error, info: any) {
    console.error('[App crash]', error.message, error.stack, info)
    try { document.body.innerText = `[Error] ${error.message}\n\n${error.stack}` } catch {}
  }
  render() {
    if (this.state.error) return null
    return this.props.children
  }
}

function Toast() {
  const toast = useAppStore((s) => s.toast)
  const icons = { error: XCircle, success: CheckCircle, info: Info }
  const colors = { error: 'border-error/30 text-error', success: 'border-success/30 text-success', info: 'border-primary/30 text-primary' }
  const bg = { error: 'bg-error/10', success: 'bg-success/10', info: 'bg-primary/10' }
  const Icon = toast ? icons[toast.type] : Info

  return (
    <AnimatePresence>
      {toast && (
        <motion.div
          initial={{ y: -60, opacity: 0, scale: 0.9 }} animate={{ y: 0, opacity: 1, scale: 1 }} exit={{ y: -60, opacity: 0, scale: 0.9 }}
          transition={{ type: 'spring', damping: 22, stiffness: 400 }}
          className={`fixed top-4 left-1/2 -translate-x-1/2 z-[100] flex items-center gap-2.5 px-5 py-3 rounded-2xl border backdrop-blur-xl shadow-lg shadow-black/10 text-[13px] font-medium ${colors[toast.type]} ${bg[toast.type]}`}
        >
          <Icon className="size-4 shrink-0" />
          <span>{toast.message}</span>
        </motion.div>
      )}
    </AnimatePresence>
  )
}

export default function App() {
  const refresh = useAppStore((s) => s.refresh)
  const theme = useAppStore((s) => s.theme)
  const loading = useAppStore((s) => s.loading)
  const files = useAppStore((s) => s.files)
  const classifyExport = useAppStore((s) => s.classifyExport)
  const [showConfirm, setShowConfirm] = useState(false)
  const [showPresetSave, setShowPresetSave] = useState(false)
  const refreshRef = useRef(refresh)
  refreshRef.current = refresh

  useEffect(() => {
    document.documentElement.dataset.theme = theme
  }, [theme])

  useEffect(() => {
    if (window.__INITIAL_STATE__) {
      useAppStore.getState().loadInitialState(window.__INITIAL_STATE__)
    } else {
      refreshRef.current()
    }
  }, [])

  useEffect(() => {
    const handleKey = (e: KeyboardEvent) => {
      const store = useAppStore.getState()
      if (e.key === 'ArrowUp') { e.preventDefault(); if (store.previewIndex > 0) store.setPreviewIndex(store.previewIndex - 1) }
      else if (e.key === 'ArrowDown') { e.preventDefault(); if (store.previewIndex < store.files.length - 1) store.setPreviewIndex(store.previewIndex + 1) }
      else if (e.key === 'Delete' && store.selectedSegmentIndex >= 0) { e.preventDefault(); store.removeSegment(store.selectedSegmentIndex) }
      else if (e.key === 'z' && (e.ctrlKey || e.metaKey)) { e.preventDefault(); store.undoRename() }
    }
    window.addEventListener('keydown', handleKey)
    return () => window.removeEventListener('keydown', handleKey)
  }, [])

  const doClassifyExport = async () => {
    await refreshRef.current()
    const p = await bridge.pickFolder()
    if (p) {
      await classifyExport(p)
      await refreshRef.current()
    }
  }

  return (
    <ErrorBoundary>
    <div className="flex flex-col h-screen bg-bg text-text-primary font-sans overflow-hidden">
      <Toast />
      {loading && (
        <div className="fixed top-4 right-4 z-[99]">
          <Loader2 className="size-4 text-primary animate-spin" />
        </div>
      )}
      <div className="flex items-center px-4 py-2.5">
        <Toolbar
          onExecute={async () => { await refreshRef.current(); setShowConfirm(true) }}
          onSavePreset={() => setShowPresetSave(true)}
          onClassifyExport={doClassifyExport}
        />
        <div className="flex-1" />
        <PreviewCard />
      </div>
      <div className="px-4 pb-1.5"><SegmentBar /></div>
      <AuxPanel />
      {files.length > 0 && (
        <div className="px-4 py-1">
          <ClassifyBar />
          <ClassifyResult />
        </div>
      )}
      <div className="flex-1" />
      <StatusBar />
      <FileDrawer />
      <ConfirmDialog open={showConfirm} onOpenChange={setShowConfirm} />
      <PresetSaveDialog open={showPresetSave} onOpenChange={setShowPresetSave} />
    </div>
    </ErrorBoundary>
  )
}
