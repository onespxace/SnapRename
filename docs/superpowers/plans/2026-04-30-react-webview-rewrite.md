# React + WebView2 UI Rewrite — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace PySide6/Qt Widgets UI with React 19 + WebView2 (via pywebview). Also refactor `core/extractor.py` into a modular `py_engine/` package with pattern library, disambiguation, blacklist filtering, and table comparator.

**Architecture:** Python launches pywebview (WebView2 on Windows), loads React SPA. Python functions exposed via `webview.expose()`. React calls bridge functions → Zustand store → re-render. Acrylic/Mica effect applied via DWM API.

**Tech Stack:** Python 3.10+, pywebview 5.x, React 19, TypeScript, Vite 6, Tailwind CSS 4, Radix UI Primitives, framer-motion, Zustand 5, @dnd-kit/core + sortable, Lucide React, @tanstack/react-virtual

---

### Task 1: Create React + Vite + TypeScript project

**Files:**
- Create: `frontend/` directory tree (via `npm create vite`)

- [ ] **Step 1: Scaffold Vite project**

Run:
```bash
cd C:/Users/ASUS/Desktop/cloude/batch_renamer
npm create vite@latest frontend -- --template react-ts
```

- [ ] **Step 2: Install runtime dependencies**

```bash
cd frontend
npm install zustand @dnd-kit/core @dnd-kit/sortable @dnd-kit/utilities framer-motion lucide-react @tanstack/react-virtual @radix-ui/react-dialog @radix-ui/react-popover @radix-ui/react-checkbox @radix-ui/react-select @radix-ui/react-tooltip class-variance-authority clsx tailwind-merge
```

- [ ] **Step 3: Install dev dependencies**

```bash
cd frontend
npm install -D @types/node tailwindcss @tailwindcss/vite
```

- [ ] **Step 4: Commit**

---

### Task 2: Configure Tailwind CSS 4 + shadcn/ui tooling

**Files:**
- Create: `frontend/vite.config.ts`, `frontend/src/index.css`, `frontend/src/lib/utils.ts`

- [ ] **Step 1: Write `vite.config.ts`**

```typescript
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'
import path from 'path'

export default defineConfig({
  plugins: [react(), tailwindcss()],
  base: './',
  resolve: {
    alias: { '@': path.resolve(__dirname, './src') },
  },
  build: {
    outDir: 'dist',
  },
  server: {
    port: 5173,
  },
})
```

- [ ] **Step 2: Write `frontend/src/index.css` with Tailwind 4 import + theme tokens**

```css
@import "tailwindcss";

@theme {
  --color-bg: #09090b;
  --color-surface: #121217;
  --color-surface-raised: #1a1a23;
  --color-surface-overlay: #22222f;
  --color-text-primary: #f4f4f8;
  --color-text-secondary: #a1a1b0;
  --color-text-dim: #6b6b80;
  --color-primary: #3b82f6;
  --color-primary-hover: #60a5fa;
  --color-primary-muted: #1e3a5f;
  --color-success: #22c55e;
  --color-warning: #f59e0b;
  --color-error: #ef4444;
  --color-border: #1e1e2e;
  --color-border-hover: #2e2e42;
  --color-border-focus: #3b82f6;
  --font-sans: "Microsoft YaHei UI", "Segoe UI", "Noto Sans SC", system-ui, sans-serif;
}

/* shadcn/ui base variables */
:root {
  --background: var(--color-bg);
  --foreground: var(--color-text-primary);
  --card: var(--color-surface);
  --card-foreground: var(--color-text-primary);
  --border: var(--color-border);
  --input: var(--color-surface-raised);
  --ring: var(--color-primary);
  --radius: 0.625rem;
}

* {
  box-sizing: border-box;
}

body {
  margin: 0;
  font-family: var(--font-sans);
  background: var(--color-bg);
  color: var(--color-text-primary);
  overflow: hidden;
  user-select: none;
}
```

- [ ] **Step 3: Write `frontend/src/lib/utils.ts` (cn helper)**

```typescript
import { type ClassValue, clsx } from 'clsx'
import { twMerge } from 'tailwind-merge'

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}
```

- [ ] **Step 4: Write base shadcn-style UI primitives for Button**

Create `frontend/src/components/ui/button.tsx`:
```tsx
import * as React from 'react'
import { cva, type VariantProps } from 'class-variance-authority'
import { cn } from '@/lib/utils'

const buttonVariants = cva(
  'inline-flex items-center justify-center gap-2 rounded-lg text-sm font-medium ring-offset-background transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:opacity-50 [&_svg]:pointer-events-none [&_svg]:size-4',
  {
    variants: {
      variant: {
        default: 'bg-primary text-white hover:bg-primary-hover font-semibold tracking-wide',
        ghost: 'bg-transparent border border-border text-text-secondary hover:text-text-primary hover:border-text-dim',
        subtle: 'bg-transparent text-text-secondary hover:text-text-primary hover:bg-surface-raised',
        success: 'bg-success text-white hover:bg-green-600 font-semibold',
      },
      size: {
        default: 'h-8 px-3.5 py-1.5',
        sm: 'h-7 px-3 text-xs',
        icon: 'size-9 rounded-full p-0',
      },
    },
    defaultVariants: { variant: 'default', size: 'default' },
  },
)

export interface ButtonProps
  extends React.ButtonHTMLAttributes<HTMLButtonElement>,
    VariantProps<typeof buttonVariants> {}

export const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className, variant, size, ...props }, ref) => (
    <button className={cn(buttonVariants({ variant, size, className }))} ref={ref} {...props} />
  ),
)
Button.displayName = 'Button'
```

- [ ] **Step 5: Commit**

---

### Task 3: Add `to_dict()` to FileItem model

**Files:**
- Modify: `models/file_item.py`

- [ ] **Step 1: Add to_dict method to FileItem**

Add after line 31:
```python
def to_dict(self) -> dict:
    return {
        "path": self.path,
        "original_name": self.original_name,
        "new_name": self.new_name,
        "extracted_fields": self.extracted_fields,
        "status": self.status,
    }
```

- [ ] **Step 2: Commit**

---

### Task 4: Create `py_engine/__init__.py` + `patterns.py` — pattern library

**Files:**
- Create: `py_engine/__init__.py`
- Create: `py_engine/patterns.py`

- [ ] **Step 1: Write `py_engine/__init__.py`**

```python
"""py_engine — Smart filename field extraction and table matching."""
```

- [ ] **Step 2: Write `py_engine/patterns.py`**

```python
"""Pre-compiled regex pattern library for Chinese academic filenames."""

from __future__ import annotations
import re
from dataclasses import dataclass, field
from typing import Pattern


@dataclass
class FieldPattern:
    name: str                      # Field name, e.g. "学号"
    pattern: Pattern               # Compiled regex
    priority: int = 0              # Higher = preferred when patterns overlap
    min_len: int = 1
    max_len: int = 64
    allow_alpha: bool = True
    allow_digit: bool = False


# ============================================================
# Comprehensive Chinese surname list (百家姓 + common)
# ============================================================
SURNAMES: set[str] = set(
    "李王张刘陈杨赵黄周吴徐孙胡朱高林何郭马罗"
    "梁宋郑谢韩唐冯于董萧程曹袁邓许傅沈曾彭吕"
    "苏卢蒋蔡贾丁魏薛叶阎余潘杜戴夏钟汪田任姜"
    "范方石姚谭廖邹熊金陆郝孔白崔康毛邱秦江史"
    "顾侯邵孟龙万段雷钱汤尹黎易常武乔贺赖龚文"
    "庞樊兰殷陶翟安严牛温芦季俞章鲁葛伍申尤"
    "毕聂焦向柳邢岳齐沿梅莫庄辛管祝左涂谷祁时"
    "舒耿牟卜路詹关苗凌费纪靳盛童欧甄项曲成游"
    "阳裴席卫查屈鲍覃霍隋植甘景薄单包司柏宁柯"
    "阮桂闵欧阳解强柴华车冉房边辜吉饶刁瞿戚丘"
    "古米池滕晋苑邬臧畅宫来嵺苟全褚廉娄"
)


# ============================================================
# Pattern Library
# ============================================================

PATTERNS: list[FieldPattern] = [
    # Date (highest priority — unambiguous)
    FieldPattern(
        name="日期",
        pattern=re.compile(r'(\d{4}[-_]?\d{2}[-_]?\d{2})'),
        priority=10,
    ),

    # Student ID — 6-12 digit sequence, not part of a longer number
    FieldPattern(
        name="学号",
        pattern=re.compile(r'(?<![a-zA-Z0-9])(\d{6,12})(?![a-zA-Z0-9])'),
        priority=9,
    ),

    # Class identifier: major prefix + year/digits
    # e.g. "计算机2101", "医学2020", "法学21"
    FieldPattern(
        name="班级",
        pattern=re.compile(
            r'(计算机|医学|法学|经济|管理|外语|数学|物理|化学|生物|机械|电子|'
            r'土木|建筑|环境|材料|自动化|软件|网络|信息|通信|电气|会计|金融|'
            r'临床|护理|药学|口腔|公卫|基础|哲学|历史|新闻|中文|英语|日语)\d{2,4}'
        ),
        priority=8,
    ),

    # Chinese name — 2-4 consecutive Chinese chars
    FieldPattern(
        name="姓名",
        pattern=re.compile(r'([一-鿿]{2,4})'),
        priority=7,
        min_len=2,
        max_len=4,
    ),

    # Assignment/homework number: keyword + digits
    FieldPattern(
        name="作业编号",
        pattern=re.compile(r'(作业|实验|报告|论文|习题|项目|考试|答辩|平时|期中|期末)\s*[#_]?\s*(\d+)'),
        priority=5,
    ),
    FieldPattern(
        name="作业类型",
        pattern=re.compile(r'(作业|实验|报告|论文|习题|项目|考试|答辩|平时|期中|期末)'),
        priority=5,
    ),

    # English name (fallback — only if no Chinese name found)
    FieldPattern(
        name="英文名",
        pattern=re.compile(r'([a-zA-Z]{2,}(?:\s[a-zA-Z]{2,})?)'),
        priority=3,
        min_len=2,
        max_len=40,
    ),

    # Generic numeric ID (catch-all for various ID formats)
    FieldPattern(
        name="编号",
        pattern=re.compile(r'(?<![a-zA-Z])(\d{3,8})(?![a-zA-Z])'),
        priority=2,
    ),
]


def get_pattern(name: str) -> FieldPattern | None:
    for p in PATTERNS:
        if p.name == name:
            return p
    return None
```

- [ ] **Step 3: Commit**

---

### Task 5: Create `py_engine/blacklist.py` — noise filter

**Files:**
- Create: `py_engine/blacklist.py`

- [ ] **Step 1: Write `py_engine/blacklist.py`**

```python
"""Business blacklist — exclude long major/department names from field extraction."""

# Full department/major names that should NOT be extracted as "姓名" or other fields.
# These are 4+ character institutional terms common in Chinese university filenames.
DEPARTMENT_BLACKLIST: set[str] = {
    # 计算机/软件
    "计算机科学与技术", "计算机科学", "软件工程", "网络工程", "信息安全",
    "物联网工程", "数字媒体技术", "数据科学", "人工智能", "智能科学与技术",

    # 医学
    "临床医学", "基础医学", "预防医学", "口腔医学", "中医学", "中西医结合",
    "临床药学", "护理学", "医学检验技术", "医学影像学", "康复治疗学",
    "药学", "中药学", "制药工程",

    # 工程
    "电子信息工程", "通信工程", "电气工程及其自动化", "自动化",
    "机械设计制造及其自动化", "机械电子工程", "车辆工程",
    "土木工程", "建筑学", "环境工程", "材料科学与工程",
    "化学工程与工艺", "生物工程",

    # 理科
    "数学与应用数学", "信息与计算科学", "物理学", "应用物理学",
    "化学", "应用化学", "生物科学", "生物技术",

    # 经管
    "工商管理", "市场营销", "会计学", "财务管理", "人力资源管理",
    "国际经济与贸易", "金融学", "经济学",

    # 文法
    "汉语言文学", "新闻学", "法学", "行政管理", "社会学",
    "英语", "日语",

    # 其他
    "思想政治教育", "体育教育",
}

# Substrings that indicate a block is likely a department, not a person name
NOISE_KEYWORDS = [
    "专业", "学院", "大学", "系", "班", "级",
    "实验", "报告", "作业", "论文", "习题", "考试",
    "第", "次", "份", "组", "队",
]


def is_blacklisted(text: str) -> bool:
    """Check if text matches a known department/major blacklist entry."""
    return text.strip() in DEPARTMENT_BLACKLIST


def is_noise(text: str) -> bool:
    """Check if text contains keywords that suggest it's not a person name."""
    for kw in NOISE_KEYWORDS:
        if kw in text:
            return True
    return False


def filter_blacklist(candidates: dict[str, str]) -> dict[str, str]:
    """Remove blacklisted entries from candidate fields."""
    return {k: v for k, v in candidates.items()
            if not is_blacklisted(v) and not is_noise(v)}
```

- [ ] **Step 2: Commit**

---

### Task 6: Create `py_engine/disambiguate.py` — disambiguation & confidence

**Files:**
- Create: `py_engine/disambiguate.py`

- [ ] **Step 1: Write `py_engine/disambiguate.py`**

```python
"""Disambiguation — resolve overlapping matches, surname check, confidence score."""

from __future__ import annotations
from dataclasses import dataclass, field
from py_engine.patterns import SURNAMES
from py_engine.blacklist import is_blacklisted, is_noise


@dataclass
class Extraction:
    field: str
    value: str
    start: int
    end: int
    confidence: float = 0.0

    @property
    def span(self) -> tuple[int, int]:
        return (self.start, self.end)

    def overlaps(self, other: Extraction) -> bool:
        return self.start < other.end and other.start < self.end


def resolve_overlaps(extractions: list[Extraction]) -> list[Extraction]:
    """Given overlapping extractions, keep the one with higher priority/confidence."""
    if not extractions:
        return []
    sorted_ex = sorted(extractions, key=lambda e: (e.start, -e.confidence))
    result: list[Extraction] = []
    for ex in sorted_ex:
        if result and ex.overlaps(result[-1]):
            if ex.confidence > result[-1].confidence:
                result[-1] = ex
        else:
            result.append(ex)
    return result


def score_chinese_name(value: str) -> float:
    """Score how likely `value` is a real Chinese person name."""
    score = 0.0
    # Length: 2-3 chars is ideal for Chinese names
    if len(value) == 2:
        score += 0.4
    elif len(value) == 3:
        score += 0.5
    elif len(value) == 4:
        score += 0.2  # Rare but possible (compound surname + 2-char given)
    else:
        return 0.0

    # Surname check
    if value[0] in SURNAMES:
        score += 0.4

    # Common given-name characters (soft hint, not exhaustive)
    common_given = set("伟芳娜秀英敏静丽强磊洋勇军杰涛明超平刚华文辉玲桂兰凤梅红鑫斌峰乐建中华秀丽慧峰云海波燕鹏飞龙")
    if len(value) >= 2 and any(c in common_given for c in value[1:]):
        score += 0.1

    return min(score, 1.0)


def score_student_id(value: str) -> float:
    """Score how likely `value` is a student ID."""
    score = 0.0
    n = len(value)
    if 8 <= n <= 12:
        score += 0.6
        # Common patterns: starts with year (20xx, 201x, 202x)
        if value.startswith(("20", "19", "18")):
            score += 0.3
    elif 6 <= n <= 7:
        score += 0.3
    return min(score, 1.0)


def score_class_id(value: str) -> float:
    """Score how likely `value` is a class identifier."""
    if len(value) >= 4:
        return 0.8
    return 0.4
```

- [ ] **Step 2: Commit**

---

### Task 7: Create `py_engine/extractor.py` — smart extractor (v2)

**Files:**
- Create: `py_engine/extractor.py`

- [ ] **Step 1: Write `py_engine/extractor.py`**

```python
"""Smart filename field extractor — uses pattern library, disambiguation, blacklist."""

from __future__ import annotations
from collections import defaultdict
from models.file_item import FileItem
from py_engine.patterns import PATTERNS, FieldPattern, SURNAMES
from py_engine.disambiguate import (
    Extraction, resolve_overlaps,
    score_chinese_name, score_student_id, score_class_id,
)
from py_engine.blacklist import is_blacklisted, is_noise, filter_blacklist


class SmartExtractor:
    """Extracts structured fields (name, ID, date, class, homework) from filenames."""

    def __init__(self):
        self._field_cache: dict[str, set[str]] = defaultdict(set)

    def extract(self, filename: str) -> dict[str, str]:
        """Extract all recognizable fields from a filename. Returns {field: value}."""
        base = filename.rsplit(".", 1)[0] if "." in filename else filename
        extractions: list[Extraction] = []

        # Run all patterns
        for pat in PATTERNS:
            for m in pat.pattern.finditer(base):
                value = m.group(1) if m.lastindex and m.lastindex >= 1 else m.group(0)
                if value is None:
                    continue
                if pat.name == "学号" and not value.isdigit():
                    continue

                # Apply blacklist filter
                if is_blacklisted(value) or is_noise(value):
                    continue

                confidence = self._score(pat, value)
                extractions.append(Extraction(
                    field=pat.name,
                    value=value,
                    start=m.start(),
                    end=m.end(),
                    confidence=confidence,
                ))

        # Resolve overlaps
        resolved = resolve_overlaps(extractions)

        # Convert to dict, merging same-field results
        result: dict[str, str] = {}
        for ex in resolved:
            name = ex.field
            # For 姓名: prefer surname-matched block, skip blacklisted
            if name == "姓名" and ex.value[0] not in SURNAMES and "姓名" in result:
                continue
            name, _ = self._deduplicate_field(name, ex.value, result)
            if name not in result or ex.confidence > 0.3:
                result[name] = ex.value

        # Cache values
        for k, v in result.items():
            self._field_cache[k].add(v)

        return filter_blacklist(result)

    def _score(self, pat: FieldPattern, value: str) -> float:
        """Compute confidence score for a match."""
        score = 0.0
        if pat.name == "姓名":
            score = score_chinese_name(value)
        elif pat.name == "学号":
            score = score_student_id(value)
        elif pat.name == "班级":
            score = score_class_id(value)
        elif pat.name == "日期":
            score = 0.9  # Date patterns are very reliable
        elif pat.name in ("作业编号", "作业类型"):
            score = 0.8
        else:
            score = 0.5
        return min(score, 1.0)

    def _deduplicate_field(self, name: str, value: str, result: dict[str, str]) -> tuple[str, str]:
        """Handle duplicate field names (e.g. multiple Chinese character blocks)."""
        if name not in result:
            return name, value
        base = name
        i = 2
        while f"{base}_{i}" in result:
            i += 1
        return f"{base}_{i}", value

    def get_available_fields(self, files: list[FileItem]) -> list[str]:
        """Return unique field names found across all files."""
        fields: set[str] = set()
        for f in files:
            fields.update(f.extracted_fields.keys())
        # Remove numbered fallback keys like 姓名_2
        clean = {k for k in fields if not (k.rsplit("_", 1)[-1].isdigit() and len(k) > 3)}
        return sorted(clean)

    def get_field_values(self, field_name: str) -> list[str]:
        return sorted(self._field_cache.get(field_name, set()))
```

- [ ] **Step 2: Update `bridge.py` import to use `py_engine.extractor`**

In `bridge.py`, change:
```python
from core.extractor import SmartExtractor
```
to:
```python
from py_engine.extractor import SmartExtractor
```

- [ ] **Step 3: Commit**

---

### Task 8: Create `py_engine/comparator.py` — table/file matching

**Files:**
- Create: `py_engine/comparator.py`

- [ ] **Step 1: Write `py_engine/comparator.py`**

```python
"""Table comparator — match files to table rows using extracted fields."""

from __future__ import annotations
import pandas as pd
from models.file_item import FileItem


class TableComparator:
    """Match files to table roster rows based on extracted name/ID fields."""

    def match(
        self,
        files: list[FileItem],
        table_df: pd.DataFrame,
    ) -> dict[int, int | None]:
        """
        Return mapping: file_index → table_row_index (or None if no match).
        Uses name and student ID for matching.
        """
        mapping: dict[int, int | None] = {}

        # Detect name/id columns in table
        name_col = self._find_column(table_df, {"姓名", "name", "名字", "学生姓名"})
        sid_col = self._find_column(table_df, {"学号", "id", "student_id", "studentId", "工号"})

        table_names = table_df[name_col].astype(str).tolist() if name_col else []
        table_sids = table_df[sid_col].astype(str).tolist() if sid_col else []

        for i, f in enumerate(files):
            file_name = f.extracted_fields.get("姓名", "")
            file_sid = f.extracted_fields.get("学号", "")
            match_idx = self._find_match(file_name, file_sid, table_names, table_sids)
            mapping[i] = match_idx

        return mapping

    def lookup_column(
        self,
        file_item: FileItem,
        table_df: pd.DataFrame,
        column: str,
    ) -> str | None:
        """Find the value in `column` for the table row matching this file."""
        name_col = self._find_column(table_df, {"姓名", "name", "名字"})
        sid_col = self._find_column(table_df, {"学号", "id", "student_id"})
        file_name = file_item.extracted_fields.get("姓名", "")
        file_sid = file_item.extracted_fields.get("学号", "")

        for _, row in table_df.iterrows():
            row_name = str(row.get(name_col, "")) if name_col else ""
            row_sid = str(row.get(sid_col, "")) if sid_col else ""
            if self._is_match(file_name, file_sid, row_name, row_sid):
                val = row.get(column)
                return str(val) if pd.notna(val) else None
        return None

    def _find_column(self, df: pd.DataFrame, candidates: set[str]) -> str | None:
        """Find the first matching column name from candidates."""
        for col in df.columns:
            if col in candidates or col.lower() in {c.lower() for c in candidates}:
                return col
        return None

    def _find_match(
        self,
        file_name: str,
        file_sid: str,
        table_names: list[str],
        table_sids: list[str],
    ) -> int | None:
        for j in range(max(len(table_names), len(table_sids))):
            row_name = table_names[j] if j < len(table_names) else ""
            row_sid = table_sids[j] if j < len(table_sids) else ""
            if self._is_match(file_name, file_sid, row_name, row_sid):
                return j
        return None

    @staticmethod
    def _is_match(file_name: str, file_sid: str, row_name: str, row_sid: str) -> bool:
        """Check if file fields match a table row."""
        if file_sid and row_sid and file_sid.strip() == row_sid.strip():
            return True
        if file_name and row_name and (file_name in row_name or row_name in file_name):
            return True
        return False
```

- [ ] **Step 2: Commit**

---

### Task 9: Remove old `core/extractor.py` and update references

**Files:**
- Delete: `core/extractor.py`
- Modify: `bridge.py` (import updated in Task 7 already)

- [ ] **Step 1: Delete old extractor**

```bash
rm core/extractor.py
```

- [ ] **Step 2: Verify all imports reference py_engine**

Run `grep -r "from core.extractor" . --include="*.py"` — should return nothing.

- [ ] **Step 3: Commit**

---

### Task 10: Create `bridge.py` — pywebview JS Bridge

**Files:**
- Create: `bridge.py`

- [ ] **Step 1: Write `bridge.py`**

```python
"""pywebview JS bridge — exposes Python API to React frontend."""

from __future__ import annotations
import webview

from models.file_item import FileItem
from models.rule_segment import RuleSegment, SegmentType
from core.extractor import SmartExtractor
from core.renamer import RenameEngine
from core.backup import BackupManager
from core.table_importer import TableImporter
from core.preset_manager import PresetManager


class Bridge:
    """API class exposed to JavaScript via webview.expose."""

    def __init__(self):
        self.files: list[FileItem] = []
        self.segments: list[RuleSegment] = []
        self.preview_index: int = -1
        self.selected_segment_index: int = -1
        self.table_df = None
        self.table_columns: list[str] = []
        self._window: webview.Window | None = None

        self.extractor = SmartExtractor()
        self.renamer = RenameEngine()
        self.backup_mgr = BackupManager()
        self.table_importer = TableImporter()
        self.preset_mgr = PresetManager()
        self.preset_mgr.ensure_builtin_presets()

        self._dark = True

    def set_window(self, window: webview.Window):
        self._window = window

    # ── File operations ──

    def add_files(self, paths: list[str]):
        existing = {f.path for f in self.files}
        new = [FileItem(path=p) for p in paths if p not in existing]
        if not new:
            return
        self.files.extend(new)
        for f in new:
            f.extracted_fields = self.extractor.extract(f.original_name)
        self._refresh_derived()
        if not self.files or self.preview_index < 0:
            self.preview_index = 0
        self._notify_state()

    def add_folder(self, path: str):
        import os
        gathered = []
        for root, _, filenames in os.walk(path):
            for fn in filenames:
                gathered.append(os.path.join(root, fn))
        self.add_files(gathered)

    def clear_files(self):
        self.files.clear()
        self.preview_index = -1
        self._notify_state()

    def get_files(self) -> list[dict]:
        return [f.to_dict() for f in self.files]

    def get_preview_file(self) -> dict | None:
        if 0 <= self.preview_index < len(self.files):
            f = self.files[self.preview_index]
            idx = self.files.index(f) + 1
            f.new_name = self.renamer.generate_name(f, self.segments, idx, self.table_df)
            return f.to_dict()
        return None

    def set_preview_index(self, index: int):
        if 0 <= index < len(self.files):
            self.preview_index = index
            self._notify_state()

    # ── Segment operations ──

    def add_segment(self, segment_type: str, **kwargs):
        try:
            st = SegmentType[segment_type]
        except KeyError:
            return
        seg = RuleSegment(type=st, position=len(self.segments), **kwargs)
        self.segments.append(seg)
        self._notify_state()

    def remove_segment(self, index: int):
        if 0 <= index < len(self.segments):
            del self.segments[index]
        self._reindex()
        self._notify_state()

    def move_segment(self, from_idx: int, to_idx: int):
        n = len(self.segments)
        if 0 <= from_idx < n and 0 <= to_idx < n:
            seg = self.segments.pop(from_idx)
            self.segments.insert(to_idx, seg)
        self._reindex()
        self._notify_state()

    def update_segment(self, index: int, data: dict):
        if 0 <= index < len(self.segments):
            seg = self.segments[index]
            for k, v in data.items():
                if hasattr(seg, k):
                    try:
                        st = SegmentType[v] if k == "type" and isinstance(v, str) else None
                        setattr(seg, k, st if st else v)
                    except (KeyError, TypeError):
                        setattr(seg, k, v)
        self._notify_state()

    def select_segment(self, index: int):
        self.selected_segment_index = index
        for i, s in enumerate(self.segments):
            s.selected = (i == index)
        self._notify_state()

    def get_segments(self) -> list[dict]:
        return [s.to_dict() for s in self.segments]

    def get_selected_segment(self) -> dict | None:
        if 0 <= self.selected_segment_index < len(self.segments):
            return self.segments[self.selected_segment_index].to_dict()
        return None

    def get_available_fields(self) -> list[str]:
        return self.extractor.get_available_fields(self.files)

    # ── Table operations ──

    def import_table(self, path: str) -> dict | None:
        result = self.table_importer.import_file(path)
        if result is not None:
            self.table_df, self.table_columns = result
            self._notify_state()
            return {"columns": self.table_columns, "rows": len(self.table_df)}
        return None

    def get_table_info(self) -> dict | None:
        if self.table_df is not None:
            return {"columns": self.table_columns, "rows": len(self.table_df)}
        return None

    # ── Rename operations ──

    def execute_rename(self) -> dict:
        if not self.files or not self.segments:
            return {"success": 0, "failed": 0}
        rename_map = {}
        for i, f in enumerate(self.files):
            new_name = self.renamer.generate_name(f, self.segments, i + 1, self.table_df)
            rename_map[f.path] = new_name
        conflicts = self.renamer.check_conflicts(self.files, rename_map)
        self.backup_mgr.backup(self.files)
        success, failed = self.renamer.execute(rename_map)
        self._notify_state()
        return {"success": success, "failed": failed, "conflicts": len(conflicts)}

    def undo_rename(self) -> int:
        restored = self.backup_mgr.restore()
        if restored:
            for f in self.files:
                f.new_name = f.original_name
            self._notify_state()
        return len(restored)

    # ── Preset operations ──

    def save_preset(self, name: str):
        self.preset_mgr.save(name, self.segments)

    def load_preset(self, name: str) -> list[dict]:
        segs = self.preset_mgr.load(name)
        if segs:
            self.segments = segs
            self._notify_state()
            return [s.to_dict() for s in segs]
        return []

    def list_presets(self) -> list[str]:
        return self.preset_mgr.list_presets()

    # ── Theme ──

    def cycle_theme(self) -> str:
        from theme import toggle_theme
        self._dark = not self._dark
        toggle_theme()
        return "dark" if self._dark else "light"

    def get_is_dark(self) -> bool:
        return self._dark

    # ── Native dialogs ──

    def pick_files(self) -> list[str]:
        import tkinter.filedialog as fd
        import tkinter as tk
        root = tk.Tk()
        root.withdraw()
        root.attributes('-topmost', True)
        paths = fd.askopenfilenames(title="选择文件")
        root.destroy()
        return list(paths)

    def pick_folder(self) -> str:
        import tkinter.filedialog as fd
        import tkinter as tk
        root = tk.Tk()
        root.withdraw()
        root.attributes('-topmost', True)
        path = fd.askdirectory(title="选择文件夹")
        root.destroy()
        return path

    def pick_table(self) -> str:
        import tkinter.filedialog as fd
        import tkinter as tk
        root = tk.Tk()
        root.withdraw()
        root.attributes('-topmost', True)
        path = fd.askopenfilename(
            title="导入表格",
            filetypes=[("表格文件", "*.csv *.xlsx *.xls"), ("CSV", "*.csv"), ("Excel", "*.xlsx *.xls")],
        )
        root.destroy()
        return path

    # ── Full state sync (for initial load / refresh) ──

    def get_full_state(self) -> dict:
        if self.files and self.preview_index < 0:
            self.preview_index = 0
        preview = None
        if self.files and 0 <= self.preview_index < len(self.files):
            f = self.files[self.preview_index]
            idx = self.files.index(f) + 1
            f.new_name = self.renamer.generate_name(f, self.segments, idx, self.table_df)
            preview = f.to_dict()
        return {
            "files": [f.to_dict() for f in self.files],
            "segments": [s.to_dict() for s in self.segments],
            "previewIndex": self.preview_index,
            "selectedSegmentIndex": self.selected_segment_index,
            "previewFile": preview,
            "availableFields": self.extractor.get_available_fields(self.files),
            "tableInfo": {"columns": self.table_columns, "rows": len(self.table_df)} if self.table_df is not None else None,
            "isDark": self._dark,
        }

    # ── Internal ──

    def _refresh_derived(self):
        for f in self.files:
            if not f.extracted_fields:
                f.extracted_fields = self.extractor.extract(f.original_name)

    def _reindex(self):
        for i, s in enumerate(self.segments):
            s.position = i

    def _notify_state(self):
        if self._window:
            self._window.evaluate_js('window.__bridge_event__ && window.__bridge_event__("state_update")')
```

- [ ] **Step 2: Commit**

---

### Task 11: Rewrite `main.py` with pywebview

**Files:**
- Modify: `main.py`
- Modify: `theme.py`

- [ ] **Step 1: Rewrite `main.py`**

```python
"""Entry point for Batch File Renamer — pywebview + React frontend."""

import sys
import os
import json
import webview

from bridge import Bridge
from theme import apply_acrylic

FRONTEND_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "frontend", "dist")
INDEX_HTML = os.path.join(FRONTEND_DIR, "index.html")


def build_html_with_initial_state(bridge: Bridge) -> str:
    """Inject initial state as window.__INITIAL_STATE__ into index.html."""
    with open(INDEX_HTML, "r", encoding="utf-8") as f:
        html = f.read()
    state = bridge.get_full_state()
    script = f'<script>window.__INITIAL_STATE__ = {json.dumps(state, ensure_ascii=False)};</script>'
    html = html.replace("</head>", script + "</head>", 1)
    return html


def main():
    bridge = Bridge()

    # Check if built frontend exists; fall back to dev server
    if os.path.exists(INDEX_HTML):
        html = build_html_with_initial_state(bridge)
        window = webview.create_window(
            "批量文件重命名工具",
            html=html,
            width=1152,
            height=700,
            min_size=(960, 550),
            js_api=bridge,
        )
    else:
        # Development mode: load Vite dev server
        window = webview.create_window(
            "批量文件重命名工具",
            url="http://localhost:5173",
            width=1152,
            height=700,
            min_size=(960, 550),
            js_api=bridge,
        )

    bridge.set_window(window)

    # Apply acrylic/mica effect after window is created
    def on_shown():
        apply_acrylic(int(window.hwnd))

    window.events.shown += on_shown
    webview.start(debug=not os.path.exists(INDEX_HTML))


if __name__ == "__main__":
    main()
```

- [ ] **Step 2: Simplify `theme.py` — remove QSS, keep colors + acrylic**

Keep the `Colors` class, `toggle_theme()` function, `apply_acrylic()` function, and `is_dark()`. Remove `build_stylesheet()` entirely.

Replace `build_stylesheet` with:
```python
def get_color(key: str) -> str:
    """Get a design token value by name (e.g. 'bg', 'primary')."""
    return getattr(Colors, key, "")
```

- [ ] **Step 3: Commit**

---

### Task 12: React bridge wrapper (`bridge.ts`)

**Files:**
- Create: `frontend/src/bridge.ts`

- [ ] **Step 1: Write `frontend/src/bridge.ts`**

```typescript
// Python bridge — wraps window.pywebview.api calls
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
  type: string  // 'TEXT' | 'COUNTER' | 'DATE' | 'EXTRACT' | 'TABLE_FIELD'
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
}

export interface TableInfo {
  columns: string[]
  rows: number
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
}

const api = () => window.pywebview.api

export const bridge = {
  async getFullState(): Promise<FullState> {
    return api().get_full_state()
  },

  async addFiles(paths: string[]): Promise<void> {
    return api().add_files(paths)
  },

  async addFolder(path: string): Promise<void> {
    return api().add_folder(path)
  },

  async clearFiles(): Promise<void> {
    return api().clear_files()
  },

  async addSegment(type: string, kwargs: Record<string, any> = {}): Promise<void> {
    return api().add_segment(type, kwargs)
  },

  async removeSegment(index: number): Promise<void> {
    return api().remove_segment(index)
  },

  async moveSegment(fromIdx: number, toIdx: number): Promise<void> {
    return api().move_segment(fromIdx, toIdx)
  },

  async updateSegment(index: number, data: Record<string, any>): Promise<void> {
    return api().update_segment(index, data)
  },

  async selectSegment(index: number): Promise<void> {
    return api().select_segment(index)
  },

  async importTable(path: string): Promise<TableInfo | null> {
    return api().import_table(path)
  },

  async executeRename(): Promise<{ success: number; failed: number; conflicts: number }> {
    return api().execute_rename()
  },

  async undoRename(): Promise<number> {
    return api().undo_rename()
  },

  async savePreset(name: string): Promise<void> {
    return api().save_preset(name)
  },

  async loadPreset(name: string): Promise<RuleSegment[]> {
    return api().load_preset(name)
  },

  async listPresets(): Promise<string[]> {
    return api().list_presets()
  },

  async cycleTheme(): Promise<string> {
    return api().cycle_theme()
  },

  async pickFiles(): Promise<string[]> {
    return api().pick_files()
  },

  async pickFolder(): Promise<string> {
    return api().pick_folder()
  },

  async pickTable(): Promise<string> {
    return api().pick_table()
  },

  onStateUpdate(callback: () => void) {
    window.__bridge_event__ = callback
  },
}
```

- [ ] **Step 2: Commit**

---

### Task 13: Zustand store

**Files:**
- Create: `frontend/src/store/types.ts`
- Create: `frontend/src/store/useAppStore.ts`

- [ ] **Step 1: Write `frontend/src/store/types.ts`**

```typescript
export type { FileItem, RuleSegment, TableInfo, FullState } from '@/bridge'
```

- [ ] **Step 2: Write `frontend/src/store/useAppStore.ts`**

```typescript
import { create } from 'zustand'
import type { FileItem, RuleSegment, TableInfo, FullState } from '@/bridge'
import { bridge } from '@/bridge'

interface AppState {
  // Data
  files: FileItem[]
  segments: RuleSegment[]
  previewIndex: number
  selectedSegmentIndex: number
  availableFields: string[]
  tableInfo: TableInfo | null
  isDark: boolean
  statusText: string
  statusLevel: 'info' | 'warning' | 'error'

  // Actions
  loadInitialState: (state: FullState) => void
  refresh: () => Promise<void>
  setStatus: (text: string, level?: 'info' | 'warning' | 'error') => void

  addFiles: (paths: string[]) => Promise<void>
  addFolder: (path: string) => Promise<void>
  clearFiles: () => Promise<void>

  addSegment: (type: string, kwargs?: Record<string, any>) => Promise<void>
  removeSegment: (index: number) => Promise<void>
  moveSegment: (from: number, to: number) => Promise<void>
  updateSegment: (index: number, data: Record<string, any>) => Promise<void>
  selectSegment: (index: number) => Promise<void>

  setPreviewIndex: (index: number) => void

  importTable: (path: string) => Promise<void>

  executeRename: () => Promise<{ success: number; failed: number; conflicts: number }>
  undoRename: () => Promise<void>

  savePreset: (name: string) => Promise<void>
  loadPreset: (name: string) => Promise<void>

  cycleTheme: () => Promise<void>
}

export const useAppStore = create<AppState>((set, get) => ({
  files: [],
  segments: [],
  previewIndex: -1,
  selectedSegmentIndex: -1,
  availableFields: [],
  tableInfo: null,
  isDark: true,
  statusText: '就绪 | 已加载 0 个文件',
  statusLevel: 'info',

  loadInitialState: (state) => set({
    files: state.files,
    segments: state.segments,
    previewIndex: state.previewIndex,
    selectedSegmentIndex: state.selectedSegmentIndex,
    availableFields: state.availableFields,
    tableInfo: state.tableInfo,
    isDark: state.isDark,
  }),

  refresh: async () => {
    const state = await bridge.getFullState()
    set({
      files: state.files,
      segments: state.segments,
      previewIndex: state.previewIndex,
      selectedSegmentIndex: state.selectedSegmentIndex,
      availableFields: state.availableFields,
      tableInfo: state.tableInfo,
      isDark: state.isDark,
    })
    const { files } = get()
    set({ statusText: `已加载 ${files.length} 个文件 | 预览：第 ${(state.previewIndex ?? -1) + 1} 个` })
  },

  setStatus: (text, level = 'info') => set({ statusText: text, statusLevel: level }),

  addFiles: async (paths) => {
    await bridge.addFiles(paths)
    await get().refresh()
  },

  addFolder: async (path) => {
    await bridge.addFolder(path)
    await get().refresh()
  },

  clearFiles: async () => {
    await bridge.clearFiles()
    await get().refresh()
  },

  addSegment: async (type, kwargs) => {
    await bridge.addSegment(type, kwargs)
    await get().refresh()
  },

  removeSegment: async (index) => {
    await bridge.removeSegment(index)
    await get().refresh()
  },

  moveSegment: async (from, to) => {
    await bridge.moveSegment(from, to)
    await get().refresh()
  },

  updateSegment: async (index, data) => {
    await bridge.updateSegment(index, data)
    await get().refresh()
  },

  selectSegment: async (index) => {
    await bridge.selectSegment(index)
    await get().refresh()
  },

  setPreviewIndex: async (index) => {
    await bridge.set_preview_index(index)
    await get().refresh()
  },

  importTable: async (path) => {
    const result = await bridge.importTable(path)
    if (result) {
      await get().refresh()
      set({ statusText: `已导入表格：${result.columns.length} 列, ${result.rows} 行` })
    }
  },

  executeRename: async () => {
    const result = await bridge.executeRename()
    await get().refresh()
    set({ statusText: `重命名完成：${result.success} 成功, ${result.failed} 失败` })
    return result
  },

  undoRename: async () => {
    const count = await bridge.undoRename()
    await get().refresh()
    set({ statusText: count > 0 ? `已撤销 ${count} 个文件的重命名` : '没有可撤销的操作' })
  },

  savePreset: async (name) => {
    await bridge.savePreset(name)
    set({ statusText: `预设已保存：${name}` })
  },

  loadPreset: async (name) => {
    await bridge.loadPreset(name)
    await get().refresh()
    set({ statusText: `已加载预设：${name}` })
  },

  cycleTheme: async () => {
    const theme = await bridge.cycleTheme()
    set({ isDark: theme === 'dark', statusText: `主题：${theme === 'dark' ? '深色' : '浅色'}` })
  },
}))
```

- [ ] **Step 3: Commit**

---

### Task 14: App layout + Toolbar

**Files:**
- Create: `frontend/src/App.tsx`
- Create: `frontend/src/components/layout/Toolbar.tsx`
- Create: `frontend/src/components/layout/StatusBar.tsx`
- Modify: `frontend/src/main.tsx`

- [ ] **Step 1: Write `main.tsx`**

```tsx
import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import App from './App'
import './index.css'

const container = document.getElementById('root')!
const root = createRoot(container)
root.render(
  <StrictMode>
    <App />
  </StrictMode>,
)
```

- [ ] **Step 2: Write `App.tsx`**

```tsx
import { useEffect } from 'react'
import { Toolbar } from '@/components/layout/Toolbar'
import { StatusBar } from '@/components/layout/StatusBar'
import { SegmentBar } from '@/components/segments/SegmentBar'
import { PreviewCard } from '@/components/preview/PreviewCard'
import { AuxPanel } from '@/components/panels/AuxPanel'
import { FileDrawer } from '@/components/layout/FileDrawer'
import { ConfirmDialog } from '@/components/dialogs/ConfirmDialog'
import { PresetSaveDialog } from '@/components/dialogs/PresetSaveDialog'
import { useAppStore } from '@/store/useAppStore'
import { bridge } from '@/bridge'

export default function App() {
  const refresh = useAppStore((s) => s.refresh)

  useEffect(() => {
    // Load initial state if present (production mode)
    if (window.__INITIAL_STATE__) {
      useAppStore.getState().loadInitialState(window.__INITIAL_STATE__)
    } else {
      refresh()
    }
    // Set up state update listener from Python
    bridge.onStateUpdate(() => refresh())
  }, [refresh])

  return (
    <div className="flex flex-col h-screen bg-bg text-text-primary font-sans overflow-hidden">
      <div className="flex items-center px-3 py-2">
        <Toolbar />
        <div className="flex-1" />
        <PreviewCard />
      </div>
      <div className="px-3 py-1">
        <SegmentBar />
      </div>
      <AuxPanel />
      <div className="flex-1" />
      <StatusBar />
      <FileDrawer />
      <ConfirmDialog />
      <PresetSaveDialog />
    </div>
  )
}
```

- [ ] **Step 3: Write `frontend/src/components/layout/Toolbar.tsx`**

```tsx
import { useState, useEffect } from 'react'
import { Button } from '@/components/ui/button'
import { useAppStore } from '@/store/useAppStore'
import { bridge } from '@/bridge'
import { FolderOpen, FilePlus, Table, Undo2, Trash2, SunMoon, List, Play } from 'lucide-react'
import { Popover, PopoverContent, PopoverTrigger } from '@/components/ui/popover'

export function Toolbar() {
  const [presets, setPresets] = useState<string[]>([])
  const [presetOpen, setPresetOpen] = useState(false)

  const addFiles = useAppStore((s) => s.addFiles)
  const addFolder = useAppStore((s) => s.addFolder)
  const clearFiles = useAppStore((s) => s.clearFiles)
  const importTable = useAppStore((s) => s.importTable)
  const undoRename = useAppStore((s) => s.undoRename)
  const cycleTheme = useAppStore((s) => s.cycleTheme)
  const loadPreset = useAppStore((s) => s.loadPreset)
  const savePreset = useAppStore((s) => s.savePreset)
  const executeRename = useAppStore((s) => s.executeRename)
  const toggleFileDrawer = useAppStore((s) => s.toggleFileDrawer)

  useEffect(() => {
    bridge.listPresets().then(setPresets)
  }, [])

  const handlePickFolder = async () => {
    const path = await bridge.pickFolder()
    if (path) addFolder(path)
  }

  const handlePickFiles = async () => {
    const paths = await bridge.pickFiles()
    if (paths.length) addFiles(paths)
  }

  const handlePickTable = async () => {
    const path = await bridge.pickTable()
    if (path) importTable(path)
  }

  return (
    <div className="flex items-center gap-1.5 flex-wrap">
      <Button variant="ghost" size="default" onClick={handlePickFolder}>
        <FolderOpen className="size-3.5" />
        选择文件夹
      </Button>
      <Button variant="ghost" size="default" onClick={handlePickFiles}>
        <FilePlus className="size-3.5" />
        添加文件
      </Button>
      <Button variant="ghost" size="default" onClick={handlePickTable}>
        <Table className="size-3.5" />
        导入表格
      </Button>

      {/* Separator */}
      <div className="w-px h-5 bg-border mx-1.5" />

      {/* Presets popover */}
      <Popover open={presetOpen} onOpenChange={setPresetOpen}>
        <PopoverTrigger asChild>
          <Button variant="ghost" size="default">预设</Button>
        </PopoverTrigger>
        <PopoverContent className="w-40 p-1" align="start">
          {presets.map((name) => (
            <button
              key={name}
              className="w-full text-left px-3 py-2 rounded-md text-sm hover:bg-primary hover:text-white transition-colors"
              onClick={() => { loadPreset(name); setPresetOpen(false) }}
            >
              {name}
            </button>
          ))}
          <div className="h-px bg-border my-1" />
          <button
            className="w-full text-left px-3 py-2 rounded-md text-sm text-text-dim hover:bg-primary hover:text-white transition-colors"
            onClick={() => { savePreset(prompt('预设名称：') || ''); setPresetOpen(false) }}
          >
            保存当前为预设...
          </button>
        </PopoverContent>
      </Popover>

      <div className="w-px h-5 bg-border mx-1.5" />

      <Button variant="ghost" size="default" onClick={undoRename}>
        <Undo2 className="size-3.5" />
        撤销
      </Button>
      <Button variant="ghost" size="default" onClick={clearFiles}>
        <Trash2 className="size-3.5" />
        清空
      </Button>
      <Button variant="ghost" size="default" onClick={cycleTheme}>
        <SunMoon className="size-3.5" />
        主题
      </Button>
      <Button variant="ghost" size="default" onClick={toggleFileDrawer}>
        <List className="size-3.5" />
        文件列表
      </Button>

      <div className="flex-1" />

      <Button variant="default" size="default" onClick={executeRename}>
        <Play className="size-3.5" />
        执行重命名
      </Button>
    </div>
  )
}
```

- [ ] **Step 4: Write `frontend/src/components/layout/StatusBar.tsx`**

```tsx
import { useAppStore } from '@/store/useAppStore'

export function StatusBar() {
  const text = useAppStore((s) => s.statusText)
  const level = useAppStore((s) => s.statusLevel)

  const colors = { info: 'text-text-dim', warning: 'text-warning', error: 'text-error' }

  return (
    <div className="h-7 border-t border-border bg-surface flex items-center px-3 shrink-0">
      <span className={`text-xs ${colors[level]}`}>{text}</span>
    </div>
  )
}
```

- [ ] **Step 5: Create basic UI primitives needed for Toolbar**

Create `frontend/src/components/ui/popover.tsx`:
```tsx
import * as PopoverPrimitive from '@radix-ui/react-popover'
import { cn } from '@/lib/utils'
import { ComponentPropsWithoutRef, ElementRef, forwardRef } from 'react'

const Popover = PopoverPrimitive.Root
const PopoverTrigger = PopoverPrimitive.Trigger

const PopoverContent = forwardRef<
  ElementRef<typeof PopoverPrimitive.Content>,
  ComponentPropsWithoutRef<typeof PopoverPrimitive.Content>
>(({ className, align = 'center', sideOffset = 4, ...props }, ref) => (
  <PopoverPrimitive.Portal>
    <PopoverPrimitive.Content
      ref={ref}
      align={align}
      sideOffset={sideOffset}
      className={cn(
        'z-50 w-72 rounded-xl border border-border bg-surface p-2 shadow-lg outline-none',
        'data-[state=open]:animate-in data-[state=closed]:animate-out data-[state=closed]:fade-out-0 data-[state=open]:fade-in-0',
        className,
      )}
      {...props}
    />
  </PopoverPrimitive.Portal>
))
PopoverContent.displayName = PopoverPrimitive.Content.displayName

export { Popover, PopoverTrigger, PopoverContent }
```

- [ ] **Step 6: Add `toggleFileDrawer` to store**

Add to `useAppStore.ts` interface and actions:
```typescript
showFileDrawer: boolean
toggleFileDrawer: () => void
```

And the implementation:
```typescript
showFileDrawer: false,
toggleFileDrawer: () => set((s) => ({ showFileDrawer: !s.showFileDrawer })),
```

- [ ] **Step 7: Commit**

---

### Task 15: SegmentBar + SegmentCard with dnd-kit

**Files:**
- Create: `frontend/src/components/segments/SegmentBar.tsx`
- Create: `frontend/src/components/segments/SegmentCard.tsx`
- Create: `frontend/src/components/segments/AddSegmentMenu.tsx`

- [ ] **Step 1: Write `AddSegmentMenu.tsx`**

```tsx
import { useState } from 'react'
import { Popover, PopoverContent, PopoverTrigger } from '@/components/ui/popover'
import { Button } from '@/components/ui/button'
import { Plus } from 'lucide-react'
import { useAppStore } from '@/store/useAppStore'

export function AddSegmentMenu() {
  const [open, setOpen] = useState(false)
  const addSegment = useAppStore((s) => s.addSegment)
  const availableFields = useAppStore((s) => s.availableFields)
  const tableInfo = useAppStore((s) => s.tableInfo)

  return (
    <Popover open={open} onOpenChange={setOpen}>
      <PopoverTrigger asChild>
        <Button size="icon" className="rounded-full size-9 shrink-0">
          <Plus className="size-5" />
        </Button>
      </PopoverTrigger>
      <PopoverContent className="w-44 p-1" align="end">
        <button className="w-full text-left px-3 py-2 rounded-md text-sm hover:bg-primary hover:text-white transition-colors"
          onClick={() => { addSegment('TEXT', { text: '输入文本' }); setOpen(false) }}>
          固定文本
        </button>
        <button className="w-full text-left px-3 py-2 rounded-md text-sm hover:bg-primary hover:text-white transition-colors"
          onClick={() => { addSegment('COUNTER', { counter_start: 1, counter_padding: 2 }); setOpen(false) }}>
          序号
        </button>
        <button className="w-full text-left px-3 py-2 rounded-md text-sm hover:bg-primary hover:text-white transition-colors"
          onClick={() => { addSegment('DATE'); setOpen(false) }}>
          日期
        </button>
        <div className="h-px bg-border my-1" />
        <div className="px-3 py-1 text-xs text-text-dim font-semibold uppercase tracking-wider">自动识别</div>
        {availableFields.length > 0
          ? availableFields.map((f) => (
              <button key={f} className="w-full text-left px-3 py-2 rounded-md text-sm hover:bg-primary hover:text-white transition-colors"
                onClick={() => { addSegment('EXTRACT', { extract_field: f }); setOpen(false) }}>
                {f}
              </button>
            ))
          : <div className="px-3 py-1 text-xs text-text-dim">(添加文件后自动检测)</div>
        }
        <div className="h-px bg-border my-1" />
        <div className="px-3 py-1 text-xs text-text-dim font-semibold uppercase tracking-wider">表格字段</div>
        {tableInfo
          ? tableInfo.columns.map((c) => (
              <button key={c} className="w-full text-left px-3 py-2 rounded-md text-sm hover:bg-primary hover:text-white transition-colors"
                onClick={() => { addSegment('TABLE_FIELD', { table_column: c }); setOpen(false) }}>
                {c}
              </button>
            ))
          : <div className="px-3 py-1 text-xs text-text-dim">(需先导入表格)</div>
        }
      </PopoverContent>
    </Popover>
  )
}
```

- [ ] **Step 2: Write `SegmentCard.tsx`**

```tsx
import { useSortable } from '@dnd-kit/sortable'
import { CSS } from '@dnd-kit/utilities'
import { GripVertical, Trash2 } from 'lucide-react'
import type { RuleSegment } from '@/store/types'
import { useAppStore } from '@/store/useAppStore'
import { cn } from '@/lib/utils'
import { Fragment } from 'react'

const TYPE_ICONS: Record<string, string> = {
  TEXT: '文', COUNTER: '#', DATE: '日', EXTRACT: '识', TABLE_FIELD: '表',
}

interface Props {
  segment: RuleSegment
  index: number
  isSelected: boolean
}

export function SegmentCard({ segment, index, isSelected }: Props) {
  const { attributes, listeners, setNodeRef, transform, transition, isDragging } = useSortable({ id: `${index}` })
  const selectSegment = useAppStore((s) => s.selectSegment)
  const removeSegment = useAppStore((s) => s.removeSegment)
  const updateSegment = useAppStore((s) => s.updateSegment)

  const style = { transform: CSS.Transform.toString(transform), transition, opacity: isDragging ? 0.4 : 1 }

  return (
    <div
      ref={setNodeRef}
      style={style}
      className={cn(
        'flex-shrink-0 w-[170px] rounded-xl border p-2.5 cursor-pointer transition-all',
        isSelected
          ? 'border-primary bg-primary-muted/30 ring-1 ring-primary'
          : 'border-border bg-surface hover:border-border-hover',
      )}
      onClick={() => selectSegment(index)}
    >
      <div className="flex items-center gap-1.5 mb-1.5">
        <button {...attributes} {...listeners} className="text-text-dim hover:text-text-secondary cursor-grab active:cursor-grabbing">
          <GripVertical className="size-3.5" />
        </button>
        <span className="inline-flex items-center justify-center size-[26px] rounded-md bg-primary text-white text-xs font-bold shrink-0">
          {TYPE_ICONS[segment.type] || '?'}
        </span>
        <span className="text-xs font-semibold text-text-primary truncate flex-1">{segment.label}</span>
        <button
          className="text-text-dim hover:text-error shrink-0"
          onClick={(e) => { e.stopPropagation(); removeSegment(index) }}
        >
          <Trash2 className="size-3" />
        </button>
      </div>

      {/* Inline editor based on type */}
      <div className="flex items-center gap-1">
        {segment.type === 'TEXT' && (
          <input
            className="w-full h-7 rounded-md bg-surface-raised border border-border px-2 text-xs text-text-primary placeholder:text-text-dim focus:outline-none focus:border-primary"
            value={segment.text}
            placeholder="输入文本..."
            onChange={(e) => updateSegment(index, { text: e.target.value })}
            onClick={(e) => e.stopPropagation()}
          />
        )}
        {segment.type === 'COUNTER' && (
          <div className="flex items-center gap-1 text-xs text-text-dim">
            <span>起</span>
            <input
              type="number" min={0} max={9999}
              className="w-10 h-7 rounded-md bg-surface-raised border border-border px-1 text-xs text-text-primary text-center focus:outline-none focus:border-primary"
              value={segment.counter_start}
              onChange={(e) => updateSegment(index, { counter_start: Number(e.target.value) })}
              onClick={(e) => e.stopPropagation()}
            />
            <span>位</span>
            <input
              type="number" min={0} max={10}
              className="w-8 h-7 rounded-md bg-surface-raised border border-border px-1 text-xs text-text-primary text-center focus:outline-none focus:border-primary"
              value={segment.counter_padding}
              onChange={(e) => updateSegment(index, { counter_padding: Number(e.target.value) })}
              onClick={(e) => e.stopPropagation()}
            />
          </div>
        )}
        {segment.type === 'DATE' && (
          <select
            className="w-full h-7 rounded-md bg-surface-raised border border-border px-1 text-xs text-text-primary focus:outline-none focus:border-primary"
            value={segment.date_format}
            onChange={(e) => updateSegment(index, { date_format: e.target.value })}
            onClick={(e) => e.stopPropagation()}
          >
            <option value="%Y%m%d">%Y%m%d</option>
            <option value="%Y-%m-%d">%Y-%m-%d</option>
            <option value="%Y_%m_%d">%Y_%m_%d</option>
            <option value="%m%d">%m%d</option>
            <option value="%Y%m">%Y%m</option>
          </select>
        )}
        {segment.type === 'EXTRACT' && (
          <select
            className="w-full h-7 rounded-md bg-surface-raised border border-border px-1 text-xs text-text-primary focus:outline-none focus:border-primary"
            value={segment.extract_field || ''}
            onChange={(e) => updateSegment(index, { extract_field: e.target.value })}
            onClick={(e) => e.stopPropagation()}
          >
            <option value="">选择字段</option>
          </select>
        )}
        {segment.type === 'TABLE_FIELD' && (
          <select
            className="w-full h-7 rounded-md bg-surface-raised border border-border px-1 text-xs text-text-primary focus:outline-none focus:border-primary"
            value={segment.table_column || ''}
            onChange={(e) => updateSegment(index, { table_column: e.target.value })}
            onClick={(e) => e.stopPropagation()}
          >
            <option value="">选择列</option>
          </select>
        )}
      </div>
    </div>
  )
}
```

- [ ] **Step 3: Write `SegmentBar.tsx`**

```tsx
import { DndContext, closestCenter, PointerSensor, useSensor, useSensors, DragEndEvent } from '@dnd-kit/core'
import { SortableContext, horizontalListSortingStrategy } from '@dnd-kit/sortable'
import { useAppStore } from '@/store/useAppStore'
import { SegmentCard } from './SegmentCard'
import { AddSegmentMenu } from './AddSegmentMenu'

export function SegmentBar() {
  const segments = useAppStore((s) => s.segments)
  const selectedIndex = useAppStore((s) => s.selectedSegmentIndex)
  const moveSegment = useAppStore((s) => s.moveSegment)

  const sensors = useSensors(useSensor(PointerSensor, { activationConstraint: { distance: 8 } }))

  const handleDragEnd = (event: DragEndEvent) => {
    const { active, over } = event
    if (over && active.id !== over.id) {
      moveSegment(Number(active.id), Number(over.id))
    }
  }

  return (
    <div className="min-h-[94px] rounded-xl border border-border bg-surface p-2 flex items-center gap-2">
      <DndContext sensors={sensors} collisionDetection={closestCenter} onDragEnd={handleDragEnd}>
        <SortableContext items={segments.map((_, i) => `${i}`)} strategy={horizontalListSortingStrategy}>
          <div className="flex gap-2 overflow-x-auto flex-1 items-center px-1 scrollbar-thin">
            {segments.map((seg, i) => (
              <SegmentCard key={i} segment={seg} index={i} isSelected={i === selectedIndex} />
            ))}
            {segments.length === 0 && (
              <span className="text-sm text-text-dim px-2">点击 + 添加规则片段</span>
            )}
          </div>
        </SortableContext>
      </DndContext>
      <div className="shrink-0">
        <AddSegmentMenu />
      </div>
    </div>
  )
}
```

- [ ] **Step 4: Commit**

---

### Task 16: PreviewCard

**Files:**
- Create: `frontend/src/components/preview/PreviewCard.tsx`

- [ ] **Step 1: Write `PreviewCard.tsx`**

```tsx
import { useAppStore } from '@/store/useAppStore'
import { Copy, AlertTriangle } from 'lucide-react'

export function PreviewCard() {
  const files = useAppStore((s) => s.files)
  const previewIndex = useAppStore((s) => s.previewIndex)

  const file = files[previewIndex] ?? null
  const changed = file && file.original_name !== file.new_name

  return (
    <div className="shrink-0 w-[380px] h-[100px] rounded-2xl border border-border bg-surface p-4 flex flex-col gap-1">
      <span className="text-xs text-text-dim">
        原文件名：{file?.original_name ?? '—'}
      </span>
      <span className={`text-[15px] font-semibold ${changed ? 'text-primary' : 'text-text-dim'}`}>
        新文件名：{file?.new_name ?? '—'}
      </span>
      {file?.status === 'conflict' && (
        <span className="text-xs text-error flex items-center gap-1">
          <AlertTriangle className="size-3" />
          文件名冲突
        </span>
      )}
    </div>
  )
}
```

- [ ] **Step 2: Commit**

---

### Task 17: AuxPanel

**Files:**
- Create: `frontend/src/components/panels/AuxPanel.tsx`

- [ ] **Step 1: Write `AuxPanel.tsx`**

```tsx
import { useAppStore } from '@/store/useAppStore'
import type { RuleSegment } from '@/store/types'
import { AnimatePresence, motion } from 'framer-motion'

export function AuxPanel() {
  const segments = useAppStore((s) => s.segments)
  const selectedIndex = useAppStore((s) => s.selectedSegmentIndex)
  const updateSegment = useAppStore((s) => s.updateSegment)

  const seg: RuleSegment | undefined = selectedIndex >= 0 ? segments[selectedIndex] : undefined

  return (
    <AnimatePresence>
      {seg && (
        <motion.div
          initial={{ height: 0, opacity: 0 }}
          animate={{ height: 140, opacity: 1 }}
          exit={{ height: 0, opacity: 0 }}
          transition={{ duration: 0.2 }}
          className="overflow-hidden mx-3"
        >
          <div className="rounded-b-xl border border-t-0 border-border bg-surface p-4 pt-3">
            <div className="flex items-center gap-4 flex-wrap">
              <span className="text-sm font-bold text-primary">【{seg.label}】</span>

              {seg.type === 'EXTRACT' && (
                <>
                  <label className="text-xs text-text-dim">正则：</label>
                  <input className="w-44 h-7 rounded-md bg-surface-raised border border-border px-2 text-xs text-text-primary focus:outline-none focus:border-primary"
                    value={seg.extract_regex} placeholder="自定义正则..."
                    onChange={(e) => updateSegment(selectedIndex, { extract_regex: e.target.value })} />

                  <label className="text-xs text-text-dim">字数范围：</label>
                  <input type="number" min={1} max={64} className="w-10 h-7 rounded-md bg-surface-raised border border-border px-1 text-xs text-text-primary text-center focus:outline-none focus:border-primary"
                    value={seg.extract_min_len} onChange={(e) => updateSegment(selectedIndex, { extract_min_len: Number(e.target.value) })} />
                  <span className="text-xs text-text-dim">—</span>
                  <input type="number" min={1} max={64} className="w-10 h-7 rounded-md bg-surface-raised border border-border px-1 text-xs text-text-primary text-center focus:outline-none focus:border-primary"
                    value={seg.extract_max_len} onChange={(e) => updateSegment(selectedIndex, { extract_max_len: Number(e.target.value) })} />

                  <label className="text-xs text-text-dim">前置词：</label>
                  <input className="w-24 h-7 rounded-md bg-surface-raised border border-border px-2 text-xs text-text-primary focus:outline-none focus:border-primary"
                    value={seg.extract_keywords_before} onChange={(e) => updateSegment(selectedIndex, { extract_keywords_before: e.target.value })} />

                  <label className="text-xs text-text-dim">后置词：</label>
                  <input className="w-24 h-7 rounded-md bg-surface-raised border border-border px-2 text-xs text-text-primary focus:outline-none focus:border-primary"
                    value={seg.extract_keywords_after} onChange={(e) => updateSegment(selectedIndex, { extract_keywords_after: e.target.value })} />
                </>
              )}

              {seg.type === 'COUNTER' && (
                <>
                  <label className="text-xs text-text-dim">起始：</label>
                  <input type="number" min={0} max={9999} className="w-14 h-7 rounded-md bg-surface-raised border border-border px-1 text-xs text-text-primary text-center focus:outline-none focus:border-primary"
                    value={seg.counter_start} onChange={(e) => updateSegment(selectedIndex, { counter_start: Number(e.target.value) })} />
                  <label className="text-xs text-text-dim">步长：</label>
                  <input type="number" min={1} max={100} className="w-12 h-7 rounded-md bg-surface-raised border border-border px-1 text-xs text-text-primary text-center focus:outline-none focus:border-primary"
                    value={seg.counter_step} onChange={(e) => updateSegment(selectedIndex, { counter_step: Number(e.target.value) })} />
                  <label className="text-xs text-text-dim">补零位数：</label>
                  <input type="number" min={0} max={10} className="w-12 h-7 rounded-md bg-surface-raised border border-border px-1 text-xs text-text-primary text-center focus:outline-none focus:border-primary"
                    value={seg.counter_padding} onChange={(e) => updateSegment(selectedIndex, { counter_padding: Number(e.target.value) })} />
                </>
              )}

              {seg.type === 'DATE' && (
                <>
                  <label className="text-xs text-text-dim">格式：</label>
                  <select className="w-36 h-7 rounded-md bg-surface-raised border border-border px-1 text-xs text-text-primary focus:outline-none focus:border-primary"
                    value={seg.date_format} onChange={(e) => updateSegment(selectedIndex, { date_format: e.target.value })}>
                    <option value="%Y%m%d">%Y%m%d</option>
                    <option value="%Y-%m-%d">%Y-%m-%d</option>
                    <option value="%Y_%m_%d">%Y_%m_%d</option>
                    <option value="%m%d">%m%d</option>
                    <option value="%Y%m">%Y%m</option>
                    <option value="%Y">%Y</option>
                    <option value="%Y%m%d_%H%M">%Y%m%d_%H%M</option>
                    <option value="%d%m%Y">%d%m%Y</option>
                  </select>
                </>
              )}

              {seg.type === 'TABLE_FIELD' && (
                <>
                  <label className="text-xs text-text-dim">匹配列：</label>
                  <select className="w-36 h-7 rounded-md bg-surface-raised border border-border px-1 text-xs text-text-primary focus:outline-none focus:border-primary"
                    value={seg.table_column || ''} onChange={(e) => updateSegment(selectedIndex, { table_column: e.target.value })}>
                    <option value="">（请先导入表格）</option>
                  </select>
                </>
              )}
            </div>
          </div>
        </motion.div>
      )}
    </AnimatePresence>
  )
}
```

- [ ] **Step 2: Commit**

---

### Task 18: FileDrawer

**Files:**
- Create: `frontend/src/components/layout/FileDrawer.tsx`

- [ ] **Step 1: Write `FileDrawer.tsx`**

```tsx
import { useAppStore } from '@/store/useAppStore'
import { AnimatePresence, motion } from 'framer-motion'
import { X, Check, AlertTriangle, XCircle } from 'lucide-react'
import { useVirtualizer } from '@tanstack/react-virtual'
import { useRef } from 'react'

const statusIcons = {
  ok: <Check className="size-3 text-success" />,
  conflict: <AlertTriangle className="size-3 text-warning" />,
  error: <XCircle className="size-3 text-error" />,
}

export function FileDrawer() {
  const show = useAppStore((s) => s.showFileDrawer)
  const files = useAppStore((s) => s.files)
  const previewIndex = useAppStore((s) => s.previewIndex)
  const setPreviewIndex = useAppStore((s) => s.setPreviewIndex)
  const toggleFileDrawer = useAppStore((s) => s.toggleFileDrawer)

  const parentRef = useRef<HTMLDivElement>(null!)
  const rowVirtualizer = useVirtualizer({
    count: files.length,
    getScrollElement: () => parentRef.current,
    estimateSize: () => 40,
    overscan: 5,
  })

  return (
    <AnimatePresence>
      {show && (
        <motion.aside
          initial={{ x: -420, opacity: 0 }}
          animate={{ x: 0, opacity: 1 }}
          exit={{ x: -420, opacity: 0 }}
          transition={{ type: 'spring', damping: 25, stiffness: 260 }}
          className="fixed left-0 top-0 bottom-0 w-[420px] bg-surface border-r border-border z-50 flex flex-col shadow-xl"
        >
          {/* Header */}
          <div className="h-11 bg-surface-raised flex items-center px-4 shrink-0">
            <span className="text-[15px] font-bold text-text-primary">文件列表</span>
            <div className="flex-1" />
            <button className="text-text-dim hover:text-text-primary transition-colors" onClick={toggleFileDrawer}>
              <X className="size-4" />
            </button>
          </div>

          {/* Virtual list */}
          <div ref={parentRef} className="flex-1 overflow-auto">
            <div style={{ height: `${rowVirtualizer.getTotalSize()}px`, position: 'relative' }}>
              {rowVirtualizer.getVirtualItems().map((vRow) => {
                const f = files[vRow.index]
                if (!f) return null
                return (
                  <button
                    key={vRow.index}
                    style={{ position: 'absolute', top: 0, left: 0, width: '100%', height: `${vRow.size}px`, transform: `translateY(${vRow.start}px)` }}
                    className={`flex items-center gap-3 px-4 text-left border-b border-border/50 transition-colors
                      ${vRow.index === previewIndex ? 'bg-primary text-white' : 'hover:bg-border-hover/30 text-text-primary'}
                    `}
                    onClick={() => setPreviewIndex(vRow.index)}
                    onDoubleClick={() => {/* open in explorer */}}
                  >
                    <span className="text-xs w-8 shrink-0 tabular-nums">{vRow.index + 1}</span>
                    <span className="text-xs flex-1 truncate">{f.original_name}</span>
                    <span className="text-xs flex-1 truncate text-text-dim">{f.new_name}</span>
                    <span className="shrink-0">{statusIcons[f.status]}</span>
                  </button>
                )
              })}
            </div>
          </div>
        </motion.aside>
      )}
    </AnimatePresence>
  )
}
```

- [ ] **Step 2: Commit**

---

### Task 19: Dialogs (ConfirmDialog + PresetSaveDialog)

**Files:**
- Create: `frontend/src/components/dialogs/ConfirmDialog.tsx`
- Create: `frontend/src/components/dialogs/PresetSaveDialog.tsx`

- [ ] **Step 1: Write `ConfirmDialog.tsx`**

```tsx
import { useState } from 'react'
import { Button } from '@/components/ui/button'
import { useAppStore } from '@/store/useAppStore'

export function ConfirmDialog() {
  const [open, setOpen] = useState(false)
  const executeRename = useAppStore((s) => s.executeRename)

  const handleExecute = () => {
    executeRename()
    setOpen(false)
  }

  // This dialog is triggered imperatively from the execute button
  // For MVP, we call executeRename directly. A full confirmation can be added later.
  return null
}
```

Actually, let's make it a proper dialog that shows rename preview. We'll use the Radix Dialog.

```tsx
import * as Dialog from '@radix-ui/react-dialog'
import { Button } from '@/components/ui/button'
import { useAppStore } from '@/store/useAppStore'
import { X, ArrowRight } from 'lucide-react'
import { useState } from 'react'

interface Props {
  open: boolean
  onOpenChange: (v: boolean) => void
}

export function ConfirmDialog({ open, onOpenChange }: Props) {
  const files = useAppStore((s) => s.files)
  const executeRename = useAppStore((s) => s.executeRename)

  const handleExecute = async () => {
    await executeRename()
    onOpenChange(false)
  }

  return (
    <Dialog.Root open={open} onOpenChange={onOpenChange}>
      <Dialog.Portal>
        <Dialog.Overlay className="fixed inset-0 bg-black/60 data-[state=open]:animate-in data-[state=closed]:animate-out data-[state=closed]:fade-out-0 data-[state=open]:fade-in-0" />
        <Dialog.Content className="fixed left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2 w-[520px] max-h-[440px] bg-surface border border-border rounded-2xl p-6 shadow-2xl data-[state=open]:animate-in data-[state=closed]:animate-out data-[state=closed]:fade-out-0 data-[state=open]:fade-in-0 data-[state=closed]:zoom-out-95 data-[state=open]:zoom-in-95">
          <div className="flex items-center justify-between mb-3">
            <Dialog.Title className="text-lg font-bold text-text-primary">确认批量重命名</Dialog.Title>
            <Dialog.Close className="text-text-dim hover:text-text-primary">
              <X className="size-4" />
            </Dialog.Close>
          </div>

          <p className="text-xs text-text-dim mb-3">即将重命名 {files.length} 个文件</p>

          <div className="max-h-60 overflow-auto border border-border rounded-lg bg-surface-raised p-1 space-y-px">
            {files.map((f, i) => {
              const changed = f.new_name !== f.original_name
              return (
                <div key={i} className="flex items-center gap-2 px-3 py-1.5 text-xs">
                  <span className={changed ? 'text-text-primary' : 'text-text-dim'}>{f.original_name}</span>
                  <ArrowRight className={`size-3 ${changed ? 'text-primary' : 'text-text-dim'}`} />
                  <span className={changed ? 'text-primary font-semibold' : 'text-text-dim'}>{f.new_name}</span>
                </div>
              )
            })}
          </div>

          <div className="flex justify-end gap-2 mt-4">
            <Dialog.Close asChild>
              <Button variant="ghost">取消</Button>
            </Dialog.Close>
            <Button variant="success" onClick={handleExecute}>确认执行</Button>
          </div>
        </Dialog.Content>
      </Dialog.Portal>
    </Dialog.Root>
  )
}
```

- [ ] **Step 2: Write `PresetSaveDialog.tsx`**

```tsx
import * as Dialog from '@radix-ui/react-dialog'
import { Button } from '@/components/ui/button'
import { useAppStore } from '@/store/useAppStore'
import { X } from 'lucide-react'
import { useState } from 'react'

interface Props {
  open: boolean
  onOpenChange: (v: boolean) => void
}

export function PresetSaveDialog({ open, onOpenChange }: Props) {
  const [name, setName] = useState('')
  const savePreset = useAppStore((s) => s.savePreset)

  const handleSave = async () => {
    if (name.trim()) {
      await savePreset(name.trim())
      setName('')
      onOpenChange(false)
    }
  }

  return (
    <Dialog.Root open={open} onOpenChange={onOpenChange}>
      <Dialog.Portal>
        <Dialog.Overlay className="fixed inset-0 bg-black/60 data-[state=open]:animate-in data-[state=closed]:animate-out data-[state=closed]:fade-out-0 data-[state=open]:fade-in-0" />
        <Dialog.Content className="fixed left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2 w-[360px] bg-surface border border-border rounded-2xl p-6 shadow-2xl data-[state=open]:animate-in data-[state=closed]:animate-out data-[state=closed]:fade-out-0 data-[state=open]:fade-in-0 data-[state=closed]:zoom-out-95 data-[state=open]:zoom-in-95">
          <div className="flex items-center justify-between mb-3">
            <Dialog.Title className="text-[15px] font-bold text-text-primary">保存当前规则为预设</Dialog.Title>
            <Dialog.Close className="text-text-dim hover:text-text-primary">
              <X className="size-4" />
            </Dialog.Close>
          </div>

          <label className="text-xs text-text-dim">预设名称：</label>
          <input
            className="w-full h-9 rounded-lg bg-surface-raised border border-border px-3 text-sm text-text-primary placeholder:text-text-dim focus:outline-none focus:border-primary mt-1.5"
            placeholder="输入预设名称..."
            value={name}
            onChange={(e) => setName(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && handleSave()}
          />

          <div className="flex justify-end gap-2 mt-4">
            <Dialog.Close asChild>
              <Button variant="ghost">取消</Button>
            </Dialog.Close>
            <Button variant="default" onClick={handleSave}>保存</Button>
          </div>
        </Dialog.Content>
      </Dialog.Portal>
    </Dialog.Root>
  )
}
```

- [ ] **Step 3: Commit**

---

### Task 20: Wire up state management in App.tsx

**Files:**
- Modify: `frontend/src/App.tsx`

- [ ] **Step 1: Rewrite `App.tsx` with dialog state**

```tsx
import { useEffect, useState, useCallback } from 'react'
import { Toolbar } from '@/components/layout/Toolbar'
import { StatusBar } from '@/components/layout/StatusBar'
import { SegmentBar } from '@/components/segments/SegmentBar'
import { PreviewCard } from '@/components/preview/PreviewCard'
import { AuxPanel } from '@/components/panels/AuxPanel'
import { FileDrawer } from '@/components/layout/FileDrawer'
import { ConfirmDialog } from '@/components/dialogs/ConfirmDialog'
import { PresetSaveDialog } from '@/components/dialogs/PresetSaveDialog'
import { useAppStore } from '@/store/useAppStore'
import { bridge } from '@/bridge'

export default function App() {
  const refresh = useAppStore((s) => s.refresh)
  const [showConfirm, setShowConfirm] = useState(false)
  const [showPresetSave, setShowPresetSave] = useState(false)
  const executeRename = useAppStore((s) => s.executeRename)

  useEffect(() => {
    if (window.__INITIAL_STATE__) {
      useAppStore.getState().loadInitialState(window.__INITIAL_STATE__)
    } else {
      refresh()
    }
    bridge.onStateUpdate(() => refresh())
  }, [refresh])

  // Keyboard shortcuts
  useEffect(() => {
    const handleKey = (e: KeyboardEvent) => {
      const store = useAppStore.getState()
      if (e.key === 'ArrowUp') {
        e.preventDefault()
        if (store.previewIndex > 0) store.setPreviewIndex(store.previewIndex - 1)
      } else if (e.key === 'ArrowDown') {
        e.preventDefault()
        if (store.previewIndex < store.files.length - 1) store.setPreviewIndex(store.previewIndex + 1)
      } else if (e.key === 'Delete' && store.selectedSegmentIndex >= 0) {
        e.preventDefault()
        store.removeSegment(store.selectedSegmentIndex)
        store.selectSegment(-1)
      } else if (e.key === 'z' && (e.ctrlKey || e.metaKey)) {
        e.preventDefault()
        store.undoRename()
      }
    }
    window.addEventListener('keydown', handleKey)
    return () => window.removeEventListener('keydown', handleKey)
  }, [])

  // Expose dialog controls to store for Toolbar
  const handleExecuteClick = useCallback(async () => {
    setShowConfirm(true)
  }, [])

  return (
    <div className="flex flex-col h-screen bg-bg text-text-primary font-sans overflow-hidden">
      <div className="flex items-center px-3 py-2">
        <Toolbar
          onExecute={handleExecuteClick}
          onSavePreset={() => setShowPresetSave(true)}
        />
        <div className="flex-1" />
        <PreviewCard />
      </div>
      <div className="px-3 py-1">
        <SegmentBar />
      </div>
      <AuxPanel />
      <div className="flex-1" />
      <StatusBar />
      <FileDrawer />
      <ConfirmDialog open={showConfirm} onOpenChange={setShowConfirm} />
      <PresetSaveDialog open={showPresetSave} onOpenChange={setShowPresetSave} />
    </div>
  )
}
```

- [ ] **Step 2: Update Toolbar to accept callback props**

Add `onExecute` and `onSavePreset` props to Toolbar, wire the primary button to call `onExecute` and the "save as preset" menu item to call `onSavePreset`.

- [ ] **Step 3: Commit**

---

### Task 21: Delete old UI code

**Files:**
- Delete: `app.py`
- Delete: `ui/main_window.py`
- Delete: `ui/toolbar.py`
- Delete: `ui/preview_card.py`
- Delete: `ui/segment_bar.py`
- Delete: `ui/segment_widget.py`
- Delete: `ui/aux_panel.py`
- Delete: `ui/file_drawer.py`
- Delete: `ui/dialogs.py`
- Delete: `ui/__init__.py`

- [ ] **Step 1: Remove the ui/ directory and app.py**

```bash
cd C:/Users/ASUS/Desktop/cloude/batch_renamer
rm -rf ui/
rm app.py
```

- [ ] **Step 2: Clean up `theme.py` — remove `build_stylesheet()` function**

The `build_stylesheet()` function (lines 167-563) should be removed since it's QSS-specific.

- [ ] **Step 3: Remove PySide6 from requirements.txt**

Replace `requirements.txt`:
```
pywebview>=5.0
pandas>=2.0
openpyxl>=3.1
```

- [ ] **Step 4: Commit**

---

### Task 22: Final integration verification

**Files:**
- No file changes — verification only

- [ ] **Step 1: Install Python dependencies**

```bash
cd C:/Users/ASUS/Desktop/cloude/batch_renamer
pip install pywebview
```

- [ ] **Step 2: Build React frontend**

```bash
cd frontend
npm run build
```

- [ ] **Step 3: Run the app**

```bash
python main.py
```

Expected: Window opens with WebView2 loading the React app. Toolbar visible, segment bar with + button, preview card showing "—". Can add files, segments appear, preview updates, rename works.

- [ ] **Step 4: Verify dev mode**

```bash
# Terminal 1
cd frontend && npm run dev

# Terminal 2
python main.py
```

Expected: App loads from `localhost:5173` instead of built files.

- [ ] **Step 5: Commit**
