#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
tests/test_pipeline.py: Tests for cross-tool meta pipeline orchestration.
"""
import unittest
import os
import sys
import tempfile
from pathlib import Path

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from core.pipeline_runner import MetaToolchainPipeline


class TestPipeline(unittest.TestCase):

    def test_pipeline_on_temporary_repo(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            p_core = Path(tmpdir) / "core"
            p_core.mkdir(parents=True)
            (p_core / "tool.py").write_text("""
import sys
import math

def calculate(x):
    return x * 2
""", encoding="utf-8")

            # Run pipeline
            res = MetaToolchainPipeline.run_pipeline(tmpdir)
            self.assertEqual(res["target_input"], tmpdir)
            self.assertIsNotNone(res["phase_stack_optima"])
            self.assertEqual(res["phase_stack_optima"]["profile"]["dominant_language"], "Python")

            # Render markdown
            md = MetaToolchainPipeline.render_markdown(res)
            self.assertIn("工业软件母机全域协同审计报告", md)
            self.assertIn("物理事实", md)


if __name__ == "__main__":
    unittest.main()
