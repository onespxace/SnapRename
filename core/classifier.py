"""Classifier — groups files by field values with grade auto-detection."""

from __future__ import annotations
from datetime import datetime
from models.file_item import FileItem


def compute_grade(big_id: str) -> str:
    """Compute grade level (大一~大四) from 大学号 prefix vs current date."""
    if not big_id:
        return "未知"
    now = datetime.now()
    # Determine current academic year start
    if now.month >= 9:
        current_academic_year = now.year
    else:
        current_academic_year = now.year - 1
    # Extract enrollment year from 大学号
    for l in (4, 2):
        prefix = big_id[:l]
        if prefix.isdigit():
            year = int(prefix)
            if year < 100:
                year += 2000
            if 2000 <= year <= now.year:
                grade = current_academic_year - year + 1
                if grade == 1:
                    return "大一"
                elif grade == 2:
                    return "大二"
                elif grade == 3:
                    return "大三"
                elif grade == 4:
                    return "大四"
                elif grade > 4:
                    return "已毕业"
                break
    return "未知"


def derive_id_prefix(big_id: str, digits: int = 2) -> str:
    """Extract first N digits of 大学号."""
    if not big_id or len(big_id) < digits:
        return big_id[:digits] if big_id else ""
    return big_id[:digits]


def group_files(
    files: list[FileItem],
    group_fields: list[str],
) -> dict[str, list[FileItem]]:
    """Group files by ordered classification fields. Returns {label: files}."""
    groups: dict[str, list[FileItem]] = {}

    for f in files:
        key_parts: list[str] = []
        for field in group_fields:
            if field == "年级":
                bid = f.extracted_fields.get("大学号") or f.extracted_fields.get("学号", "")
                key_parts.append(compute_grade(bid))
            elif field == "大学号前2位":
                bid = f.extracted_fields.get("大学号") or f.extracted_fields.get("学号", "")
                key_parts.append(derive_id_prefix(bid, 2))
            elif field == "大学号前4位":
                bid = f.extracted_fields.get("大学号") or f.extracted_fields.get("学号", "")
                key_parts.append(derive_id_prefix(bid, 4))
            elif field == "大学号前6位":
                bid = f.extracted_fields.get("大学号") or f.extracted_fields.get("学号", "")
                key_parts.append(derive_id_prefix(bid, 6))
            else:
                val = f.extracted_fields.get(field, "未知")
                key_parts.append(val)

        key = "｜".join(key_parts) if key_parts else "全部"
        groups.setdefault(key, []).append(f)

    return groups


def get_classify_fields(files: list[FileItem]) -> list[str]:
    """Return available classification fields."""
    base = {"年级", "大学号前2位", "大学号前4位", "大学号前6位"}
    for f in files:
        base.update(f.extracted_fields.keys())
    return sorted(base)
