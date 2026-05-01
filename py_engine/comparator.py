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
        mapping: dict[int, int | None] = {}
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
        for col in df.columns:
            if col in candidates or col.lower() in {c.lower() for c in candidates}:
                return col
        return None

    def _find_match(
        self, file_name: str, file_sid: str,
        table_names: list[str], table_sids: list[str],
    ) -> int | None:
        for j in range(max(len(table_names), len(table_sids))):
            row_name = table_names[j] if j < len(table_names) else ""
            row_sid = table_sids[j] if j < len(table_sids) else ""
            if self._is_match(file_name, file_sid, row_name, row_sid):
                return j
        return None

    @staticmethod
    def _is_match(file_name: str, file_sid: str, row_name: str, row_sid: str) -> bool:
        if file_sid and row_sid and file_sid.strip() == row_sid.strip():
            return True
        if file_name and row_name and (file_name in row_name or row_name in file_name):
            return True
        return False
