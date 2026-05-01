import { create } from 'zustand'
import type { FileItem, RuleSegment, TableInfo, FullState } from '@/bridge'
import { bridge } from '@/bridge'

interface Toast { message: string; type: 'info' | 'error' | 'success' }

interface AppState {
  files: FileItem[]
  segments: RuleSegment[]
  previewIndex: number
  selectedSegmentIndex: number
  availableFields: string[]
  tableInfo: TableInfo | null
  isDark: boolean
  theme: string
  statusText: string
  statusLevel: 'info' | 'warning' | 'error'
  showFileDrawer: boolean
  toast: Toast | null
  loading: boolean
  classifyRules: string[]
  classifyFields: string[]
  classifyGroups: Record<string, FileItem[]>

  loadInitialState: (state: FullState) => void
  refresh: () => Promise<void>
  setStatus: (text: string, level?: 'info' | 'warning' | 'error') => void
  showToast: (message: string, type?: Toast['type']) => void

  addFiles: (paths: string[]) => Promise<void>
  addFolder: (path: string) => Promise<void>
  clearFiles: () => Promise<void>
  addSegment: (type: string, kwargs?: Record<string, any>) => Promise<void>
  removeSegment: (index: number) => Promise<void>
  moveSegment: (from: number, to: number) => Promise<void>
  updateSegment: (index: number, data: Record<string, any>) => Promise<void>
  selectSegment: (index: number) => void
  setPreviewIndex: (index: number) => void
  importTable: (path: string) => Promise<void>
  executeRename: () => Promise<{ success: number; failed: number; conflicts: number }>
  undoRename: () => Promise<void>
  savePreset: (name: string) => Promise<void>
  loadPreset: (name: string) => Promise<void>
  cycleTheme: () => Promise<void>
  toggleFileDrawer: () => void
  setClassifyRules: (fields: string[]) => Promise<void>
  classifyExport: (outputDir: string) => Promise<void>
}

function uiRefresh(filesLen: number, previewIdx: number) {
  return { statusText: `已加载 ${filesLen} 个文件 | 预览：第 ${previewIdx + 1} 个` }
}

const safe = async (fn: () => Promise<void>, set: any) => {
  set({ loading: true })
  try {
    await fn()
  } catch (e: any) {
    set({ toast: { message: e?.message || String(e), type: 'error' } })
  } finally {
    set({ loading: false })
  }
}

// Debounce helper
let _debounceTimers = new Map<string, ReturnType<typeof setTimeout>>()

export const useAppStore = create<AppState>((set, get) => ({
  files: [],
  segments: [],
  previewIndex: -1,
  selectedSegmentIndex: -1,
  availableFields: [],
  tableInfo: null,
  isDark: false,
  theme: "light",
  statusText: '就绪 | 已加载 0 个文件',
  statusLevel: 'info',
  showFileDrawer: false,
  toast: null,
  loading: false,
  classifyRules: [],
  classifyFields: [],
  classifyGroups: {},

  loadInitialState: (state) => {
    set({
      files: state.files, segments: state.segments,
      previewIndex: state.previewIndex, selectedSegmentIndex: state.selectedSegmentIndex,
      availableFields: state.availableFields, tableInfo: state.tableInfo, isDark: state.isDark, theme: state.theme,
      classifyRules: state.classifyRules, classifyFields: state.classifyFields, classifyGroups: state.classifyGroups,
    })
    document.documentElement.dataset.theme = state.theme || (state.isDark ? 'dark' : 'light')
  },

  refresh: async () => {
    await safe(async () => {
      const s = await bridge.getFullState()
      set({
        files: s.files, segments: s.segments,
        previewIndex: s.previewIndex, selectedSegmentIndex: s.selectedSegmentIndex,
        availableFields: s.availableFields, tableInfo: s.tableInfo, isDark: s.isDark, theme: s.theme,
        classifyRules: s.classifyRules, classifyFields: s.classifyFields, classifyGroups: s.classifyGroups,
        ...uiRefresh(s.files.length, s.previewIndex),
      })
    }, set)
  },

  showToast: (message, type = 'info') => {
    set({ toast: { message, type } })
    setTimeout(() => set({ toast: null }), 3000)
  },

  setStatus: (text, level = 'info') => set({ statusText: text, statusLevel: level }),

  // ── File operations (full refresh needed) ──
  addFiles: async (paths) => safe(async () => {
    await bridge.addFiles(paths)
    await get().refresh()
  }, set),

  addFolder: async (path) => safe(async () => {
    await bridge.addFolder(path)
    await get().refresh()
  }, set),

  clearFiles: async () => safe(async () => {
    await bridge.clearFiles()
    await get().refresh()
  }, set),

  // ── Segment operations (optimistic + lightweight refresh) ──
  addSegment: async (type, kwargs) => safe(async () => {
    await bridge.addSegment(type, kwargs)
    await get().refresh()
  }, set),

  removeSegment: async (index) => safe(async () => {
    await bridge.removeSegment(index)
    await get().refresh()
  }, set),

  moveSegment: async (from, to) => {
    const segs = get().segments
    if (from < 0 || from >= segs.length || to < 0 || to >= segs.length || from === to) return
    // Optimistic reorder — immediately update UI for dnd-kit
    const newSegs = [...segs]
    const [moved] = newSegs.splice(from, 1)
    newSegs.splice(to, 0, moved)
    set({ segments: newSegs })
    // Sync to backend (fire-and-forget with refresh)
    try {
      await bridge.moveSegment(from, to)
      await get().refresh()
    } catch {
      // Rollback on failure
      set({ segments: segs })
    }
  },

  updateSegment: async (index, data) => {
    const segs = get().segments
    const seg = segs[index]
    if (!seg) return
    let changed = false
    for (const [k, v] of Object.entries(data)) {
      if ((seg as any)[k] !== v) { changed = true; break }
    }
    if (!changed) return
    const newSegs = [...segs]
    newSegs[index] = { ...seg, ...data }
    set({ segments: newSegs })
    // Debounce sync to Python, then refresh preview
    const key = `update_${index}`
    clearTimeout(_debounceTimers.get(key))
    _debounceTimers.set(key, setTimeout(async () => {
      try { await bridge.updateSegment(index, data); await get().refresh() } catch {}
    }, 150))
  },

  selectSegment: (index) => {
    set({ selectedSegmentIndex: index })
    bridge.selectSegment(index).catch(() => {})
  },

  setPreviewIndex: (index) => {
    set({ previewIndex: index })
    bridge.set_preview_index(index).catch(() => {})
  },

  importTable: async (path) => safe(async () => {
    const result = await bridge.importTable(path)
    if (result) {
      await get().refresh()
      get().showToast(`已导入表格：${result.columns.length} 列, ${result.rows} 行`, 'success')
    }
  }, set),

  executeRename: async () => {
    let result = { success: 0, failed: 0, conflicts: 0 }
    await safe(async () => {
      result = await bridge.executeRename()
      await get().refresh()
      get().showToast(`重命名完成：${result.success} 成功, ${result.failed} 失败`, result.failed > 0 ? 'error' : 'success')
    }, set)
    return result
  },

  undoRename: async () => safe(async () => {
    const count = await bridge.undoRename()
    await get().refresh()
    get().showToast(count > 0 ? `已撤销 ${count} 个文件` : '没有可撤销的操作', count > 0 ? 'success' : 'info')
  }, set),

  savePreset: async (name) => safe(async () => {
    await bridge.savePreset(name)
    get().showToast(`预设已保存：${name}`, 'success')
  }, set),

  loadPreset: async (name) => safe(async () => {
    await bridge.loadPreset(name)
    await get().refresh()
    get().showToast(`已加载预设：${name}`, 'success')
  }, set),

  cycleTheme: async () => {
    const theme = await bridge.cycleTheme()
    const isDark = theme !== 'light'
    document.documentElement.dataset.theme = theme
    set({ theme, isDark, statusText: `主题：${theme === 'light' ? '浅色' : theme === 'highcontrast' ? '高对比度' : '深色'}` })
  },

  setClassifyRules: async (fields) => {
    set({ classifyRules: fields })
    await bridge.setClassifyRules(fields)
    await get().refresh()
  },

  classifyExport: async (outputDir) => safe(async () => {
    const result = await bridge.classifyExport(outputDir)
    if ((result as any).error) {
      get().showToast(`导出失败：${(result as any).error}`, 'error')
    } else {
      get().showToast(`导出完成：${result.success} 成功, ${result.failed} 失败`, result.failed > 0 ? 'error' : 'success')
    }
  }, set),

  toggleFileDrawer: () => set((s) => ({ showFileDrawer: !s.showFileDrawer })),
}))
