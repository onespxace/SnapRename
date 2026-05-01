"""Tests for rename engine."""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from models.file_item import FileItem
from models.rule_segment import RuleSegment, SegmentType
from core.renamer import RenameEngine


class TestRenameEngine:
    """Name generation from rule segments."""

    def setup_method(self):
        self.engine = RenameEngine()

    def test_text_only(self):
        f = FileItem(path="C:/test/a.docx")
        segs = [RuleSegment(type=SegmentType.TEXT, text="prefix_")]
        name = self.engine.generate_name(f, segs)
        assert name == "prefix_.docx"

    def test_counter_padded(self):
        f = FileItem(path="C:/test/a.pdf")
        segs = [RuleSegment(type=SegmentType.COUNTER, counter_start=1, counter_padding=3)]
        name = self.engine.generate_name(f, segs, index=5)
        assert name == "005.pdf"

    def test_text_and_counter(self):
        f = FileItem(path="C:/test/old.txt")
        segs = [
            RuleSegment(type=SegmentType.TEXT, text="作业", position=0),
            RuleSegment(type=SegmentType.COUNTER, counter_start=1, counter_padding=2, position=1),
        ]
        name = self.engine.generate_name(f, segs, index=3)
        assert name == "作业03.txt"

    def test_extract_field(self):
        f = FileItem(path="C:/test/张三_报告.docx")
        f.extracted_fields = {"姓名": "张三"}
        segs = [RuleSegment(type=SegmentType.EXTRACT, extract_field="姓名")]
        name = self.engine.generate_name(f, segs)
        assert name == "张三.docx"

    def test_sanitize_removes_invalid_chars(self):
        f = FileItem(path="C:/test/a.txt")
        segs = [RuleSegment(type=SegmentType.TEXT, text='file<name>:test?.txt')]
        name = self.engine.generate_name(f, segs)
        # The extension .txt comes from the original file, not the text
        assert '<' not in name
        assert '>' not in name
        assert ':' not in name
        assert '?' not in name

    def test_multiple_segments_ordered(self):
        f = FileItem(path="C:/test/x.doc")
        f.extracted_fields = {"姓名": "张三", "学号": "2023001"}
        segs = [
            RuleSegment(type=SegmentType.EXTRACT, extract_field="学号", position=0),
            RuleSegment(type=SegmentType.TEXT, text="_", position=1),
            RuleSegment(type=SegmentType.EXTRACT, extract_field="姓名", position=2),
        ]
        name = self.engine.generate_name(f, segs)
        assert name == "2023001_张三.doc"

    def test_conflict_detection(self):
        f1 = FileItem(path="C:/test/a.docx")
        f2 = FileItem(path="C:/test/b.docx")
        files = [f1, f2]
        rename_map = {f1.path: "same.docx", f2.path: "same.docx"}
        conflicts = self.engine.check_conflicts(files, rename_map)
        assert len(conflicts) > 0

    def test_no_conflict_when_unique(self):
        f1 = FileItem(path="C:/test/a.docx")
        f2 = FileItem(path="C:/test/b.docx")
        files = [f1, f2]
        rename_map = {f1.path: "x.docx", f2.path: "y.docx"}
        conflicts = self.engine.check_conflicts(files, rename_map)
        assert len(conflicts) == 0


if __name__ == "__main__":
    import pytest
    pytest.main([__file__, "-v"])
