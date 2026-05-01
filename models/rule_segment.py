from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Any


class SegmentType(Enum):
    TEXT = auto()
    COUNTER = auto()
    DATE = auto()
    EXTRACT = auto()
    TABLE_FIELD = auto()
    KEYWORD = auto()


@dataclass
class RuleSegment:
    type: SegmentType
    label: str = ""

    # TEXT
    text: str = ""

    # COUNTER
    counter_start: int = 1
    counter_step: int = 1
    counter_padding: int = 0

    # DATE
    date_format: str = "%Y%m%d"

    # EXTRACT
    extract_field: str = ""
    extract_regex: str = ""
    extract_min_len: int = 1
    extract_max_len: int = 64
    extract_allow_alpha: bool = True
    extract_allow_digit: bool = False
    extract_keywords_before: str = ""
    extract_keywords_after: str = ""

    # TABLE_FIELD
    table_column: str = ""

    # KEYWORD — comma-separated keywords, extract surrounding text
    keyword_list: str = ""
    keyword_range: int = 3  # chars before/after keyword to extract

    # Display / state
    position: int = 0
    selected: bool = False

    def __post_init__(self):
        if not self.label:
            self.label = self._default_label()

    def _default_label(self) -> str:
        labels = {
            SegmentType.TEXT: "固定文本",
            SegmentType.COUNTER: "序号",
            SegmentType.DATE: "日期",
            SegmentType.EXTRACT: "自动识别",
            SegmentType.TABLE_FIELD: "表格字段",
            SegmentType.KEYWORD: "关键词",
        }
        return labels.get(self.type, "未知")

    def to_dict(self) -> dict[str, Any]:
        return {
            "type": self.type.name,
            "label": self.label,
            "text": self.text,
            "counter_start": self.counter_start,
            "counter_step": self.counter_step,
            "counter_padding": self.counter_padding,
            "date_format": self.date_format,
            "extract_field": self.extract_field,
            "extract_regex": self.extract_regex,
            "extract_min_len": self.extract_min_len,
            "extract_max_len": self.extract_max_len,
            "extract_allow_alpha": self.extract_allow_alpha,
            "extract_allow_digit": self.extract_allow_digit,
            "extract_keywords_before": self.extract_keywords_before,
            "extract_keywords_after": self.extract_keywords_after,
            "table_column": self.table_column,
            "keyword_list": self.keyword_list,
            "keyword_range": self.keyword_range,
        }

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> RuleSegment:
        return cls(
            type=SegmentType[d["type"]],
            label=d.get("label", ""),
            text=d.get("text", ""),
            counter_start=d.get("counter_start", 1),
            counter_step=d.get("counter_step", 1),
            counter_padding=d.get("counter_padding", 0),
            date_format=d.get("date_format", "%Y%m%d"),
            extract_field=d.get("extract_field", ""),
            extract_regex=d.get("extract_regex", ""),
            extract_min_len=d.get("extract_min_len", 1),
            extract_max_len=d.get("extract_max_len", 64),
            extract_allow_alpha=d.get("extract_allow_alpha", True),
            extract_allow_digit=d.get("extract_allow_digit", False),
            extract_keywords_before=d.get("extract_keywords_before", ""),
            extract_keywords_after=d.get("extract_keywords_after", ""),
            table_column=d.get("table_column", ""),
            keyword_list=d.get("keyword_list", ""),
            keyword_range=d.get("keyword_range", 3),
        )
