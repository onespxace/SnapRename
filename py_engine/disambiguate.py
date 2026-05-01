"""Disambiguation — resolve overlapping matches, surname check, confidence score."""

from __future__ import annotations
from dataclasses import dataclass
from py_engine.patterns import SURNAMES
from py_engine.blacklist import is_blacklisted, is_noise


@dataclass
class Extraction:
    field: str
    value: str
    start: int
    end: int
    confidence: float = 0.0
    priority: int = 0

    @property
    def span(self) -> tuple[int, int]:
        return (self.start, self.end)

    def overlaps(self, other: Extraction) -> bool:
        return self.start < other.end and other.start < self.end


def resolve_overlaps(extractions: list[Extraction]) -> list[Extraction]:
    """Resolve overlapping matches — higher priority wins, then higher confidence.
    Different field types can coexist at the same position."""
    if not extractions:
        return []
    sorted_ex = sorted(extractions, key=lambda e: (e.start, -e.priority, -e.confidence))
    result: list[Extraction] = []
    for ex in sorted_ex:
        if result and ex.overlaps(result[-1]):
            if ex.field == result[-1].field:
                if ex.priority > result[-1].priority:
                    result[-1] = ex
                elif ex.priority == result[-1].priority and ex.confidence > result[-1].confidence:
                    result[-1] = ex
            else:
                result.append(ex)
        else:
            result.append(ex)
    return result


def score_chinese_name(value: str) -> float:
    score = 0.0
    if len(value) == 2:
        score += 0.4
    elif len(value) == 3:
        score += 0.5
    elif len(value) == 4:
        score += 0.2
    else:
        return 0.0
    if value[0] in SURNAMES:
        score += 0.4
    common_given = set("伟芳娜秀英敏静丽强磊洋勇军杰涛明超平刚华文辉玲桂兰凤梅红鑫斌峰乐建中华秀丽慧峰云海波燕鹏飞龙")
    if len(value) >= 2 and any(c in common_given for c in value[1:]):
        score += 0.1
    return min(score, 1.0)


def score_student_id(value: str) -> float:
    score = 0.0
    n = len(value)
    if 8 <= n <= 12:
        score += 0.7
        if value.startswith(("20", "19", "18")):
            score += 0.2
    elif 6 <= n <= 7:
        score += 0.6
    return min(score, 1.0)


def score_class_id(value: str) -> float:
    if len(value) >= 4:
        return 0.8
    return 0.4
