"""Smart filename field extractor — uses pattern library, disambiguation, blacklist."""

from __future__ import annotations
from collections import defaultdict
from models.file_item import FileItem
from py_engine.patterns import PATTERNS, FieldPattern, SURNAMES, derive_small_id
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
                if pat.name in ("学号", "大学号") and not value.isdigit():
                    continue

                if is_blacklisted(value) and pat.name not in ("专业", "课程"):
                    continue
                if pat.name not in ("作业编号", "专业", "课程") and is_noise(value):
                    continue

                confidence = self._score(pat, value)
                extractions.append(Extraction(
                    field=pat.name,
                    value=value,
                    start=m.start(),
                    end=m.end(),
                    confidence=confidence,
                    priority=pat.priority,
                ))

        # Resolve overlaps
        resolved = resolve_overlaps(extractions)

        # Post-processing: if 专业 matches same text as a longer 课程, prefer 课程
        for ex in list(resolved):
            if ex.field == "专业":
                for orig in extractions:
                    if orig.field == "课程" and ex.overlaps(orig) and len(orig.value) > len(ex.value):
                        if ex in resolved:
                            resolved.remove(ex)
                        if orig not in resolved:
                            resolved.append(orig)
                        break

        # Convert to dict — avoid duplicate 大学号+学号
        result: dict[str, str] = {}
        has_big_id = False
        big_id_value = ""
        for ex in resolved:
            name = ex.field
            value = ex.value

            # Skip 学号 if it overlaps with 大学号 range
            if name == "学号" and has_big_id and value in big_id_value:
                continue
            if name == "大学号":
                has_big_id = True
                big_id_value = value

            if name == "姓名" and value[0] not in SURNAMES and "姓名" in result:
                continue
            if name not in result:
                result[name] = ex.value
            elif len(value) > len(result[name]) and ex.confidence > 0.3:
                result[name] = ex.value
            elif name == "姓名" and value[0] in SURNAMES and result[name][0] not in SURNAMES:
                result[name] = ex.value

        # Derive 小学号 from 大学号 (if no table takes priority)
        if "大学号" in result and "小学号" not in result:
            result["小学号"] = derive_small_id(result["大学号"])

        # Cache values
        for k, v in result.items():
            self._field_cache[k].add(v)

        return filter_blacklist(result)

    def _score(self, pat: FieldPattern, value: str) -> float:
        """Compute confidence score for a match."""
        if pat.name == "姓名":
            return score_chinese_name(value)
        if pat.name == "大学号":
            return self._score_big_id(value)
        if pat.name == "学号":
            return score_student_id(value)
        if pat.name == "班级":
            return score_class_id(value)
        if pat.name == "专业":
            return 0.85
        if pat.name == "课程":
            return 0.65
        if pat.name in ("日期",):
            return 0.95
        if pat.name in ("作业编号",):
            return 0.85
        if pat.name == "编号":
            return 0.30
        return 0.5

    def _score_big_id(self, value: str) -> float:
        """Score how likely value is a full school ID (大学号)."""
        n = len(value)
        if n >= 12:
            return 0.95
        if n >= 10:
            return 0.93
        return 0.60

    def _deduplicate_field(self, name: str, value: str, result: dict[str, str]) -> tuple[str, str]:
        if name not in result:
            return name, value
        return name, value

    def get_available_fields(self, files: list[FileItem]) -> list[str]:
        """Return unique field names found across all files."""
        fields: set[str] = set()
        for f in files:
            fields.update(f.extracted_fields.keys())
        # Remove auto-suffixed duplicates like 姓名_1
        clean = {k for k in fields if not (k.rsplit("_", 1)[-1].isdigit() and len(k) > 3)}
        return sorted(clean)

    def get_field_values(self, field_name: str) -> list[str]:
        return sorted(self._field_cache.get(field_name, set()))
