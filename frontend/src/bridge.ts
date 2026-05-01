declare global {
  interface Window {
    __INITIAL_STATE__?: FullState
    __bridge_event__?: (event: string) => void
    pywebview: { api: Record<string, (...args: any[]) => any> }
  }
}

export interface FileItem {
  path: string
  original_name: string
  new_name: string
  extracted_fields: Record<string, string>
  status: 'ok' | 'conflict' | 'error'
}

export interface RuleSegment {
  type: string
  label: string
  text: string
  counter_start: number
  counter_step: number
  counter_padding: number
  date_format: string
  extract_field: string
  extract_regex: string
  extract_min_len: number
  extract_max_len: number
  extract_allow_alpha: boolean
  extract_allow_digit: boolean
  extract_keywords_before: string
  extract_keywords_after: string
  table_column: string
  keyword_list: string
  keyword_range: number
}

export interface TableInfo {
  columns: string[]
  rows: number
}

export interface ClassifyGroup {
  [label: string]: FileItem[]
}

export interface FullState {
  files: FileItem[]
  segments: RuleSegment[]
  previewIndex: number
  selectedSegmentIndex: number
  previewFile: FileItem | null
  availableFields: string[]
  tableInfo: TableInfo | null
  isDark: boolean
  theme: string
  classifyRules: string[]
  classifyFields: string[]
  classifyGroups: Record<string, FileItem[]>
}

async function api(): Promise<Record<string, (...args: any[]) => any>> {
  if (window.pywebview?.api) return window.pywebview.api
  for (let i = 0; i < 40; i++) {
    await new Promise((r) => setTimeout(r, 50))
    if (window.pywebview?.api) return window.pywebview.api
  }
  throw new Error('pywebview API not available')
}

export const bridge = {
  async getFullState(): Promise<FullState> { return (await api()).get_full_state() },
  async addFiles(paths: string[]): Promise<void> { return (await api()).add_files(paths) },
  async addFolder(path: string): Promise<void> { return (await api()).add_folder(path) },
  async clearFiles(): Promise<void> { return (await api()).clear_files() },
  async addSegment(type: string, kwargs: Record<string, any> = {}): Promise<void> { return (await api()).add_segment(type, kwargs) },
  async removeSegment(index: number): Promise<void> { return (await api()).remove_segment(index) },
  async moveSegment(fromIdx: number, toIdx: number): Promise<void> { return (await api()).move_segment(fromIdx, toIdx) },
  async updateSegment(index: number, data: Record<string, any>): Promise<void> { return (await api()).update_segment(index, data) },
  async selectSegment(index: number): Promise<void> { return (await api()).select_segment(index) },
  async set_preview_index(index: number): Promise<void> { return (await api()).set_preview_index(index) },
  async importTable(path: string): Promise<TableInfo | null> { return (await api()).import_table(path) },
  async executeRename(): Promise<{ success: number; failed: number; conflicts: number }> { return (await api()).execute_rename() },
  async undoRename(): Promise<number> { return (await api()).undo_rename() },
  async savePreset(name: string): Promise<void> { return (await api()).save_preset(name) },
  async loadPreset(name: string): Promise<RuleSegment[]> { return (await api()).load_preset(name) },
  async listPresets(): Promise<string[]> { return (await api()).list_presets() },
  async cycleTheme(): Promise<string> { return (await api()).cycle_theme() },
  async pickFiles(): Promise<string[]> { return (await api()).pick_files() },
  async pickFolder(): Promise<string> { return (await api()).pick_folder() },
  async pickTable(): Promise<string> { return (await api()).pick_table() },
  async setClassifyRules(fields: string[]): Promise<void> { return (await api()).set_classify_rules(fields) },
  async getClassifyGroups(): Promise<{ groups: Record<string, FileItem[]>; rules: string[] }> { return (await api()).get_classify_groups() },
  async getClassifyFields(): Promise<string[]> { return (await api()).get_classify_fields() },
  async classifyExport(outputDir: string): Promise<{ success: number; failed: number }> { return (await api()).classify_export(outputDir) },
  onStateUpdate(callback: () => void) { window.__bridge_event__ = callback },
}
