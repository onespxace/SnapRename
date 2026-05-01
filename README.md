# SnapRename

<picture>
  <img alt="SnapRename" src="biao.png" width="96" height="96">
</picture>

**智能批量文件重命名工具** — 规则化重命名、智能字段提取、分组导出、毛玻璃 UI

[![Platform](https://img.shields.io/badge/platform-Windows%2010%2B-blue)](https://github.com)
[![Python](https://img.shields.io/badge/python-3.10+-green)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-blue)](LICENSE)

---

## 功能特点

- **规则化重命名** — 拖拽式规则片段：固定文本、序号、日期、智能识别、表格匹配、关键词提取
- **智能提取** — 自动从文件名识别姓名、学号、专业（覆盖 120+ 中国高校专业）、班级、课程、作业编号等
- **实时预览** — 修改任何规则立即刷新新文件名，确认弹窗两列对比
- **分组导出** — 按专业 / 班级 / 学号前缀等规则，层级文件夹导出（如 `专业/姓名/文件.pdf`）
- **表格匹配** — 导入 CSV / Excel 名单，将文件与表格行精确关联
- **安全撤销** — 自动备份、一键恢复
- **预设系统** — 内置 9 套预设（通用、计科、医学、专业课程等），支持保存自定义
- **Windows 10 / 11 亚克力效果** — 毛玻璃窗口背景，Light / Dark / High Contrast 三主题

---

## 下载

前往 [Releases](https://github.com/yourusername/snap-rename/releases) 页面获取最新版本。

| 版本 | 说明 |
|------|------|
| `SnapRename-x.x.x-Setup.exe` | 安装包 — 安装到 Program Files，创建桌面 / 开始菜单快捷方式 |
| `SnapRename-x.x.x-portable.zip` | 绿色版 — 解压即用，数据保存在程序目录内 |

> 绿色版会在程序目录创建 `data/` 文件夹存放日志、备份和预设；安装版使用 `%APPDATA%\SnapRename`。

---

## 从源码运行

### 环境要求

- Python 3.10+
- Node.js 20+（仅开发 / 构建前端时需要）

### 安装

```bash
git clone https://github.com/yourusername/snap-rename.git
cd snap-rename
pip install -r requirements.txt
```

### 运行（开发模式）

```bash
# 终端 1：启动前端开发服务器
cd frontend
npm install
npm run dev

# 终端 2：启动应用（自动连接 Vite dev server）
python main.py
```

### 构建可执行文件

```bash
python scripts/build_windows.py
```

要求：
- 安装 `pyinstaller>=6.0`（脚本会自动安装）
- 安装 [Inno Setup 6](https://jrsoftware.org/isinfo.php)（可选，用于生成安装包）

构建产物在 `release/` 目录。

---

## 使用说明

### 基本流程

1. **添加文件** — 点击「选择文件夹」或「添加文件」
2. **构建规则** — 点击 `+` 按钮添加规则片段，拖拽调整顺序
3. **预览结果** — 右侧卡片实时显示改名前后对比
4. **执行重命名** — 点击「执行重命名」，确认后批量改名

### 规则片段类型

| 类型 | 说明 |
|------|------|
| 固定文本 | 直接输入的文本内容 |
| 序号 | 自动递增序号（可设起始值、步长、补零位数） |
| 日期 | 当前日期，支持多种格式 |
| 自动识别 | 从文件名智能提取姓名 / 学号 / 专业 / 课程 / 作业编号 |
| 表格字段 | 从导入的 CSV / Excel 名单中匹配列值 |
| 关键词 | 围绕指定关键词提取前后文本 |

### 分组导出

1. 在「分类」栏添加分组维度的滑块（如 专业、姓名）
2. 拖拽调整分组层级顺序
3. 点击「分组导出」，选择输出文件夹
4. 文件按层级结构复制到目标文件夹

### 辅助面板

点击规则片段展开高级设置：
- 自动识别：正则表达式、字数限制、前后关键词锚定
- 序号：起始值、步长、补零位数
- 关键词：逗号分隔的关键词列表、提取范围

---

## 项目结构

```
snap-rename/
├── main.py                  # 应用入口
├── bridge.py                # Python ↔ JavaScript API 桥接
├── app_paths.py             # 路径管理（便携 / 安装模式）
├── theme.py                 # 主题 & 亚克力效果
│
├── core/                    # 核心逻辑
│   ├── renamer.py           # 重命名 & 分组导出引擎
│   ├── backup.py            # 备份 & 撤销
│   ├── classifier.py        # 文件分组
│   ├── preset_manager.py    # 预设管理
│   ├── table_importer.py    # CSV / Excel 导入
│   └── logger.py            # 日志系统
│
├── py_engine/               # 智能提取引擎
│   ├── extractor.py         # 多字段正则提取
│   ├── disambiguate.py      # 冲突消解 & 置信度评分
│   ├── patterns.py          # 120+ 专业 / 姓氏 / 正则库
│   ├── comparator.py        # 表格行匹配
│   └── blacklist.py         # 噪音词过滤
│
├── models/                  # 数据模型
│   ├── file_item.py         # FileItem
│   └── rule_segment.py      # RuleSegment, SegmentType
│
├── presets/                 # 预设 JSON 文件
├── scripts/                 # 构建脚本
│   └── build_windows.py     # 一键打包（绿色版 + 安装包）
│
├── tests/                   # 单元测试
└── frontend/                # React 前端
    ├── src/
    │   ├── components/      # UI 组件
    │   │   ├── dialogs/     # 确认弹窗、预设保存
    │   │   ├── layout/      # 工具栏、文件列表、状态栏
    │   │   ├── panels/      # 辅助设置面板
    │   │   ├── preview/     # 预览卡片
    │   │   └── segments/    # 规则片段（含分类栏）
    │   └── store/           # Zustand 状态管理
    ├── public/              # 静态资源
    └── index.html           # HTML 入口
```

---

## 技术栈

| 层级 | 技术 |
|------|------|
| 容器 | [pywebview](https://pywebview.flowrl.com/) — Python WebView 桌面壳 |
| 前端 | React 19 + TypeScript + Tailwind CSS 4 + Vite |
| 状态管理 | Zustand |
| 拖拽 | dnd-kit |
| UI 组件 | Radix UI (Dialog, Popover) + Framer Motion |
| 数据处理 | pandas + openpyxl |
| 打包 | PyInstaller + Inno Setup |
| 图标 | Pillow (PNG → ICO) |

---

## 许可证

[MIT](LICENSE)
