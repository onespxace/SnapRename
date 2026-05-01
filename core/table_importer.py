"""Table importer — reads CSV and Excel files for name/ID cross-referencing."""

from __future__ import annotations

import os
import csv


class TableImporter:
    """Import table data from CSV or Excel files."""

    def import_file(self, path: str) -> tuple | None:
        """Import a CSV or Excel file. Returns (DataFrame, column_names) or None."""
        ext = os.path.splitext(path)[1].lower()
        try:
            if ext == ".csv":
                return self._import_csv(path)
            elif ext in (".xlsx", ".xls"):
                return self._import_excel(path)
        except Exception:
            return None
        return None

    def _import_csv(self, path: str) -> tuple | None:
        try:
            import pandas as pd
            df = pd.read_csv(path)
            return df, list(df.columns)
        except ImportError:
            return self._import_csv_fallback(path)

    def _import_csv_fallback(self, path: str) -> tuple | None:
        """Fallback CSV reader without pandas."""
        try:
            import pandas as pd
            with open(path, "r", encoding="utf-8-sig") as f:
                reader = csv.DictReader(f)
                rows = list(reader)
            if not rows:
                return None
            df = pd.DataFrame(rows)
            return df, list(df.columns)
        except Exception:
            return None

    def _import_excel(self, path: str) -> tuple | None:
        try:
            import pandas as pd
            df = pd.read_excel(path)
            return df, list(df.columns)
        except ImportError:
            return None
