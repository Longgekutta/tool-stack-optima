#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
tests/test_v2_evolutions.py: Tests for HotspotProfiler and DifferentialTester.
"""
import os
import sys
import unittest
import tempfile
from pathlib import Path

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from core.code_profiler_flame import HotspotProfiler
from core.differential_tester import DifferentialTester


class TestV2Evolutions(unittest.TestCase):

    def test_hotspot_profiler_on_minimal_script(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            script = Path(tmpdir) / "work.py"
            script.write_text("""
def compute():
    total = 0
    for i in range(1000):
        total += i
    return total

if __name__ == '__main__':
    compute()
""", encoding="utf-8")

            res = HotspotProfiler.profile_target(
                tmpdir,
                custom_cmd=f'"{sys.executable}" work.py'
            )

            self.assertTrue(res["success"])
            self.assertGreater(res["total_calls"], 0)
            self.assertGreaterEqual(len(res["top_cumulative_hotspots"]), 1)
            markdown = HotspotProfiler.render_markdown(res)
            self.assertIn("高精热点剖析报告", markdown)

    def test_differential_tester_on_mock_bridge(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            bridge = Path(tmpdir) / "bridge_glue.py"
            bridge.write_text("""
def is_native_accelerated():
    return False

def execute_accelerated_task(payload: bytes) -> bytes:
    return payload
""", encoding="utf-8")

            res = DifferentialTester.run_differential_test(tmpdir, iterations=100)
            self.assertTrue(res["success"])
            self.assertEqual(res["iterations_tested"], 100)
            self.assertEqual(res["counterexamples_count"], 0)
            self.assertFalse(res["is_native_accelerated"])

            markdown = DifferentialTester.render_markdown(res)
            self.assertIn("双轨差分模糊测试与语义等价性报告", markdown)
            self.assertIn("PASS (完全一致)", markdown)


if __name__ == "__main__":
    unittest.main()
