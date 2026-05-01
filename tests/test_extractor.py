"""Tests for smart filename extractor."""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from py_engine.extractor import SmartExtractor


class TestSmartExtractor:
    """Filename field extraction."""

    def setup_method(self):
        self.ext = SmartExtractor()

    def test_extract_student_id(self):
        fields = self.ext.extract("张三_2023001_作业1.docx")
        assert "学号" in fields
        assert fields["学号"] == "2023001"

    def test_extract_chinese_name(self):
        fields = self.ext.extract("计算机科学与技术_张三_作业1.docx")
        assert "姓名" in fields
        assert fields["姓名"] == "张三"

    def test_extract_date(self):
        fields = self.ext.extract("实验报告_2024-03-15_张三.docx")
        assert "日期" in fields
        assert "2024-03-15" in fields["日期"]

    def test_extract_homework_number(self):
        fields = self.ext.extract("张三_作业2.docx")
        assert "作业编号" in fields
        assert fields["作业编号"] == "2"

    def test_typo_name_still_extracts_id(self):
        """学号提取不受错别字影响."""
        fields = self.ext.extract("章三_2023001_报告.docx")
        assert "学号" in fields
        assert fields["学号"] == "2023001"

    def test_mixed_chinese_english(self):
        fields = self.ext.extract("Wang_计算机_实验报告3.docx")
        assert "英文名" in fields

    def test_no_fields_in_plain_text(self):
        fields = self.ext.extract("report.docx")
        # Should not crash, may find nothing
        assert isinstance(fields, dict)

    def test_get_available_fields(self):
        from models.file_item import FileItem
        f1 = FileItem(path="a.docx")
        f1.extracted_fields = self.ext.extract("张三_2023001_作业1.docx")
        f2 = FileItem(path="b.docx")
        f2.extracted_fields = self.ext.extract("李四_2023002_作业2.docx")
        fields = self.ext.get_available_fields([f1, f2])
        assert "学号" in fields
        assert "姓名" in fields


if __name__ == "__main__":
    import pytest
    pytest.main([__file__, "-v"])
