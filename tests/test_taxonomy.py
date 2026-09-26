#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
test_taxonomy.py: 黄金编译器语言矩阵与淘汰技术栈测试
"""

import unittest
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from core.taxonomy import GOLDEN_COMPILER_STACKS, DISCARDED_STACKS, get_golden_summary_table


class TestTaxonomy(unittest.TestCase):
    """测试黄金技术栈与淘汰语言台账"""

    def test_golden_stacks_properties(self):
        self.assertGreaterEqual(len(GOLDEN_COMPILER_STACKS), 5)
        for key, item in GOLDEN_COMPILER_STACKS.items():
            self.assertIn("name", item)
            self.assertIn("roi_score", item)
            self.assertIn("necessity_score", item)
            self.assertIn("ai_synthesis_pass_rate", item)
            self.assertIn("compile_ram_mb", item)
            self.assertIn("runtime_ram_mb", item)
            # 刚性契约：ROI >= 8 或 必要性 >= 9
            self.assertTrue(item["roi_score"] >= 8.0 or item["necessity_score"] >= 9.0)

    def test_discarded_stacks_have_rationales(self):
        self.assertGreaterEqual(len(DISCARDED_STACKS), 5)
        for key in ["JAVA", "SCALA", "PHP", "RUBY", "HASKELL"]:
            self.assertIn(key, DISCARDED_STACKS)
            self.assertTrue(len(DISCARDED_STACKS[key]["reason"]) > 0)
            self.assertTrue(len(DISCARDED_STACKS[key]["details"]) > 0)

    def test_summary_table_generation(self):
        tbl = get_golden_summary_table()
        self.assertIn("Go (Golang)", tbl)
        self.assertIn("Rust", tbl)
        self.assertIn("TypeScript", tbl)
        self.assertIn("Python", tbl)


if __name__ == "__main__":
    unittest.main()
