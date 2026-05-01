"""Tests for data models."""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

from models.rule_segment import RuleSegment, SegmentType
from models.file_item import FileItem


class TestRuleSegment:
    """RuleSegment serialization and defaults."""

    def test_text_segment_defaults(self):
        seg = RuleSegment(type=SegmentType.TEXT, text="hello")
        assert seg.label == "固定文本"
        assert seg.text == "hello"

    def test_counter_defaults(self):
        seg = RuleSegment(type=SegmentType.COUNTER, counter_start=10, counter_padding=3)
        assert seg.label == "序号"
        assert seg.counter_start == 10
        assert seg.counter_padding == 3

    def test_extract_defaults(self):
        seg = RuleSegment(type=SegmentType.EXTRACT, extract_field="学号")
        assert seg.label == "自动识别"
        assert seg.extract_field == "学号"
        assert seg.extract_min_len == 1
        assert seg.extract_max_len == 64

    def test_roundtrip(self):
        seg = RuleSegment(type=SegmentType.EXTRACT, extract_field="姓名",
                          extract_min_len=2, extract_max_len=4,
                          extract_allow_alpha=False)
        d = seg.to_dict()
        restored = RuleSegment.from_dict(d)
        assert restored.type == SegmentType.EXTRACT
        assert restored.extract_field == "姓名"
        assert restored.extract_min_len == 2
        assert restored.extract_max_len == 4
        assert restored.extract_allow_alpha is False

    def test_all_types_roundtrip(self):
        for st in SegmentType:
            seg = RuleSegment(type=st, text="x", extract_field="f", table_column="c",
                              counter_start=5, counter_padding=2)
            d = seg.to_dict()
            restored = RuleSegment.from_dict(d)
            assert restored.type == st


class TestFileItem:
    """FileItem creation and properties."""

    def test_auto_name_from_path(self):
        f = FileItem(path="C:/test/张三_作业1.docx")
        assert f.original_name == "张三_作业1.docx"

    def test_preserve_original_name(self):
        f = FileItem(path="C:/test/report.pdf", original_name="custom.pdf")
        assert f.original_name == "custom.pdf"

    def test_get_ext(self):
        assert FileItem.get_ext("test.docx") == ".docx"
        assert FileItem.get_ext("noext") == ""
        assert FileItem.get_ext("a.b.c.txt") == ".txt"

    def test_get_stem(self):
        assert FileItem.get_stem("test.docx") == "test"
        assert FileItem.get_stem("张三_作业1.pdf") == "张三_作业1"

    def test_new_path(self):
        f = FileItem(path="C:/dir/old.docx")
        f.new_name = "new.docx"
        expected = os.path.join("C:/dir", "new.docx")
        assert f.new_path() == expected


if __name__ == "__main__":
    import pytest
    pytest.main([__file__, "-v"])
