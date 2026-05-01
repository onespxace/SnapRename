# Design: React + WebView2 前端重写

## 目标

将 PySide6/Qt Widgets 界面替换为 React 19 + WebView2 前端。保持 Python 核心逻辑不变。

## 架构

```
Python (main.py 启动)
├── pywebview → WebView2 窗口 (1152×700, min 960×550)
│   ├── Window: Acrylic/Mica DWM 效果
│   └── React SPA (Vite build 产物 / dev server)
├── bridge.py — pywebview.expose API
│   ├── add_files(paths) → void
│   ├── add_folder(path) → void
│   ├── clear_files() → void
│   ├── get_files() → FileItem[]
│   ├── set_preview_index(i) → void
│   ├── add_segment(type, kwargs) → void
│   ├── remove_segment(i) → void
│   ├── move_segment(fr, to) → void
│   ├── update_segment(i, data) → void
│   ├── select_segment(i) → void
│   ├── get_segments() → RuleSegment[]
│   ├── import_table(path) → table_info | null
│   ├── execute_rename() → {success, failed}
│   ├── undo_rename() → int
│   ├── save_preset(name) → void
│   ├── load_preset(name) → RuleSegment[]
│   ├── list_presets() → string[]
│   ├── cycle_theme() → "dark"|"light"
│   ├── get_is_dark() → bool
│   ├── pick_files() → string[]  (native file dialog)
│   ├── pick_folder() → string   (native folder dialog)
│   └── pick_table() → string | null
├── core/ (不变)
│   ├── extractor.py
│   ├── renamer.py
│   ├── backup.py
│   ├── table_importer.py
│   └── preset_manager.py
└── models/ (加 to_dict)
    ├── file_item.py
    └── rule_segment.py
```

## 前端组件树

```
App (flex-col, h-screen, bg-background)
├── Toolbar
│   ├── GhostButton × 4 (选择文件夹, 添加文件, 导入表格, 预设下拉)
│   ├── Separator
│   ├── GhostButton × 4 (撤销, 清空, 主题, 文件列表)
│   ├── Spacer
│   └── PrimaryButton (执行重命名)
├── MainContent (flex-1, px-4, py-3)
│   ├── SegmentBar (横向滚动, 圆角 card 容器)
│   │   ├── SegmentCard[] (dnd-kit sortable)
│   │   │   ├── DragHandle (⋮⋮)
│   │   │   ├── TypeIcon (文/#/日/识/表)
│   │   │   ├── Label
│   │   │   └── InlineEditor (按类型: Input/Spin/Combo)
│   │   └── AddButton (+)
│   ├── AuxPanel (collapsible, 选中 segment 时展开)
│   └── PreviewCard (fixed, right-aligned)
├── FileDrawer (slide-over, Sheet 组件)
│   ├── Header (标题 + 关闭按钮)
│   └── VirtualList (tanstack/react-virtual)
├── StatusBar (h-7, border-t)
└── Dialogs
    ├── ConfirmDialog (重命名确认, scrollable list)
    └── PresetSaveDialog (输入预设名称)
```

## 数据流

```
User Action → Zustand Store → bridge.py → core/ → 返回 → Store 更新 → React re-render
                                          ↓ (重命名等耗时操作)
                                     线程执行 → 结果 → Store 更新
```

- Zustand store 持有: files[], segments[], previewIndex, selectedSegmentIndex, tableInfo, isDark
- bridge 调用是异步的 (pywebview JS bridge 本身是同步，但我们在 Python 侧用线程处理耗时操作)
- 文件选择用 Python 原生对话框 (pywebview bridge)，保证原生体验

## 视觉设计

- 风格: Soft UI Evolution (与现有一致)
- 颜色: Tailwind CSS 变量映射 theme.py 颜色 token
- 窗口: Acrylic/Mica 保持 (DWM API via ctypes)
- 动画: framer-motion (布局动画, 进入/退出), motion (hover/press 微交互)
- 拖拽: @dnd-kit/sortable (规则片段排序)
- 字体: "Microsoft YaHei UI", system-ui

## 迁移策略

1. 先建 React 项目骨架 (Vite + Tailwind + shadcn/ui)
2. 实现 bridge.py + main.py (pywebview 封装)
3. 逐组件实现: Toolbar → SegmentBar → PreviewCard → AuxPanel → FileDrawer → Dialogs
4. 删除 app.py 和 ui/ (PySide6 旧代码)
5. theme.py 精简为颜色 + Acrylic/Mica

## 不做

- 不引入状态管理以外的依赖（不需要后端 API 层）
- 不改变 core/ 模块的 API
- 不添加新功能
