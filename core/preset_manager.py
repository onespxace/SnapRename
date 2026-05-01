"""Preset manager — load and save rule presets as JSON files."""

from __future__ import annotations

import os
import json
import shutil
from app_paths import get_bundled_presets_dir, get_presets_dir
from models.rule_segment import RuleSegment


class PresetManager:
    """Manages rule presets stored as JSON files."""

    def __init__(self, presets_dir: str = ""):
        if not presets_dir:
            presets_dir = get_presets_dir()
        self._dir = presets_dir
        os.makedirs(self._dir, exist_ok=True)
        self._seed_bundled_presets()

    def _seed_bundled_presets(self):
        bundled_dir = get_bundled_presets_dir()
        if not os.path.isdir(bundled_dir):
            return
        for fn in os.listdir(bundled_dir):
            if not fn.endswith(".json"):
                continue
            src = os.path.join(bundled_dir, fn)
            dst = os.path.join(self._dir, fn)
            if not os.path.exists(dst):
                shutil.copy2(src, dst)

    def list_presets(self) -> list[str]:
        """Return list of available preset names (without extension)."""
        presets = []
        if os.path.isdir(self._dir):
            for fn in os.listdir(self._dir):
                if fn.endswith(".json"):
                    presets.append(fn[:-5])
        return sorted(presets)

    def load(self, name: str) -> list[RuleSegment] | None:
        """Load a preset by name. Returns list of RuleSegments or None."""
        path = os.path.join(self._dir, f"{name}.json")
        if not os.path.exists(path):
            return None
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            segments = []
            for i, seg_dict in enumerate(data.get("segments", [])):
                seg = RuleSegment.from_dict(seg_dict)
                seg.position = i
                segments.append(seg)
            return segments
        except (json.JSONDecodeError, KeyError):
            return None

    def save(self, name: str, segments: list[RuleSegment]):
        """Save current segments as a preset."""
        path = os.path.join(self._dir, f"{name}.json")
        data = {
            "name": name,
            "segments": [s.to_dict() for s in segments],
        }
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def delete(self, name: str) -> bool:
        """Delete a preset. Returns True if successful."""
        path = os.path.join(self._dir, f"{name}.json")
        if os.path.exists(path):
            os.remove(path)
            return True
        return False

    def ensure_builtin_presets(self):
        """Create built-in presets if they don't exist."""
        from models.rule_segment import SegmentType

        builtins = {
            "通用-学号姓名": [
                RuleSegment(type=SegmentType.EXTRACT, label="学号", extract_field="学号"),
                RuleSegment(type=SegmentType.TEXT, text="_"),
                RuleSegment(type=SegmentType.EXTRACT, label="姓名", extract_field="姓名"),
            ],
            "通用-小学号姓名": [
                RuleSegment(type=SegmentType.EXTRACT, label="小学号", extract_field="小学号"),
                RuleSegment(type=SegmentType.TEXT, text="_"),
                RuleSegment(type=SegmentType.EXTRACT, label="姓名", extract_field="姓名"),
            ],
            "计科-学号姓名作业": [
                RuleSegment(type=SegmentType.EXTRACT, label="学号", extract_field="学号"),
                RuleSegment(type=SegmentType.TEXT, text="_"),
                RuleSegment(type=SegmentType.EXTRACT, label="姓名", extract_field="姓名"),
                RuleSegment(type=SegmentType.TEXT, text="_"),
                RuleSegment(type=SegmentType.EXTRACT, label="作业", extract_field="作业编号"),
            ],
            "计科-大学号姓名": [
                RuleSegment(type=SegmentType.EXTRACT, label="大学号", extract_field="大学号"),
                RuleSegment(type=SegmentType.TEXT, text="_"),
                RuleSegment(type=SegmentType.EXTRACT, label="姓名", extract_field="姓名"),
            ],
            "医学-学号姓名": [
                RuleSegment(type=SegmentType.TEXT, text="医"),
                RuleSegment(type=SegmentType.EXTRACT, label="学号", extract_field="学号"),
                RuleSegment(type=SegmentType.TEXT, text="_"),
                RuleSegment(type=SegmentType.EXTRACT, label="姓名", extract_field="姓名"),
            ],
            "专业课程-序号": [
                RuleSegment(type=SegmentType.EXTRACT, label="专业", extract_field="专业"),
                RuleSegment(type=SegmentType.TEXT, text="_"),
                RuleSegment(type=SegmentType.EXTRACT, label="课程", extract_field="课程"),
                RuleSegment(type=SegmentType.TEXT, text="作业"),
                RuleSegment(type=SegmentType.COUNTER, label="序号", counter_start=1, counter_padding=2),
            ],
        }

        for name, segs in builtins.items():
            path = os.path.join(self._dir, f"{name}.json")
            if not os.path.exists(path):
                self.save(name, segs)
